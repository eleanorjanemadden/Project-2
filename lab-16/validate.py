"""Independent known-answer checks and a temporary-file later-date run."""
from pathlib import Path
import subprocess
import sys
import tempfile
import asof

root = Path(__file__).resolve().parent
panel, naive, funnel = asof.filter_rows(asof.TABLE, asof.DECISION_DATE)
assert [removed for _, removed in funnel] == [[11], [7], [3, 8, 10], [2]]
assert [row[0] for row in panel] == [1, 4, 5, 6, 9, 12]
actual = asof.signals(panel)
comparison = asof.signals(naive)
expected = {"AAA": ("2026-02", 1.98), "BBB": ("2026-02", -1.02), "CCC": ("2026-02", 0.91)}
expected_naive = {"AAA": ("2026-03", 5.83), "BBB": ("2026-03", -5.15), "CCC": ("2026-02", 1.82)}
for ticker in expected:
    assert (actual[ticker][0], round(actual[ticker][1], 2)) == expected[ticker]
    assert (comparison[ticker][0], round(comparison[ticker][1], 2)) == expected_naive[ticker]
print("PASS: all four funnel steps, all six panel rows, and all six known signals.")
source = (root / "asof.py").read_text()
with tempfile.TemporaryDirectory() as directory:
    changed = Path(directory) / "asof.py"
    changed.write_text(source.replace('DECISION_DATE = "2026-03-31"', 'DECISION_DATE = "2026-04-15"'))
    result = subprocess.run([sys.executable, str(changed)], capture_output=True, text=True, check=True)
    (root / "outputs" / "later_date_run.txt").write_text(result.stdout)
    for ticker, signal in comparison.items():
        text = asof.format_signal(signal)
        assert f"{ticker}: as-of {text}; naive {text}" in result.stdout
assert (root / "asof.py").read_text() == source
assert asof.DECISION_DATE == "2026-03-31"
print("PASS: edited temporary file to April 15; all three as-of signals equal naive signals.")
print("PASS: submitted file remains at March 31; later-date output saved.")
# Check publication boundary and order independence for the revision step.
boundary, _, _ = asof.filter_rows(asof.TABLE, "2026-03-25")
assert 4 in [row[0] for row in boundary] and 2 not in [row[0] for row in boundary]
assert asof.latest_publications(list(reversed(panel)))[0] == panel
print("PASS: same-day publication is included; revision selection does not require input sorting.")
print("ALL CHECKS PASSED")
