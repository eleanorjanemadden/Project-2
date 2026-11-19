# Lab 18 — Eleanor Madden

Start with [Lab_18.md](Lab_18.md). The package includes a reusable Buffett skill, a Streamlit app, actual saved SEC downloads, COST/JPM memos, and executed validation outputs. Lab 17 remains unchanged.

Run from this folder:

```bash
python3 -m pip install -r requirements.txt
python3 skill/buffett-sec/scripts/buffett.py COST --offline --memo memos/COST_memo.md
python3 skill/buffett-sec/scripts/buffett.py JPM --offline --memo memos/JPM_memo.md
python3 validate.py
python3 -m streamlit run buffett_app.py
```

The app starts with the saved SEC download and offers live downloads for a typed ticker. To refresh both submitted tickers:

```bash
python3 refresh_data.py
```

The current workspace has no operating-system DNS resolver. The submitted downloads were obtained with `python3 refresh_data.py --dns-fallback`, which uses HTTPS DNS lookup only after OS resolution fails. SEC remains the financial data source and HTTPS certificate verification remains enabled. Normal machines do not need this option. The live app can use ordinary network access; on this workspace, refresh with the helper and select saved downloads.

After refreshing, ask Codex to use `$buffett-sec` on COST/JPM, read the printed evidence, and revise any stale memo. Numbers and verdicts are not hardcoded in the app. The current memos were written by Codex after executing the skill's script.

The submitted skill folder is `skill/buffett-sec`. A copy has been installed at `~/.agents/skills/buffett-sec`. On another computer, copy that folder to the same user skill location, or into the repository's `.agents/skills/`. Restart Codex if it has not discovered the new skill.

Key files:

- [Lab report and reflection drafts](Lab_18.md)
- [Skill instructions](skill/buffett-sec/SKILL.md) and [bundled script](skill/buffett-sec/scripts/buffett.py)
- [Streamlit app](buffett_app.py)
- [COST memo](memos/COST_memo.md) and [JPM memo](memos/JPM_memo.md)
- [Known-answer comparison](outputs/known_answer_comparison.csv), [validation transcript](outputs/validation_run.txt), and [number probe](outputs/number_probe.txt)
- Raw `data/*_companyfacts.json` files with source manifests; `outputs/*_run.txt` files include XBRL and filing provenance.
- [Submission checklist](SUBMISSION_CHECKLIST.md) and [fresh-chat worksheet](fresh_chat_comparison.md)

Upload the full contents of this folder to a Lab 18 GitHub repository, keeping the directory structure. Submit GitHub file links for the report, app, skill and bundled script, and include the memos and supporting data/outputs. The lab's submission format is GitHub links, not just a ZIP. No repository has been created, pushed, or submitted to Brightspace by this local task.

Remaining student actions: review the personal drafts, perform the fresh browser-chat comparison, complete the no-AI partner explanation/discussions, and submit the links. These activities are not claimed as completed in the report.
