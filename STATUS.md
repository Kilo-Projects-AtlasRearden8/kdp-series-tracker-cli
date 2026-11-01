# STATUS

## What was built

A local-first Python CLI for tracking KDP (Kindle Direct Publishing) series
books, blurbs, keywords, and royalties per title. Built for Dylan Asdale /
Asdale Dynamics, LLC (Indiana, formed October 2026).

Files:
- `kdp_tracker.py` — the CLI and library logic (stdlib only, no dependencies)
- `tests/test_kdp_tracker.py` — unit tests for royalty math and library logic
- `LICENSE` — MIT License, copyright line exactly
  `Copyright (c) 2026 Asdale Dynamics, LLC`
- `README.md` — usage docs, credits Asdale Dynamics, LLC
- `.gitignore` — keeps local data files (JSON/CSV) and bytecode out of git
- `STATUS.md` — this file

## Features

Commands:
- `add-book` — title, series, series number, price, royalty rate (35%/70%),
  units sold, blurb, comma-separated keywords
- `list-books` — all tracked titles with prices, rates, units, royalties
- `series-report` — books, units, and royalties grouped by series, plus total
- `royalties-report` — total royalties and title count
- `export-csv --output <file>` — full library export to CSV
- `update-book --id <id> --<field> <value>` — update any field
- `delete-book --id <id>` — remove a title

Calculations:
- Royalty per title = units sold × price × royalty rate, rounded to cents
- Totals sum across titles

Data:
- Stored locally in `kdp_library.json` (JSON) in the working directory
- No network access, no API keys, no accounts, no secrets

## How to run

Requires Python 3.8+. No `pip install` needed — standard library only.

```bash
python3 kdp_tracker.py add-book \
  --title "The Massive AI Manual" \
  --series "AI Guides" --series-number 1 \
  --price 9.99 --royalty-rate 0.70 --units-sold 120 \
  --blurb "Learn AI plain English." \
  --keywords "AI,artificial intelligence,beginners"
python3 kdp_tracker.py list-books
python3 kdp_tracker.py series-report
python3 kdp_tracker.py royalties-report
python3 kdp_tracker.py export-csv --output kdp_export.csv
```

## Verification results

Unit tests (`python3 -m unittest discover -s tests -v`):
- 10 tests, 10 passed, 0 failed
- Covers 35% and 70% royalty math, zero units, totals, series grouping,
  keyword parsing, update, delete, invalid rate rejection

CLI smoke test (two titles: 120 × $9.99 × 70% = $839.16; 300 × $4.99 × 35% =
$523.95):
- `add-book`, `list-books`, `series-report`, `royalties-report`,
  `export-csv` all ran successfully
- Series total $1,363.11 matched the sum of per-title royalties
- CSV export produced correct rows with `;`-joined keywords

No lint/typecheck tooling is configured in the project (no dependencies).

## Known gaps

- No graphical or web interface; CLI only
- No built-in backup/restore beyond copying `kdp_library.json`
- Royalty model is simplified (price × rate × units); does not model KDP
  delivery fees, taxes, or currency conversion
- No data migration or schema versioning if the JSON format changes
- Tests use `unittest` from the standard library; no pytest configured

## Git

Initialized in this folder. One commit on branch `master`, committed as the
existing git identity (Dylan Asdale), no co-author trailers. Nothing pushed,
no remote created, nothing published.
