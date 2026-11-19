"""SEC-only Buffett screen. Dollar amounts are displayed in USD millions."""
import argparse
from datetime import date, datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import time

import requests

TAGS = {
    'revenue': ['RevenueFromContractWithCustomerExcludingAssessedTax', 'Revenues'],
    'net_income': ['NetIncomeLoss'],
    'operating_cash_flow': ['NetCashProvidedByUsedInOperatingActivities'],
    'capital_spending': ['PaymentsToAcquirePropertyPlantAndEquipment', 'PaymentsToAcquireProductiveAssets'],
    'equity': ['StockholdersEquity'],
}
LABELS = {'revenue': 'Revenue', 'net_income': 'Net income',
          'operating_cash_flow': 'Operating cash flow', 'capital_spending': 'Capital spending',
          'equity': 'Equity', 'roe': 'ROE %', 'owner_earnings': 'Owner earnings'}
USER_AGENT = 'Eleanor Madden madden42@purdue.edu FIN43900 academic project'


def get_json(url, path):
    """Preserve the exact SEC response, with its URL, time and checksum."""
    response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=45)
    response.raise_for_status()
    data = response.json()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(response.content)
    record = {'url': url, 'retrieved_utc': datetime.now(timezone.utc).isoformat(),
              'user_agent': USER_AGENT, 'sha256': hashlib.sha256(response.content).hexdigest()}
    path.with_suffix('.source.json').write_text(json.dumps(record, indent=2)+'\n')
    time.sleep(0.2)
    return data


def download(ticker, data_dir):
    ticker = clean_ticker(ticker)
    mapping = get_json('https://www.sec.gov/files/company_tickers.json', data_dir / 'company_tickers.json')
    match = next((x for x in mapping.values() if x['ticker'].upper() == ticker), None)
    if match is None:
        raise ValueError(f'Ticker {ticker} not found in the SEC ticker file.')
    cik = int(match['cik_str'])
    return get_json(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json',
                    data_dir / f'{ticker}_companyfacts.json')


def clean_ticker(ticker):
    ticker = ticker.strip().upper()
    if not re.fullmatch(r'[A-Z][A-Z0-9.-]{0,14}', ticker):
        raise ValueError('Enter one ticker using letters, digits, periods or hyphens.')
    return ticker


def annual(fact):
    """Accept normal calendar years and retail 52/53-week years, never quarters/YTD."""
    if fact.get('form') != '10-K' or not fact.get('start'):
        return False
    days = (date.fromisoformat(fact['end']) - date.fromisoformat(fact['start'])).days + 1
    return 350 <= days <= 380


def records(facts, tag):
    return facts.get('facts', {}).get('us-gaap', {}).get(tag, {}).get('units', {}).get('USD', [])


def choose_fact(facts, tags, end, flow):
    """Tag precedence first, then latest filing for this exact annual period/end."""
    for tag in tags:
        candidates = [x for x in records(facts, tag)
                      if x.get('form') == '10-K' and x.get('end') == end
                      and (annual(x) if flow else not x.get('start'))]
        if candidates:
            chosen = max(candidates, key=lambda x: (x['filed'], x.get('accn', '')))
            return chosen['val'], {'tag': f'us-gaap:{tag}', **chosen}
    return None, {'tag': 'not found', 'searched': [f'us-gaap:{t}' for t in tags]}


def year_row(facts, end):
    """Turn one fiscal-year-end into a row; no imputation or bank-specific substitutions."""
    row = {'fiscal_year_end': end, 'provenance': {}}
    for metric, tags in TAGS.items():
        value, source = choose_fact(facts, tags, end, flow=metric != 'equity')
        row[metric] = value
        row['provenance'][metric] = source
    income, equity = row['net_income'], row['equity']
    row['roe'] = income / equity * 100 if income is not None and equity is not None and equity > 0 else None
    ocf, capex = row['operating_cash_flow'], row['capital_spending']
    row['owner_earnings'] = ocf - capex if ocf is not None and capex is not None else None
    row['provenance']['roe'] = {'tag': 'derived: us-gaap:NetIncomeLoss / us-gaap:StockholdersEquity × 100'}
    row['provenance']['owner_earnings'] = {'tag': 'derived: '+row['provenance']['operating_cash_flow']['tag']+' − '+row['provenance']['capital_spending']['tag']}
    return row


