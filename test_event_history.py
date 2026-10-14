import unittest
from pathlib import Path

from event_history import events_known_before_decision


SAMPLE_EVENTS = Path(__file__).with_name("sample_events.csv")


class EventHistoryTest(unittest.TestCase):
    def test_day_four_decision_excludes_later_click_and_visit(self):
        known = events_known_before_decision(SAMPLE_EVENTS, "D1")
        self.assertEqual([event["event_id"] for event in known], ["E1"])

    def test_day_eight_decision_includes_previous_visit_but_not_its_outcome(self):
        known = events_known_before_decision(SAMPLE_EVENTS, "D2")
        self.assertEqual([event["event_id"] for event in known], ["E1", "E2", "E3", "E4", "E5"])

    def test_later_decision_sees_short_playback_but_earlier_one_does_not(self):
        first = events_known_before_decision(SAMPLE_EVENTS, "D3")
        later = events_known_before_decision(SAMPLE_EVENTS, "D4")
        self.assertNotIn("E11", [event["event_id"] for event in first])
        short_play = next(event for event in later if event["event_id"] == "E11")
        self.assertEqual(short_play["event_type"], "video_playback")
        self.assertEqual(short_play["watch_seconds"], "5")
        self.assertEqual(short_play["video_id"], "B")
        self.assertNotIn("E11", [event["event_id"] for event in events_known_before_decision(SAMPLE_EVENTS, "D2")])

    def test_unknown_decision_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown decision"):
            events_known_before_decision(SAMPLE_EVENTS, "D99")


if __name__ == "__main__":
    unittest.main()
