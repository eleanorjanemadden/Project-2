# Lab 19 — Legend Panel

Eleanor Madden | November 5, 2026

## D — The question

**When three investors' skills read the same 10-K facts, where do they agree, where do they split — and would I trust the panel?**

They can agree about the facts while disagreeing about what makes a business worth studying. On NVIDIA, Buffett and Graham pass every assigned check, while Burry flags cash flow below earnings. I would trust the panel to organize research, with a condition: I need to investigate that disagreement before making a decision.

**Opening discussion:** Buffett would focus on Costco's positive owner earnings and consistent ROE. Graham would stop at its latest current ratio of 1.06 because it falls below his 2.0 defensive standard, even though the earnings record passes. Burry's emphasis is whether the earnings are backed by operating cash, rather than treating profit growth alone as sufficient.

## Build — My request and method

**My request to the AI:** Keep my Lab 18 SEC method, Buffett checks, chart and number flag. Add separate Graham and Burry skills using the assigned checks on exactly the same facts, plus current assets, current liabilities and total liabilities. Show every investor's checks, verdict and memo side by side; flag unprinted numbers across every memo. Match COST, run the liquidity-threshold probe, and analyze VT's largest company. Preserve missing facts and keep all judgments separate from the calculations.

ROE = net income / year-end equity; owner earnings = operating cash flow − capital spending; current ratio = current assets / current liabilities; liabilities / equity = total liabilities / year-end equity. No ratios use averages. Checks use unrounded values. Missing amounts print **not found**. Missing inputs and undefined ratios print **not known**. Nonpositive equity makes ROE and liabilities / equity undefined; nonpositive current liabilities make the current ratio undefined. An all-years check requires five periods. A latest-year check uses only the latest period, and first-to-last growth compares endpoints rather than requiring growth in every intervening year.

The raw responses have SEC URLs, retrieval times and checksums in `data/*.source.json`. COST and JPM reproduce the saved Lab 18 downloads; NVDA was downloaded for this lab. An optional HTTPS DNS fallback was needed in this workspace; the responses still came from SEC with certificate verification. FAskills was read as a philosophy reference, not installed or used as a data service. The lab's shortened business-only rules take precedence over the reference pages' broader valuation and JSON templates.

The app retains the owner-earnings/net-income chart, full table, tags and filing provenance. Its three columns show model-written verdicts and memos; the check totals are separate from those judgments. Each memo is tied to a fingerprint of its complete financial result. Changed facts or thresholds make the saved memo stale. The number flag checks digit-based tokens against printed values, dates, totals and thresholds, preserving the distinction between percentages and dollar amounts. It cannot establish whether a supported number is attached to the right metric, so I also reviewed the prose.

## V — COST known answer and threshold probe

| Fiscal year end | Current ratio | Liabilities / equity |
|---|---:|---:|
| 2022-08-28 | 1.02 | 2.11 |
| 2023-09-03 | 1.07 | 1.75 |
| 2024-09-01 | 0.97 | 1.96 |
| 2025-08-31 | 1.03 | 1.64 |
| 2026-08-30 | 1.06 | 1.49 |

| Investor | Check | COST |
|---|---|---|
| Buffett | ROE at least 15% every year | pass |
| Buffett | Owner earnings positive every year | pass |
| Buffett | Owner earnings grew, first to last | pass |
| Graham | Latest current ratio at least 2.0 | fail |
| Graham | Net income positive every year | pass |
| Graham | Net income grew, first to last | pass |
| Burry | Operating cash flow at least net income every year | pass |
| Burry | Latest liabilities no more than twice equity | pass |

**Totals:** Buffett 3 of 3, Graham 2 of 3, Burry 2 of 2. The model's verdicts are Buffett **own the business**, Graham **watch it**, and Burry **watch it; the narrow accounting screen passes**. Burry can pass his checks while still wanting footnote review. The separate [Buffett memo](memos/COST_Buffett_memo.md), [Graham memo](memos/COST_Graham_memo.md) and [Burry memo](memos/COST_Burry_memo.md) explain the judgments.

