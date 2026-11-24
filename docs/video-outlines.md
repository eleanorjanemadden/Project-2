# Project 2 recording scripts

These drafts are for recording. The final transcripts will reflect the recorded videos.

## Video 1 — How it changed

I used ChatGPT through Codex to package and reproduce my work, test allocation sensitivity, and draft these materials. The analysis and decision are mine. Education, not investment advice.

I started with the Meridian mandate checker. It taught me to turn a client request into rules I could evaluate. For my scholarship foundation, four quarterly payments of $750,000 add up to $3 million, so I set a 3% reserve floor on a $100 million portfolio. Whether IEF counts toward that floor still depends on how the committee treats fluctuations in payout reserves.

My first full-sample result was 60% BIL and 40% VT. Codex suggested checking whether it survived a shorter estimation window. I held the price snapshot and mandate rules fixed and changed from 59 monthly returns to 36. VT fell from 40% to 15%, with BIL rising by the same 25 points. Both mixes passed the numerical screen, but their difference was five times my five-point review limit. I accepted the test and withdrew the case for live adoption. I kept the 60/40 mix as a paper reference because it gives the committee a concrete allocation to monitor under different assumptions. [Mandate](../PROJECT2-MANDATE.md) · [AI-output register](validation-and-ai-use.md#ai-output-register)

## Video 2 — Technical walkthrough

I used ChatGPT through Codex to reproduce the app, check the optimizer and draft these materials. The analysis and decision are mine. Education, not investment advice.

The README starts the analysis and Streamlit app. The default input is a frozen set of adjusted monthly prices. In `estimate_from_csv`, I turn adjacent prices into monthly returns. The code annualizes the mean and covariance, then passes estimates into `search_portfolio`. The search enumerates fully invested, long-only mixes in five-point steps. It drops mixes with less than 3% in eligible reserve assets or less than 6.50% estimated return after costs. It chooses the lowest volatility among the remaining mixes.

The comparison table applies the same screens to equal weight and inverse volatility. Their weights come from fixed formulas. At default settings they both fail the return screen. I can change only the annual cost to 15 basis points and see the constrained portfolio move from 60/40 to 55/45. An independent grid calculation reproduces the result. The original portfolio falls to 6.4645% after cost. The selected portfolio clears the hurdle at 6.8342%, with higher volatility. The two figures show why fee assumptions matter even when the app still returns a feasible portfolio.

The GS10 panel uses saved vintages. On September 30 the latest visible month was August at 4.68%. The October 1 vintage first shows September at 4.99% among the saved cutoffs. That panel gives me timing context for the bond sleeves. The optimizer uses ETF inputs. [README](../README.md) · [15 bp experiment](validation-and-ai-use.md#changed-input-experiment--additional-annual-cost) · [GS10 validation](../outputs/gs10-validation.txt)

## Video 3 — Committee presentation

*Opening visual: the running app on the default portfolio comparison.*

I used ChatGPT through Codex to reproduce the portfolio analysis, check model sensitivity, and draft these materials. The analysis and decision are mine. Education, not investment advice.

I ask the committee to approve a 90-day paper pilot with zero live capital. The reference is 60% BIL and 40% VT. On the frozen data through September 2026, the app estimates 6.61% annual return at zero additional cost and 6.05% annual volatility. The return clears our numerical screen by about 11 basis points. It is a historical arithmetic estimate. The foundation's objective requires rolling five-year net returns against inflation.

Across the two estimation windows and tested costs, BIL ranged from 45% to 85% and VT from 15% to 55%, with 0% IEF and up to 5% LQD. The window alone moved the equity weight by 25 points. A fee of 15 basis points made the reference fail the screen and pushed the optimizer to take more equity risk. Those results give me two concrete reasons to defer live funding.

I would ask the committee to confirm whether IEF counts toward the $3 million payout reserve. The portfolio analyst will log the simulated outcomes monthly and report to the committee at day 90. I would stop the pilot early if there is no mix that meets both the return screen and reserve rule. I would revisit funding only once the committee verifies the implementation terms and costs, reviews forward evidence for the net objective and sees no more than a five-point allocation shift under the stress tests. Today I am asking for approval of the paper pilot and designation of its monitoring owner. [Decision memo](decision-memo.md)
