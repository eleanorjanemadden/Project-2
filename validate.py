"""Executed engine and Streamlit checks. Run: python3 validate.py."""
import contextlib
import csv
from datetime import date
from decimal import Decimal
import io
import json
from itertools import product
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
import gs10
import portfolio as p

ROOT = Path(__file__).resolve().parent


def check(condition, description):
    assert condition, description
    print('PASS:', description)


def run_search(returns=p.RETURNS, correlations=p.CORRELATIONS, objective=.065,
               eligible=p.RESERVE_ELIGIBLE, minimum=.03):
    return p.search_portfolio(returns, p.VOLATILITIES, correlations,
                              objective, eligible, minimum)


def check_comparison(at, monthly, constrained_weights, *, estimates=None,
                     eligible=(True, True, False, False), minimum=.03, cost=0):
    """Compare the actual displayed rows with calculations from raw returns."""
    import numpy as np

    table = at.dataframe[0].value.set_index("Measure or rule")
    covariance = monthly.cov().to_numpy() * 12
    returns = monthly.mean().to_numpy() * 12 if estimates is None else estimates
    inverse = 1 / np.sqrt(covariance.diagonal())
    names = ["Equal-weight baseline", "Inverse-volatility baseline", "Constrained portfolio"]
    assert list(table.columns) == names
    for name, weights in zip(names, (
        np.full(len(returns), 1 / len(returns)),
        inverse / inverse.sum(),
        np.array(constrained_weights),
    )):
        estimated_return = weights @ returns
        volatility = np.sqrt(weights @ covariance @ weights)
        after_cost = estimated_return - cost
        reserve = weights @ np.array(eligible)
        expected = {
            **{f"{asset} weight": f"{weight:.2%}" for asset, weight in zip(monthly.columns, weights)},
            "Annual return before additional cost": f"{estimated_return:.2%}",
            "Annual return after additional cost": f"{after_cost:.2%}",
            "Estimated annual volatility": f"{volatility:.2%}",
            "Reserve-eligible weight": f"{reserve:.2%}",
            "Fully invested (100%)": "Pass",
            "Long-only weights": "Pass",
            "After-cost return screen (≥ 6.50%)": "Pass" if after_cost >= .065 - 1e-12 else "Fail",
            f"Reserve allocation (≥ {minimum:.2%})": "Pass" if reserve >= minimum - 1e-12 else "Fail",
            "Project 2 universe (BIL, IEF, LQD, VT)": "Pass",
            "Liquidity (≥ 90% within 5 business days)": "Unresolved",
            "Company issuer limit (≤ 8%, subject to exemptions)": "Unresolved",
            "Live borrowing, short sales and derivatives restrictions": "Unresolved",
            "Rolling five-year net return objective (CPI + 4%)": "Unresolved",
        }
        assert table[name].to_dict() == expected, (name, table[name].to_dict(), expected)
    return table


def check_cost_scenarios(at, monthly):
    """Independently enumerate and score every four-asset allocation on the grid."""
    import numpy as np

    scenarios = at.dataframe[1].value
    covariance = monthly.cov().to_numpy() * 12
    returns = monthly.mean().to_numpy() * 12
    grid = np.array([units for units in product(range(21), repeat=4) if sum(units) == 20]) / 20
    grid_reserves = grid[:, :2].sum(axis=1)
    grid_returns = grid @ returns
    grid_variances = np.einsum("ij,jk,ik->i", grid, covariance, grid)
    inverse = 1 / np.sqrt(covariance.diagonal())
    expected = []
    for bps in (0, 25, 50, 100):
        cost = bps / 10_000
        feasible = np.flatnonzero((grid_returns - cost >= .065 - 1e-12)
                                 & (grid_reserves >= .03 - 1e-12))
        assert len(feasible), bps
        best = feasible[np.argmin(grid_variances[feasible])]
        for name, weights in (
            ("Equal-weight baseline", np.full(4, .25)),
            ("Inverse-volatility baseline", inverse / inverse.sum()),
            ("Constrained portfolio", grid[best]),
        ):
            before = weights @ returns
            after = before - cost
            expected.append({
                "Annual cost (bps)": bps,
                "Portfolio": name,
                "Weights": ", ".join(f"{asset} {weight:.2%}"
                                     for asset, weight in zip(monthly.columns, weights)),
                "Return before cost": f"{before:.2%}",
                "Return after cost": f"{after:.2%}",
                "Volatility": f"{np.sqrt(weights @ covariance @ weights):.2%}",
                "Reserve weight": f"{sum(weights[:2]):.2%}",
                "After-cost screen": "Pass" if after >= .065 - 1e-12 else "Fail",
            })
    assert scenarios.to_dict("records") == expected, scenarios.to_string()
    return scenarios


