# Validation and AI use

I used ChatGPT through Codex to consolidate files, check execution, test the stability claim, run the 15 bp experiment, and draft the written materials. Earlier Lab 17 and 19 AI disclosures are linked in the [evidence index](evidence-index.md).

## Week 12 prework

I would give an independent challenger the price snapshot, assumptions and comparison tables. The challenger can restrict model use if historical arithmetic returns are the only evidence for a forward rolling five-year net objective, if a rerun exceeds the five-point weight limit, or if reserve eligibility or vintage timing cannot be verified. I would assign monthly monitoring to the portfolio analyst and return to the committee if the reserve rule and after-cost screen cannot both be satisfied. [Week 12 handout model-risk reference](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-12/student-handout.md#local-model-risk-reference)

## Riskiest claim and test

**Claim under challenge:** The 60% BIL / 40% VT result is stable enough for live adoption. **Test:** On the same frozen CSV, switch from all 59 monthly returns to the last 36. Hold the 6.5% objective, 3% reserve minimum, BIL/IEF eligibility and five-point grid fixed. Use the largest absolute weight change and compare it to the five-point review limit from Lab 15. The window changes estimates of means, volatility, and correlation together.

**Disposition:** Qualify the recommendation to a paper pilot. The reproduced switch moved BIL from 60% to 85% and VT from 40% to 15%, a 25-percentage-point maximum change. The screen was feasible in both cases and the stability condition failed. This checks an existing comparison. [Executed allocations](../outputs/allocations.csv)

## Portfolio comparison validation

Codex helped implement and test the Streamlit comparison. Equal-weight and inverse-volatility baselines use their formula weights. The constrained portfolio uses the existing minimum-volatility search. Each portfolio is evaluated with the same selected window, edited annual return estimates, annual covariance and reserve settings. The sensitivity section continues to compare the current constrained result with the original all-month constrained result.

`python3 validate.py` independently recomputed the rendered weights, return, volatility, reserve and rule verdicts from the monthly prices using pandas and NumPy. Streamlit checks covered default inputs, the 36-month switch, a return override, an eligibility edit, a 100% reserve threshold, the upload path, Meridian and infeasibility. The 25.00-percentage-point window sensitivity was reproduced. [Executed check log and rendered tables](../outputs/portfolio-comparison-validation.txt)

At the default 0 bps additional cost, the all-month estimated return was 3.01% for equal weight, 3.37% for inverse volatility, and 6.61% for the constrained portfolio. Over the last 36 months these estimates were 8.13%, 4.61%, and 6.75%, respectively. All three met the 3% reserve allocation screen in both windows under the assumed eligibility. The rolling five-year net CPI + 4% objective remains unresolved because the numerical screen uses annual estimates and the model does not evaluate rolling outcomes net of costs and against realized inflation. Actual liquidity, issuer exposure and exemptions, and live implementation restrictions also remain unresolved.

## Annual additional cost validation

Codex added and tested a flat annual cost deduction in the Streamlit comparison and constrained search. The assumption covers costs beyond fund expenses already reflected in adjusted prices. The comparison subtracts basis points divided by 10,000 from the annual return estimate. The constrained search uses that after-cost estimate with the original numerical threshold and reserve minimum.

`python3 validate.py` independently enumerated the four-asset weight grid and matched the app's 0, 25, 50, and 100 bps scenarios for the full and 36-month windows. The checks covered the exact threshold, invalid costs, unchanged zero-cost behavior, reoptimization after a widget edit, and an infeasible case that kept the 6.5% threshold. [Executed check log and scenario tables](../outputs/cost-stress-validation.txt)

The illustrative costs changed the selected weights. The paper-pilot recommendation and live deferral still apply, given the differences between windows and the need for actual cost and forward return evidence. The rolling five-year net CPI + 4% objective remains unresolved. [Executed results and decision implications](../outputs/week-12-result.md#annual-additional-cost-stress)

### Sensitivity display follow-up

The simulated partner review found that the same-cost comparator could be mistaken for the fixed zero-cost paper reference. The app now shows both comparisons on the bundled snapshot. Changing only cost to 15 bp results in 0.00 percentage points versus the all-month allocation at 15 bp and 5.00 percentage points versus the fixed 60/40 paper reference at 0 bp. Both changes are unavailable when the current search is infeasible. [Partner review](partner-review.md#follow-up-on-the-sensitivity-display) · [Validation code](../validate.py)

## GS10 point-in-time monitoring validation

Codex added a GS10 monitoring panel that reads the saved Lab 17 ALFRED CSV listed for the selected cutoff in the download manifest. It selects the latest nonmissing observation from that vintage and preserves the archived value for that month. The observation month labels the measured period. Date-level availability comes from the saved vintage, and same-day pre-trade timing remains unresolved without a verified timestamp. For an opening decision, the prior calendar day's vintage is the conservative input. [Lab 17 data card](../evidence/lab-17/Lab_17.md#r--represent-my-data-card) · [Source manifest](../evidence/lab-17/data/download_manifest.json)

`python3 validate.py` confirmed that September's observation was absent from the September 30 vintage, which ended with August at 4.68% per annum. September's 4.99% is present in the October 1 and October 29 vintages. Compared with September 30, both later vintages add one month and have zero changed values for shared months. Streamlit checks verified all three readouts, their source links and timing caveat, and unchanged portfolio results when the cutoff changed. A missing saved vintage produced an unresolved warning without substituting a value. [Executed validation and app readouts](../outputs/gs10-validation.txt)

The panel covers the three saved dates and supplies monitoring context for IEF and LQD. The ETF allocation and mandate screens are independent of GS10. The evidence establishes a historical availability boundary. A trading or allocation rule tied to GS10 and any effect on returns remain unvalidated.

## Changed-input experiment — additional annual cost

**Prediction.** I expected a move from 0 to 15 bp of annual additional costs to make the unchanged 60% BIL / 40% VT portfolio miss the 6.50% screen. Its zero-cost headroom was about 11 bp. I expected the search to shift five percentage points from BIL into VT, where the estimated return was higher, and to produce a feasible mix with higher volatility and a lower eligible reserve weight. I expected to retain the paper pilot and defer live funding. [Timestamped AI-assisted prediction](changed-input-prediction.md) · [Local pre-run commit `ffb2071`](https://github.com/eleanorjanemadden/Project-2/commit/ffb2071228f66c0cf77cf8a0bbcb1c64cf3568d3), recorded November 23, 2026 at 19:35:33 EST (November 24 at 00:35:33 UTC).

**Execution.** With Codex I ran the Streamlit app through AppTest on November 23, 2026, using the frozen October 20 UTC price snapshot and all 59 monthly returns through September 2026. I changed only the annual additional cost widget. I held the 6.50% objective, 3% reserve minimum, BIL/IEF eligibility, five-point grid and all estimates fixed. An independent enumeration of the weight grid using pandas/NumPy means and covariance matched the app's weights, annualized risk and return in both runs. [Saved before/after output](../outputs/changed-input-cost.csv)

| Measure | Before, 0 bp | After, 15 bp | Change |
|---|---:|---:|---:|
| BIL | 60% | 55% | −5 pp |
| VT | 40% | 45% | +5 pp |
| IEF and LQD | 0% each | 0% each | 0 pp |
| Estimated annual return before additional cost | 6.6145% | 6.9842% | +0.3696 pp |
| Estimated annual return after additional cost | 6.6145% | 6.8342% | +0.2196 pp |
| Estimated annual volatility | 6.0518% | 6.7901% | +0.7382 pp |
| Eligible reserve | 60% | 55% | −5 pp |
| 6.50% return and 3% reserve screens | Pass | Pass | Both optimized mixes feasible |

**Reconciliation and committee effect.** At a fixed 60/40, the 15 bp fee reduces the return estimate to 6.4645%, missing the hurdle by 3.55 bp. The next five-point shift into VT adds 36.96 bp to the gross return estimate. That exceeds the 15 bp fee and leaves the reoptimized net estimate 21.96 bp above the original zero-cost estimate, with higher equity exposure and risk. The fixed-mix result and the reoptimized result answer different questions. I would retain 60/40 as the zero-cost paper reference and track 55/45 as the 15 bp scenario. I would keep live funding deferred because the fee sensitivity compounds the 25-point window sensitivity and the forward five-year net objective remains unproven. [Decision memo](decision-memo.md)

**Locked Changed-Input Record status.** The prediction was saved in commit `ffb2071` before execution. The commit was local at the time of the run. 

## AI-output register

I used ChatGPT through Codex for the entries below. Dates identify the event documented by each source. 

| Material ChatGPT/Codex suggestion or output | AI-output date and dated evidence | Supporting check | Proposed disposition |
|---|---|---|---|
| Use the October 20 snapshot to reproduce the allocation. | AI-output date unavailable. Source audit documented November 17, 2026. | Compared the retained Yahoo responses with every row in the saved CSV and reproduced the full-precision allocations. The source audit found that a later Lab 15 CSV mixed vintages. [Run record](week-12.md) · [Validation](../outputs/portfolio-comparison-validation.txt) | **Accept.** Pair the frozen CSV with its matching raw responses. |
| Challenge the stability of 60/40 by changing the return window. | AI-output date unavailable. App-level test documented November 17, 2026. | Reran the same snapshot and rules on 59 and 36 returns. The maximum weight change was 25 pp against a 5 pp review limit. [Allocations](../outputs/allocations.csv) | **Accept the test and reject live stability.** Keep the result as a paper reference. |
| Put equal weight and inverse volatility beside the optimized allocation. | AI-output date unavailable. Comparison and validation log committed November 19, 2026 (`59675a9`). | Recomputed each portfolio independently. At zero additional cost equal weight passed only in the recent window, and inverse volatility failed the 6.50% screen in both. All three passed the assumed 3% reserve rule in both. [Comparison check](../outputs/portfolio-comparison-validation.txt) | **Accept.** The common inputs make the differences interpretable. Keep live mandate terms unresolved. |
| Deduct a flat annual cost before applying the return screen. | AI-output date unavailable. Cost stress and validation log committed November 19, 2026 (`59bac78`). | Independently enumerated the grid at 0/25/50/100 bp and checked threshold, infeasibility and widget behavior. The 15 bp run also showed the reference failing while reoptimization remained feasible. [Cost checks](../outputs/cost-stress-validation.txt) · [15 bp output](../outputs/changed-input-cost.csv) | **Qualify.** Use the deduction as a sensitivity assumption. Actual trading and advisory costs still require a documented estimate. |
| Predict that a 15 bp fee will make the fixed 60/40 mix fail and shift the optimized allocation five points toward VT. | November 23, 2026 (EST). Prediction committed before the assisted run in `ffb2071`. | Streamlit AppTest and an independent pandas/NumPy grid calculation agreed. The fixed mix fell to 6.4645%, and the reoptimized mix passed at 6.8342% with higher volatility. [Prediction](changed-input-prediction.md) · [Saved output](../outputs/changed-input-cost.csv) | **Accept as an illustrative sensitivity test.** The fee is an assumption. The pilot recommendation stands. |
| Use the saved ALFRED vintage to monitor GS10. | AI-output date unavailable. Panel and validation log committed November 19, 2026 (`2832a67`). | September 30 ended at August's 4.68%. October 1 and October 29 added September's 4.99% with no shared-month revisions. Changing vintages left ETF allocations unchanged. [Timing check](../outputs/gs10-validation.txt) | **Accept for dated monitoring.** Use the prior day's vintage for an opening decision unless release time is verified. A GS10 trading rule remains unvalidated. |
| Use the automated cold run as reproducibility evidence. | AI-output date unavailable. Automated run logged November 19, 2026. | A fresh clone reached healthy Streamlit in 22.2 seconds and passed 53 checks. [Cold-run transcript](../outputs/automated-cold-run.txt) | **Qualify.** This verifies automated execution. The simulated partner review is recorded. An uncoached human check remains unverified. |
| Recommend a paper pilot, with a stop rule and a separate live-funding gate. | Original AI-output date unavailable. The 90-day pilot draft was committed November 23, 2026 (`c806543`). | The default search passed, the window gap exceeded the review limit, and a 15 bp fee broke the unchanged reference's return screen. [Allocations](../outputs/allocations.csv) · [15 bp output](../outputs/changed-input-cost.csv) | **Accept as the proposed committee action.** Use quarterly governance and monthly monitoring while collecting forward return, cost and liquidity evidence. |

## Independent review

The automated cold run established that the published command can reach the result from a fresh clone. The [simulated partner review](partner-review.md) records the command, first failure, elapsed time and result location for a separate fresh-clone run. 
