"""Read the bundled Lab 17 GS10 point-in-time evidence."""
import csv
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

EVIDENCE = Path(__file__).resolve().parent / "evidence" / "lab-17"
DATA = EVIDENCE / "data"


def saved_vintages():
    """Index the dated ALFRED downloads by cutoff, without using the current FRED file."""
    with (DATA / "download_manifest.json").open() as manifest:
        records = json.load(manifest)

    vintages = {}
    for record in records:
        filename = Path(record["file"]).name
        if filename.startswith("GS10_") and filename.endswith(".csv") and filename != "GS10_today.csv":
            vintage = date.fromisoformat(Path(filename).stem.removeprefix("GS10_"))
            source = f"https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=GS10&vintage_date={vintage}"
            if record["url"] != source:
                raise ValueError(f"GS10 source record does not match vintage {vintage}.")
            vintages[vintage] = record
    return vintages


def read_vintage(vintage):
    """Read only the version stored for this date, omitting missing values."""
    path = DATA / f"GS10_{vintage}.csv"
    column = f"GS10_{vintage:%Y%m%d}"
    with path.open(newline="") as file:
        rows = csv.DictReader(file)
        if rows.fieldnames != ["observation_date", column]:
            raise ValueError(f"Unexpected GS10 vintage columns in {path.name}.")
        return {
            date.fromisoformat(row["observation_date"]): Decimal(row[column])
            for row in rows
            if row[column].strip() not in {"", "."}
        }
