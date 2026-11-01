"""KDP Series Tracker CLI.

Local-first command line tool for tracking Kindle Direct Publishing (KDP)
series books, blurbs, keywords, and royalties per title.

Data is stored in a local JSON file (kdp_library.json by default). No
network access, no API keys, no accounts required.

Usage:
    python kdp_tracker.py add-book --title "The Massive AI Manual" --series "AI Guides" \
        --series-number 1 --price 9.99 --royalty-rate 0.70 --units-sold 120 \
        --blurb "Learn AI plain English." --keywords "AI, artificial intelligence, beginners"
    python kdp_tracker.py list-books
    python kdp_tracker.py series-report
    python kdp_tracker.py royalties-report
    python kdp_tracker.py export-csv --output kdp_export.csv

Tests:
    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import uuid
from typing import Any

DEFAULT_DATA_FILE = "kdp_library.json"
VALID_ROYALTY_RATES = (0.35, 0.70)


class KDPLibrary:
    """In-memory collection of KDP titles persisted to a local JSON file."""

    def __init__(self, data_file: str = DEFAULT_DATA_FILE) -> None:
        self.data_file = data_file
        self.books: list[dict[str, Any]] = []
        self._load()

    # ------------------------------------------------------------------ IO

    def _load(self) -> None:
        if not os.path.exists(self.data_file):
            self.books = []
            return
        try:
            with open(self.data_file, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (json.JSONDecodeError, OSError):
            self.books = []
            return
        if isinstance(data, list):
            self.books = data
        elif isinstance(data, dict) and isinstance(data.get("books"), list):
            self.books = data["books"]
        else:
            self.books = []

    def save(self) -> None:
        with open(self.data_file, "w", encoding="utf-8") as handle:
            json.dump(self.books, handle, indent=2, ensure_ascii=False)

    # --------------------------------------------------------------- books

    def add_book(
        self,
        title: str,
        series: str | None = None,
        series_number: float | None = None,
        price: float = 0.0,
        royalty_rate: float = 0.70,
        units_sold: int = 0,
        blurb: str = "",
        keywords: str | list[str] | None = None,
    ) -> dict[str, Any]:
        if royalty_rate not in VALID_ROYALTY_RATES:
            raise ValueError(
                f"royalty_rate must be one of {VALID_ROYALTY_RATES}, got {royalty_rate!r}"
            )
        if price < 0:
            raise ValueError("price must be non-negative")
        if units_sold < 0:
            raise ValueError("units_sold must be non-negative")

        if isinstance(keywords, str):
            keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
        elif keywords is None:
            keyword_list = []
        else:
            keyword_list = [str(k).strip() for k in keywords if str(k).strip()]

        book = {
            "id": str(uuid.uuid4()),
            "title": title.strip(),
            "series": series.strip() if series else None,
            "series_number": series_number,
            "price": float(price),
            "royalty_rate": float(royalty_rate),
            "units_sold": int(units_sold),
            "blurb": blurb.strip(),
            "keywords": keyword_list,
        }
        book["royalty_earned"] = self.royalty_for_book(book)
        self.books.append(book)
        self.save()
        return book

    def list_books(self) -> list[dict[str, Any]]:
        return list(self.books)

    def find_book(self, book_id: str) -> dict[str, Any] | None:
        for book in self.books:
            if book.get("id") == book_id:
                return book
        return None

    def update_book(self, book_id: str, **fields: Any) -> dict[str, Any] | None:
        book = self.find_book(book_id)
        if book is None:
            return None
        allowed = {
            "title",
            "series",
            "series_number",
            "price",
            "royalty_rate",
            "units_sold",
            "blurb",
            "keywords",
        }
        for key, value in fields.items():
            if key not in allowed:
                continue
            if key == "royalty_rate" and value not in VALID_ROYALTY_RATES:
                raise ValueError(
                    f"royalty_rate must be one of {VALID_ROYALTY_RATES}"
                )
            if key in ("price",) and value is not None and float(value) < 0:
                raise ValueError("price must be non-negative")
            if key in ("units_sold",) and value is not None and int(value) < 0:
                raise ValueError("units_sold must be non-negative")
            if key == "keywords" and isinstance(value, str):
                value = [k.strip() for k in value.split(",") if k.strip()]
            book[key] = value
        book["royalty_earned"] = self.royalty_for_book(book)
        self.save()
        return book

    def delete_book(self, book_id: str) -> bool:
        for index, book in enumerate(self.books):
            if book.get("id") == book_id:
                self.books.pop(index)
                self.save()
                return True
        return False

    # ----------------------------------------------------------- calculations

    @staticmethod
    def royalty_for_book(book: dict[str, Any]) -> float:
        """Royalty earned for a single title: units * price * rate."""
        units = int(book.get("units_sold", 0))
        price = float(book.get("price", 0.0))
        rate = float(book.get("royalty_rate", 0.70))
        return round(units * price * rate, 2)

    def total_royalties(self) -> float:
        return round(sum(self.royalty_for_book(b) for b in self.books), 2)

    def series_totals(self) -> list[dict[str, Any]]:
        totals: dict[str, dict[str, Any]] = {}
        for book in self.books:
            series = book.get("series") or "(No series)"
            entry = totals.setdefault(
                series,
                {"series": series, "books": 0, "units_sold": 0, "royalties": 0.0},
            )
            entry["books"] += 1
            entry["units_sold"] += int(book.get("units_sold", 0))
            entry["royalties"] = round(entry["royalties"] + self.royalty_for_book(book), 2)
        return sorted(totals.values(), key=lambda e: e["royalties"], reverse=True)

    # --------------------------------------------------------------- export

    def export_csv(self, output_file: str) -> list[dict[str, Any]]:
        fields = [
            "id",
            "title",
            "series",
            "series_number",
            "price",
            "royalty_rate",
            "units_sold",
            "royalty_earned",
            "blurb",
            "keywords",
        ]
        with open(output_file, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            for book in self.books:
                row = dict(book)
                row["keywords"] = "; ".join(book.get("keywords", []))
                writer.writerow({f: row.get(f, "") for f in fields})
        return list(self.books)


# --------------------------------------------------------------------- CLI


def _currency(value: float) -> str:
    return f"${value:,.2f}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kdp_tracker.py",
        description="Local-first KDP series book, blurb, keyword, and royalty tracker.",
    )
    parser.add_argument(
        "--data-file", default=DEFAULT_DATA_FILE, help="Local JSON data file path."
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add-book", help="Add a new KDP title.")
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--series", default=None)
    p_add.add_argument("--series-number", type=float, default=None)
    p_add.add_argument("--price", type=float, default=0.0)
    p_add.add_argument(
        "--royalty-rate", type=float, default=0.70, choices=list(VALID_ROYALTY_RATES)
    )
    p_add.add_argument("--units-sold", type=int, default=0)
    p_add.add_argument("--blurb", default="")
    p_add.add_argument("--keywords", default="", help="Comma-separated keywords.")

    sub.add_parser("list-books", help="List all tracked titles.")

    sub.add_parser("series-report", help="Royalty and units grouped by series.")

    sub.add_parser("royalties-report", help="Total royalty earnings across all titles.")

    p_upd = sub.add_parser("update-book", help="Update an existing title by ID.")
    p_upd.add_argument("--id", required=True)
    p_upd.add_argument("--title")
    p_upd.add_argument("--series")
    p_upd.add_argument("--series-number", type=float)
    p_upd.add_argument("--price", type=float)
    p_upd.add_argument("--royalty-rate", type=float, choices=list(VALID_ROYALTY_RATES))
    p_upd.add_argument("--units-sold", type=int)
    p_upd.add_argument("--blurb")
    p_upd.add_argument("--keywords")

    p_del = sub.add_parser("delete-book", help="Delete a title by ID.")
    p_del.add_argument("--id", required=True)

    p_exp = sub.add_parser("export-csv", help="Export library to a CSV file.")
    p_exp.add_argument("--output", required=True, help="Destination CSV path.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    lib = KDPLibrary(data_file=args.data_file)

    if args.command == "add-book":
        try:
            book = lib.add_book(
                title=args.title,
                series=args.series,
                series_number=args.series_number,
                price=args.price,
                royalty_rate=args.royalty_rate,
                units_sold=args.units_sold,
                blurb=args.blurb,
                keywords=args.keywords,
            )
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(f"Added: {book['title']} (id={book['id']})")
        print(f"  Series: {book['series'] or '-'} #{book['series_number'] or '-'}")
        print(f"  Price: {_currency(book['price'])}  Rate: {int(book['royalty_rate']*100)}%")
        print(f"  Units: {book['units_sold']}  Royalties: {_currency(book['royalty_earned'])}")
        return 0

    if args.command == "list-books":
        books = lib.list_books()
        if not books:
            print("No titles tracked yet.")
            return 0
        for book in books:
            print(
                f"{book['id']} | {book['title']} | "
                f"{book['series'] or '-'} #{book['series_number'] or '-'} | "
                f"{_currency(book['price'])} | {int(book['royalty_rate']*100)}% | "
                f"{book['units_sold']} units | {_currency(book['royalty_earned'])}"
            )
            if book["blurb"]:
                print(f"    blurb: {book['blurb']}")
            if book["keywords"]:
                print(f"    keywords: {', '.join(book['keywords'])}")
        return 0

    if args.command == "series-report":
        totals = lib.series_totals()
        if not totals:
            print("No titles tracked yet.")
            return 0
        for entry in totals:
            print(
                f"{entry['series']}: {entry['books']} book(s), "
                f"{entry['units_sold']} units, {_currency(entry['royalties'])} royalties"
            )
        print(f"TOTAL: {_currency(lib.total_royalties())}")
        return 0

    if args.command == "royalties-report":
        print(f"Total royalties: {_currency(lib.total_royalties())}")
        print(f"Titles tracked: {len(lib.books)}")
        return 0

    if args.command == "update-book":
        fields = {}
        for key in ("title", "series", "series_number", "price", "royalty_rate", "units_sold", "blurb", "keywords"):
            value = getattr(args, key, None)
            if value is not None:
                fields[key] = value
        if not fields:
            print("error: no fields provided to update", file=sys.stderr)
            return 1
        try:
            book = lib.update_book(args.id, **fields)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        if book is None:
            print(f"error: no book with id {args.id}", file=sys.stderr)
            return 1
        print(f"Updated: {book['title']}")
        return 0

    if args.command == "delete-book":
        if lib.delete_book(args.id):
            print(f"Deleted book id={args.id}")
        else:
            print(f"error: no book with id {args.id}", file=sys.stderr)
            return 1
        return 0

    if args.command == "export-csv":
        lib.export_csv(args.output)
        print(f"Exported {len(lib.books)} title(s) to {args.output}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
