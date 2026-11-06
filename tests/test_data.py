from __future__ import annotations

import unittest

from src.data import DEFAULT_DATA_PATH, load_player_data, overview_metrics, scouting_table


class FootballDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = load_player_data(DEFAULT_DATA_PATH)

    def test_source_shape_and_leagues(self) -> None:
        self.assertEqual(len(self.data), 2839)
        self.assertEqual(self.data["League"].nunique(), 5)

    def test_reconciled_totals(self) -> None:
        metrics = overview_metrics(self.data)
        self.assertEqual(metrics["players"], 2687)
        self.assertEqual(metrics["goals"], 4714)
        self.assertEqual(metrics["assists"], 3291)
        self.assertEqual(metrics["contributions"], 8005)
        self.assertEqual(metrics["minutes"], 3459549)

    def test_rates_are_finite(self) -> None:
        for column in [
            "Goals Per 90",
            "Assists Per 90",
            "Shot Accuracy",
            "Defensive Actions Per 90",
        ]:
            self.assertFalse(self.data[column].isna().any(), column)

    def test_scouting_threshold(self) -> None:
        result = scouting_table(self.data, 900)
        self.assertTrue((result["Min"] >= 900).all())
        self.assertTrue((result["Position Group"] != "Goalkeeper").all())
        self.assertTrue(result["Scouting Score"].between(0, 100).all())


if __name__ == "__main__":
    unittest.main()

