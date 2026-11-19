# FIN43900 Project 2 — Scholarship foundation portfolio pilot

**AI disclosure.** I used ChatGPT through Codex to consolidate my lab work, verify reproducibility, test the stability claim, and draft the Week 12 materials. The analysis and decision are mine. Education, not investment advice. [Validation and AI use](docs/validation-and-ai-use.md)

The fictional scholarship foundation’s committee is deciding whether to pilot a long-only ETF allocation. The draft recommendation is a paper pilot at 60% BIL / 40% VT, with live allocation deferred. [Decision memo](docs/decision-memo.md)

## Install

Open a terminal in this folder. Use Python 3.13 (verified with 3.13.1). On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate with `.\.venv\Scripts\Activate.ps1` after creating the environment. Dependency installation requires internet. The portfolio run uses only bundled inputs and needs no credentials.

## Run

```bash
python analyze.py && python -m streamlit run app.py
```

Open the local URL printed by Streamlit, normally http://localhost:8501. **Portfolio comparison** shows equal-weight, inverse-volatility, and constrained portfolios side by side. All three use the selected window and the same current return estimates, covariance, reserve eligibility, and mandate thresholds. Each column shows weights, estimated annual returns before and after the additional cost, volatility, reserve weight, and rule verdicts. The constrained search minimizes estimated volatility on a five-percentage-point grid subject to the after-cost numerical return screen and reserve minimum. The app flags universe compliance from the ticker labels and marks requirements that need external evidence as unresolved, including live liquidity, issuer limits, and the rolling five-year net CPI + 4% objective.

Set **Annual additional cost assumption (bps)** in the sidebar. It defaults to 0 bps to reproduce the original run. Enter only costs beyond fund expenses already reflected in the adjusted-price returns. The app subtracts the same flat annual cost from each portfolio's estimate and keeps the numerical threshold fixed when the search is infeasible. Expand **Illustrative annual cost stress** to compare 0, 25, 50, and 100 bps on the current inputs. These values are scenarios, not estimates of actual trading or advisory costs. [Executed cost scenarios and decision implications](outputs/week-12-result.md#annual-additional-cost-stress)

**Sensitivity** compares the constrained mix from the original all-month inputs with the constrained mix from the current inputs. The bundled data opens at 60% BIL / 40% VT. Select **Last 36 months** to see 85% BIL / 15% VT and a 25.00-percentage-point change. Keep the 6.5% return screen, 3% reserve minimum, 0 bps additional cost, and BIL/IEF eligibility at their defaults for that comparison. Clear **Use included Project 2 prices.csv** to see the Meridian training inputs. Stop the app with Ctrl+C.

Run `python validate.py` for calculation checks and Streamlit interaction tests. [Executed comparison and cost checks](outputs/cost-stress-validation.txt)

The command writes [allocations.csv](outputs/allocations.csv), full-precision estimates in `outputs/results.json`, and mandate-checker output in `outputs/mandate_search_run.txt`. [Visible executed result](outputs/week-12-result.md)

## Files and limitations

- [Mandate](PROJECT2-MANDATE.md), [Streamlit app](app.py), [portfolio engine](portfolio.py), and [frozen prices](prices.csv). The saved Yahoo adjusted monthly closes were retrieved October 20, 2026 UTC and cover October 2021–September 2026. [Download record](data/price_download.txt)
- [Labs 13–19 evidence map](docs/evidence-index.md). The Lab 14 verdicts are supporting evidence. The GS10 vintage check and the NVDA panel are standalone supporting work. The optimizer uses ETF prices and its sidebar inputs.
- [Week 12 audit and must-fix list](docs/week-12.md), [draft manifest](docs/manifest.md), and [video outlines](docs/video-outlines.md).

The historical annualized return screen and minimum-volatility search support the paper pilot. Live adoption requires stable weights, verified reserve terms, forward return evidence and an explicit cost allowance.