def check_gs10(at):
    september = date(2026, 9, 1)
    cutoffs = {
        date(2026, 9, 30): (date(2026, 8, 1), Decimal("4.68")),
        date(2026, 10, 1): (september, Decimal("4.99")),
        date(2026, 10, 29): (september, Decimal("4.99")),
    }
    vintages = gs10.saved_vintages()
    check(vintages.keys() == cutoffs.keys(), 'GS10 offers exactly the dated Lab 17 ALFRED vintages')
    snapshots = {cutoff: gs10.read_vintage(cutoff) for cutoff in cutoffs}
    before, after, later = snapshots.values()
    check(september not in before and after[september] == Decimal("4.99"),
          'September GS10 is absent September 30 and present in the October 1 vintage')
    for next_snapshot in (after, later):
        check(next_snapshot.keys() - before.keys() == {september}
              and all(next_snapshot[month] == before[month] for month in before),
              'Later GS10 vintage adds September with zero revisions to shared months')
    comparison = at.dataframe[0].value.copy()
    readouts = []
    for cutoff, (month, value) in cutoffs.items():
        records = snapshots[cutoff]
        check(max(records) == month and records[month] == value,
              f'{cutoff} saved GS10 observation is {month:%B %Y} at {value}% per annum')
        at.selectbox[0].set_value(cutoff).run()
        lines = [node.value for node in at.markdown]
        captions = [node.value for node in at.caption]
        signal = next(line for line in lines if line.startswith("**Decision cutoff:**"))
        source = next(line for line in lines if line.startswith("Source: Federal Reserve Board"))
        check(not at.exception and f"**Decision cutoff:** {cutoff}" in signal
              and f"**Latest observation in the cutoff vintage:** {month:%B %Y}" in signal
              and f"**Signal value:** {value}% per annum" in signal
              and f"**ALFRED vintage date:** {cutoff}" in signal
              and vintages[cutoff]["url"] in source and "Lab_17.md#r--represent-my-data-card" in source
              and any("Monitoring only." in line for line in captions)
              and any("Same-day pre-trade availability is unresolved." in line for line in captions),
              f'{cutoff} app displays the cutoff, observation, value, units, vintage, source and timing caveat')
        check(at.dataframe[0].value.equals(comparison),
              f'{cutoff} GS10 selection leaves the portfolio comparison unchanged')
        readouts.append((signal, source))

    with patch('gs10.read_vintage', side_effect=FileNotFoundError("saved test vintage")):
        at.run()
    check(not at.exception and any("GS10 is unresolved" in item.value for item in at.warning)
          and not any("**Signal value:**" in item.value for item in at.markdown)
          and at.dataframe[0].value.equals(comparison),
          'Missing GS10 evidence reports unresolved without substituting a value or changing weights')
    at.selectbox[0].set_value(next(iter(cutoffs))).run()
    return readouts


