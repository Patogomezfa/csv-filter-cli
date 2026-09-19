#!/usr/bin/env python3
"""Filter CSV or Excel rows by column conditions."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:  # pragma: no cover - optional dependency path
    pd = None


def parse_filter(raw: str) -> tuple[str, str]:
    if ":" not in raw:
        raise ValueError(f"Invalid filter '{raw}'. Use column:value")
    column, value = raw.split(":", 1)
    column = column.strip()
    value = value.strip()
    if not column:
        raise ValueError("Filter column cannot be empty")
    return column, value


def filter_with_pandas(path: Path, filters: list[tuple[str, str]], output: Path | None, print_rows: bool) -> int:
    assert pd is not None
    if path.suffix.lower() in {".xlsx", ".xls"}:
        frame = pd.read_excel(path)
    else:
        frame = pd.read_csv(path)
    for column, value in filters:
        if column not in frame.columns:
            raise KeyError(f"Column not found: {column}")
        frame = frame[frame[column].astype(str) == value]
    if print_rows:
        print(frame.to_csv(index=False), end="")
    elif output:
        if output.suffix.lower() in {".xlsx", ".xls"}:
            frame.to_excel(output, index=False)
        else:
            frame.to_csv(output, index=False)
        print(f"Wrote {len(frame)} rows to {output}")
    else:
        print(frame.to_csv(index=False), end="")
    return len(frame)


def filter_with_csv(path: Path, filters: list[tuple[str, str]], output: Path | None, print_rows: bool) -> int:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header row")
        rows = []
        for row in reader:
            keep = True
            for column, value in filters:
                if column not in row:
                    raise KeyError(f"Column not found: {column}")
                if str(row[column]) != value:
                    keep = False
                    break
            if keep:
                rows.append(row)
    if print_rows or output is None:
        writer = csv.DictWriter(sys.stdout, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    else:
        with output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {len(rows)} rows to {output}")
    return len(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Filter CSV/Excel rows by column=value conditions")
    parser.add_argument("input", type=Path, help="Input .csv or .xlsx file")
    parser.add_argument("--filter", action="append", required=True, help="Filter as column:value")
    parser.add_argument("--output", type=Path, help="Output file (.csv or .xlsx)")
    parser.add_argument("--print", action="store_true", help="Print filtered rows to stdout")
    args = parser.parse_args(argv)

    if not args.input.exists():
        print(f"Input not found: {args.input}", file=sys.stderr)
        return 1

    filters = [parse_filter(item) for item in args.filter]
    suffix = args.input.suffix.lower()
    if suffix not in {".csv", ".xlsx", ".xls"}:
        print("Supported inputs: .csv, .xlsx, .xls", file=sys.stderr)
        return 1

    try:
        if suffix != ".csv" and pd is None:
            print("Excel support requires pandas and openpyxl: pip install pandas openpyxl", file=sys.stderr)
            return 1
        if pd is not None:
            count = filter_with_pandas(args.input, filters, args.output, args.print)
        else:
            count = filter_with_csv(args.input, filters, args.output, args.print)
    except (ValueError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if count == 0:
        print("Warning: no rows matched the filters", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
