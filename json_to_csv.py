"""Convert a UTF-8 JSON array of flat objects to a CSV file (Python 3.10+)."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, TextIO


def validate_records(value: Any) -> list[dict[str, Any]]:
    """Reject ambiguous non-table inputs before opening the output file."""
    if not isinstance(value, list):
        raise ValueError("input must be a JSON array of objects")
    for index, record in enumerate(value):
        if not isinstance(record, dict):
            raise ValueError(f"row {index + 1} must be an object")
        for key, cell in record.items():
            if isinstance(cell, (dict, list)):
                raise ValueError(f"row {index + 1}, field {key!r}: nested values are not supported")
    return value


def write_csv(records: list[dict[str, Any]], output: TextIO) -> None:
    """Write the union of keys in first-seen order, with empty missing cells."""
    fields = list(dict.fromkeys(key for record in records for key in record))
    if not fields:
        return
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for record in records:
        # JSON null maps to an empty cell; JSON boolean spelling stays lowercase.
        row = {
            key: "" if value is None else str(value).lower()
            if isinstance(value, bool) else value
            for key, value in record.items()
        }
        writer.writerow(row)


def convert(input_path: Path, output_path: Path) -> int:
    """Validate JSON and convert it, returning the number of input records."""
    if input_path.resolve() == output_path.resolve():
        raise ValueError("input and output must be different files")
    with input_path.open("r", encoding="utf-8-sig") as source:
        records = validate_records(json.load(source))
    with output_path.open("w", encoding="utf-8", newline="") as output:
        write_csv(records, output)
    return len(records)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="UTF-8 JSON input file")
    parser.add_argument("output", type=Path, help="CSV output file (overwritten if present)")
    args = parser.parse_args(argv)
    try:
        count = convert(args.input, args.output)
    except (OSError, ValueError) as error:
        print(f"json_to_csv: {error}", file=sys.stderr)
        return 1
    print(f"Converted {count} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

