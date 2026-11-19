# Lab 16 submission

Start with [Lab_16.md](Lab_16.md) for the answers, data card, calculations, explanations, reflections, and instruction audit.

Run from this directory (Python 3, no packages required):

```bash
python3 asof.py
python3 validate.py
```

Visible executed results:

- [March 31 funnel, full panel, and signals](outputs/asof_run.txt)
- [April 15 full run](outputs/later_date_run.txt)
- [Known-answer and later-date validation](outputs/validation_run.txt)

To refresh the saved logs:

```bash
python3 asof.py > outputs/asof_run.txt
python3 validate.py > outputs/validation_run.txt
```

`validate.py` automatically regenerates `outputs/later_date_run.txt` using a temporary copy with an edited date. The submitted `asof.py` stays at March 31. `instructions/` preserves the three course Markdown materials read for the lab.

Upload this folder to GitHub and submit links to `Lab_16.md`, `asof.py`, and the supporting validation/output files. GitHub publication and course checkout have not been performed. Personal answers are drafts; review them and complete the independent quiz and real partner explanation/file swap before checkout.
