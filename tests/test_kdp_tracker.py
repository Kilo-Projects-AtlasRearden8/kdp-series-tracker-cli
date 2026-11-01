"""Unit tests for the KDP Series Tracker royalty math and library logic."""

from __future__ import annotations

import os
import tempfile
import unittest

from kdp_tracker import KDPLibrary, VALID_ROYALTY_RATES


class TestRoyaltyMath(unittest.TestCase):
    def test_royalty_70_percent(self):
        book = {
            "units_sold": 100,
            "price": 9.99,
            "royalty_rate": 0.70,
        }
        self.assertAlmostEqual(KDPLibrary.royalty_for_book(book), 699.30)

    def test_royalty_35_percent(self):
        book = {
            "units_sold": 200,
            "price": 4.99,
            "royalty_rate": 0.35,
        }
        self.assertAlmostEqual(KDPLibrary.royalty_for_book(book), 349.30)

    def test_zero_units_earns_nothing(self):
        book = {"units_sold": 0, "price": 9.99, "royalty_rate": 0.70}
        self.assertEqual(KDPLibrary.royalty_for_book(book), 0.0)

    def test_total_royalties_sums_books(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "lib.json")
            lib = KDPLibrary(data_file=path)
            lib.add_book(title="A", price=10.0, royalty_rate=0.70, units_sold=10)
            lib.add_book(title="B", price=10.0, royalty_rate=0.35, units_sold=10)
            self.assertEqual(lib.total_royalties(), 105.0)

    def test_series_totals_group_by_series(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "lib.json")
            lib = KDPLibrary(data_file=path)
            lib.add_book(title="Book 1", series="Saga", series_number=1, price=10.0, royalty_rate=0.70, units_sold=10)
            lib.add_book(title="Book 2", series="Saga", series_number=2, price=10.0, royalty_rate=0.70, units_sold=10)
            lib.add_book(title="Other", series="Different", price=10.0, royalty_rate=0.70, units_sold=5)
            totals = lib.series_totals()
            self.assertEqual(len(totals), 2)
            saga = next(t for t in totals if t["series"] == "Saga")
            self.assertEqual(saga["books"], 2)
            self.assertEqual(saga["units_sold"], 20)
            self.assertEqual(saga["royalties"], 140.0)

    def test_valid_royalty_rates(self):
        self.assertEqual(VALID_ROYALTY_RATES, (0.35, 0.70))

    def test_invalid_royalty_rate_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "lib.json")
            lib = KDPLibrary(data_file=path)
            with self.assertRaises(ValueError):
                lib.add_book(title="X", price=5.0, royalty_rate=0.50, units_sold=1)

    def test_keywords_parsed_from_comma_string(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "lib.json")
            lib = KDPLibrary(data_file=path)
            book = lib.add_book(title="X", price=5.0, keywords="AI, artificial intelligence,  beginners ")
            self.assertEqual(book["keywords"], ["AI", "artificial intelligence", "beginners"])

    def test_update_book_changes_royalty(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "lib.json")
            lib = KDPLibrary(data_file=path)
            book = lib.add_book(title="X", price=10.0, royalty_rate=0.70, units_sold=10)
            updated = lib.update_book(book["id"], units_sold=20)
            self.assertEqual(updated["royalty_earned"], 140.0)

    def test_delete_book_removes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "lib.json")
            lib = KDPLibrary(data_file=path)
            book = lib.add_book(title="X", price=5.0)
            self.assertTrue(lib.delete_book(book["id"]))
            self.assertIsNone(lib.find_book(book["id"]))
            self.assertEqual(lib.total_royalties(), 0.0)


if __name__ == "__main__":
    unittest.main()