def main():
    for invalid_cost in (-.01, float("inf"), float("nan")):
        try:
            p.search_portfolio(p.RETURNS, p.VOLATILITIES, p.CORRELATIONS, .065,
                               p.RESERVE_ELIGIBLE, .03, additional_cost=invalid_cost)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid cost accepted")
    check(True, 'Negative and nonfinite cost assumptions rejected')
    costs = dict(returns=[.07] * 3, volatilities=[.1] * 3,
                 correlations=[[float(i == j) for j in range(3)] for i in range(3)],
                 objective=.065, eligible=[True] * 3, reserve_minimum=.03)
    check(p.search_portfolio(**costs, additional_cost=.005) is not None and
          p.search_portfolio(**costs, additional_cost=.005001) is None,
          'An exact after-cost threshold is feasible and a higher cost makes the same grid infeasible')

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
    guidance = "\n".join(node.value for node in at.markdown)
    check("Stop the paper pilot and return to committee if the agreed reserve rule or "
          "after-cost return screen becomes infeasible." in guidance
          and "A weight shift above five percentage points keeps live adoption deferred." in guidance,
          'App distinguishes the pilot stop rule from the live-adoption deferral threshold')
    captions = "\n".join(node.value for node in at.caption)
    check("55–85% BIL, 15–45% VT, and 0% IEF/LQD" in captions
          and "45–85% BIL, 15–55% VT, 0% IEF, and 0–5% LQD" in captions,
          'App labels both historical stress ranges separately')
    check('60.00' in at.table[0].value.to_string(), 'Project 2 snapshot is the default view')
    monthly = df.pct_change().dropna()
    gs10_readouts = check_gs10(at)
    all_months = check_comparison(at, monthly, [.60, 0, 0, .40])
    stress_all = check_cost_scenarios(at, monthly)
    check(True, 'All-month 0/25/50/100 bps tables match independent grid and baseline calculations')
    next(w for w in at.number_input if w.label == "Annual additional cost assumption (bps)").set_value(25.0).run()
    check_comparison(at, monthly, [.55, 0, 0, .45], cost=.0025)
    check(at.metric[0].value == "0.00" and
          all(list(table.value["Weight (%)"]) == ["55.00", "0.00", "0.00", "45.00"]
              for table in at.table),
          'Editable 25 bps cost reoptimizes both all-month sensitivity mixes at the unchanged objective')
    next(w for w in at.number_input if w.label == "Annual additional cost assumption (bps)").set_value(0.0).run()
    check(True, 'All-month app weights, risk, return, reserve, and verdicts agree with independent calculations')
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
    recent = monthly.tail(36)
    last_36 = check_comparison(at, recent, [.85, 0, 0, .15])
    stress_recent = check_cost_scenarios(at, recent)
    check(True, '36-month 0/25/50/100 bps tables match independent grid and baseline calculations')
    check(True, '36-month app weights, risk, return, reserve, and verdicts agree with independent calculations')
    estimates = (recent.mean() * 12).to_numpy()
    estimates[0] = .07
    next(w for w in at.number_input if w.label == "BIL return estimate (%)").set_value(7.0)
    next(w for w in at.checkbox if w.label == "IEF reserve-eligible").set_value(False).run()
    check(not at.exception, 'App accepts a return override and a reserve eligibility edit')
    check_comparison(at, recent, [1, 0, 0, 0], estimates=estimates,
                     eligible=(True, False, False, False))
    check(True, 'All three comparisons use the edited return and reserve eligibility')

    next(w for w in at.number_input if w.label == "Reserve minimum (%)").set_value(100.0).run()
    check_comparison(at, recent, [1, 0, 0, 0], estimates=estimates,
                     eligible=(True, False, False, False), minimum=1.0)
    check(True, 'A 100% reserve threshold fails both baselines and passes the all-BIL constrained mix')
    cost_widget = next(w for w in at.number_input if w.label == "Annual additional cost assumption (bps)")
    cost_widget.set_value(100.0).run()
    cost_failure = at.dataframe[0].value.set_index("Measure or rule")
    stress_failure = at.dataframe[1].value
    check(not at.exception and len(at.error) == 1 and "6.50%" in at.error[0].value
          and "Stop the paper pilot and return to committee" in at.error[0].value
          and all(cost_failure["Constrained portfolio"] == "N/A")
          and list(stress_failure.loc[
              (stress_failure["Annual cost (bps)"] == 100)
              & (stress_failure["Portfolio"] == "Constrained portfolio"),
              "After-cost screen"]) == ["Infeasible"]
          and next(w for w in at.number_input if w.label == "Objective (%)").value == 6.5,
          '100 bps makes the reserve-constrained app case infeasible while the objective stays at 6.5%')
    next(w for w in at.number_input if w.label == "Annual additional cost assumption (bps)").set_value(0.0)
    next(w for w in at.number_input if w.label == "Reserve minimum (%)").set_value(3.0).run()

    # Upload path (same bytes, separate Streamlit input).
    with patch('streamlit.delta_generator.DeltaGenerator.file_uploader', return_value=io.BytesIO((ROOT/'prices.csv').read_bytes())):
        uploaded=AppTest.from_file(str(ROOT/'app.py'),default_timeout=20).run()
    check(not uploaded.exception and '60.00' in uploaded.table[0].value.to_string(),
          'Uploaded CSV bytes load through the uploader path')
    next(w for w in at.number_input if w.label == "Objective (%)").set_value(50.0).run()
    check(not at.exception and len(at.warning)==2 and
          all('50.00% after-cost screen' in x.value for x in at.warning),
          'App reports infeasibility without lowering the objective')
    failed = at.dataframe[0].value.set_index("Measure or rule")
    check(all(failed.loc["After-cost return screen (≥ 50.00%)",
                         ["Equal-weight baseline", "Inverse-volatility baseline"]] == "Fail")
          and all(failed["Constrained portfolio"] == "N/A"),
          'Infeasible search still displays both failing baselines and leaves the constrained column unavailable')
    # Edit the actual engine file in an isolated copy; app must change on reload.
    with tempfile.TemporaryDirectory() as folder:
        temp=Path(folder)
        for name in ['app.py','portfolio.py','mandate.py','gs10.py','prices.csv']:
            shutil.copy2(ROOT/name,temp/name)
        shutil.copytree(gs10.DATA, temp / 'evidence/lab-17/data')
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
    print('\nRendered comparison, 59 monthly returns:')
    print(all_months.to_string())
    print('\nRendered comparison, 36 monthly returns:')
    print(last_36.to_string())
    print('\nRendered cost scenarios, 59 monthly returns:')
    print(stress_all.to_string(index=False))
    print('\nRendered cost scenarios, 36 monthly returns:')
    print(stress_recent.to_string(index=False))
    print('\nRendered GS10 panel, saved decision cutoffs:')
    for signal, source in gs10_readouts:
        print(signal)
        print(source)
        print()
    print('All checks passed.')


if __name__=='__main__':
    main()
