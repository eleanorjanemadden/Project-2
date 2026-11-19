# Executed portfolio result

Assistant run on November 17, 2026, using the frozen Yahoo adjusted-close snapshot retrieved October 20, 2026 UTC. The last data month is September 2026. These original runs use 0 bps of additional cost. The screens are 6.5% annual return, a 3% reserve minimum with BIL/IEF eligible, and a fully invested long-only grid in five-percentage-point steps.

| Run | Monthly returns | BIL | IEF | LQD | VT | Annual return estimate | Annual volatility estimate |
|---|---:|---:|---:|---:|---:|---:|---:|
| All months | 59 | 60% | 0% | 0% | 40% | 6.61% | 6.05% |
| Last 36 | 36 | 85% | 0% | 0% | 15% | 6.75% | 1.79% |
| All months, VT estimate down one percentage point | 59 | 55% | 0% | 0% | 45% | 6.53% | 6.79% |
| Last 36, VT estimate down one percentage point | 36 | 85% | 0% | 0% | 15% | 6.60% | 1.79% |

The window switch changed the largest weight by 25 percentage points, above the five-point review condition. The draft decision is a paper pilot at the zero-additional-cost reference of 60% BIL / 40% VT, with live allocation deferred. The original window and return stresses produced 55–85% BIL, 15–45% VT, and 0% IEF/LQD. [Decision memo](../docs/decision-memo.md) · [Generated allocations](allocations.csv) · [Full-precision results](results.json) · [Mandate-checker output](mandate_search_run.txt)

## Annual additional cost stress

Assistant validation run using the same frozen snapshot, 6.5% after-cost screen, 3% reserve minimum with BIL/IEF eligible, and five-point grid. The scenarios subtract a flat annual 0, 25, 50, or 100 bps beyond fund expenses already reflected in adjusted prices. They are illustrative assumptions, with no estimates of actual trading or advisory costs.

| Window | Annual cost (bps) | Constrained weights (BIL / IEF / LQD / VT) | Annual return before cost | Annual return after cost | Annual volatility | Constrained screen |
|---|---:|---|---:|---:|---:|---|
| All 59 months | 0 | 60% / 0% / 0% / 40% | 6.61% | 6.61% | 6.05% | Pass |
| All 59 months | 25 | 55% / 0% / 0% / 45% | 6.98% | 6.73% | 6.79% | Pass |
| All 59 months | 50 | 50% / 0% / 0% / 50% | 7.35% | 6.85% | 7.53% | Pass |
| All 59 months | 100 | 45% / 0% / 0% / 55% | 7.72% | 6.72% | 8.27% | Pass |
| Last 36 months | 0 | 85% / 0% / 0% / 15% | 6.75% | 6.75% | 1.79% | Pass |
| Last 36 months | 25 | 80% / 0% / 5% / 15% | 6.77% | 6.52% | 2.08% | Pass |
| Last 36 months | 50 | 80% / 0% / 0% / 20% | 7.54% | 7.04% | 2.37% | Pass |
| Last 36 months | 100 | 80% / 0% / 0% / 20% | 7.54% | 6.54% | 2.37% | Pass |

The baseline weights stay fixed within each window. Equal weight fails the numerical screen at all four costs in the all-month window and passes at all four in the 36-month window. Inverse volatility fails at all four costs in both windows. [Executed tables with both baselines, weights, returns, reserve and verdicts](cost-stress-validation.txt)

At 25 bps, the unchanged 60% BIL / 40% VT reference falls to 6.36% after cost. Reoptimization raises estimated risk and shifts the weights to clear the same hurdle. The largest cross-window weight difference is 25, 25, 30, and 35 percentage points at 0, 25, 50, and 100 bps, respectively. The cost stresses across both windows produced 45–85% BIL, 15–55% VT, 0% IEF, and 0–5% LQD. All four cross-window shifts exceed the five-point review condition and keep live adoption deferred. Stop the paper pilot and return to committee if the agreed reserve rule or after-cost return screen becomes infeasible. The decision remains a paper pilot with live allocation deferred. The rolling five-year net CPI + 4% objective remains unresolved. [Decision memo](../docs/decision-memo.md)