def screen(facts, ticker):
    ends = sorted({x['end'] for tags in TAGS.values() for tag in tags
                   for x in records(facts, tag) if annual(x)})[-5:]
    if not ends:
        raise ValueError('No annual USD 10-K facts found; cannot construct a fiscal-year table.')
    rows = [year_row(facts, end) for end in ends]
    def check(values, condition):
        return 'not known' if len(rows) != 5 or any(v is None for v in values) else ('pass' if condition(values) else 'fail')
    roe = [r['roe'] for r in rows]
    owner = [r['owner_earnings'] for r in rows]
    checks = {
        'ROE of 15% or more every year': check(roe, lambda a: all(v >= 15 for v in a)),
        'Owner earnings positive every year': check(owner, lambda a: all(v > 0 for v in a)),
        'Owner earnings grew, first year to last': check([owner[0], owner[-1]], lambda a: a[-1] > a[0]),
    }
    return {'ticker': clean_ticker(ticker), 'company': facts['entityName'], 'cik': facts['cik'],
            'units': 'USD millions; ROE percent', 'rows': rows, 'checks': checks}


def display_value(metric, value):
    if value is None:
        return 'not known' if metric == 'roe' else 'not found'
    return f'{value:.1f}%' if metric == 'roe' else f'{value / 1_000_000:,.3f}'.rstrip('0').rstrip('.')


def table_rows(result):
    return [{'Fiscal year end': r['fiscal_year_end'],
             **{LABELS[k]: display_value(k, r[k]) for k in LABELS}} for r in result['rows']]


def evidence(result):
    """Only displayed financial values, dates and explicit check thresholds are authorized."""
    lines = ['Amounts in USD millions. ROE in percent. Thresholds: ROE >= 15%; owner earnings > 0.']
    for row in table_rows(result):
        lines.append(' | '.join(f'{k}: {v}' for k, v in row.items()))
    lines.extend(f'{k}: {v}' for k, v in result['checks'].items())
    return '\n'.join(lines)


def fingerprint(result):
    return hashlib.sha256(evidence(result).encode()).hexdigest()


# Keep a date intact; keep percent tokens distinct from dollar/plain numbers.
NUMBER = re.compile(r'\d{4}-\d{2}-\d{2}|[+−-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:[eE][+−-]?\d+)?\s*%?')


def number_key(token):
    token = token.strip().replace(',', '').replace('−', '-')
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', token):
        return ('date', token)
    percent = token.endswith('%')
    return ('percent' if percent else 'number', Decimal(token.rstrip('%').strip()))


def unsupported_numbers(memo, result):
    allowed = {number_key(m.group()) for m in NUMBER.finditer(evidence(result))}
    return [{'number': m.group().strip(), 'position': m.start()}
            for m in NUMBER.finditer(memo) if number_key(m.group()) not in allowed]


def report(result):
    lines = [f"# {result['ticker']} — {result['company']}", evidence(result), '', 'XBRL sources (USD):']
    for r in result['rows']:
        lines.append(r['fiscal_year_end'])
        for metric in LABELS:
            p = r['provenance'][metric]
            lines.append(f"  {LABELS[metric]}: {display_value(metric, r[metric])}; {p['tag']}"
                         + (f"; period {p.get('start', 'instant')} to {p['end']}; filed {p['filed']}; accession {p.get('accn', 'not found')}" if 'end' in p else ''))
    return '\n'.join(lines)+'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ticker')
    parser.add_argument('--data-dir', type=Path, default=Path('data'))
    parser.add_argument('--output-dir', type=Path, default=Path('outputs'))
    parser.add_argument('--offline', action='store_true', help='Use an explicitly saved SEC download.')
    parser.add_argument('--memo', type=Path, help='Check a model-written Markdown memo.')
    args = parser.parse_args()
    ticker = clean_ticker(args.ticker)
    facts = json.loads((args.data_dir / f'{ticker}_companyfacts.json').read_text()) if args.offline else download(ticker, args.data_dir)
    result = screen(facts, ticker)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / f'{ticker}_results.json').write_text(json.dumps(result, indent=2)+'\n')
    text = report(result)
    (args.output_dir / f'{ticker}_run.txt').write_text(text)
    print(text)
    if args.memo:
        flags = unsupported_numbers(args.memo.read_text(), result)
        print('Memo unsupported numbers:', json.dumps(flags))
        if flags:
            raise SystemExit(1)


if __name__ == '__main__':
    main()
