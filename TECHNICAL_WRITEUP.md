# Technical Write-Up — Mini Project 4: Build Hub (Track B)

INF601 - Advanced Programming in Python

## What Build Hub is

Build Hub (Track B) is a small data-processing toolkit called `datakit`, wrapped in a command-line interface called `buildhub`. It reads tabular records from a `.csv` or `.json` file, and lets a caller filter those records, group and aggregate them, pull out the top N records by a numeric field, and render a summary as a short text report.

The starter repository provided the public contract for the toolkit as docstrings on five `NotImplementedError` stubs in `buildhub/datakit.py`, a CLI stub in `buildhub/__main__.py`, two fixture files (`fixtures/sample.csv` and `fixtures/sample.json`), and a public smoke test suite (`tests/public/test_smoke.py`) described as a subset of a hidden instructor grader.

The original Track B starter package included a SPEC.md file outside the starter/ folder, so it was not copied into this repository. During the Claude Code implementation session, the function docstrings and public tests were used as the available in-repository contract. The completed implementation was later reviewed against the original SPEC.md and confirmed to match its required behavior.

## What was implemented

- All five functions in `buildhub/datakit.py`: `load_records`, `filter_records`, `summarize`, `top_n`, and `to_report`.
- The `buildhub/__main__.py` CLI, with `summarize` and `top` subcommands built with `argparse`.
- An additional test file, `tests/test_datakit_additional.py`, covering documented behavior that the public smoke tests do not fully exercise.
- A later improvement to `summarize()` so the `count` aggregation does not unnecessarily convert the requested value field to a float.

`tests/public/test_smoke.py` was read but never modified.

## Overall design

`datakit.py` contains the project logic as plain functions that operate on `list[dict]` data. There are no classes or global state, and the only file I/O occurs in `load_records`.

`__main__.py` is kept as a thin command-line layer. It parses arguments, calls functions from `datakit.py`, and prints the resulting output.

This separation keeps the reusable data-processing logic independent from the command-line interface. It also allows the grader to import and test functions from `buildhub.datakit` directly without depending on the CLI.

## How the five functions work

- **`load_records(path)`** checks the file extension. For `.csv`, it opens the file and reads it with `csv.DictReader`, which produces string values. For `.json`, it calls `json.load`, which preserves normal JSON-to-Python types such as integers, floats, and strings. Any unsupported file extension raises `ValueError`.

- **`filter_records(records, **criteria)`** loops through the records and keeps a row only when every supplied `field=value` criterion satisfies `str(row[field]) == str(value)`. Converting both sides to strings makes filtering work consistently between CSV records, where values are strings, and JSON records, where values may already be numeric. If no criteria are supplied, every row passes the check and is returned.

- **`summarize(records, group_by, value, agg, decimals=2)`** first rejects aggregation names outside `{"count", "sum", "mean", "min", "max"}` with `ValueError`. Records are grouped using the raw `group_by` field. For `count`, the function counts records without converting the requested `value` field because the numeric contents of that field are not needed. For `sum`, `mean`, `min`, and `max`, the value field is converted with `float(...)` so the function behaves consistently with both CSV strings and JSON numeric values. `count` returns an integer, while the numeric aggregations return floats. `mean` is rounded using the supplied `decimals` argument.

- **`top_n(records, key, n)`** sorts the records by `float(row[key])` in descending order and returns the first `n`. This allows numeric sorting to work consistently whether the source data came from CSV or JSON.

- **`to_report(summary)`** builds one `"key: value"` string for each item in the summary. It iterates over `sorted(summary)` so the output is deterministic and then joins the lines with `"\n"`. Because `join()` is used, no trailing newline is added.

## CLI design

`buildhub/__main__.py` defines an `argparse.ArgumentParser` with two required subcommands: `summarize` and `top`.

The `summarize` command follows this structure:

```text
summarize <file> --group-by G --value V --agg A [--decimals D]
```

It loads the requested file, calls `summarize(...)`, converts the result with `to_report(...)`, and prints the formatted summary.

The `top` command follows this structure:

```text
top <file> --key K --n N
```

It loads the requested file, calls `top_n(...)`, and prints each returned row on its own line.

The `--decimals` option defaults to `2`, matching the default value in `summarize()`.

Reusable processing logic remains in `datakit.py` instead of being duplicated inside the CLI.

