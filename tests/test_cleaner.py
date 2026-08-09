"""Unit tests for the data-cleaning workflow — run: python3 -m unittest discover -s tests"""
import os
import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cleaner import tools
from cleaner.agent import clean
from cleaner.planner import RuleBasedPlanner
from cleaner.profile import profile_frame

MESSY = Path(__file__).resolve().parent.parent / "examples" / "messy.csv"


class TestTools(unittest.TestCase):
    def test_snake_case_headers(self):
        df = pd.DataFrame(columns=["Full Name ", "Amount Paid"])
        self.assertEqual(list(tools.snake_case_headers(df).columns), ["full_name", "amount_paid"])

    def test_coerce_numeric(self):
        df = pd.DataFrame({"a": ["€1.200,50", "$900", "1000", "900,50"]})
        self.assertEqual(tools.coerce_numeric(df, "a")["a"].tolist(), [1200.50, 900.0, 1000.0, 900.50])

    def test_standardize_dates(self):
        df = pd.DataFrame({"d": ["2023-01-05", "05/01/2023", "2023/03/01"]})
        self.assertEqual(tools.standardize_dates(df, "d")["d"].tolist(),
                         ["2023-01-05", "2023-01-05", "2023-03-01"])

    def test_standardize_categorical(self):
        df = pd.DataFrame({"c": ["NL", "nederland", "Germany"]})
        mapping = {"nl": "Netherlands", "nederland": "Netherlands", "germany": "Germany"}
        self.assertEqual(tools.standardize_categorical(df, "c", mapping)["c"].tolist(),
                         ["Netherlands", "Netherlands", "Germany"])

    def test_strip_whitespace(self):
        df = pd.DataFrame({"a": [" Alice ", " Bob"]})
        self.assertEqual(tools.strip_whitespace(df, "a")["a"].tolist(), ["Alice", "Bob"])


class TestPlanner(unittest.TestCase):
    def test_plans_expected_tools(self):
        df = tools.snake_case_headers(pd.read_csv(MESSY, skipinitialspace=True))
        chosen = {(a["column"], a["tool"]) for a in RuleBasedPlanner().plan(profile_frame(df))}
        self.assertIn(("country", "standardize_categorical"), chosen)
        self.assertIn(("signup_date", "standardize_dates"), chosen)
        self.assertIn(("amount_paid", "coerce_numeric"), chosen)


class TestAgentEndToEnd(unittest.TestCase):
    def test_clean_messy_csv(self):
        df = pd.read_csv(MESSY, skipinitialspace=True)
        cleaned, log = clean(df)
        self.assertEqual(list(cleaned.columns), ["full_name", "country", "signup_date", "amount_paid"])
        self.assertEqual(set(cleaned["country"]), {"Netherlands", "Germany", "Belgium"})
        self.assertTrue(all(len(d) == 10 and d[4] == "-" for d in cleaned["signup_date"]))
        self.assertTrue(all(isinstance(v, float) for v in cleaned["amount_paid"]))
        self.assertEqual(len(cleaned), 4)          # the duplicate Alice row is removed
        self.assertTrue(any("drop_duplicate_rows" in step for step in log))

    def test_log_reports_unparseable_and_unmapped(self):
        # a value that can't be parsed and a category not in the mapping should be surfaced
        df = pd.DataFrame({"Country": ["nederland", "MARS"], "Amount": ["100", "n/a"],
                           "When": ["2023-01-05", "notadate"]})
        _, log = clean(df)
        text = " ".join(log)
        self.assertIn("not in the mapping", text)      # MARS is flagged, not silently kept
        self.assertIn("MARS", text)
        self.assertIn("could not be parsed", text)     # "notadate" is flagged


if __name__ == "__main__":
    unittest.main()
