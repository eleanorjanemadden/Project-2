# Partner review

**Reviewer name:** Mrigna Goel

## What I ran and where I found the result

I cloned the published repository into a new directory, opened the README, and followed its macOS instructions using Python 3.13.1 and an empty virtual environment. Pip reused cached wheels. I ran these commands from the clone.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python analyze.py && python -m streamlit run app.py
```

It took **30.51 seconds** from the start of environment setup to the first successful app health response, excluding the clone and follow-up tests. I found no blocking failure on the documented path. The app page at `http://localhost:8501/` returned HTTP 200. I used Streamlit AppTest to exercise and inspect the rendered controls and tables. That let me verify their behavior, while visual layout on a physical screen and Windows setup remain untested. I found the numerical result in the **Portfolio comparison** and **Sensitivity** sections, and the published evidence in [`outputs/week-12-result.md`](../outputs/week-12-result.md), [`outputs/allocations.csv`](../outputs/allocations.csv), and [`outputs/results.json`](../outputs/results.json). The commands regenerated the tracked output without a tracked-file diff. [Setup log](../outputs/partner-review/setup.txt) · [Run log](../outputs/partner-review/run.txt) · [Timing](../outputs/partner-review/timing.txt) · [HTTP checks](../outputs/partner-review/health.txt) · [Regeneration check](../outputs/partner-review/regeneration.txt)

## What I reproduced

I reran `python validate.py`. All 55 checks passed in 84.44 seconds. I separately moved the return, window, cost, and reserve controls. My first supplemental probe failed because AppTest resolved the relative app path against the probe’s directory. I switched the probe to an absolute path resolved from the clone and reran it successfully. The README path required no correction. [First probe attempt](../outputs/partner-review/probe-first-attempt.txt) The table below uses zero additional cost and the draft BIL/IEF eligibility. In each window, all three portfolios passed the 3% reserve allocation rule.

| Window | Portfolio | Estimated annual return | Estimated annual volatility | Eligible reserve | 6.50% screen |
|---|---|---:|---:|---:|---|
| 59 returns | Equal weight | 3.01% | 7.55% | 50.00% | Fail |
| 59 returns | Inverse volatility | 3.37% | 1.37% | 92.79% | Fail |
| 59 returns | Constrained | 6.61% | 6.05% | 60.00% | Pass |
| 36 returns | Equal weight | 8.13% | 5.88% | 50.00% | Pass |
| 36 returns | Inverse volatility | 4.61% | 0.61% | 95.78% | Fail |
| 36 returns | Constrained | 6.75% | 1.79% | 85.00% | Pass |

Equal weight gave each ETF 25%. Inverse volatility put 87.24% in BIL in the full window and 92.80% in the recent window. I could see why it was low-risk and why it missed the hurdle. The constrained column used the same estimates and screens. The bundled ETF universe, long-only weights, and full investment passed. The validator checked all four adjusted-close series against the bundled Yahoo responses. Actual five-day liquidity, issuer limits and exemptions, live implementation restrictions, and the rolling five-year net CPI + 4% objective remained unresolved. In particular, a historical arithmetic mean above 6.50% does not establish a forward compounded return after actual costs and inflation. [Validator log](../outputs/partner-review/validate.txt) · [Reviewer probe](../outputs/partner-review/probe.txt)

## The claim I distrusted most

I distrusted whether the 60/40 result was robust enough to fund. Changing only the lookback to 36 returns cut VT from 40% to 15% and raised BIL from 60% to 85%. Both runs passed the 6.50% numerical screen. The 25-point change exceeded the five-point review limit, so the live-funding claim failed. Cutting only the annual VT estimate by one percentage point in the full sample produced 55% BIL / 45% VT at 6.53% estimated return and 6.79% volatility. The optimizer needed more of the higher-return asset to reach the unchanged hurdle.

At 15 bp, I calculated **6.4645%** after cost for the unchanged 60/40 reference. It failed the 6.50% screen. The optimizer chose 55% BIL / 45% VT at **6.8342%** after cost and **6.7901%** volatility. The validator independently reproduced the 0, 25, 50, and 100 bp tables in both windows. At 100 bp the full-window mix reached 55% VT and 8.27% volatility. With IEF ineligible at 15 bp, the selected mix stayed at 55/45. Then raising the bills-only reserve minimum to 100% made the search infeasible and the app retained the 6.50% hurdle. That is a concrete case for returning to committee. [Reviewer probe](../outputs/partner-review/probe.txt) · [Validator log](../outputs/partner-review/validate.txt)

My first usability concern surfaced during the 15 bp stress. The sensitivity metric showed **0.00 pp** even though VT had risen five points from the zero-cost reference. The caption explains that the “As loaded” comparison also reoptimizes at the current cost. The metric therefore answers a narrower question than the reference framing led me to expect. I would label it “change versus all-month mix at current cost and thresholds” and display the change from the zero-cost paper reference alongside it, or point directly to the cost table.

## Timing and decision

The GS10 checks reproduced August 2026 at 4.68% for the September 30 vintage and September at 4.99% for October 1 and October 29. The later files added September without changing observations shared with the September 30 file. Changing that control left ETF weights unchanged. The ALFRED date supports the dated availability boundary. I could not establish a time of day for trading or any performance gain from GS10. [GS10 data card](../evidence/lab-17/Lab_17.md#r--represent-my-data-card) · [Validator log](../outputs/partner-review/validate.txt)

My skeptical committee question is **“If a 15 bp cost makes the reference miss the hurdle and the equity weight moves 25 points when you shorten the history, what after-cost forward evidence would persuade you to risk scholarship capital?”** I would support the 90-day paper pilot with zero live capital, monthly ownership by the portfolio analyst, and a committee review at day 90. I would record reserve coverage and agreed cost assumptions at every review. If no allocation jointly clears the reserve and return screens, I would stop and refer the result to the committee. A stress shift above five points would continue to block live funding even when an allocation is feasible. Before a funded vote I would want verified eligibility and liquidity, a documented cost allowance, and forward evidence for the rolling net objective.

## Findings at the time of review

The app, memo, and saved output agree on the zero-cost reference, the stress ranges, and deferring live funding. The memo adds the operating schedule. The validation record distinguishes the assisted run from the required student-authored prediction and AI-off execution. I would keep that distinction in the manifest, complete the course's Locked Changed-Input Record, and add the three video URLs, timing details, and corrected transcripts. I would also clarify the moving sensitivity comparator and update the studio notes so that the older checklist's baseline and cost items are clearly historical.


## Follow-up on the sensitivity display

The original observations above apply to the reviewed commit. The app now shows the same-cost comparison and, when using the bundled snapshot, a separate comparison against the fixed zero-cost paper reference. At 15 bp the validator checks for 0.00 and 5.00 percentage points respectively. An infeasible current mix shows N/A for both. [README](../README.md#run) · [Validation code](../validate.py)

The [submission manifest](manifest.md) now links the three recordings, cue timestamps, and transcripts. The [Week 12 studio record](week-12.md) distinguishes current status from the original checklist. The student-authored AI-off Locked Changed-Input Record remains unresolved.
