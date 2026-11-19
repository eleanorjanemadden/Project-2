# Lab 18 — Legend Investor as Skill

Eleanor Madden | November 3, 2026

## D — Define

**Can an investor's philosophy become a skill my AI runs the same way every time — every number computed by code from the 10-K, the judgment the model's?**

Yes, for a clearly defined screen. My skill fixes the data source, annual periods, formulas and missing-data rules. Python computes the financial evidence, and the AI decides how convincing that evidence is. A consistent process does not guarantee a correct investment judgment.

**Opening discussion:** Code can calculate owner earnings from operating cash flow and capital spending. Deciding whether the business has a lasting competitive advantage requires judgment and more evidence than a passing screen.


## R — Represent

My script downloads SEC's ticker-to-CIK mapping and the company's facts using `Eleanor Madden madden42@purdue.edu FIN43900 academic project` as its User-Agent. The email matches the workspace Git configuration. The raw SEC files and `.source.json` records retain the URL, retrieval time and checksum.

The script uses only USD facts from **10-K** filings. Annual flows require a period of 350–380 inclusive days, covering ordinary calendar years and retail 52/53-week years while excluding quarters and year-to-date periods. It selects the last five distinct annual end dates, rather than trusting `fy` on comparative facts. `fy` can describe the filing year while the fact describes an earlier period. For each required tag and fiscal end, the latest filing wins; the course's first-choice tag is preferred when available, followed by its named fallback. Equity is an instant at that same year-end.

ROE is net income divided by **year-end** equity, expressed as a percent. Owner earnings are operating cash flow minus capital spending. This is the course's simplified proxy; the broader Buffett reference discusses maintenance spending, which this lab does not estimate. Missing facts print “not found”; missing or nonpositive equity makes ROE “not known.” Missing inputs make the relevant checks “not known.” Derived metrics show their input tags rather than pretending to have a separate XBRL tag.

**Threshold choice:** I kept ROE at or above 15% in every year because it is the required course screen and makes consistency visible. It is a screening choice, not proof of a moat. The checks use unrounded ROE; only the displayed values are rounded.

## I — Implement

**My request to the AI:** Build a reusable Buffett skill using only SEC annual 10-K facts and the course's tag and missing-value rules. Bundle a Python ticker script, compute the required metrics and checks, and then write a short business-quality memo from the printed evidence. Build a Streamlit app with the chart, table, sources, checks, editable memo and unsupported-number flag. Run COST and JPM and verify the results against the lab. Keep the code simple and preserve my earlier work.

The app defaults to the saved SEC downloads so the submitted results can be reproduced without network access. Its live mode downloads fresh data for a typed ticker. Saved memos are tied to a fingerprint of their financial evidence, so a changed table produces a stale-memo warning. For a new ticker, run the skill to write its memo or paste an AI-written draft into the app. The app itself does not call a paid model or generate a canned verdict.

The number checker compares each digit-based numeric token against the financial values, dates and thresholds printed by the script. It normalizes commas and trailing decimal zeros and keeps percentages distinct from plain amounts. It reports each unsupported occurrence with its character position. A matching number can still be attached to the wrong metric, so the prose needs review too.

## V — Validate

[The executed validation transcript](outputs/validation_run.txt) records **seven passing tests**, including app interactions. The [live app check](outputs/live_app_check.json) also confirmed a fresh COST SEC download, and the [server health check](outputs/server_health.txt) returned HTTP 200. [The independent cell comparison](outputs/known_answer_comparison.csv) checks the course table against the computed output. All **35 financial cells** and all five fiscal-year ends match; dollar differences are zero and ROE matches at the instructor's displayed precision.

Dollar amounts below are USD millions.

