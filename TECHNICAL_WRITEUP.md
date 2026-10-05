# Technical Write-Up — Mini Project 4: Build Hub (Track B)

INF601 - Advanced Programming in Python
Nicholas Pollard

## What Build Hub is

Build Hub (Track B) is a small data-processing toolkit called `datakit`, wrapped in a
command-line interface called `buildhub`. It reads tabular records from a `.csv` or
`.json` file, and lets a caller filter those records, group-and-aggregate them, pull
out the top N by some numeric field, and render a summary as a short text report. The
starter repository shipped the public contract for this toolkit as docstrings on five
`NotImplementedError` stubs in `buildhub/datakit.py`, a CLI stub in
`buildhub/__main__.py`, two small fixture files (`fixtures/sample.csv`,
`fixtures/sample.json`), and a public smoke test suite
(`tests/public/test_smoke.py`) described as a subset of a hidden instructor grader.

No `SPEC.md` was present in the repository, even though both stub files reference it
in a comment. Every implementation decision below is based only on the function
docstrings, the public smoke tests, and the other starter files — not on any
reconstructed or invented spec text.

## What was implemented

- All five functions in `buildhub/datakit.py`: `load_records`, `filter_records`,
  `summarize`, `top_n`, `to_report`.
- The `buildhub/__main__.py` CLI, with `summarize` and `top` subcommands built on
  `argparse`.
- An additional test file, `tests/test_datakit_additional.py`, covering documented
  behavior the public smoke tests don't fully exercise.

`tests/public/test_smoke.py` was read but never modified.

## Overall design

`datakit.py` holds all the logic as plain functions over `list[dict]` — no classes,
no global state, no I/O beyond `load_records` reading a file. `__main__.py` is a thin
shell: it parses arguments, calls into `datakit.py`, and prints the result. This split
matters for two reasons. First, it's what the docstrings and `__main__.py`'s own
comment ask for ("keep reusable logic in datakit.py"). Second, it's what the hidden
grader needs — the public tests import `buildhub.datakit` directly and call its
functions with arbitrary arguments, so the aggregation/filtering/formatting behavior
has to be correct independent of the CLI.

## How the five functions work

- **`load_records(path)`** checks the file extension. For `.csv` it opens the file and
  reads it with `csv.DictReader`, which always produces string values, matching the
  docstring's "(every value is a str)" note confirmed by the public test
  (`rows[0]["points"] == "10"`). For `.json` it calls `json.load`, which returns the
  file's own list of objects with Python's native JSON→Python types (int, float, str,
  etc.) intact. Any other extension raises `ValueError`.

