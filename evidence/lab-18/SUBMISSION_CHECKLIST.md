# Lab 18 requirement audit

The course grades this as a completion checkout, 25 or 0. This audit reports evidence rather than predicting a grade.

| Requirement | Status and evidence |
|---|---|
| Read full lab, slides, prework, handout, Buffett framework and FAskills README | Read; retained under `instructions/` |
| Inspect/build on Lab 17; preserve earlier work | Existing local and GitHub files inspected; only Lab 18 files added |
| Own request to the AI | Recorded in `Lab_18.md` |
| Discoverable skill with name, description and bundled script | `skill/buffett-sec/`; installed copy recorded in `outputs/skill_installation.txt` |
| Keyless ticker-to-CIK and company facts, named/email User-Agent | Script and `data/*.source.json` |
| 10-K only, five fiscal ends, full-year flows, latest filing, specified tag precedence | Script; validation includes annual, fallback and latest-filing checks |
| Required metrics and XBRL tags; derived formulas shown | `outputs/COST_run.txt`, `outputs/JPM_run.txt` |
| Three Buffett checks computed in code | Both result JSON files and app |
| COST AI memo saved as Markdown, permitted verdict, no price data | `memos/COST_memo.md`, validated numeric support |
| Chart owner earnings and net income; table/checks/memo | `buffett_app.py`; executed AppTest |
| Required caption under title | AppTest confirms caption |
| COST matches all provided values and checks | 35 matching financial cells; `known_answer_comparison.csv` |
| JPM missing capital spending/owner earnings; checks not known; memo admits gap | Executed JPM test and memo |
| Hand-typed unsupported ROE flagged in app | `outputs/number_probe.txt` |
| Fresh browser AI chat with no skill | **Not executed: browser/native chat unavailable.** Prepared `fresh_chat_comparison.md` |
| Opening partner discussion; six-minute no-AI explanation and swap | **Student activity still required.** Draft talking points and line-by-line practice in report |
| Trust decision directly under memo | Included and marked personal draft |
| Learn questions and reflection answers | Completed drafts in report |
| Thursday prework: largest company in a Project 2 fund, ticker; Graham/Burry reading | VT → NVIDIA/NVDA; Vanguard holdings source and notes in report |
| GitHub links in Brightspace → Quizzes → Lab 18 | **Not uploaded/submitted.** Full folder prepared; README gives submission steps |

All executable checks available here passed. The rubric floor's software/data/memo requirements are satisfied; the remaining human and external submission steps above must be completed before calling the entire lab submitted.
