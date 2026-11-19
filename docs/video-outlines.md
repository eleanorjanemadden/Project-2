# Three video outlines

> I used ChatGPT through Codex to help package and reproduce my work, audit the stability claim, and prepare these materials. The analysis and decision are mine. Education, not investment advice.

Use this opening aloud in each recording. For Video 3, put the running app on screen from the first frame.

## Video 1 — How it changed (up to 3:00)

- Start with the Meridian mandate checker from Lab 13, then explain how it informed the scholarship foundation’s 3% payout reserve and the BIL/IEF eligibility question.
- Explain how checking the assistant’s stability-test proposal changed the case for adoption. Reproduce the September 2026 snapshot comparison and show 40% VT on all 59 returns versus 15% on the last 36. The 25-point gap exceeds the five-point condition, so qualify the result to a paper pilot.
- Give your own account of which parts of the decision evolved and why. [Mandate](../PROJECT2-MANDATE.md) · [Validation](validation-and-ai-use.md)

## Video 2 — Technical walkthrough (up to 5:00)

- Show the README run command and trace the saved adjusted prices through `estimate_from_csv`, annualized estimates and covariance, and `search_portfolio` in `portfolio.py`. Explain the long-only five-point grid and 6.5% return and 3% reserve screens.
- Toggle the last-36 switch with the default inputs and point to the saved 25-point movement in `outputs/allocations.csv`. Show why a correct calculation can fail the stability test.
- Show the GS10 timing panel in the app and its Lab 17 data card. At the September 30, 2026 cutoff the latest visible GS10 is August’s 4.68%. September’s 4.99% belongs to the later vintage. [Evidence map](evidence-index.md)

## Video 3 — Committee decision (up to 5:00)

- Open with the app live and speak the disclosure, then ask the committee to approve a paper pilot at 60% BIL / 40% VT and defer live allocation.
- On data through September 2026, show 6.61% estimated return and 6.05% volatility for the reference portfolio. Label the reference as zero additional cost. The original window and return stresses produced 55–85% BIL, 15–45% VT, and 0% IEF/LQD. The illustrative cost stresses across both windows produced 45–85% BIL, 15–55% VT, 0% IEF, and 0–5% LQD.
- Ask the client to confirm BIL/IEF eligibility. Monitor reserve eligibility, screen feasibility and weights monthly. Require credible forward estimates and a cost allowance before adoption. A weight shift above five percentage points keeps live adoption deferred. Stop the paper pilot and return to committee if the agreed reserve rule or after-cost return screen becomes infeasible.
- Rehearse with a sceptic. If asked whether 6.61% establishes the rolling five-year net objective, say that the system estimates historical arithmetic return and needs forward return and cost evidence for that decision. [Committee memo](decision-memo.md)
