import unittest
from datetime import datetime
from pathlib import Path

from compare_return_journeys import compare_return_journeys
from engaged_return import engaged_return_status


LOG = Path(__file__).with_name("generated_two_visits.csv")
DEADLINE = datetime(2026, 10, 15, 10, 1)


class CompareReturnJourneysTest(unittest.TestCase):
    def test_recorded_d2_choice_affects_possible_later_engaged_visit(self):
        original = LOG.read_bytes()
        result = compare_return_journeys()
        self.assertEqual(LOG.read_bytes(), original)
        random_rows = result["random"]
        history_rows = result["history_rule"]
        self.assertEqual(random_rows[:5], history_rows[:5])
        self.assertEqual([row["event_id"] for row in random_rows],
                         [f"E{i}" for i in range(1, len(random_rows) + 1)])
        self.assertEqual([row["event_id"] for row in history_rows],
                         [f"E{i}" for i in range(1, len(history_rows) + 1)])
        self.assertEqual([row["video_id"] for row in random_rows if row["event_type"] == "video_shown"],
                         ["A", "C"])
        self.assertEqual([row["video_id"] for row in history_rows if row["event_type"] == "video_shown"][:2],
                         ["A", "B"])
        self.assertFalse(any(row["visit_id"] == "V3" for row in random_rows))
        self.assertTrue(any(row["visit_id"] == "V3" for row in history_rows))
        self.assertTrue(any(row["visit_id"] == "V3" and row["event_type"] == "video_playback"
                            and int(row["watch_seconds"]) >= 30 for row in history_rows))
        self.assertEqual(engaged_return_status(random_rows, "D2", DEADLINE), "no")
        self.assertEqual(engaged_return_status(history_rows, "D2", DEADLINE), "yes")
        self.assertEqual(engaged_return_status(history_rows, "D3", datetime(2026, 10, 12)), "pending")

    def test_return_without_watch_is_not_engaged(self):
        rows = compare_return_journeys(return_draw=0.05, v3_response_seed=1)["history_rule"]
        self.assertTrue(any(row["visit_id"] == "V3" and row["event_type"] == "visit_started"
                            for row in rows))
        self.assertFalse(any(row["visit_id"] == "V3" and row["event_type"] == "video_playback"
                             for row in rows))
        self.assertEqual(engaged_return_status(rows, "D2", datetime(2026, 10, 12)), "pending")
        self.assertEqual(engaged_return_status(rows, "D2", DEADLINE), "no")

    def test_runs_reproduce_when_draws_match(self):
        self.assertEqual(compare_return_journeys(), compare_return_journeys())


if __name__ == "__main__":
    unittest.main()
