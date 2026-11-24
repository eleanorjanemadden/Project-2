# Week 12 studio record

[Course handout](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-12/student-handout.md) · [Prework answer and claim test](validation-and-ai-use.md) · [Recording scripts](video-outlines.md)

## Assistant reproducibility run — November 17, 2026

Installed the requirements in a fresh Python 3.13.1 environment and ran `python analyze.py && python -m streamlit run app.py`. The first source audit uncovered mixed price vintages. The Lab 15 folder held a later CSV and later raw prices. The original October 20 CSV reproduces the saved full-precision allocations, and its matching raw responses are in Lab 14. The bundle restores them together. Streamlit now opens directly on that snapshot.

The executed CSV and full-precision JSON are in `outputs/`. The local Streamlit health endpoint returned `ok`. The app-level window test and other checks are in the validation log. [Executed result](../outputs/week-12-result.md) · [Validation log](../outputs/week-12-validation.txt)

## Automated cold run and submission audit — November 19, 2026

A separate fresh clone at `2832a67` ran the documented setup, analysis, and Streamlit commands. The server health check returned HTTP 200 in 22.2 seconds from clone, 53 checks passed, and the regenerated tracked files matched the checkout. The transcript omits the machine's local network address. [Automated cold-run transcript](../outputs/automated-cold-run.txt) · [Original link findings and post-repair checks](../outputs/submission-link-audit.txt)

The app now shows the original stress range, the broader illustrative cost-stress range, and the pilot stop condition separately from the live-adoption deferral threshold. The historical list below records the earlier studio state.

## Partner record — simulated review completed

The [simulated partner review](partner-review.md) records the fresh-clone setup and app checks, with preserved logs. Independent human review and rehearsal remain unverified.

## Submission status

The public repository, three recordings, and caption-derived transcripts are linked in the [submission manifest](manifest.md). The current app includes both baselines with verdicts and an explicit cost stress. The student-authored AI-off Locked Changed-Input Record remains unresolved.

## Historical studio must-fix list

This list records the original studio findings.

1. **Delivery and independent review.** Publish the single Project 2 folder to GitHub with instructional-team access. Replace unresolved manifest locations with verified links as artifacts become available. Capture the uncoached partner run and repair any failure it surfaces.
2. **Submission evidence.** Complete the AI-off Locked Changed-Input Record with a pre-run GitHub commit. Review the paper-pilot recommendation and confirm monthly monitoring and the stop trigger. Rehearse and record the three distinct videos, correct their captions and transcripts, and complete the manifest.
3. **Existing app coverage.** The preserved Lab 14 baselines and mandate verdicts are separate from the Lab 15 app, and its stress controls cover the window, return estimates and reserve constraints. The final Project 2 brief asks for both baseline verdicts in the app and an explicit cost stress. At the studio stage, both items were still open. The current app now includes both. Keep the GS10 timing evidence separate from any unverified trading claim.

## Committee answer and readiness reflection

I recommend a 90-day paper pilot with no live funding. My most reversible claim is that the full-sample 60/40 mix is stable enough to fund. A 25-point allocation change when I shorten the window, and failure of the unchanged mix after a 15 bp fee, are enough to withhold funding. I would reconsider if the committee verifies reserve and liquidity terms, agrees on costs, and sees a forward case that clears the net objective with stress shifts of five points or less. [Decision memo](decision-memo.md) · [Changed-input experiment](validation-and-ai-use.md#changed-input-experiment--additional-annual-cost)

The automated cold run found that a fresh clone could regenerate the same files without relying on my working folder. The link audit found broken paths in copied course handouts that I would have missed by clicking only the top-level README. The subsequent link audit reported zero broken local links. The current app includes the two baselines, cost stress and GS10 panel. The [simulated partner run](partner-review.md) is recorded. Independent human review remains unverified. For the final review I would freeze the price snapshot, allocation grid and reserve assumptions so the memo and visible output continue to refer to the same experiment. [Cold-run transcript](../outputs/automated-cold-run.txt) · [Link audit](../outputs/submission-link-audit.txt)

The decision number comes from `search_portfolio`. I first convert adjusted monthly closes into simple returns. I annualize their arithmetic means by multiplying by 12 and compute annual covariance from monthly co-movements. Each candidate has 20 weight units, each worth five percentage points. For every candidate, I multiply the weights by the annual return estimates, sum the products and deduct additional annual cost. I sum eligible weights for the reserve check. Among candidates clearing both screens, I choose the one with the lowest square root of portfolio variance. A flat fee leaves a fixed portfolio's volatility unchanged. It can change the chosen portfolio's volatility by removing a low-risk allocation from the feasible set. That is what happened at 15 bp. [Portfolio engine](../portfolio.py) · [Saved cost experiment](../outputs/changed-input-cost.csv)

## Honest failure memo — Week 12 hypothetical

I would reject live adoption if the process failed to beat its baseline after agreed costs. The strongest claim I would retain is that a check of dated inputs can protect the decision from using a number before it was available. My GS10 example shows exactly that boundary. The evidence would leave three claims unsupported: durable outperformance after costs, achievement of the foundation’s rolling five-year net objective, and a repeatable trading advantage from GS10. The hypothetical baseline failure is the premise of this exercise. My ETF evidence consists of fitted estimates and sensitivity tests. [Studio challenge](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-12/open-ended-challenge.md) · [GS10 evidence](../outputs/gs10-validation.txt)

I used Codex to develop three responses to the premise. **Reject [assumption]** if the policy baseline wins after agreed costs, because added optimization needs a decision benefit. **Redesign [source]** around a dated availability gate, which is supported by the September 30 and October 1 vintage comparison. **Pilot [speculation]** because requiring a dated input log might reduce unsupported overrides in prospective use. The actual app readout [output] shows August's 4.68% at the September 30 cutoff, with September's 4.99% first appearing among the saved dates on October 1.

I would approve only a 90-day, zero-dollar paper pilot of the redesigned monitoring workflow. Before day one I would freeze the benchmark, comparable cost assumptions, reserve rule and decision timestamps. The portfolio analyst would log monthly results for the baseline and candidate using only evidence available at each cutoff, measuring after-cost performance, reserve coverage and provenance exceptions. The analyst would stop the pilot at a material timing breach or if both screens cannot be met and report the cause to the committee. At day 90 I would review whether the workflow produced an auditable decision and whether further observation is justified. Any case for live funding would require longer prospective evidence and a separate committee decision.