**Threshold probe:** I ran the installed Graham skill with `--graham-threshold 1.0`. Its liquidity check changes from fail to pass, producing Graham 3 of 3. The facts and the other investors' checks are unchanged. The [installed-skill probe](outputs/installed_graham_threshold_probe.txt) records the run; the app also supports the comparison and warns that the old memos are stale.

**Threshold kept — draft:** I keep 2.0 because I want the original defensive liquidity standard; lowering it to 1.0 makes COST pass without improving its balance sheet. This line also appears under Graham's COST memo.

## My company — NVIDIA inside VT

My [Project 2 mandate](instructions/PROJECT2-MANDATE.md) includes BIL, IEF, LQD and VT. I chose the equity fund, VT. [Vanguard's fact sheet](https://fund-docs.vanguard.com/F3141.pdf), dated September 30, 2026, lists NVIDIA first at 4.6% of total net assets, followed by Apple at 4.1%. The [saved fact sheet](data/VT_fact_sheet.pdf) preserves that source. NVDA files 10-Ks on EDGAR, so no next-largest-company substitution was needed. Holdings dates and company fiscal ends are different dates for different purposes.

These are the last five annual fiscal ends in the saved NVDA SEC facts. Dollar amounts are **USD millions**. The [complete table](outputs/NVDA_table.csv), [panel](outputs/NVDA_panel.csv), [filing provenance](outputs/NVDA_run.txt), and [app checks](outputs/app_check.json) are included.

| Fiscal year end | Revenue | Net income | Operating cash flow | Capital spending | Equity | Owner earnings | ROE | Current ratio | Liabilities / equity |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022-01-30 | 26,914 | 9,752 | 9,108 | 976 | 26,612 | 8,132 | 36.6% | 6.65 | 0.66 |
| 2023-01-29 | 26,974 | 4,368 | 5,641 | 1,833 | 22,101 | 3,808 | 19.8% | 3.52 | 0.86 |
| 2024-01-28 | 60,922 | 29,760 | 28,090 | 1,069 | 42,978 | 27,021 | 69.2% | 4.17 | 0.53 |
| 2025-01-26 | 130,497 | 72,880 | 64,089 | 3,236 | 79,327 | 60,853 | 91.9% | 4.44 | 0.41 |
| 2026-01-25 | 215,938 | 120,067 | 102,718 | 6,042 | 157,293 | 96,676 | 76.3% | 3.91 | 0.31 |

| Investor | Check | NVDA |
|---|---|---|
| Buffett | ROE at least 15% every year | pass |
| Buffett | Owner earnings positive every year | pass |
| Buffett | Owner earnings grew, first to last | pass |
| Graham | Latest current ratio at least 2.0 | pass |
| Graham | Net income positive every year | pass |
| Graham | Net income grew, first to last | pass |
| Burry | Operating cash flow at least net income every year | fail |
| Burry | Latest liabilities no more than twice equity | pass |

**Totals and verdicts:** Buffett 3 of 3 — **own the business, conditional on understanding its durability**; Graham 3 of 3 — **own the business on this limited screen, subject to further defensive analysis**; Burry 1 of 2 — **watch it**. Read the separate [Buffett](memos/NVDA_Buffett_memo.md), [Graham](memos/NVDA_Graham_memo.md) and [Burry](memos/NVDA_Burry_memo.md) memos. These are simulated perspectives drafted by the AI after reading the script output, not the investors' actual opinions.

The split comes from cash versus earnings. Operating cash flow falls below net income at 2022-01-30, 2024-01-28, 2025-01-26 and 2026-01-25. Latest operating cash flow is 102,718 against income of 120,067. Positive owner earnings can pass Buffett's proxy even when operating cash does not cover net income, so the results are consistent rather than contradictory. All assigned NVDA inputs are present; the broader reasons for the cash gap remain unknown from this table.

## V — Explain the code, bull and bear

In `graham_checks()` in [panel.py](panel.py), `latest = rows[-1]` picks the latest fiscal end. The income list collects the annual profits, and `complete` checks that five periods exist. The returned dictionary calls `check()` for each rule: latest liquidity against the chosen threshold, all annual profits above zero, and last profit above first. The last two require the complete five-period window; liquidity requires the latest input. `check()` first returns **not known** if a required input is missing or the window is incomplete; otherwise it applies the condition and returns **pass** or **fail**. Missing liquidity is never replaced by zero or inferred from earnings.

**Partner question — what happens when an input is missing?** If current assets are absent, the ratio is `None`, and Graham's liquidity check becomes not known. If an annual net-income input is missing, the positivity check becomes not known; endpoint growth also becomes not known when a required endpoint is absent. A missing middle-year income is not an input to endpoint growth, so that specific check can still be known.

**Bull case:** NVIDIA passes all of Buffett's and Graham's assigned checks, with positive owner earnings throughout and a latest current ratio of 3.91. Owner earnings rise from 8,132 to 96,676, supporting further business research even though the path is uneven.

**Bear case:** Burry's cash-flow check fails because operating cash flow is below net income in several years, including 102,718 versus 120,067 in the latest year. I would need to understand that gap before trusting the earnings record, and favorable liquidity does not answer that question.

## My decision

**Only with a condition: I would let the panel prioritize Project 2 company research if I investigate every failed or unknown check—especially NVDA's cash-versus-earnings gap—and separately assess valuation and portfolio fit before acting.**

## Learn — A panel of AI agents

**What is it?** A group of specialized AI roles that examines a shared task from different perspectives. Here the roles are Buffett's business earning power, Graham's defensive financial condition, and Burry's accounting skepticism.

**How does it work, and why disagree on the same facts?** The numerical evidence is shared, but each role applies different rules and emphasizes different risks. The code fixes those checks; the model explains their significance and chooses a verdict. Agreement is not independent confirmation when every role uses the same data and model. This implementation runs the skills sequentially with one AI, not independent autonomous model services.

**Partner explanation:** Think of it as asking different questions of the same spreadsheet. Buffett asks whether the business produces attractive owner earnings, Graham asks whether it meets defensive standards, and Burry asks whether cash supports earnings. I learn more from investigating their disagreement than from counting votes.

## Reflect

**Where did the panel agree and split on my company?** Buffett and Graham agree that NVDA passes their assigned profitability and financial-condition checks, and Burry agrees that latest liabilities / equity clears his limit. Burry splits on cash backing earnings. The combined view helps me avoid treating rapid profit growth as enough evidence by itself.

**What does the threshold probe say about any screen's verdict?** A screen embeds choices about what counts as acceptable. COST's facts did not change when I lowered the liquidity threshold, but the pass count did. I should disclose the rule and its reason rather than change it just to obtain the result I want.

## Validation and honest gaps

[Eight executed tests pass](outputs/validation_run.txt), covering the COST tables, all panel checks, threshold behavior, actual NVDA and JPM runs, source checksums and latest filings, missing inputs and nonpositive denominators, all memo fingerprints and numeric flags, packaged scripts, and app interactions. [Memo validation](outputs/memo_validation.json) shows no unsupported numbers in the nine saved memos. The [app probe](outputs/app_number_probe.txt) inserts an unsupported 40.0% separately into Buffett, Graham and Burry; every occurrence is attributed to the correct investor. Repeated unsupported tokens are also caught in [the cross-memo probe](outputs/number_probe.json).

[JPM's saved run](outputs/JPM_run.txt) retains capital spending and owner earnings as **not found**, with Buffett's related checks **not known**. Current assets and liabilities are also not found, leaving Graham's ratio check **not known**. Its [three memos](memos/) explicitly retain the limitations; no missing amount is estimated. Synthetic changes used to verify missing-data behavior stay inside the tests and never become submitted company facts.
