# KDP Series Tracker CLI

A local-first Python command line tool for tracking Kindle Direct Publishing
(KDP) series books, blurbs, keywords, and royalties per title. Built for
independent authors and small presses who want their data to stay on their own
machine — no network calls, no API keys, no accounts.

Created by **Dylan Asdale**, registered nurse turned AI author and founder of
**Asdale Dynamics, LLC** (Indiana, formed October 2026). Asdale Dynamics
publishes beginner-friendly AI education, books and guides, and practical
open-source tools. Learn more at dylanasdale.github.io and in *The Massive AI
Manual*.

## What it tracks

Per title:
- Title, series name, and series number
- Cover price and KDP royalty rate (35% or 70%)
- Units sold and royalty earned (units × price × rate)
- Blurb (book description)
- Keywords (comma-separated)

Reports:
- List all titles
- Series report: books, units, and royalties grouped by series
- Total royalties across all titles
- CSV export of the whole library

## Data storage

Everything is stored in a local JSON file (`kdp_library.json` by default) in
the folder where you run the tool. Nothing is uploaded, and no credentials are
ever required.

## Install

Python 3.8+ is required. No dependencies are installed — the tool uses only
the Python standard library.

```bash
git clone https://github.com/dylanasdale/kdp-series-tracker-cli.git
cd kdp-series-tracker-cli
```

## Run

```bash
# Add a title
python kdp_tracker.py add-book \
  --title "The Massive AI Manual" \
  --series "AI Guides" --series-number 1 \
  --price 9.99 --royalty-rate 0.70 --units-sold 120 \
  --blurb "Learn AI plain English, step by step." \
  --keywords "AI,artificial intelligence,beginners"

# List all titles
python kdp_tracker.py list-books

# Series earnings report
python kdp_tracker.py series-report

# Total royalties
python kdp_tracker.py royalties-report

# Export to CSV
python kdp_tracker.py export-csv --output kdp_export.csv

# Use a different data file
python kdp_tracker.py --data-file my_library.json list-books
```

## Tests

Tests cover the royalty math and library logic. Run with the standard library:

```bash
python -m unittest discover -s tests -v
```

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See `LICENSE`.

## About Asdale Dynamics, LLC

Asdale Dynamics, LLC is an Indiana LLC founded by Dylan Asdale in October
2026. The LLC focuses on beginner-friendly AI education, books and guides, and
practical tools that can be published or sold — including open-source apps and
templates for authors, small businesses, and anyone who wants AI explained
"like a friend would": plain English, step by step, never condescending.
