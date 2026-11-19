---
name: buffett-sec
description: Analyze a ticker with the FIN43900 Buffett business screen using SEC 10-K facts, compute annual metrics in Python, and write an evidence-limited Markdown memo. Use for Lab 18 or a Buffett business-quality screen without price valuation.
---

Run `scripts/buffett.py TICKER --data-dir data --output-dir outputs` from the chosen project directory. The script path is relative to this skill. It downloads SEC ticker mapping and company facts with Eleanor Madden's academic User-Agent. Use `--offline` only to reproduce a saved SEC download, and disclose that choice.

Use only annual USD 10-K facts for the latest five fiscal-year ends. The script applies the course tag precedence, selects the latest filing of a period, computes net income / year-end equity and operating cash flow minus capital spending, and computes the three course checks. Do not calculate or estimate missing inputs yourself. Values remain “not found”; undefined ROE and checks remain “not known”. Do not substitute a bank's investing cash flow for capital spending. Read the printed sources and flag incomplete years.

After running the script, read its output and write `memos/TICKER_memo.md` in a simulated Buffett perspective. Choose **own the business**, **watch it**, or **pass**. Judge earning power, consistency, and the limits of evidence. A passing screen does not establish a moat or management quality. Use only numbers in the printed financial table or check thresholds, in the same units. Do not insert scores, forecasts, prices, price targets, or facts not supported by the output. This is the lab's simplified owner-earnings proxy, not maintenance-capex estimation from the broader FAskills framework. For JPM or other gaps, explicitly say you cannot judge owner earnings.

Add the student's draft trust decision immediately under the memo, marked for later personal review. Validate with `scripts/buffett.py TICKER --offline --memo memos/TICKER_memo.md`. Fix every flagged number. Save `memos/TICKER_memo.evidence.json` containing `{"fingerprint": "..."}` using the script's `fingerprint(result)` so the app can detect stale memos after data changes. The memo is written by the AI after reading output; the script does not produce a canned verdict.

Launch `python3 -m streamlit run buffett_app.py` in the lab folder to inspect the chart, table, sources, checks, memo and editable number probe. Source philosophy: https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/warren_buffett.md . Read FAskills as a reference only; do not install it or use paid feeds.
