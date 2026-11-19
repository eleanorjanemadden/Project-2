# Sources and evidence

All pages were accessed for this lab on November 5, 2026. Course and framework Markdown copies are in `instructions/`; SEC raw files and source records are in `data/`. The course's narrow lab rules govern this submission when they differ from the broader investor reference templates.

| Purpose | Source | Local evidence |
|---|---|---|
| Full lab and five-part merit rubric | [Lab 19](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-11/lab-19-legend-panel.md) | `instructions/lab-19-legend-panel.md` |
| Original formulas, tag precedence and known answer | [Lab 18](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-11/lab-18-legend-investor-as-skill.md) | `instructions/lab-18-legend-investor-as-skill.md` |
| Weekly context, prework, rules and session | [Week 11](https://github.com/CinderZhang/FIN43900-Fall2026/tree/main/lessons/week-11) | `instructions/README.md`, `student-prework.md`, `student-handout.md`, `slides-session-19.md` |
| Plugin description, read only | [FAskills README](https://github.com/CinderZhang/FAskills/blob/main/README.md) | `instructions/FAskills_README.md` |
| Buffett philosophy | [Buffett reference](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/warren_buffett.md) | `instructions/warren_buffett.md` |
| Graham philosophy | [Graham reference](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/ben_graham.md) | `instructions/ben_graham.md` |
| Burry philosophy | [Burry reference](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/michael_burry.md) | `instructions/michael_burry.md` |
| Existing student work | [Eleanor's Lab 18](https://github.com/eleanorjanemadden/Lab-18) | Published app/report checked against local files; local extraction reused in `buffett.py` |
| Fund selection | Local Lab 15 mandate | `instructions/PROJECT2-MANDATE.md` |
| Largest company holding | [Vanguard VT fact sheet](https://fund-docs.vanguard.com/F3141.pdf), September 30, 2026, page 2 | `data/VT_fact_sheet.pdf`; NVIDIA listed first at 4.6% |
| SEC API and annual facts semantics | [EDGAR API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) | SEC response records and printed provenance |
| Ticker-to-CIK mapping | [SEC ticker file](https://www.sec.gov/files/company_tickers.json) | `data/company_tickers.json` and `.source.json` |
| COST financial facts | [SEC COST facts](https://data.sec.gov/api/xbrl/companyfacts/CIK0000909832.json) | `data/COST_companyfacts.json`, original Nov 3 source record; copied from Lab 18 |
| NVDA financial facts | [SEC NVDA facts](https://data.sec.gov/api/xbrl/companyfacts/CIK0001045810.json) | `data/NVDA_companyfacts.json`, new Nov 5 source record |
| JPM actual missing-data probe | [SEC JPM facts](https://data.sec.gov/api/xbrl/companyfacts/CIK0000019617.json) | `data/JPM_companyfacts.json`, original Nov 3 source record; copied from Lab 18 |
| App layout | [Streamlit columns](https://docs.streamlit.io/develop/api-reference/layout/st.columns) | `panel_app.py`, three columns verified with AppTest |
| Skill folder conventions | [Codex skill docs](https://developers.openai.com/codex/skills), [Antigravity skills](https://antigravity.google/docs/skills) | Named `SKILL.md` files with descriptions and bundled executable scripts |

SEC flows and instants retain each selected accession, filing date, period and tag in `outputs/*_results.json` and `*_run.txt`. The source manifests' retrieval times describe the downloaded responses; each metric's filing date can be earlier. The course asks for latest available filings, not a historical as-of screen.

`outputs/source_inventory.json` records hashes for saved instructions and the holdings PDF. The SEC responses have their own independently checked download hashes. `outputs/prior_work_comparison.json` records that the two published Lab 18 files match their local counterparts. FAskills was not installed, and no paid keys, price data or reference price targets were used.
