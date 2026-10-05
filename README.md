# Mini Project 4 - Build Hub

INF601 - Advanced Programming in Python

Nicholas Pollard

Track: B

## What this project does

This project implements Build Hub, a small Python data-processing toolkit with a command-line interface.

The project can:

- load records from CSV and JSON files
- filter records using one or more field values
- group records and calculate count, sum, mean, minimum, or maximum values
- return the top records based on a numeric field
- format summary results as a text report
- run the toolkit from the command line using `summarize` and `top`

The project was completed using an agentic Claude Code workflow where the repository was inspected, code was implemented, tests were run, and the results were verified before moving to the next stage.

## Project files

```text
buildhub/
    __init__.py
    __main__.py
    datakit.py

fixtures/
    sample.csv
    sample.json

tests/
    public/
        test_smoke.py
    test_datakit_additional.py

CLAUDE.md
TECHNICAL_WRITEUP.md
pytest.ini
requirements.txt
README.md
```

`tests/public/test_smoke.py` contains the professor-provided public tests and was not modified.

`tests/test_datakit_additional.py` contains additional tests for behavior that is not fully covered by the public smoke tests.

## Requirements

- Python 3.12 or a compatible Python 3 version
- pytest

Install the required package with:

```powershell
pip install -r requirements.txt
```

The Build Hub program itself uses only the Python standard library.

## Virtual environment setup

From the project root, create a virtual environment:

```powershell
python -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then install the requirements:

```powershell
pip install -r requirements.txt
```

## Running the tests

Run the professor-provided public tests with:

```powershell
python -m pytest
```

Final result:

```text
7 passed
```

The additional tests are outside the `tests/public` path configured in `pytest.ini`, so they are run separately:

```powershell
python -m pytest tests/test_datakit_additional.py -v
```

Final result:

```text
20 passed
```

All 27 tests passed after the final code change.

## Running Build Hub

### Summarize data

Example using the sample CSV file:

```powershell
python -m buildhub summarize fixtures/sample.csv --group-by team --value points --agg sum
```

Example output:

```text
blue: 65.0
red: 95.0
```

Mean can also be calculated with a selected number of decimal places:

```powershell
python -m buildhub summarize fixtures/sample.csv --group-by team --value points --agg mean --decimals 2
```

Example output:

```text
blue: 32.5
red: 31.67
```

Supported aggregations are:

- `count`
- `sum`
- `mean`
- `min`
- `max`

### Show top records

Example:

```powershell
python -m buildhub top fixtures/sample.csv --key points --n 2
```

This returns the two records with the highest numeric `points` values in descending order.

## Technical write-up

A complete explanation of the design, testing process, agentic workflow, limitations, and project decisions is included in:

```text
TECHNICAL_WRITEUP.md
```

## AI Usage

### What I used AI for

Claude Code was used as the main agentic development tool for the project. It inspected the starter repository, implemented the five functions in `buildhub/datakit.py`, implemented the command-line interface, created additional tests, ran tests and CLI verification, and created the first five project commits.

### What I wrote myself

I completed the initial local project setup, created and managed the repository, reviewed the generated implementation, ran the final verification tests, connected the local repository to GitHub, and completed the final project review before submission.

### What I changed in the AI-generated code

After reviewing the generated `summarize()` function, I changed the `count` aggregation so it no longer converts the requested value field to `float`.

Counting records only depends on the number of rows in each group, so numeric conversion was unnecessary for that operation. The numeric aggregations (`sum`, `mean`, `min`, and `max`) still convert their values to `float`.

After making this change, I reran both test suites. All 7 public tests and all 20 additional tests passed. I committed the change separately with:

```text
Improve count aggregation handling
```