## Important implementation decisions

- **Numeric conversion is only performed when numeric processing is needed.** The `sum`, `mean`, `min`, and `max` aggregations convert their `value` field using `float(...)`, and `top_n` converts its sorting key. The `count` aggregation only needs the number of records in each group, so it does not require numeric conversion.

- **Filtering compares string versions of values.** This follows the documented contract and allows equivalent values from CSV and JSON input to compare consistently.

- **Grouping uses the raw loaded group value.** The `group_by` field is not converted before it is used as the result dictionary key.

- **No fixture-specific values are hard-coded.** The functions operate on the records, field names, criteria, grouping values, and numeric keys supplied to them.

- **The implementation uses only the Python standard library.** `requirements.txt` only lists `pytest` for testing, so no additional dependencies were necessary.

## Testing approach

Testing was handled in two layers.

### Professor-provided public tests

`tests/public/test_smoke.py` was run unmodified using:

```text
python -m pytest
```

The repository's `pytest.ini` configures pytest to collect tests from `tests/public`.

The original starter implementation produced seven failures because the required functions still contained `NotImplementedError`.

After implementation, all seven public tests passed.

### Additional tests

A second file, `tests/test_datakit_additional.py`, was created to exercise documented behavior that the public smoke tests do not fully cover.

The additional tests include:

- unsupported file extensions
- JSON native numeric types
- CSV string values
- filtering with no criteria
- filtering with multiple criteria
- filtering on fields other than `team`
- numeric filtering across CSV and JSON
- `mean`
- alternate `decimals` values
- `min`
- `max`
- invalid aggregation names
- different grouping and value fields
- `top_n` with `n=1`
- `top_n` with an `n` larger than the number of records
- `top_n` with different numeric fields
- JSON numeric handling
- deterministic `to_report` ordering
- no trailing newline
- CLI `summarize`
- CLI `top`

Because `pytest.ini` scopes normal collection to `tests/public`, the additional tests are run explicitly:

```text
python -m pytest tests/test_datakit_additional.py -v
```

All 20 additional tests passed.

After the later change to the `count` aggregation, both test suites were run again:

```text
python -m pytest
python -m pytest tests/test_datakit_additional.py -v
```

The results remained:

```text
7 public tests passed
20 additional tests passed
27 total tests passed
```

## Agentic workflow — actual development trajectory

The development process used Claude Code as an agent rather than only as a one-time code generator.

### 1. Repository inspection

**Goal:** Establish the actual project requirements before writing code.

**Action:** The repository structure, `CLAUDE.md`, starter Python files, fixtures, tests, `pytest.ini`, `requirements.txt`, `.gitignore`, Git status, and Git history were inspected.

**Observed:** The repository contained unimplemented `NotImplementedError` stubs and did not contain the referenced `SPEC.md`.

**Review:** The function docstrings, supplied tests, and starter files were treated as the available source of truth.

### 2. Baseline verification

**Goal:** Record the original project state.

**Action:**

```text
python -m pytest -v
```

**Observed:** Seven tests were collected and all seven failed because the required functionality had not yet been implemented.

This established an objective starting point for the verification loop.

### 3. Initial setup commit

The starter project was committed before implementation using the commit:

```text
Initial Mini Project 4 starter setup
```

This preserved the original project state before functional changes were introduced.

### 4. Core data functions

**Goal:** Implement the five functions in `datakit.py`.

**Action:** `load_records`, `filter_records`, `summarize`, `top_n`, and `to_report` were implemented from their documented contracts.

**Verification:**

```text
python -m pytest -v
```

**Observed:** All seven public tests passed.

Additional ad hoc checks were also run with synthetic data using field names and values unrelated to the supplied fixtures to verify that the implementation was general and not hard-coded.

The completed work was committed as:

```text
Implement core Build Hub data functions
```

### 5. Command-line interface

**Goal:** Implement the Build Hub CLI.

**Action:** `buildhub/__main__.py` was implemented using `argparse` as a thin wrapper around `datakit.py`.

**Verification:**

```text
python -m pytest -v
```

All seven public tests continued to pass.

The CLI was also tested manually using commands including:

```text
python -m buildhub summarize fixtures/sample.csv --group-by team --value points --agg sum
```

