# INF601 - Advanced Programming in Python
# Nicholas Pollard
# Mini Project 4

"""Additional specification-oriented tests for buildhub.datakit and the CLI.

These supplement (and do not modify) tests/public/test_smoke.py. They exercise
documented behavior the public smoke tests don't fully cover, and they
deliberately use data beyond fixtures/sample.csv and fixtures/sample.json so
that passing them cannot be achieved by special-casing the shipped fixtures.

pytest.ini sets testpaths = tests/public, so this file is NOT collected by a
plain `pytest` / `python -m pytest` run. Run it explicitly:

    python -m pytest tests/test_datakit_additional.py -v
"""
import json
import os

import pytest

from buildhub import __main__ as cli
from buildhub import datakit as dk

FIX = os.path.join(os.path.dirname(__file__), "..", "fixtures")
CSV = os.path.join(FIX, "sample.csv")
JSON = os.path.join(FIX, "sample.json")


# ---------------------------------------------------------------------------
# load_records
# ---------------------------------------------------------------------------


def test_load_records_unsupported_extension(tmp_path):
    bad_file = tmp_path / "data.txt"
    bad_file.write_text("name,team\nAna,red\n")
    with pytest.raises(ValueError):
        dk.load_records(str(bad_file))


def test_load_records_json_preserves_native_types(tmp_path):
    data = [
        {"city": "Erie", "region": "east", "pop": 300000, "ratio": 1.5},
        {"city": "Troy", "region": "east", "pop": 20000, "ratio": 2.0},
    ]
    path = tmp_path / "cities.json"
    path.write_text(json.dumps(data))

    rows = dk.load_records(str(path))
    assert rows == data
    assert isinstance(rows[0]["pop"], int)
    assert isinstance(rows[0]["ratio"], float)


def test_load_records_csv_values_are_strings(tmp_path):
    path = tmp_path / "cities.csv"
    path.write_text("city,region,pop\nErie,east,300000\nTroy,east,20000\n")

    rows = dk.load_records(str(path))
    assert rows[0]["pop"] == "300000"
    assert isinstance(rows[0]["pop"], str)


# ---------------------------------------------------------------------------
# filter_records
# ---------------------------------------------------------------------------


def test_filter_records_no_criteria_returns_all_rows():
    rows = dk.load_records(CSV)
    assert dk.filter_records(rows) == rows


def test_filter_records_multiple_criteria():
    rows = dk.load_records(CSV)
    matches = dk.filter_records(rows, team="red", level="1")
    assert [r["name"] for r in matches] == ["Eve"]


def test_filter_records_different_field_than_team():
    rows = dk.load_records(CSV)
    matches = dk.filter_records(rows, level="3")
    assert sorted(r["name"] for r in matches) == ["Ana", "Dee"]


def test_filter_records_numeric_value_across_csv_and_json():
    csv_rows = dk.load_records(CSV)
    json_rows = dk.load_records(JSON)

    # CSV stores "3" as a string, JSON stores 3 as an int; str(value) == str(value)
    # comparison means both should match the same criterion the same way.
    csv_matches = dk.filter_records(csv_rows, level=3)
    json_matches = dk.filter_records(json_rows, level="3")

    assert sorted(r["name"] for r in csv_matches) == ["Ana", "Dee"]
    assert sorted(r["name"] for r in json_matches) == ["Ana", "Dee"]


# ---------------------------------------------------------------------------
# summarize
# ---------------------------------------------------------------------------


def test_summarize_mean_with_default_decimals():
    rows = dk.load_records(CSV)
    result = dk.summarize(rows, "team", "points", "mean")
    # red: (10+30+55)/3 = 31.666... -> 31.67, blue: (25+40)/2 = 32.5
    assert result == {"red": 31.67, "blue": 32.5}


def test_summarize_mean_with_alternate_decimals():
    rows = dk.load_records(CSV)
    result = dk.summarize(rows, "team", "points", "mean", decimals=0)
    assert result == {"red": 32.0, "blue": 32.0}

    result4 = dk.summarize(rows, "team", "points", "mean", decimals=4)
    assert result4 == {"red": 31.6667, "blue": 32.5}


def test_summarize_min_and_max():
    rows = dk.load_records(CSV)
    assert dk.summarize(rows, "team", "points", "min") == {"red": 10.0, "blue": 25.0}
    assert dk.summarize(rows, "team", "points", "max") == {"red": 55.0, "blue": 40.0}


def test_summarize_invalid_aggregation_raises_value_error():
    rows = dk.load_records(CSV)
    with pytest.raises(ValueError):
        dk.summarize(rows, "team", "points", "median")


def test_summarize_on_arbitrary_group_and_value_fields():
    # Use fields/values that have nothing to do with the shipped fixtures to
    # confirm summarize() is not special-cased to team/points.
    data = [
        {"dept": "eng", "salary": 100},
        {"dept": "eng", "salary": 120},
        {"dept": "ops", "salary": 80},
    ]
    assert dk.summarize(data, "dept", "salary", "sum") == {"eng": 220.0, "ops": 80.0}
    assert dk.summarize(data, "dept", "salary", "count") == {"eng": 2, "ops": 1}


# ---------------------------------------------------------------------------
# top_n
# ---------------------------------------------------------------------------


def test_top_n_with_n_equal_to_one():
    rows = dk.load_records(CSV)
    top = dk.top_n(rows, "points", 1)
    assert [r["name"] for r in top] == ["Eve"]


def test_top_n_with_n_larger_than_available_rows():
    rows = dk.load_records(CSV)
    top = dk.top_n(rows, "points", 100)
    assert len(top) == len(rows)
    assert [r["name"] for r in top] == ["Eve", "Dee", "Cy", "Ben", "Ana"]


def test_top_n_on_a_different_numeric_key():
    rows = dk.load_records(CSV)
    top = dk.top_n(rows, "level", 2)
    assert [r["name"] for r in top] == ["Ana", "Dee"]


def test_top_n_works_on_json_numeric_values():
    rows = dk.load_records(JSON)
    top = dk.top_n(rows, "points", 2)
    assert [r["name"] for r in top] == ["Eve", "Dee"]
    # Rows returned must be the original dicts, not copies missing fields.
    assert set(top[0].keys()) == {"name", "team", "points", "level"}


# ---------------------------------------------------------------------------
# to_report
# ---------------------------------------------------------------------------


def test_to_report_sorts_regardless_of_input_order():
    summary = {"zebra": 1, "apple": 2, "mango": 3}
    assert dk.to_report(summary) == "apple: 2\nmango: 3\nzebra: 1"


def test_to_report_has_no_trailing_newline():
    report = dk.to_report({"a": 1})
    assert report == "a: 1"
    assert not report.endswith("\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def test_cli_summarize_prints_report(capsys):
    cli.main(["summarize", CSV, "--group-by", "team", "--value", "points", "--agg", "sum"])
    out = capsys.readouterr().out
    assert out == "blue: 65.0\nred: 95.0\n"


def test_cli_top_prints_each_row(capsys):
    cli.main(["top", CSV, "--key", "points", "--n", "2"])
    out = capsys.readouterr().out.splitlines()
    assert len(out) == 2
    assert "Eve" in out[0]
    assert "Dee" in out[1]