| Fiscal year end | Revenue | Net income | Operating cash flow | Capital spending | Equity | ROE | Owner earnings |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2022-08-28 | 226,954 | 5,844 | 7,392 | 3,891 | 20,642 | 28.3% | 3,501 |
| 2023-09-03 | 242,290 | 6,292 | 11,068 | 4,323 | 25,058 | 25.1% | 6,745 |
| 2024-09-01 | 254,453 | 7,367 | 11,339 | 4,710 | 23,622 | 31.2% | 6,629 |
| 2025-08-31 | 275,235 | 8,099 | 13,335 | 5,498 | 29,164 | 27.8% | 7,837 |
| 2026-08-30 | 303,154 | 9,226 | 15,817 | 6,435 | 35,803 | 25.8% | 9,382 |

| Buffett check | COST | JPM |
|---|---|---|
| ROE at least 15% every year | pass | fail |
| Owner earnings positive every year | pass | not known |
| Owner earnings increased from first to last year | pass | not known |

Both Costco lines finish above their initial values, although owner earnings decline in the middle of the period. The first-to-last growth check does not mean growth every year. The full [COST run](outputs/COST_run.txt) includes every tag, fiscal period, filing date and accession. For example, Costco's fiscal 2022 revenue comes from the later comparative 10-K filed in 2024, not automatically its original filing.

**JPM probe:** The [JPM run](outputs/JPM_run.txt) covers fiscal year-ends 2021–2025; a completed fiscal 2026 annual filing is not yet available. Both permitted capital-spending tags are absent for these years. Capital spending and owner earnings therefore stay “not found,” and the owner-earnings checks stay “not known.” ROE fails the every-year threshold because fiscal 2022 is 12.9%. The [JPM memo](memos/JPM_memo.md) explicitly says it cannot judge owner earnings. Missing tags do not mean the company spent nothing.

**Hand-typed-number probe:** AppTest appends `Invented ROE: 40.0%.` to the COST memo. The app reports [“Unsupported memo numbers: 40.0%”](outputs/number_probe.txt). The unedited COST and JPM memos have no unsupported numeric tokens. Additional tests verify annual rather than quarterly selection, tag fallback, latest filings, missing flows, nonpositive equity, and repeated unsupported numbers.

**Fresh chat without the skill:** This part could not be executed here: no browser or native chat surface is available. I have not invented a comparison transcript. [The comparison worksheet](fresh_chat_comparison.md) contains the exact prompt, the computed reference values, and the source questions to answer after a fresh browser chat. The important comparison is whether the other answer identifies annual SEC facts, fiscal ends, equity convention and filing dates; matching numbers alone would not prove that it followed the same process.


**Partner question: Where does “not found” come from?** `choose_fact()` returns `None` when no permitted fact survives the filters. `display_value()` converts that missing amount to the literal words “not found.” The later check code turns a missing required input into “not known.” The model does not decide which missing number to fill in.

## Buffett memo and my decision

Its verdict is **own the business**, with limits about unverified competitive advantage and management. My draft trust decision appears directly under the memo. I agree with using it as a first screen because the cash and ROE are traceable, but I would investigate the moat and management before acting. The memo does not judge the stock's price.

## Learn — Agent skills

**What is a skill?** A reusable folder of instructions, optionally with scripts and references, that tells an AI how to handle a specific kind of task. Here it fixes how the financial evidence is prepared before the AI writes a judgment.

**How does it work, and why load the name and description first?** Those short fields help the AI decide whether the skill matches the request. It reads the full instructions when needed and runs the bundled script for the calculations. Loading relevant details later keeps unrelated instructions out of the working context.

**Why do the numbers belong in code?** The same filing inputs should give the same calculations and missing-data results. Code makes the filters, units and formulas inspectable. The model can explain the result, but plausible language is not a substitute for calculating it.

## Reflect

**What stays the same, and what is left to the model?** The SEC source, tag order, annual-period rule, latest-filing rule, formulas, thresholds and missing-value behavior stay fixed. The model decides how much confidence to place in the business and explains what the evidence does not establish. Fresh SEC filings can change the inputs, so repeatability means the same method on the same data, not frozen results forever.

**Why is “not found” better than an estimate?** It shows the boundary of the evidence. An estimated capital-spending figure could make JPM's owner earnings look complete and change the verdict without a basis in the permitted data. I would rather know what I still need to investigate than present a precise-looking answer I cannot defend.
