"""Reproduce the submitted estimates, allocations and mandate-checker output."""
import contextlib
import csv
import io
import json
from pathlib import Path
import portfolio as p
import mandate

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs'
ELIGIBLE = [True, True, False, False]
OBJECTIVE = .065
MINIMUM = .03


def main():
    OUT.mkdir(exist_ok=True)
    results = {}
    training = {}
    for name, returns, correlations in [
        ('as_loaded', p.RETURNS, p.CORRELATIONS),
        ('equity_minus_one', p.RETURNS[:-1] + [.07], p.CORRELATIONS),
        ('correlation_050', p.RETURNS,
         [row[:2] + ([1.0, .50] if i == 2 else [.50, 1.0])
          if i in (2, 3) else row[:] for i, row in enumerate(p.CORRELATIONS)])]:
        training[name] = p.search_portfolio(returns, p.VOLATILITIES,
                                            correlations, OBJECTIVE, ELIGIBLE, MINIMUM)
    results['training'] = training
    for name, last in [('all_months', False), ('last_36', True)]:
        x = p.estimate_from_csv(ROOT / 'prices.csv', last)
        answer = p.search_portfolio(x['returns'], x['volatilities'], x['correlations'],
                                   OBJECTIVE, ELIGIBLE, MINIMUM)
        stressed = x['returns'].copy()
        stressed[-1] -= .01
        attack = p.search_portfolio(stressed, x['volatilities'], x['correlations'],
                                   OBJECTIVE, ELIGIBLE, MINIMUM)
        results[name] = {'estimates': x, 'answer': answer, 'VT_minus_one': attack}
        with (OUT / f'{name}_estimates.csv').open('w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['Asset', 'Annual_return_estimate', 'Annual_volatility_estimate'])
            w.writerows(zip(x['assets'], x['returns'], x['volatilities']))
        with (OUT / f'{name}_correlations.csv').open('w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['Asset'] + x['assets'])
            w.writerows([a] + row for a, row in zip(x['assets'], x['correlations']))
    (OUT / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
    with (OUT / 'allocations.csv').open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Run', 'BIL_or_bills', 'IEF_or_note', 'LQD_or_IG', 'VT_or_equity',
                    'Return_estimate', 'Volatility', 'Reserve_weight'])
        for name, answer in training.items():
            w.writerow([name] + answer['weights'] + [answer['return'], answer['volatility'], answer['reserve']])
        for name in ['all_months', 'last_36']:
            for label in ['answer', 'VT_minus_one']:
                a = results[name][label]
                w.writerow([name + '_' + label] + a['weights'] + [a['return'], a['volatility'], a['reserve']])
    # Feed every new mix into the existing checker, mapping ETF roles to course holdings.
    candidates = dict(training)
    for name in ['all_months', 'last_36']:
        candidates[name] = results[name]['answer']
        candidates[name + '_attack'] = results[name]['VT_minus_one']
    mandate.CANDIDATES = tuple(candidates)
    mapping = {'Treasury bills': 0, 'Treasury 10-year note': 1,
               'Investment-grade bond fund': 2, 'Global equity index fund': 3}
    mandate.WEIGHTS = {holding: tuple(a['weights'][mapping[holding]] * 100
                       if holding in mapping else 0 for a in candidates.values())
                       for holding, _, _, _ in mandate.HOLDINGS}
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        mandate.main()
    (OUT / 'mandate_search_run.txt').write_text(buffer.getvalue())
    for name, group in results.items():
        print(name)
        if name == 'training':
            for label, a in group.items():
                print(label, a)
        else:
            print('answer', group['answer'])
            print('VT minus one point', group['VT_minus_one'])
    print('All estimated mixes mapped by role into the existing mandate checker.')
    print('See outputs/mandate_search_run.txt; ETF settlement/eligibility are draft mandate assumptions.')


if __name__ == '__main__':
    main()
