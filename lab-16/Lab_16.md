# Lab 16 — Provenance Gate

Eleanor Madden | October 27, 2026

## D — Define

**On the day you would have traded, what did this data actually say — and how much of what you see now came later?**

On March 31, 2026, the latest knowable card-spend signals were AAA **+1.98%**, BBB **−1.02%**, and CCC **+0.91%**, all measuring February versus January. Looking later adds March releases for AAA and BBB and an April revision of February for CCC. Those later numbers could not have supported a March 31 decision.

My explanation to my partner: the month measured tells me when spending happened. The publication date tells me when I could see the number. A March observation published in April is still unavailable for a March 31 decision.


## R — Represent

### Data card

- **Source:** the 12-row fictional training table in the [Lab 16 instructions](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-10/lab-16-provenance-gate.md), saved in [instructions/](instructions/).
- **Measure and units:** monthly card-spend index for fictional retailers AAA, BBB, and CCC; index points. The base period is not supplied. These are not stock prices or investment returns.
- **Decision date:** March 31, 2026; publications on that date are included. The exercise uses dates, with no intraday trading cutoff supplied.
- **Publication lag:** January values arrive February 10; initial February values arrive March 10; March values arrive April 10. CCC also has a February revision dated April 5. Measured month alone cannot establish availability.
- **Revisions and quality:** AAA February changes from 104 to 103 on March 25; CCC February changes from 111 to 112 on April 5. Row 7 duplicates row 6, excluding row ID; row 11 has no ticker.
- **Retrieval:** course materials read and saved October 27, 2026. The training values are embedded at the top of `asof.py`; no live data download or external package is required to run it.


## I — Implement

Run from this folder:

```bash
python3 asof.py
python3 validate.py
```


### Rule 4 — line-by-line explanation to practice

The block is `latest_publications` in `asof.py`.

1. `latest = {}` starts an empty dictionary that will hold one row for each ticker/month.
2. `for row in rows:` considers every row passed into the function. For the as-of panel, future publications have already been excluded.
3. `key = (row[1], row[2])` groups by ticker and measured month, so AAA January and AAA February remain separate observations.
4. `if key not in latest or row[3] > latest[key][3]:` accepts the first row in a group or a publication later than the one currently stored. The fixed-width ISO dates sort chronologically. The `or` avoids looking up a missing key. For identical publication dates the first row is retained; no conflicting same-day values occur in this table.
5. `latest[key] = row` stores the full row, keeping its original ID and value. AAA row 4 replaces row 2 because March 25 is later than March 10.
6. `panel = sorted(...)` returns the selected rows in original row-number order for an easy audit; the signal calculation sorts by measured month separately.
7. `kept_ids = {...}` collects the selected IDs.
8. `removed = [...]` identifies the input IDs replaced by later vintages.
9. `return panel, removed` supplies both the observations and their audit trail.

**Partner question:** Why not choose the latest vintage first and then filter by date?

**Answer:** CCC's April 5 revision would replace its March 10 release, and filtering afterward would remove the revision without restoring the older knowable value. The publication filter has to run first.

### AI quiz preparation

**Quiz question:** In `if key not in latest or row[3] > latest[key][3]:`, what happens for AAA row 4, and why does it not overwrite AAA January?

**Answer:** Its key is AAA and February. That key already holds row 2, but March 25 is later than March 10, so row 4 replaces it. January has a different key and stays unchanged.

**Explanation:** A dictionary key identifies one observation, while publication date chooses its vintage. The first part of the condition handles a new observation; the second handles a revision.

## V — Validate

The executed [March 31 output](outputs/asof_run.txt) matches the lab's complete known answer:

| Funnel step | Count removed | Original row IDs |
|---|---:|---|
| Missing ticker | 1 | 11 |
| Exact duplicate | 1 | 7 |
| Published after March 31 | 3 | 3, 8, 10 |
| Older vintage replaced | 1 | 2 |
| As-of panel retained | 6 retained | 1, 4, 5, 6, 9, 12 |

The count reconciles: **12 − 1 − 1 − 3 − 1 = 6**.

| Ticker | As-of calculation | As-of signal | Naive calculation | Naive signal |
|---|---|---:|---|---:|
| AAA | (103 / 101 − 1) × 100 | +1.98% (February) | (109 / 103 − 1) × 100 | +5.83% (March) |
| BBB | (97 / 98 − 1) × 100 | −1.02% (February) | (92 / 97 − 1) × 100 | −5.15% (March) |
| CCC | (111 / 110 − 1) × 100 | +0.91% (February) | (112 / 110 − 1) × 100 | +1.82% (February, revised) |

Keeping AAA row 2 would incorrectly give (104 / 101 − 1) × 100 = **+2.97%**. Row 4 was already public on March 31, so 103 is the correct February value.


## Learn — Point-in-time

**What is look-ahead bias?** It means using information in a historical decision that was only available afterward. The code can calculate a signal correctly but still give a misleading backtest if the input was unavailable then.

**How do event time, publication time, and revisions work?** Event time is the period measured, such as February spending. Publication time is when the number becomes observable. A revision updates a past period, but only becomes usable on its own publication date. The decision date determines which releases are eligible, and then I choose the latest eligible vintage for each observation.

**Why does AAA's +5.83% look better?** It uses March's 109, released April 10, against revised February's 103. On March 31, I only had January's 101 and February's 103, giving +1.98%. The naive signal is about **3.85 percentage points** higher, but it also measures a different monthly interval. The gap is a timing problem, not additional evidence available to the March decision maker.

**ALFRED reading takeaway:** ALFRED preserves vintage versions so historical analysis can use the data available on past dates. A release makes information available. It uses the source's release date when available, then the provider's date, then first FRED availability if neither can be determined. Vintage data are checked against the original source when possible and third-party services otherwise. I should verify publication provenance rather than assume an observation date is a release date. Source: [ALFRED Help, assigned headings](https://alfred.stlouisfed.org/help).

## Reflect

**Which rule mattered most to me?** I would choose rule 3, the publication cutoff. It removes AAA's March value, which makes the naive positive signal much stronger, and BBB's March value, which makes its decline look much clearer. Rule 4 still matters: even after rejecting future rows, I would get AAA wrong if I kept the first February release.

**What would a naive backtest claim?** It would act as though I could already see AAA's stronger spending growth and BBB's steeper decline on March 31. It might suggest a stronger buy-AAA or avoid-BBB decision than the available information supported. CCC shows a smaller version of the same issue through a later revision. These are spending-index changes, so the table alone does not establish actual trading profits or a profitable strategy.

**Connection to my portfolio work:** I would keep publication dates and vintages alongside any macro series I add to my BIL/IEF/LQD/VT allocation process. Testing sensitivity to estimates is useful, but a historical allocation test also needs inputs that could have been observed at each decision date.

