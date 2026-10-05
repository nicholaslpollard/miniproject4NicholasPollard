# INF601 - Advanced Programming in Python
# Nicholas Pollard
# Mini Project 4

"""datakit — a tiny data-processing toolkit.

YOUR JOB: implement every function below so it matches SPEC.md. Drive Claude Code
to help, but you must understand and be able to explain each line. Run the public
tests as you go:  pytest tests/public
"""
from __future__ import annotations

import csv
import json
import os


def load_records(path):
    """Load a .csv or .json file into a list of dict rows.

    - .csv  -> use csv.DictReader (every value is a str)
    - .json -> a list of objects (returned as-is)
    - anything else -> raise ValueError
    """
    _, ext = os.path.splitext(path)
    ext = ext.lower()

    if ext == ".csv":
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            return [dict(row) for row in reader]
    elif ext == ".json":
        with open(path) as f:
            return json.load(f)
    else:
        raise ValueError(f"unsupported file extension: {ext!r}")


def filter_records(records, **criteria):
    """Return only the rows where, for every field=value pair passed as a keyword
    argument, str(row[field]) == str(value)."""
    result = []
    for row in records:
        if all(str(row[field]) == str(value) for field, value in criteria.items()):
            result.append(row)
    return result


def summarize(records, group_by, value, agg, decimals=2):
    """Group rows by the `group_by` field and aggregate the numeric `value` field.

    agg is one of:
      "count" -> number of rows in the group (int)
      "sum"   -> sum of the values (float)
      "mean"  -> mean of the values, rounded to `decimals` places (float)
      "min"   -> smallest value (float)
      "max"   -> largest value (float)
    Return a dict mapping each group value to its aggregate. Unknown agg -> ValueError.
    """
    if agg not in ("count", "sum", "mean", "min", "max"):
        raise ValueError(f"unknown aggregation: {agg!r}")

    # Collect the numeric values for the `value` field, grouped by `group_by`.
    groups = {}
    for row in records:
        key = row[group_by]
        groups.setdefault(key, []).append(float(row[value]))

    result = {}
    for key, values in groups.items():
        if agg == "count":
            result[key] = len(values)
        elif agg == "sum":
            result[key] = float(sum(values))
        elif agg == "mean":
            result[key] = round(sum(values) / len(values), decimals)
        elif agg == "min":
            result[key] = float(min(values))
        elif agg == "max":
            result[key] = float(max(values))
    return result


def top_n(records, key, n):
    """Return the `n` rows with the largest numeric `key`, sorted descending."""
    return sorted(records, key=lambda row: float(row[key]), reverse=True)[:n]


def to_report(summary):
    """Render a {key: value} dict as lines 'key: value', one per line, sorted
    ascending by key, joined with '\\n' (no trailing newline)."""
    lines = [f"{key}: {summary[key]}" for key in sorted(summary)]
    return "\n".join(lines)
