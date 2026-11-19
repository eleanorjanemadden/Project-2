"""Lab 16: run with python3 asof.py (standard library only)."""
from datetime import date

# Editable inputs: row number, ticker, month measured, published on, index.
DECISION_DATE = "2026-03-31"
TABLE = [
    (1, "AAA", "2026-01", "2026-02-10", 101.0),
    (2, "AAA", "2026-02", "2026-03-10", 104.0),
    (3, "AAA", "2026-03", "2026-04-10", 109.0),
    (4, "AAA", "2026-02", "2026-03-25", 103.0),
    (5, "BBB", "2026-01", "2026-02-10", 98.0),
    (6, "BBB", "2026-02", "2026-03-10", 97.0),
    (7, "BBB", "2026-02", "2026-03-10", 97.0),
    (8, "BBB", "2026-03", "2026-04-10", 92.0),
    (9, "CCC", "2026-01", "2026-02-10", 110.0),
    (10, "CCC", "2026-02", "2026-04-05", 112.0),
    (11, "", "2026-02", "2026-03-10", 99.0),
    (12, "CCC", "2026-02", "2026-03-10", 111.0),
]


def latest_publications(rows):
    """Rule 4: one latest publication per ticker/month; preserve row IDs."""
    latest = {}
    for row in rows:
        key = (row[1], row[2])  # Ticker and measured month identify an observation.
        if key not in latest or row[3] > latest[key][3]:
            latest[key] = row
    panel = sorted(latest.values(), key=lambda row: row[0])
    kept_ids = {row[0] for row in panel}
    removed = [row[0] for row in rows if row[0] not in kept_ids]
    return panel, removed


def filter_rows(table, decision_date):
    cutoff = date.fromisoformat(decision_date)
    funnel = []
    # Rule 1: quarantine unidentified observations.
    rows = [row for row in table if row[1].strip()]
    funnel.append(("Quarantined: no ticker", [row[0] for row in table if not row[1].strip()]))
    # Rule 2: duplicate identity excludes the original row number.
    seen, unique, removed = set(), [], []
    for row in rows:
        if row[1:] in seen:
            removed.append(row[0])
        else:
            seen.add(row[1:])
            unique.append(row)
    funnel.append(("Exact duplicate", removed))
    # Rule 3: a release on the decision date is included.
    available = [row for row in unique if date.fromisoformat(row[3]) <= cutoff]
    funnel.append(("Published after decision date", [row[0] for row in unique
                   if date.fromisoformat(row[3]) > cutoff]))
    # Rule 4 is applied only after removing future publications.
    panel, replaced = latest_publications(available)
    funnel.append(("Older vintage replaced by a revision", replaced))
    # Naive still removes unidentified rows and duplicates, but skips the cutoff.
    naive_panel, _ = latest_publications(unique)
    return panel, naive_panel, funnel


def signals(panel):
    result = {}
    for ticker in sorted({row[1] for row in panel}):
        rows = sorted((row for row in panel if row[1] == ticker), key=lambda row: row[2])
        current = rows[-1]
        year, month = map(int, current[2].split("-"))
        previous_month = f"{year - 1}-12" if month == 1 else f"{year}-{month - 1:02d}"
        previous = next((row for row in rows if row[2] == previous_month), None)
        change = None if previous is None or previous[4] == 0 else (current[4] / previous[4] - 1) * 100
        result[ticker] = (current[2], change)
    return result


def format_signal(signal):
    month, change = signal
    month_name = date.fromisoformat(month + "-01").strftime("%B %Y")
    if change is None:
        return f"N/A ({month_name}; previous calendar month missing or zero)"
    return f"{change:+.2f}% ({month_name})"


def main(decision_date=DECISION_DATE):
    panel, naive_panel, funnel = filter_rows(TABLE, decision_date)
    print(f"Decision date: {decision_date}\nInput rows: {len(TABLE)}\n\nROW FUNNEL")
    for label, removed in funnel:
        print(f"{label}: removed {len(removed)}; rows {', '.join(map(str, removed)) or 'none'}")
    print(f"As-of panel: {len(panel)} rows; rows {', '.join(str(row[0]) for row in panel)}")
    print("\nAS-OF PANEL\nRow | Ticker | Month measured | Published on | Index")
    for number, ticker, month, published, value in panel:
        print(f"{number} | {ticker} | {month} | {published} | {value:.1f}")
    asof, naive = signals(panel), signals(naive_panel)
    print("\nSIGNALS (index percent change, not investment returns)")
    for ticker in sorted(naive):
        actual = format_signal(asof[ticker]) if ticker in asof else "N/A (no knowable data)"
        print(f"{ticker}: as-of {actual}; naive {format_signal(naive[ticker])}")


if __name__ == "__main__":
    main()
