"""Build a self-contained visible report from the executed validation artifacts."""
from pathlib import Path
import base64
from datetime import datetime
from html import escape
import pandas as pd

root = Path(__file__).resolve().parent
out = root / 'outputs'
comparisons = pd.read_csv(out / 'asof_comparisons.csv')
comparisons['Series'] = comparisons['Series'].map(lambda u: f'<a href="{escape(u)}">{escape(u.rsplit("/",1)[-1])}</a>')
checks = pd.read_csv(out / 'three_value_checks.csv')
transcript = (out / 'validation_run.txt').read_text()
assert 'ALL CHECKS PASSED' in transcript
payroll = pd.read_csv(out / 'payems_revisions.csv', index_col=0).loc['2024-12-01']

def picture(name, title):
    encoded = base64.b64encode((out / name).read_bytes()).decode()
    return f'<h2>{title}</h2><img alt="{title}" src="data:image/png;base64,{encoded}">'

body = f'''<!doctype html><html lang="en"><meta charset="utf-8">
<title>Lab 17 — Executed Evidence — Eleanor Madden</title>
<style>body{{font:16px/1.5 system-ui,sans-serif;max-width:1500px;margin:40px auto;padding:0 24px;color:#202a36}}h1,h2{{color:#14384e}}.note{{padding:16px;background:#eff5f8;border-left:4px solid #246c89}}table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{padding:10px;border:1px solid #ccd7df;text-align:left}}th{{background:#edf3f6}}.scroll{{overflow-x:auto}}pre{{white-space:pre-wrap;background:#f4f6f8;padding:20px}}img{{width:100%;height:auto;border:1px solid #ccd7df}}a{{color:#155f9d}}</style>
<h1>Lab 17 — Point-in-Time Audit</h1><p>Eleanor Madden · Live evidence downloaded October 29, 2026</p>
<p class="note"><strong>All validation checks passed.</strong> Actual FRED and ALFRED downloads reproduce all four October 5 known answers and the PAYEMS revision probe. GS10 is the chosen portfolio series. This report was built from saved executed outputs, not manually entered app answers.</p>
<p>Written deliverable: <a href="../Lab_17.md">Lab_17.md</a> · App: <a href="../asof_app.py">asof_app.py</a> · <a href="../data/download_manifest.json">Download manifest</a></p>
<h2>Historical versus current comparison</h2><p>Rates are percent; PAYEMS is thousands of jobs. Counts cover all downloaded history. Monthly dates label measured months, not publication dates.</p><div class="scroll">{comparisons.to_html(index=False,escape=False,border=0)}</div>
<h2>PAYEMS: compare the same measured month</h2><p>December 2024 was {payroll.iloc[0]:,.0f} thousand jobs as known January 15, 2025, versus {payroll.iloc[1]:,.0f} today: a revision of {payroll.iloc[1]-payroll.iloc[0]:,.0f} thousand jobs. The current latest month's value in the comparison table measures a different period.</p>
<h2>GS10: three source-page checks</h2>{checks.to_html(index=False,border=0)}
<p>The assistant checked these against the downloaded FRED page. Eleanor still needs to personally read the three values and complete the partner activity. Draft personal responses are labeled in the written submission.</p>
<h2>Executed validation transcript</h2><pre>{escape(transcript)}</pre>
{picture('app_comparison.png','Actual browser comparison table — today, including GS10')}
<details><summary>Actual browser app — four default rate charts</summary>{picture('app_default.png','Default app screenshot')}</details>
<details><summary>Actual browser app — GS10 added</summary>{picture('app_with_GS10.png','App screenshot with GS10')}</details>
<p>Built {escape(datetime.now().astimezone().isoformat())}. Built with AI help; a learning demonstration, not investment advice. The report embeds its images and works offline.</p></html>'''
(out / 'executed_report.html').write_text(body)
print('Created outputs/executed_report.html from executed artifacts.')
