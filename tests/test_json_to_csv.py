import csv
import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

from json_to_csv import convert, validate_records, write_csv

SCRIPT = Path(__file__).resolve().parents[1] / "json_to_csv.py"


def test_missing_keys_use_union_and_empty_cells():
    output = io.StringIO(newline="")
    write_csv([{"name": "Ana", "age": 20}, {"name": "Luís", "city": "Belo Horizonte"}], output)
    assert list(csv.reader(io.StringIO(output.getvalue()))) == [
        ["name", "age", "city"],
        ["Ana", "20", ""],
        ["Luís", "", "Belo Horizonte"],
    ]


def test_csv_round_trip_preserves_unicode_quotes_commas_and_newlines():
    value = 'ação, "quoted"\nsecond line'
    output = io.StringIO(newline="")
    write_csv([{"text": value, "active": True, "empty": None, "count": 0}], output)
    rows = list(csv.DictReader(io.StringIO(output.getvalue(), newline="")))
    assert rows == [{"text": value, "active": "true", "empty": "", "count": "0"}]


def test_empty_array_writes_empty_csv():
    output = io.StringIO()
    write_csv(validate_records([]), output)
    assert output.getvalue() == ""


@pytest.mark.parametrize("value", [{"name": "Ana"}, ["row"], [{"nested": [1]}]])
def test_non_table_inputs_fail(value):
    with pytest.raises(ValueError):
        validate_records(value)


def test_cli_converts_utf8_bom_input(tmp_path):
    source, output = tmp_path / "input.json", tmp_path / "output.csv"
    source.write_text(json.dumps([{"name": "Júnior"}, {"city": "São Paulo"}], ensure_ascii=False), encoding="utf-8-sig")
    run = subprocess.run([sys.executable, str(SCRIPT), str(source), str(output)], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    with output.open(encoding="utf-8", newline="") as result:
        assert list(csv.DictReader(result)) == [
            {"name": "Júnior", "city": ""},
            {"name": "", "city": "São Paulo"},
        ]


def test_invalid_input_does_not_overwrite_existing_output(tmp_path):
    source, output = tmp_path / "input.json", tmp_path / "output.csv"
    source.write_text('{"not": "an array"}', encoding="utf-8")
    output.write_text("keep this file", encoding="utf-8")
    run = subprocess.run([sys.executable, str(SCRIPT), str(source), str(output)], capture_output=True, text=True)
    assert run.returncode == 1
    assert "input must be a JSON array" in run.stderr
    assert output.read_text(encoding="utf-8") == "keep this file"


def test_same_input_output_is_rejected(tmp_path):
    source = tmp_path / "input.json"
    source.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="different files"):
        convert(source, source)
    assert source.read_text(encoding="utf-8") == "[]"

