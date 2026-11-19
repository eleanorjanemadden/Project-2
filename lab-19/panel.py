"""FIN43900 legend panel: shared SEC facts, calculations in code, judgment in memos."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import buffett

EXTRA_TAGS = {'liabilities': ['Liabilities'], 'current_assets': ['AssetsCurrent'],
              'current_liabilities': ['LiabilitiesCurrent']}
LABELS = {**buffett.LABELS, 'liabilities': 'Liabilities', 'current_assets': 'Current assets',
          'current_liabilities': 'Current liabilities', 'current_ratio': 'Current ratio',
          'liabilities_equity': 'Liabilities / equity'}
RATIOS = {'current_ratio', 'liabilities_equity'}
INVESTORS = ('Buffett', 'Graham', 'Burry')
GRAHAM_CURRENT_RATIO = 2.0


def check(values, condition, complete=True):
    """Missing required input takes priority over a conclusion from partial data."""
    if not complete or any(value is None for value in values):
        return 'not known'
    return 'pass' if condition(values) else 'fail'


def graham_checks(rows, threshold=GRAHAM_CURRENT_RATIO):
    """Latest liquidity, annual profit stability, and endpoint profit growth."""
    latest = rows[-1]
    income = [row['net_income'] for row in rows]
    complete = len(rows) == 5
    return {
        f'Current ratio of {threshold:g} or more, latest year':
            check([latest['current_ratio']], lambda v: v[0] >= threshold),
        'Net income positive every year':
            check(income, lambda v: all(x > 0 for x in v), complete),
        'Net income grew, first year to last':
            check([income[0], income[-1]], lambda v: v[-1] > v[0], complete),
    }


def burry_checks(rows):
    pairs = [(row['operating_cash_flow'], row['net_income']) for row in rows]
    inputs = [value for pair in pairs for value in pair]
    return {
        'Operating cash flow at least net income every year':
            check(inputs, lambda v: all(ocf >= ni for ocf, ni in pairs), len(rows) == 5),
        'Liabilities no more than twice equity, latest year':
            check([rows[-1]['liabilities_equity']], lambda v: v[0] <= 2),
    }


def screen(facts, ticker, threshold=GRAHAM_CURRENT_RATIO):
    # Preserve Lab 18's annual selection, tag precedence, and Buffett checks.
    result = buffett.screen(facts, ticker)
    for row in result['rows']:
        end = row['fiscal_year_end']
        for metric, tags in EXTRA_TAGS.items():
            row[metric], row['provenance'][metric] = buffett.choose_fact(facts, tags, end, flow=False)
        ca, cl = row['current_assets'], row['current_liabilities']
        liabilities, equity = row['liabilities'], row['equity']
        row['current_ratio'] = ca / cl if ca is not None and cl is not None and cl > 0 else None
        row['liabilities_equity'] = liabilities / equity if liabilities is not None and equity is not None and equity > 0 else None
        row['provenance']['current_ratio'] = {'tag': 'derived: us-gaap:AssetsCurrent / us-gaap:LiabilitiesCurrent'}
        row['provenance']['liabilities_equity'] = {'tag': 'derived: us-gaap:Liabilities / us-gaap:StockholdersEquity'}
    result['panel'] = {'Buffett': result['checks'], 'Graham': graham_checks(result['rows'], threshold),
                       'Burry': burry_checks(result['rows'])}
    result['graham_threshold'] = threshold
    result['units'] = 'USD millions; ROE percent; current ratio and liabilities / equity multiples'
    return result


def display_value(metric, value):
    if metric in RATIOS:
        return 'not known' if value is None else f'{value:.2f}'
    return buffett.display_value(metric, value)


def table_rows(result):
    return [{'Fiscal year end': row['fiscal_year_end'],
             **{label: display_value(metric, row[metric]) for metric, label in LABELS.items()}}
            for row in result['rows']]


def panel_rows(result):
    return [{'Investor': investor, 'Check': name, 'Result': status}
            for investor, checks in result['panel'].items() for name, status in checks.items()]


def summaries(result):
    return {investor: {'pass': sum(v == 'pass' for v in checks.values()),
                       'fail': sum(v == 'fail' for v in checks.values()),
                       'not known': sum(v == 'not known' for v in checks.values()),
                       'total': len(checks)} for investor, checks in result['panel'].items()}


def evidence(result):
    lines = ['Amounts in USD millions. ROE in percent. Ratios are multiples.',
             f"Thresholds: ROE >= 15%; owner earnings > 0; current ratio >= {result['graham_threshold']:.1f}; net income > 0; liabilities / equity <= 2."]
    for row in table_rows(result):
        lines.append(' | '.join(f'{key}: {value}' for key, value in row.items()))
    for row in panel_rows(result):
        lines.append(' | '.join(row.values()))
    for investor, counts in summaries(result).items():
        lines.append(f"{investor}: {counts['pass']} of {counts['total']} pass; {counts['fail']} fail; {counts['not known']} not known.")
    return '\n'.join(lines)


def fingerprint(result):
    # Bind to the full computation and provenance, including threshold and raw inputs.
    return hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()


def unsupported_numbers(memo, result):
    allowed = {buffett.number_key(m.group()) for m in buffett.NUMBER.finditer(evidence(result))}
    return [{'number': m.group().strip(), 'position': m.start()}
            for m in buffett.NUMBER.finditer(memo) if buffett.number_key(m.group()) not in allowed]


def memo_flags(memos, result):
    return [{'Investor': investor, **flag} for investor, memo in memos.items()
            for flag in unsupported_numbers(memo, result)]


def report(result):
    lines = [f"# {result['ticker']} — {result['company']}", evidence(result), '', 'XBRL sources (USD):']
    for row in result['rows']:
        lines.append(row['fiscal_year_end'])
        for metric, label in LABELS.items():
            source = row['provenance'][metric]
            detail = (f"; period {source.get('start', 'instant')} to {source['end']}; filed {source['filed']}; accession {source.get('accn', 'not found')}" if 'end' in source else '')
            lines.append(f"  {label}: {display_value(metric, row[metric])}; {source['tag']}" + detail)
    return '\n'.join(lines) + '\n'


def save(result, output_dir, suffix=''):
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = result['ticker'] + suffix
    (output_dir / f'{stem}_results.json').write_text(json.dumps(result, indent=2) + '\n')
    (output_dir / f'{stem}_run.txt').write_text(report(result))
    for name, rows in [('table', table_rows(result)), ('panel', panel_rows(result))]:
        with (output_dir / f'{stem}_{name}.csv').open('w', newline='') as out:
            writer = csv.DictWriter(out, fieldnames=list(rows[0]))
            writer.writeheader(); writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ticker')
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--dns-fallback', action='store_true', help='Optional HTTPS DNS fallback for this workspace.')
    parser.add_argument('--data-dir', type=Path, default=Path('data'))
    parser.add_argument('--output-dir', type=Path, default=Path('outputs'))
    parser.add_argument('--investor', choices=INVESTORS, help='Identify the skill whose memo will be written from the shared report.')
    parser.add_argument('--graham-threshold', type=float, default=GRAHAM_CURRENT_RATIO)
    parser.add_argument('--memo', type=Path)
    args = parser.parse_args()
    if args.graham_threshold < 0:
        parser.error('Current-ratio threshold cannot be negative.')
    if args.dns_fallback:
        from network import enable_dns_fallback
        enable_dns_fallback()
    ticker = buffett.clean_ticker(args.ticker)
    facts = json.loads((args.data_dir / f'{ticker}_companyfacts.json').read_text()) if args.offline else buffett.download(ticker, args.data_dir)
    result = screen(facts, ticker, args.graham_threshold)
    suffix = '' if args.graham_threshold == GRAHAM_CURRENT_RATIO else f'_threshold_{args.graham_threshold:g}'
    save(result, args.output_dir, suffix)
    print(report(result))
    if args.investor:
        print('Memo perspective:', args.investor)
    if args.memo:
        flags = unsupported_numbers(args.memo.read_text(), result)
        print('Memo unsupported numbers:', json.dumps(flags))
        if flags:
            raise SystemExit(1)


if __name__ == '__main__':
    main()
