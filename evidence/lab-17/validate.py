"""Run live checks and save their evidence: python3 validate.py."""
from datetime import date, timedelta
from pathlib import Path
import html
import json
import re

import pandas as pd
import requests
from streamlit.testing.v1 import AppTest
from asof_app import download_today, download_asof, compare_series, parse_csv

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
DATA = ROOT / "data"
OUT.mkdir(exist_ok=True)
DATA.mkdir(exist_ok=True)
TODAY = date.today()
manifest, lines, comparisons = [], [], []


def log(message):
    print(message, flush=True)
    lines.append(message)


def get(series_id, vintage=None):
    values = download_today(series_id, TODAY) if vintage is None else download_asof(series_id, vintage, TODAY)
    filename = f"{series_id}_{vintage or 'today'}.csv"
    (DATA / filename).write_text(values.attrs["raw_csv"])
    manifest.append({"file": f"data/{filename}", "url": values.attrs["url"], "downloaded": values.attrs["downloaded"]})
    return values


def run():
    log(f"LIVE LAB 17 VALIDATION — downloaded {TODAY}")
    expected = {"BAA": ("2026-09-01", 6.47), "FEDFUNDS": ("2026-09-01", 3.75),
                "DGS10": ("2026-10-02", 5.28), "MORTGAGE30US": ("2026-10-01", 7.28)}
    for series_id, (last_date, value) in expected.items():
        current, known = get(series_id), get(series_id, date(2026, 10, 5))
        row = compare_series(series_id, current, known)
        assert row["Last measured as known"] == last_date, row
        assert row["Value as known"] == value, row
        comparisons.append({"As known on": "2026-10-05", **row})
        log(f"PASS known answer: {series_id}: {last_date}, {value:.2f}; later={row['Later values']}, revised={row['Revised values']}")
    current, known = get("PAYEMS"), get("PAYEMS", date(2025, 1, 15))
    row = compare_series("PAYEMS", current, known)
    assert row["Last measured as known"] == "2024-12-01"
    assert row["Value as known"] == 159536
    december_today = float(current.loc["2024-12-01"])
    assert december_today < 159536 and row["Revised values"] > 10
    comparisons.append({"As known on": "2025-01-15", **row})
    log(f"PASS PAYEMS: Dec 2024 known=159,536; same month today={december_today:,.0f}; difference={december_today-159536:,.0f} thousand jobs; revised dates={row['Revised values']}")
    pd.concat([known.rename("known_2025_01_15"), current.rename("today")], axis=1).loc["2020-01-01":].to_csv(OUT / "payems_revisions.csv")
    current = get("GS10")
    prior_end = TODAY.replace(day=1) - timedelta(days=1)
    for vintage in [prior_end, TODAY]:
        known = get("GS10", vintage)
        row = compare_series("GS10", current, known)
        comparisons.append({"As known on": str(vintage), **row})
        log(f"GS10 as of {vintage}: last={row['Last measured as known']}, value={row['Value as known']:.2f}%; later={row['Later values']}; revised={row['Revised values']}")
    # Probe first availability around the month-end; do not assume a fixed lag.
    previous = get("GS10", date(2026, 9, 30))
    first = get("GS10", date(2026, 10, 1))
    assert pd.Timestamp("2026-09-01") not in previous.dropna().index
    assert first.loc["2026-09-01"] == 4.99
    log("PASS GS10 publication boundary: September absent Sep 30; 4.99 present Oct 1.")
    # Independent source-page check: read the displayed recent-observations table.
    url = "https://fred.stlouisfed.org/series/GS10"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    (DATA / "GS10_fred_page.html").write_text(response.text)
    text = html.unescape(re.sub(r"<[^>]+>", " ", response.text))
    text = re.sub(r"\s+", " ", text)
    checks = []
    for month, observation, value in [("Jul 2026", "2026-07-01", 4.60), ("Aug 2026", "2026-08-01", 4.68), ("Sep 2026", "2026-09-01", 4.99)]:
        assert re.search(re.escape(month) + r"\s*:\s*" + f"{value:.2f}", text), f"Not displayed: {month}"
        actual = float(current.loc[observation])
        assert actual == value
        checks.append({"Month measured": month, "FRED page percent": value, "Downloaded percent": actual, "Match": True})
        log(f"PASS source-page cross-check: {month}: page={value:.2f}%, CSV={actual:.2f}%")
    pd.DataFrame(checks).to_csv(OUT / "three_value_checks.csv", index=False)
    # Small independent cases check the meaning of counts and missingness.
    old = parse_csv("observation_date,X_20200103\n2020-01-01,1\n2020-01-02,.\n2020-01-03,3\n", "X", date(2020, 1, 3))
    new = parse_csv("observation_date,X\n2020-01-01,2\n2020-01-02,.\n2020-01-03,3\n2020-01-04,4\n", "X")
    synthetic = compare_series("X", new, old)
    assert old.isna().sum() == 1
    assert synthetic["Later values"] == 1 and synthetic["Revised values"] == 1
    empty = compare_series("X", new, old.iloc[:0])
    assert empty["Value as known"] is None and empty["Later values"] == 3
    log("PASS counts, missing-day handling, and empty vintage edge case.")
    app = AppTest.from_file(str(ROOT / "asof_app.py"), default_timeout=120).run()
    assert not app.exception and not app.error, app.exception
    assert len(app.get("vega_lite_chart")) == 4
    assert len(app.dataframe[0].value) == 4
    assert app.sidebar.date_input[0].value == date(2020, 1, 1)
    assert app.sidebar.date_input[1].value == TODAY
    app.sidebar.date_input[1].set_value(date(2026, 10, 5)).run()
    assert not app.exception and not app.error
    for _, result in app.dataframe[0].value.iterrows():
        series_id = result["Series"].rsplit("/", 1)[-1]
        assert (result["Last measured as known"], result["Value as known"]) == expected[series_id]
    app.sidebar.text_input[0].set_value("GS10").run()
    assert not app.exception and not app.error and len(app.dataframe[0].value) == 5
    app.sidebar.text_input[0].set_value("THISISNOTAFREDSERIES43900").run()
    assert not app.exception and len(app.error) == 1 and len(app.dataframe[0].value) == 4
    app.sidebar.multiselect[0].set_value([]).run()
    app.sidebar.text_input[0].set_value("").run()
    assert not app.exception and len(app.dataframe) == 0
    log("PASS executed Streamlit UI: four default charts/table, defaults, October known answers, typed GS10, unknown-ID isolation, empty selection.")
    pd.DataFrame(comparisons).to_csv(OUT / "asof_comparisons.csv", index=False)
    (DATA / "download_manifest.json").write_text(json.dumps(manifest, indent=2))
    log("ALL CHECKS PASSED — actual downloads, no hard-coded app results.")


if __name__ == "__main__":
    try:
        run()
    finally:
        (OUT / "validation_run.txt").write_text("\n".join(lines) + "\n")
