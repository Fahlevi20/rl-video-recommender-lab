import csv
import random
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from one_visit_log import generate_one_visit, write_events


class OneVisitLogTest(unittest.TestCase):
    def test_one_visit_rows_have_ordered_timestamps_and_selected_video(self):
        rows, candidates, chosen_index, response = generate_one_visit(
            datetime.fromisoformat("2026-10-04T10:00:00"),
            random.Random(42), random.Random(7), random.Random(42),
        )
        self.assertEqual(rows[0]["event_type"], "visit_started")
        self.assertEqual(rows[1]["event_type"], "video_shown")
        self.assertEqual(rows[1]["video_id"], candidates[chosen_index].video_id)
        self.assertEqual(rows[0]["visit_id"], rows[1]["visit_id"])
        self.assertEqual(rows[1]["decision_id"], "D1")
        self.assertTrue(all(row["source"] == "random_baseline" for row in rows[1:]))
        self.assertTrue(all(rows[i]["timestamp"] <= rows[i + 1]["timestamp"]
                            for i in range(len(rows) - 1)))
        self.assertTrue(all(row["video_id"] == rows[1]["video_id"] for row in rows[2:]))
        self.assertEqual(len(rows), 2 if not response.clicked else 4)
        if response.clicked:
            self.assertEqual([row["event_type"] for row in rows[2:]],
                             ["video_clicked", "video_playback"])
            self.assertEqual(rows[-1]["watch_seconds"], str(response.playback_seconds))

    def test_same_seeds_reproduce_rows(self):
        def run():
            return generate_one_visit(datetime(2026, 10, 4, 10),
                                      random.Random(42), random.Random(7),
                                      random.Random(42))[0]
        self.assertEqual(run(), run())

    def test_writes_separate_csv_without_overwriting_existing_file(self):
        rows, _, _, _ = generate_one_visit(datetime(2026, 10, 4, 10),
                                          random.Random(42), random.Random(7),
                                          random.Random(42))
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "generated_one_visit.csv"
            write_events(target, rows)
            with target.open(newline="", encoding="utf-8") as events_file:
                self.assertEqual(list(csv.DictReader(events_file)), rows)
            with self.assertRaises(FileExistsError):
                write_events(target, rows)
            with target.open(newline="", encoding="utf-8") as events_file:
                self.assertEqual(list(csv.DictReader(events_file)), rows)


if __name__ == "__main__":
    unittest.main()
