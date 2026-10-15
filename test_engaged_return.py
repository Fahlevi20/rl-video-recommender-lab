import csv
import unittest
from datetime import datetime
from pathlib import Path

from engaged_return import engaged_return_status
from one_visit_log import FIELDNAMES


SAMPLE_EVENTS = Path(__file__).with_name("generated_two_visits.csv")


def event(event_id, time, visit_id, event_type, decision_id="", watch_seconds="",
          viewer_id="U1"):
    return dict(zip(FIELDNAMES, [event_id, time, viewer_id, visit_id, decision_id,
                                 "A", event_type, "", watch_seconds]))


class EngagedReturnTest(unittest.TestCase):
    def test_existing_two_visit_log_stays_pending_at_day_four(self):
        with SAMPLE_EVENTS.open(newline="", encoding="utf-8") as events_file:
            rows = list(csv.DictReader(events_file))
        self.assertEqual(engaged_return_status(rows, "D1", datetime(2026, 10, 8, 11)), "pending")
        self.assertEqual(engaged_return_status(rows, "D1", datetime(2026, 10, 11, 10, 1)), "no")

    def test_later_visit_with_qualifying_watch_is_yes(self):
        rows = [event("E1", "2026-10-04T10:00:00", "V1", "visit_started"),
                event("E2", "2026-10-04T10:01:00", "V1", "video_shown", "D1"),
                event("E3", "2026-10-08T19:00:00", "V2", "visit_started"),
                event("E4", "2026-10-08T19:03:00", "V2", "video_playback", watch_seconds="40")]
        self.assertEqual(engaged_return_status(rows, "D1", datetime(2026, 10, 9)), "yes")

    def test_same_visit_watch_does_not_count_as_return(self):
        rows = [event("E1", "2026-10-04T10:00:00", "V1", "visit_started"),
                event("E2", "2026-10-04T10:01:00", "V1", "video_shown", "D1"),
                event("E3", "2026-10-04T10:03:00", "V1", "video_playback", watch_seconds="40")]
        self.assertEqual(engaged_return_status(rows, "D1", datetime(2026, 10, 11, 10, 2)), "no")

    def test_short_return_playback_is_not_qualifying(self):
        rows = [event("E1", "2026-10-04T10:00:00", "V1", "visit_started"),
                event("E2", "2026-10-04T10:01:00", "V1", "video_shown", "D1"),
                event("E3", "2026-10-08T10:00:00", "V2", "visit_started"),
                event("E4", "2026-10-08T10:03:00", "V2", "video_playback", watch_seconds="5")]
        self.assertEqual(engaged_return_status(rows, "D1", datetime(2026, 10, 8, 11)), "pending")

    def test_qualifying_watch_completed_at_deadline_counts(self):
        rows = [event("E1", "2026-10-04T10:00:00", "V1", "visit_started"),
                event("E2", "2026-10-04T10:01:00", "V1", "video_shown", "D1"),
                event("E3", "2026-10-11T09:50:00", "V2", "visit_started"),
                event("E4", "2026-10-11T10:01:00", "V2", "video_playback", watch_seconds="30")]
        self.assertEqual(engaged_return_status(rows, "D1", datetime(2026, 10, 11, 10, 1)), "yes")

    def test_qualifying_watch_completed_after_deadline_is_no(self):
        rows = [event("E1", "2026-10-04T10:00:00", "V1", "visit_started"),
                event("E2", "2026-10-04T10:01:00", "V1", "video_shown", "D1"),
                event("E3", "2026-10-11T09:50:00", "V2", "visit_started"),
                event("E4", "2026-10-11T10:01:01", "V2", "video_playback", watch_seconds="30")]
        self.assertEqual(engaged_return_status(rows, "D1", datetime(2026, 10, 11, 10, 2)), "no")

    def test_after_deadline_still_pending_without_full_observation(self):
        rows = [event("E1", "2026-10-04T10:00:00", "V1", "visit_started"),
                event("E2", "2026-10-04T10:01:00", "V1", "video_shown", "D1")]
        self.assertEqual(engaged_return_status(rows, "D1", datetime(2026, 10, 12),
                                               observed_through=datetime(2026, 10, 8)), "pending")


if __name__ == "__main__":
    unittest.main()
