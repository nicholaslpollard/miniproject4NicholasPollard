# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project context

INF601 Mini Project 4 — a coursework skeleton. Every function in `buildhub/` is a
`raise NotImplementedError` stub with a docstring that *is* the specification; the work
is filling them in. The repo has no commits yet.

Two things to keep in mind when helping here:

- The stub docstrings say the student "must understand and be able to explain each line."
  Prefer plain standard-library code over clever one-liners, and explain the reasoning
  rather than just dropping in a solution.
- `tests/public/test_smoke.py` is an explicit *subset* of a hidden instructor grader that
  "varies parameters per-student." Implementations must satisfy the docstring contract in
  general — never special-case the `fixtures/` values to make the smoke tests pass.

`buildhub/datakit.py` and `buildhub/__main__.py` both reference a `SPEC.md` that is not in
the repo. If a contract detail is ambiguous, the docstrings plus the smoke tests are the
only available source of truth; say so rather than inventing spec text.

## Commands

The project venv is `.venv/` (gitignored, Python 3.12, Windows layout).

```powershell
.\.venv\Scripts\Activate.ps1          # activate
pip install -r requirements.txt       # pytest only; the toolkit is stdlib-only
pytest                                # pytest.ini sets testpaths=tests/public, pythonpath=.
pytest tests/public/test_smoke.py::test_summarize_sum   # single test
python -m buildhub summarize fixtures/sample.csv --group-by team --value points --agg sum
python -m buildhub top fixtures/sample.csv --key points --n 2
```

Run `pytest` from the repo root — `pythonpath = .` in `pytest.ini` is what makes
`from buildhub import datakit` resolve, and the fixture paths in the smoke test are
relative to the test file, not the cwd.

## Architecture

Two layers, deliberately separated:

- `buildhub/datakit.py` — pure functions over `list[dict]`, no I/O beyond `load_records`.
  Pipeline shape: `load_records` → `filter_records` → `summarize` / `top_n` → `to_report`.
- `buildhub/__main__.py` — an argparse CLI (`summarize` and `top` subcommands) that is a
  thin shell over those functions. `summarize` prints `to_report(...)`; `top` prints each
  returned row. Keep logic in `datakit.py` so the hidden grader, which imports
  `buildhub.datakit` directly, can exercise it.

### Contract details that are easy to get wrong

These come from the docstrings and smoke tests together, and they drive most of the
implementation decisions:

- **CSV values are strings, JSON values are not.** `load_records` uses `csv.DictReader`
  for `.csv` and returns parsed JSON as-is for `.json`; the smoke test asserts
  `rows[0]["points"] == "10"`. So every numeric consumer (`summarize`, `top_n`) must coerce
  with `float(...)` itself and work identically on both file types.
- **`filter_records` compares stringified values** — `str(row[field]) == str(value)` — so
  `team="red"` and `level=3` both match across CSV and JSON input.
- **`summarize` return types are mixed:** `count` yields `int`, while `sum`/`mean`/`min`/`max`
  yield `float` (`{"red": 95.0}`, not `95`). `mean` rounds to the `decimals` argument.
  Unknown `agg` raises `ValueError`, as does an unsupported file extension in `load_records`.
- **`to_report` sorts ascending by key** and joins with `\n` with no trailing newline, so
  its output order is independent of the input row or group order.
