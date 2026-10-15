import csv
import random
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from event_history import events_known_before_decision
from one_visit_log import write_events
from two_visit_log import generate_two_visits


class TwoVisitLogTest(unittest.TestCase):
    def test_second_decision_sees_first_response_but_not_its_own(self):
        rows, selections = generate_two_visits(
            datetime(2026, 10, 4, 10),
            random.Random(42), random.Random(7), random.Random(42), random.Random(5),
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.csv"
            write_events(path, rows)
            history = events_known_before_decision(path, "D2")

        self.assertEqual([row["visit_id"] for row in rows if row["event_type"] == "visit_started"],
                         ["V1", "V2"])
        self.assertEqual([row["decision_id"] for row in rows if row["event_type"] == "video_shown"],
                         ["D1", "D2"])
        self.assertEqual([row["event_id"] for row in history],
                         [row["event_id"] for row in rows if row["visit_id"] == "V1"]
                         + [next(row["event_id"] for row in rows if row["visit_id"] == "V2")])
        self.assertEqual([row["event_id"] for row in rows],
                         [f"E{index}" for index in range(1, len(rows) + 1)])
        for decision_id, video_id in selections.items():
            shown = next(row for row in rows if row["decision_id"] == decision_id
                         and row["event_type"] == "video_shown")
            self.assertEqual(shown["video_id"], video_id)
            self.assertEqual(shown["source"], "random_baseline")
        self.assertGreater(datetime.fromisoformat(rows[-1]["timestamp"]),
                           datetime.fromisoformat(rows[0]["timestamp"]))

    def test_same_seeds_reproduce_both_visits(self):
        def run():
            return generate_two_visits(datetime(2026, 10, 4, 10),
                                       random.Random(42), random.Random(7),
                                       random.Random(42), random.Random(5))
        self.assertEqual(run(), run())


if __name__ == "__main__":
    unittest.main()
