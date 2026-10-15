import csv
import unittest
from datetime import datetime
from pathlib import Path

from engaged_return import engaged_return_status
from yes_return_example import build_yes_example


EXISTING_LOG = Path(__file__).with_name("generated_two_visits.csv")


class YesReturnExampleTest(unittest.TestCase):
    def test_adds_later_search_watch_without_changing_original_log(self):
        before = EXISTING_LOG.read_bytes()
        rows = build_yes_example()
        self.assertEqual(EXISTING_LOG.read_bytes(), before)
        self.assertEqual(rows[-1]["event_type"], "video_playback")
        self.assertEqual(rows[-1]["visit_id"], "V2")
        self.assertEqual(rows[-1]["video_id"], "C")
        self.assertEqual(rows[-1]["source"], "search")
        self.assertEqual(rows[-1]["decision_id"], "")
        self.assertEqual(rows[-1]["watch_seconds"], "40")
        self.assertEqual(rows[-1]["timestamp"], "2026-10-08T10:03:40")
        self.assertEqual(engaged_return_status(rows, "D1", datetime(2026, 10, 8, 11)), "yes")
        self.assertEqual(engaged_return_status(rows, "D2", datetime(2026, 10, 8, 11)), "pending")
        with EXISTING_LOG.open(newline="", encoding="utf-8") as events_file:
            original = list(csv.DictReader(events_file))
        self.assertEqual(rows[:-1], original)


if __name__ == "__main__":
    unittest.main()
