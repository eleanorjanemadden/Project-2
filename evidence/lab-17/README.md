# Lab 17 — Eleanor Madden

Start with [Lab_17.md](Lab_17.md). It contains the data card, actual known-answer results, GS10 audit, drafted partner responses, admission rule, and reflections.

Run from this folder:

```bash
python3 -m pip install -r requirements.txt
python3 -m streamlit run asof_app.py
python3 validate.py
```

Type `GS10` to add my series; use `PAYEMS` and January 15, 2025 for the revision probe. October 5, 2026 reproduces the four course answers. No API key is needed.

Visible executed output: [outputs/executed_report.html](outputs/executed_report.html). Open it in a browser; it works offline and includes the validation tables, transcript, and actual app screenshots. The live app is also available at http://localhost:8517 while the task's server is running.

| Files | Purpose |
|---|---|
| `asof_app.py`, `requirements.txt` | Required Streamlit app and pinned runtime packages |
| `Lab_17.md` | Written submission |
| `validate.py` | Live download and UI validation |
| `data/` | Raw CSVs, source-page snapshot, download URL/time manifest |
| `outputs/` | Executed report, screenshots, comparison CSVs, and logs |
| `instructions/` | Copies of current course instructions read for this lab |
| `AI_ASSISTANCE.md` | Assistance disclosure and remaining student-only steps |
| `capture_app.py`, `build_report.py` | Optional browser evidence/report recreation |

To recreate screenshots, start the app on port 8517 (`python3 -m streamlit run asof_app.py --server.port 8517`), then run `python3 capture_app.py`. This optional script also requires Playwright and Chromium (`python3 -m pip install playwright`, `python3 -m playwright install chromium`). Run `python3 build_report.py` after validation and capture to rebuild the standalone report. These tools are not required to run the app.

Counts use all downloaded history, not just the chart period. Current FRED values and counts may change on a later rerun; the October 29 evidence is retained here.

Before submission, revisit the drafted personal responses, personally check the three source values, and complete the partner exercise. Upload the folder to the chosen GitHub repository and paste actual GitHub file links into the Brightspace Lab 17 quiz. No fabricated GitHub links or submission confirmation are provided.