- **`filter_records(records, **criteria)`** loops over the rows and keeps a row only
  if every `field=value` keyword argument satisfies `str(row[field]) == str(value)`.
  Stringifying both sides before comparing is what the docstring specifies, and it's
  also what makes the same filter call work whether the row came from a CSV (where
  `row["level"]` is `"3"`) or JSON (where it's `3`). With no keyword arguments, every
  row passes `all(...)` on an empty iterable, so the function returns every row
  unchanged.

- **`summarize(records, group_by, value, agg, decimals=2)`** first rejects any `agg`
  outside `{"count", "sum", "mean", "min", "max"}` with `ValueError`. Then it builds a
  dict mapping each distinct `group_by` value to a list of its `value` field coerced to
  `float(...)` — this coercion is what lets the same function work on CSV strings and
  JSON numbers alike. Finally it reduces each group's list according to `agg`:
  `len(...)` as an `int` for `count`; `sum(...)`, `min(...)`, `max(...)` cast to `float`
  for the others; and `round(mean, decimals)` for `mean`.

- **`top_n(records, key, n)`** sorts a copy of the rows by `float(row[key])`
  descending and returns the first `n`. Because Python's `sorted()` is stable, rows
  that tie on `key` keep their original relative order.

- **`to_report(summary)`** builds one `"key: value"` string per entry, iterating over
  `sorted(summary)` so the output order depends only on the keys (never on dict
  insertion order or the order rows appeared in the source file), and joins the lines
  with `"\n"` — `"\n".join(...)` naturally produces no trailing newline.

## CLI design

`buildhub/__main__.py` defines an `argparse.ArgumentParser` with `required=True`
subparsers for `summarize` and `top`:

- `summarize <file> --group-by G --value V --agg A [--decimals D]` loads the file,
  calls `summarize(...)`, and prints `to_report(...)` of the result — one line per
  group, as the docstrings describe.
- `top <file> --key K --n N` loads the file, calls `top_n(...)`, and prints each
  returned row (a `dict`) on its own line.

`--decimals` defaults to `2` to match `summarize`'s own default. No other defaults or
flags were invented beyond what the stub docstring specifies.

## Important implementation decisions

- **Coerce to `float` only where the contract requires numeric comparison**
  (`summarize`'s `value` field, `top_n`'s `key`), and leave every other field
  (including the `group_by` field and whatever `to_report` renders) exactly as loaded.
  This is why `summarize`'s returned dict keys are plain CSV strings or JSON values,
  not re-typed.
- **`filter_records` and the aggregation-by-group step both key on raw, unconverted
  field values** (`str(...)` compare for filtering; the loaded value itself as a dict
  key for grouping), so grouping works whether `group_by` resolves to a string (CSV) or
  a JSON string/number.
- **No special-casing of `fixtures/sample.csv` or `fixtures/sample.json`.** Every
  function operates generically on whatever `records`, field names, and values it's
  given; this was deliberately checked (see Testing, below) with data that has nothing
  to do with the shipped fixtures.
- **No dependencies beyond the standard library** for `datakit.py`/`__main__.py`,
  matching `requirements.txt`'s existing comment that "the toolkit itself uses only the
  Python standard library." `requirements.txt` was reviewed and left unchanged —
  `pytest>=8.0` is the only listed dependency, and that remains accurate.

## Testing approach

Two layers:

1. **`tests/public/test_smoke.py`** — the professor-provided smoke tests, run
   unmodified via `python -m pytest` (configured by `pytest.ini` to collect from
   `tests/public`).
2. **`tests/test_datakit_additional.py`** (new) — additional tests for documented
   behavior the smoke tests touch only lightly or not at all: unsupported file
   extensions, multiple/zero filter criteria, filtering on a field other than `team`,
   `mean`/`min`/`max` aggregation, alternate `decimals` values, invalid aggregation
   names, `top_n` with `n=1` and with `n` larger than the record count, `to_report`'s
   sort-independent-of-input-order guarantee and lack of a trailing newline, and both
   CLI subcommands (exercised through `buildhub.__main__.main()` with `capsys`).

   Several of these tests intentionally use synthetic data unrelated to the shipped
   fixtures (e.g. a `dept`/`salary` grouping, a temporary `.json` file with
   `region`/`temp`/`pop` fields) specifically to demonstrate that `summarize`,
   `filter_records`, and `top_n` are not hard-coded to `team`/`points`/`level`.

   Because `pytest.ini` scopes `testpaths` to `tests/public`, this file is **not**
   collected by a plain `python -m pytest`. Per the project instructions, `pytest.ini`
   was left unchanged rather than "casually" edited; the additional tests must be run
   explicitly:

   ```
   python -m pytest tests/test_datakit_additional.py -v
   ```

Beyond these two files, an ad hoc verification script (not committed — run once from
the shell, not part of the repository) exercised the same functions against synthetic
JSON data with different field names, group keys, and `n`/`decimals` values, as an
extra check before committing the core implementation.

## Agentic workflow — actual development trajectory

This section records what was actually run and observed, in order, not a reconstructed
or idealized version of it.

1. **Goal:** establish ground truth about the repository before writing anything.
   **Action:** read `CLAUDE.md`, `buildhub/datakit.py`, `buildhub/__main__.py`,
   `buildhub/__init__.py`, `fixtures/sample.csv`, `fixtures/sample.json`,
   `tests/public/test_smoke.py`, `pytest.ini`, `requirements.txt`, `.gitignore`; ran
   `git status` and `git log --oneline`.
   **Observed:** repository had no commits yet; all working-tree files were
   untracked; every `datakit.py` function was a `raise NotImplementedError` stub; the
   CLI's `main()` was also `raise NotImplementedError`; no `SPEC.md` existed anywhere
   under the project (confirmed with `find . -iname "SPEC*"`).
   **Review:** docstrings plus the public test assertions were the only available
   contract; proceeded on that basis.

2. **Goal:** record an honest baseline.
   **Action:** ran `python -m pytest -v`.
   **Observed:** 7 collected, **7 failed**, every failure a
   `NotImplementedError` raised from `load_records` (the first function every test
   touches).
   **Review:** this is the expected starting state for an unimplemented stub module;
   recorded as the baseline for this write-up.

3. **Action:** created the initial commit (`Initial Mini Project 4 starter setup`)
   capturing the as-provided starter tree, since no commit existed yet and the working
   tree accurately represented the completed starter setup.

4. **Goal:** implement `datakit.py`.
   **Action:** wrote `load_records`, `filter_records`, `summarize`, `top_n`,
   `to_report` directly from their docstrings (see "How the five functions work").
   **Verification:** ran `python -m pytest -v`.
   **Observed:** **7 passed**, 0 failed, on the first run — no implementation bugs
   surfaced at this stage.
   **Further review:** rather than stop at "the visible tests pass," ran an ad hoc
   script against synthetic CSV/JSON data with different field names
   (`city`/`region`/`temp`/`pop`), different group/value fields, multiple filter
   criteria, zero filter criteria, an unknown `agg` name, and an unsupported file
   extension. **Observed:** every check passed, confirming the implementation was
   general rather than fitted to the fixtures.
   **Action:** committed (`Implement core Build Hub data functions`).

5. **Goal:** implement the CLI.
   **Action:** wrote `buildhub/__main__.py` as an `argparse` wrapper over `datakit.py`.
   **Verification:** ran `python -m pytest -v` — **7 passed** (unchanged). Then
   manually ran, from the repository root:
   ```
   python -m buildhub summarize fixtures/sample.csv --group-by team --value points --agg sum
   python -m buildhub summarize fixtures/sample.csv --group-by team --value points --agg mean --decimals 2
   python -m buildhub top fixtures/sample.csv --key points --n 2
   ```
   **Observed:** `blue: 65.0` / `red: 95.0`; `blue: 32.5` / `red: 31.67`; and the Eve,
   Dee rows in descending `points` order — all matching the aggregates computable by
   hand from `fixtures/sample.csv`. Also ran the `count` and `top --n 3` forms against
   `fixtures/sample.json` to confirm the CLI behaves the same way across both file
   types.
   **Action:** committed (`Implement and verify command-line interface`).

6. **Goal:** add specification-oriented coverage beyond the public smoke tests.
   **Action:** inspected `pytest.ini` (`testpaths = tests/public`) and decided, per
   the project instructions, not to edit it; instead wrote
   `tests/test_datakit_additional.py` and documented the explicit invocation needed to
   run it.
   **Verification:** ran `python -m pytest -v` (**7 passed**, confirming the new file
   isn't picked up by the configured `testpaths`) and then
   `python -m pytest tests/test_datakit_additional.py -v` (**20 passed**).
   **Action:** committed (`Add additional specification-oriented tests and harden
   implementation`).

7. **Goal:** produce this write-up as the final documentation milestone (this commit).

No failures were encountered after the initial `NotImplementedError` baseline. That
is reported here as it actually happened — implementing each function and the CLI
carefully from its docstring, and checking numeric-type handling (CSV string vs. JSON
native types) and return-type rules (`int` for `count`, `float` for everything else)
up front, avoided the most likely sources of bugs rather than discovering and fixing
them after the fact. No iteration was invented to make the process look longer than it
was.

## Issues encountered and how test feedback was used

The only concrete failures observed in this project were the seven baseline
`NotImplementedError` failures, which were resolved by implementing the corresponding
function — there was no ambiguity in the traceback to diagnose beyond "this function
isn't written yet." After each implementation stage, the public test suite (and, for
the CLI and additional-test stages, manual CLI runs) served as the actual verifier
before moving on, per the required inspect → plan → implement → run tests → observe →
correct → retest loop; in this project's case, every stage's first test run already
succeeded, so no "correct → retest" cycle was needed.

## Limitations

- `summarize` and `top_n` call `float(...)` on the relevant field with no
  try/except, so a non-numeric value in the `value`/`key` field raises Python's own
  `ValueError`/`TypeError` rather than a toolkit-specific error message.
- `load_records`, `filter_records`, `summarize`, and `top_n` assume every row contains
  the fields they're asked to read; a missing field raises a `KeyError` rather than a
  more descriptive error.
- The CLI has no top-level error handling — an invalid file path, missing field, or
  bad `--agg` value surfaces as an uncaught Python traceback rather than a clean CLI
  error message.
- `summarize`'s `mean` uses Python's built-in `round()`, which uses round-half-to-even
  ("banker's rounding"); this matches ordinary Python behavior but is worth knowing if
  a grader expects traditional round-half-up rounding at a tie.
- Only the five aggregations named in the docstring (`count`, `sum`, `mean`, `min`,
  `max`) are supported; there is no `median`, `stdev`, or similar.

## Possible next steps

- Add input validation with clearer error messages (e.g., catching a non-numeric
  `value`/`key` field and re-raising with the offending row/field named).
- Add a `--decimals` equivalent or rounding option to the `top` subcommand if a future
  spec calls for it.
- Support writing CLI output to a file instead of only `stdout`.
- Add more aggregation functions if a future `SPEC.md` introduces them.

## What Claude Code contributed

Claude Code (operating as an agent in this repository) read the starter files and the
existing `CLAUDE.md`, ran the baseline test command, wrote the implementations of the
five `datakit.py` functions and the `__main__.py` CLI described above, wrote the
additional test file, ran the test suite and the manual CLI commands at each stage to
verify behavior, and made the git commits recorded in this project's history (each
commit message in this repository is attributed to Claude Sonnet 5 as a co-author, as
required by this session's attribution rules). This write-up itself was drafted by
Claude Code from the actual commands run and output observed during the session.

## What remained under student review/control

The student (Nicholas Pollard) directed every stage of this session, supplied the
constraints (no invented `SPEC.md` content, no fixture special-casing, no README
changes, no edits to `CLAUDE.md` or the public test file, at least five meaningful
commits, standard-library-only implementation), and is responsible for reviewing the
generated implementation, understanding and being able to explain every line (per the
`datakit.py` module docstring's own requirement), making at least one additional
meaningful change personally, testing that change, committing it under their own
authorship, and writing `README.md` (including its AI-usage section) themselves. No
work in this write-up or commit history should be read as the student's own authorship
of the generated code — it documents what was generated and verified, not a claim of
who wrote it by hand.