```text
python -m buildhub summarize fixtures/sample.csv --group-by team --value points --agg mean --decimals 2
```

```text
python -m buildhub top fixtures/sample.csv --key points --n 2
```

The observed summary values and top rows matched the fixture data.

The CLI work was committed as:

```text
Implement and verify command-line interface
```

### 6. Additional specification-oriented tests

**Goal:** Verify behavior that was not fully covered by the seven public smoke tests.

**Action:** `tests/test_datakit_additional.py` was created without modifying the professor-provided tests or changing `pytest.ini`.

**Verification:**

```text
python -m pytest
```

Result:

```text
7 passed
```

Then:

```text
python -m pytest tests/test_datakit_additional.py -v
```

Result:

```text
20 passed
```

This work was committed as:

```text
Add additional specification-oriented tests and harden implementation
```

### 7. Technical documentation

A technical write-up and agentic workflow record were created after the implementation and test stages were complete.

This milestone was committed as:

```text
Add technical write-up and agentic workflow documentation
```

### 8. Manual review and code improvement

After the agentic implementation phase, I reviewed the generated `summarize()` function and identified an unnecessary dependency between the `count` aggregation and numeric conversion.

The original implementation converted the requested value field using `float(...)` before every aggregation, even when `agg == "count"`.

I changed the grouping logic so `count` only records the existence of each row in a group, while numeric conversion is performed only for `sum`, `mean`, `min`, and `max`.

This makes the implementation more logically consistent because counting records does not depend on whether the requested value field is numeric.

After making the change, I ran:

```text
python -m pytest
```

Result:

```text
7 passed
```

Then:

```text
python -m pytest tests/test_datakit_additional.py -v
```

Result:

```text
20 passed
```

The change was committed separately as:

```text
Improve count aggregation handling
```

## Issues encountered and how test feedback was used

The only observed failing test state was the original seven-test baseline caused by the unimplemented `NotImplementedError` stubs.

After the core functions were implemented, the public test suite passed on the first verification run. The CLI and additional tests also passed on their first verification runs.

No artificial failures or correction cycles were added to make the agentic workflow appear more complicated than it actually was.

The important feedback mechanism was still present throughout the project: implementation work was followed by execution of real tests and CLI commands before moving to the next development stage.

The later manual change to `summarize()` was also verified using both the seven public tests and all 20 additional tests before it was committed.

## Limitations

- `summarize` and `top_n` call `float(...)` for numeric operations without custom error handling, so a non-numeric value raises Python's normal `ValueError` or `TypeError`.

- `load_records`, `filter_records`, `summarize`, and `top_n` assume requested fields exist in each row. A missing field therefore raises `KeyError`.

- The CLI does not contain top-level error handling for invalid file paths, missing fields, or invalid aggregation input. These errors may therefore produce normal Python tracebacks.

- `summarize()` uses Python's built-in `round()` behavior for means.

- Only the five documented aggregations are supported: `count`, `sum`, `mean`, `min`, and `max`.

## Possible next steps

Possible future improvements include:

- clearer validation and error messages for non-numeric input
- more descriptive handling of missing fields
- cleaner top-level CLI error handling
- additional output options for the CLI
- support for additional aggregation functions if future requirements call for them

These features were not added because they are outside the available project contract.

## What Claude Code contributed

Claude Code was used as the agentic development tool for the main implementation phase.

It:

- inspected the starter repository and available project requirements
- ran the initial test baseline
- implemented the five functions in `buildhub/datakit.py`
- implemented the command-line interface in `buildhub/__main__.py`
- ran the public tests during development
- manually tested the CLI
- created additional specification-oriented tests
- ran those additional tests
- created the first five meaningful project commits
- drafted the initial technical write-up from the commands and results observed during the development session

## What I reviewed and changed

After the agentic implementation phase, I reviewed the generated code rather than treating passing tests as the end of the project.

I changed the `summarize()` implementation so the `count` aggregation no longer converts the requested value field to `float`. A count only depends on the number of records in the group, so numeric conversion was unnecessary for that operation.

The numeric aggregations (`sum`, `mean`, `min`, and `max`) still convert their value field with `float(...)`.

I then reran both test suites and confirmed that all 27 tests still passed before committing the change separately.

I also reviewed and updated this technical write-up so it reflects the final implementation rather than only the earlier AI-generated version.
