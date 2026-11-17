"""Executed engine and Streamlit checks. Run: python3 validate.py."""
import contextlib
import csv
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
import portfolio as p

ROOT = Path(__file__).resolve().parent


def check(condition, description):
    assert condition, description
    print('PASS:', description)


def run_search(returns=p.RETURNS, correlations=p.CORRELATIONS, objective=.065,
               eligible=p.RESERVE_ELIGIBLE, minimum=.03):
    return p.search_portfolio(returns, p.VOLATILITIES, correlations,
                              objective, eligible, minimum)


def main():
    # Same main function and output as the preserved GitHub engine.
    old = subprocess.check_output([sys.executable, str(ROOT / 'instructions/lab14_portfolio.py')])
    new = subprocess.check_output([sys.executable, str(ROOT / 'portfolio.py')])
    check(old == new, 'Lab 14 printed output preserved byte for byte')
    a = run_search()
    b = run_search(p.RETURNS[:-1] + [.07])
    check(a['weights'] == [0, .2, .25, .55] and
          f"{a['return']:.2%}" == '6.51%' and f"{a['volatility']:.2%}" == '9.44%',
          'Meridian as loaded: 0/20/25/55, 6.51%, 9.44%')
    check(b['weights'] == [0, .1, .1, .8] and
          f"{b['return']:.2%}" == '6.53%' and f"{b['volatility']:.2%}" == '12.94%',
          'Meridian equity 7%: 0/10/10/80, 6.53%, 12.94%')
    check(round(max(abs(x-y) for x,y in zip(a['weights'], b['weights']))*100) == 25,
          'Meridian largest change = 25 percentage points')
    check(run_search(objective=.09) is None, 'Infeasible objective returns None')
    check(run_search(eligible=[False]*4) is None, 'Positive reserve with no eligible assets is infeasible')
    check(run_search(eligible=[False]*4, minimum=0) is not None, 'Zero reserve permits no eligible assets')
    for n in [3, 6]:
        r=p.search_portfolio([.1]*n,[.1]*n,[[float(i==j) for j in range(n)] for i in range(n)],
                             .1,[False]*n,0)
        check(abs(sum(r['weights'])-1)<1e-12 and min(r['weights'])>=0,
              f'{n}-asset search fully invested and long-only')
    # Independent pandas cross-check of sample statistics.
    import pandas as pd
    df=pd.read_csv(ROOT/'prices.csv', index_col=0)
    for last in [False, True]:
        x=p.estimate_from_csv(ROOT/'prices.csv', last)
        monthly=df.pct_change().dropna()
        if last: monthly=monthly.tail(36)
        check(x['months']==len(monthly) and
              max(abs(v-w) for v,w in zip(x['returns'], monthly.mean()*12))<1e-12 and
              max(abs(v-w) for v,w in zip(x['volatilities'], monthly.std()*12**.5))<1e-12 and
              max(abs(x['correlations'][i][j]-monthly.corr().iloc[i,j])
                  for i in range(4) for j in range(4))<1e-12,
              f'CSV estimates match independent pandas calculation; last_36={last}')
    rows=list(csv.reader((ROOT/'prices.csv').open()))
    import datetime as dt
    for index,ticker in enumerate(rows[0][1:],1):
        raw=json.loads((ROOT/'data'/f'{ticker}_yahoo.json').read_text())['chart']['result'][0]
        source={dt.datetime.fromtimestamp(t,dt.timezone.utc).strftime('%Y-%m-01'):v
                for t,v in zip(raw['timestamp'],raw['indicators']['adjclose'][0]['adjclose'])}
        check(all(float(row[index])==source[row[0]] for row in rows[1:]),
              f'{ticker}: every price matches retained Yahoo response')
    check(len(rows)==61,'60 price rows retained, producing 59 returns')
    for bad in ['Date,A,B,C\n2024-02-01,1,2,3\n2024-01-01,2,3,4\n2024-03-01,3,4,5',
                'Date,A,B,C\n2024-01-01,1,2,3\n2024-02-01,nan,3,4\n2024-03-01,3,4,5']:
        try: p.estimate_from_csv(io.StringIO(bad))
        except ValueError: pass
        else: raise AssertionError('Invalid CSV accepted')
    check(True,'Unordered/missing-month and nonfinite-price CSVs rejected')
    # Run the real app, modify a widget, and check the rendered results.
    at=AppTest.from_file(str(ROOT/'app.py'), default_timeout=20).run()
    check(not at.exception,'Streamlit starts without an exception')
    check('60.00' in at.table[0].value.to_string(), 'Project 2 snapshot is the default view')
    next(w for w in at.checkbox if w.label == "Use included Project 2 prices.csv").set_value(False).run()
    check('9.44%' in '\n'.join(x.value for x in at.markdown), 'App displays training volatility')
    next(w for w in at.number_input if w.label == "Global equity index fund return estimate (%)").set_value(7.0).run()
    check(not at.exception and at.metric[0].value=='25.00' and
          '12.94%' in '\n'.join(x.value for x in at.markdown),
          'App widget stress displays 12.94% and 25.00-point change')
    next(w for w in at.checkbox if w.label == "Use included Project 2 prices.csv").set_value(True).run()
    check(not at.exception and '60.00' in at.table[0].value.to_string(),
          'Bundled CSV loads in the app')
    next(w for w in at.checkbox if w.label == "Last 36 months").set_value(True).run()
    check(not at.exception and at.metric[0].value=='25.00' and
          '85.00' in at.table[0].value.to_string(),
          '36-month app switch displays 85% BIL and 25.00-point change')
    # Upload path (same bytes, separate Streamlit input).
    with patch('streamlit.delta_generator.DeltaGenerator.file_uploader', return_value=io.BytesIO((ROOT/'prices.csv').read_bytes())):
        uploaded=AppTest.from_file(str(ROOT/'app.py'),default_timeout=20).run()
    check(not uploaded.exception and '60.00' in uploaded.table[0].value.to_string(),
          'Uploaded CSV bytes load through the uploader path')
    next(w for w in at.number_input if w.label == "Objective (%)").set_value(50.0).run()
    check(not at.exception and len(at.warning)==2 and
          all(x.value=='no mix meets the objective' for x in at.warning),
          'App reports infeasibility without lowering the objective')
    # Edit the actual engine file in an isolated copy; app must change on reload.
    with tempfile.TemporaryDirectory() as folder:
        temp=Path(folder)
        for name in ['app.py','portfolio.py','prices.csv']:
            shutil.copy2(ROOT/name,temp/name)
        source=(temp/'portfolio.py').read_text()
        changed=source.replace('[0.05, 0.80, 1.00, 0.25]', '[0.05, 0.80, 1.00, 0.50]').replace(
                               '[0.00, -0.10, 0.25, 1.00]', '[0.00, -0.10, 0.50, 1.00]')
        assert changed!=source
        (temp/'portfolio.py').write_text(changed)
        # Separate interpreter prevents imports from this validation session leaking in.
        program="""from streamlit.testing.v1 import AppTest
at=AppTest.from_file('app.py',default_timeout=20).run()
assert not at.exception
next(w for w in at.checkbox if w.label == "Use included Project 2 prices.csv").set_value(False).run()
assert not at.exception
text='\\n'.join(x.value for x in at.markdown)
assert '9.73%' in text and '6.52%' in text, text
assert list(at.table[0].value['Weight (%)'])==['0.00','40.00','0.00','60.00']
"""
        subprocess.run([sys.executable,'-c',program],cwd=temp,check=True,capture_output=True)
    check(True,'Saved engine correlation 0.50 changes actual app to 0/40/0/60, 6.52%, 9.73%')
    check(p.CORRELATIONS[2][3]==p.CORRELATIONS[3][2]==.25,'Submitted engine restored to 0.25')
    print('All checks passed.')


if __name__=='__main__':
    main()
