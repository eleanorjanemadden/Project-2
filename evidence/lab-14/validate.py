"""Reproducible known-answer and actual script mutation checks."""
import csv
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import portfolio as p

ROOT = Path(__file__).resolve().parent


def main():
    cov = p.covariance_matrix(p.VOLATILITIES, p.CORRELATIONS)
    known = [([0, 0, 40, 60], 6.80, 10.46, 0.0, True),
             ([25, 25, 25, 25], 5.20, 5.21, 50.0, False),
             ([84.3, 6.0, 7.0, 2.6], 3.77, 1.05, 90.3, False)]
    for (name, w), (weights, ret, vol, reserve, meets) in zip(p.baseline_weights().items(), known):
        assert [round(x * 100, 1) for x in w] == weights
        assert math.isclose(sum(w), 1)
        assert round(p.expected_return(w, p.RETURNS) * 100, 2) == ret
        assert round(p.portfolio_volatility(w, cov) * 100, 2) == vol
        assert round(p.reserve_weight(w, p.RESERVE_ELIGIBLE) * 100, 1) == reserve
        assert p.meets_objective(p.expected_return(w, p.RETURNS), p.OBJECTIVE) == meets
        print(f'PASS known answer: {name}, including every displayed value')
    source = (ROOT / 'portfolio.py').read_text()
    scenarios = [
        ('Correlation 0.50 in both cells', source.replace('0.25', '0.50'), 0, 'Volatility: 11.00%'),
        ('Correlation 1.3 in both cells', source.replace('0.25', '1.3'), 1, 'must be between -1 and 1'),
        ('Asymmetric correlation', source.replace('[0.05, 0.80, 1.00, 0.25]', '[0.05, 0.80, 1.00, 0.50]'), 1, 'must be symmetric'),
    ]
    for label, code, expected_code, expected_text in scenarios:
        with tempfile.TemporaryDirectory() as folder:
            script = Path(folder) / 'portfolio.py'
            script.write_text(code)
            run = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
        assert run.returncode == expected_code, run.stderr
        assert expected_text in run.stdout + run.stderr
        print(f'PASS {label}; exit {run.returncode}')
        print(run.stdout + run.stderr)
    assert (ROOT / 'portfolio.py').read_text() == source
    print('PASS original correlations restored/unchanged at 0.25')
    run = subprocess.check_output([sys.executable, str(ROOT / 'mandate.py')], text=True)
    e = run.split('Candidate E')[1]
    assert 'Reserve-eligible weight: 0.0% — FAIL' in e
    assert 'fails 1 rule(s)' in e
    print('PASS benchmark candidate E fails reserve rule, all other implemented rules pass')
    rows = list(csv.DictReader((ROOT / 'prices.csv').open()))
    assert len(rows) == 60 and list(rows[0]) == ['Date', 'BIL', 'IEF', 'LQD', 'VT']
    months = [f'{year}-{month:02}-01' for year in range(2021, 2027) for month in range(1, 13)
              if '2021-10-01' <= f'{year}-{month:02}-01' < '2026-10-01']
    assert [row['Date'] for row in rows] == months
    assert all(math.isfinite(float(row[t])) and float(row[t]) > 0 for row in rows for t in ['BIL', 'IEF', 'LQD', 'VT'])
    print('PASS prices.csv: 60 consecutive months, oldest first, unique dates, four positive complete series')


if __name__ == '__main__':
    main()
