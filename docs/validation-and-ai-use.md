# Validation and AI use

ChatGPT (Codex) helped consolidate files, check execution, test the stability claim, and draft the handoff. The student owns the analysis and decision. Earlier Lab 17 and 19 AI disclosures are linked in the [evidence index](evidence-index.md).

## Week 12 prework

An independent challenger can reject adoption even if the portfolio clears the 6.5% screen. The challenger can show that an annualized historical mean is insufficient evidence for the forward rolling five-year net objective, reproduce a window comparison that exceeds the decision's stability limit, or find that reserve eligibility or vintage timing cannot be verified. To keep use bounded, assign a monthly review to the portfolio analyst and return to committee if the screen or reserve rule becomes infeasible. [Week 12 handout model-risk reference](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-12/student-handout.md#local-model-risk-reference)

## Riskiest claim and test

**Claim under challenge:** The 60% BIL / 40% VT result is stable enough for live adoption. **Test:** On the same frozen CSV, switch from all 59 monthly returns to the last 36. Hold the 6.5% objective, 3% reserve minimum, BIL/IEF eligibility and five-point grid fixed. Use the largest absolute weight change and compare it to the five-point review limit from Lab 15. The window changes estimates of means, volatility, and correlation together.

**Disposition:** Qualify the recommendation to a paper pilot. The reproduced switch moved BIL from 60% to 85% and VT from 40% to 15%, a 25-percentage-point maximum change. The screen was feasible in both cases and the stability condition failed. This checks an existing comparison. [Executed allocations](../outputs/allocations.csv)

## Portfolio comparison validation

Codex helped implement and test the Streamlit comparison. Equal-weight and inverse-volatility baselines use their formula weights. The constrained portfolio uses the existing minimum-volatility search. Each portfolio is evaluated with the same selected window, edited annual return estimates, annual covariance and reserve settings. The sensitivity section continues to compare the current constrained result with the original all-month constrained result.

`python3 validate.py` independently recomputed the rendered weights, return, volatility, reserve and rule verdicts from the monthly prices using pandas and NumPy. Streamlit checks covered default inputs, the 36-month switch, a return override, an eligibility edit, a 100% reserve threshold, the upload path, Meridian and infeasibility. The 25.00-percentage-point window sensitivity was reproduced. [Executed check log and rendered tables](../outputs/portfolio-comparison-validation.txt)

With default settings, the all-month estimated return was 3.01% for equal weight, 3.37% for inverse volatility, and 6.61% for the constrained portfolio. Over the last 36 months these estimates were 8.13%, 4.61%, and 6.75%, respectively. All three met the 3% reserve allocation screen in both windows under the assumed eligibility. The rolling five-year net CPI + 4% objective remains unresolved because the numerical screen uses annual estimates and the model does not evaluate rolling outcomes net of costs and against realized inflation. Actual liquidity, issuer exposure and exemptions, and live implementation restrictions also remain unresolved.

## Locked Changed-Input Record — unresolved

The existing Lab 15 stresses provide comparison evidence. No Project 2 AI-off prediction, pre-run GitHub commit or locked execution was located. The Week 12 assistant test is recorded separately. For submission, independently select one material input, record its old/new values, predicted direction and decision effect with timestamp, commit the prediction to GitHub before execution, run with AI closed, then preserve and reconcile actual before/after output and the decision effect. [Lab 11 pattern](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-06/lab-11-proforma-what-if.md)

## Partner cold run — pending

Give your partner only the published README link. Have them run in their own folder without coaching and record command, first failure (or none), elapsed time, and result location. Swap roles. The assistant run is logged separately in the [Week 12 record](week-12.md).
