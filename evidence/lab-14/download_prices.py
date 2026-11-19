"""Download Yahoo monthly adjusted closes; retain unmodified JSON evidence."""
import csv
import datetime as dt
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
TICKERS = ['BIL', 'IEF', 'LQD', 'VT']
# Sixty completed months; October 2026 is still in progress.
START = '2021-10-01'
END = '2026-10-01'


def main():
    series = {}
    for ticker in TICKERS:
        start = int(dt.datetime.fromisoformat(START).replace(tzinfo=dt.timezone.utc).timestamp())
        end = int(dt.datetime.fromisoformat(END).replace(tzinfo=dt.timezone.utc).timestamp())
        url = (f'https://query2.finance.yahoo.com/v8/finance/chart/{ticker}'
               f'?period1={start}&period2={end}&interval=1mo&includeAdjustedClose=true')
        raw = subprocess.check_output(['curl', '--fail', '-Ls', '-A', 'Mozilla/5.0', url])
        result = json.loads(raw)['chart']['result'][0]
        (ROOT / 'data' / f'{ticker}_yahoo.json').write_bytes(raw)
        adjusted = result['indicators']['adjclose'][0]['adjclose']
        rows = {}
        for timestamp, price in zip(result['timestamp'], adjusted):
            month = dt.datetime.fromtimestamp(timestamp, dt.timezone.utc).strftime('%Y-%m-01')
            if START <= month < END:
                if price is None or price <= 0:
                    raise ValueError(f'{ticker}: missing/nonpositive adjusted close {month}')
                if month in rows:
                    raise ValueError(f'{ticker}: duplicate month {month}')
                rows[month] = price
        assert len(rows) == 60, (ticker, len(rows))
        series[ticker] = rows
        print(f'{ticker}: {result["meta"].get("longName", ticker)}; 60 months; source {url}')
    dates = sorted(series[TICKERS[0]])
    assert all(sorted(series[t]) == dates for t in TICKERS)
    with (ROOT / 'prices.csv').open('w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Date'] + TICKERS)
        writer.writerows([date] + [series[t][date] for t in TICKERS] for date in dates)
    print(f'Downloaded {dt.datetime.now(dt.timezone.utc).isoformat()}')
    print(f'prices.csv: {len(dates)} complete monthly rows, {dates[0]} through {dates[-1]}; no missing values.')
    print('Dates label months; values are Yahoo monthly Adj Close, USD. Current partial month excluded.')


if __name__ == '__main__':
    main()
