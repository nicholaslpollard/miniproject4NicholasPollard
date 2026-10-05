"""Public smoke tests — run these as you build:  pytest tests/public

These are a SUBSET of what the instructor's grader checks (the grader also varies
parameters per-student). Passing these does not guarantee full marks, but failing
them means something is wrong.
"""
import os

from buildhub import datakit as dk

FIX = os.path.join(os.path.dirname(__file__), "..", "..", "fixtures")
CSV = os.path.join(FIX, "sample.csv")
JSON = os.path.join(FIX, "sample.json")


def test_load_csv():
    rows = dk.load_records(CSV)
    assert len(rows) == 5
    assert rows[0]["name"] == "Ana"
    assert rows[0]["points"] == "10"  # CSV values are strings


def test_load_json():
    rows = dk.load_records(JSON)
    assert len(rows) == 5


def test_filter():
    rows = dk.load_records(CSV)
    red = dk.filter_records(rows, team="red")
    assert sorted(r["name"] for r in red) == ["Ana", "Cy", "Eve"]


def test_summarize_sum():
    rows = dk.load_records(CSV)
    assert dk.summarize(rows, "team", "points", "sum") == {"red": 95.0, "blue": 65.0}


def test_summarize_count():
    rows = dk.load_records(CSV)
    assert dk.summarize(rows, "team", "points", "count") == {"red": 3, "blue": 2}


def test_top_n():
    rows = dk.load_records(CSV)
    top = dk.top_n(rows, "points", 2)
    assert [r["name"] for r in top] == ["Eve", "Dee"]


def test_to_report():
    summary = dk.summarize(dk.load_records(CSV), "team", "points", "count")
    assert dk.to_report(summary) == "blue: 2\nred: 3"
