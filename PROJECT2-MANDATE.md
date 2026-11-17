# Project 2 mandate — draft

Eleanor Madden | October 22, 2026

This draft carries forward the four ETF roles I prepared in Lab 14 and uses a fictional scholarship foundation as my client. The client details below are choices for this exercise, not facts supplied by a real client.

The foundation has a $100 million portfolio, a seven-year horizon, and quarterly scholarship payments of $0.75 million. Its objective is CPI + 4% annually over rolling five-year periods, net of costs. Using a 2.5% CPI estimate gives a **6.5% numerical objective** for the lab. Among mixes meeting that screen, the app minimizes estimated annual volatility.

The universe is **BIL, IEF, LQD, and VT**: Treasury bills for cash and reserve, intermediate Treasury bonds, investment-grade corporate bonds, and global equities. Use only fully invested, long-only allocations, with no borrowing, short sales, or derivatives. The app searches in five-percentage-point steps.

My one additional hard constraint for the search is **at least 3% in reserve-eligible BIL and IEF**, calculated as 4 × $0.75 million / $100 million. IEF counts as a daily-liquid government-bond fund for this draft, but its market value can fall. Eligibility does not mean its principal is guaranteed. There is no separate sector, ESG, tax, or home-bias preference in this draft.

For comparison with my earlier checker, I retain Meridian's 90% liquid-within-five-business-days and 8% company-issuer rules, with diversified funds exempt from the latter. The checker maps the ETFs to their course holding roles; it does not independently establish their actual redemption terms. Before implementation, I would verify those terms and agree on a rebalancing and turnover policy.

**One question for my client:** May the payout reserve include a Treasury-bond fund whose market value can fall, or must it stay in Treasury bills?

If the client requires bills only, I would untick IEF and keep BIL eligible. The current all-month and 36-month mixes already use BIL, so that clarification alone would not change these two allocations. A strict loss guarantee would require a different risk discussion; the app's volatility calculation cannot certify it.

Historical ETF return estimates are based on adjusted prices. Fund expenses are reflected in historical performance, but this lab has no separate estimate for trading or advisory costs. Clearing 6.5% is therefore a preliminary screen, not evidence of achieving the rolling five-year net objective.
