import random
import unittest
from pathlib import Path

from candidate_generator import Video, sample_catalog
from event_history import events_known_before_decision
from history_baseline import choose_from_watches


LOG = Path(__file__).with_name("generated_two_visits.csv")
CANDIDATES = [Video("B", "cooking", 120, True),
              Video("C", "sports", 75, True),
              Video("E", "music", 80, True)]


class HistoryBaselineTest(unittest.TestCase):
    def test_d2_uses_d1_cooking_watch_not_private_interest(self):
        events = events_known_before_decision(LOG, "D2")
        index = choose_from_watches(CANDIDATES, events, sample_catalog(), "2026-10-08T10:01:00",
                                    random.Random(7))
        self.assertEqual(index, 0)
        self.assertEqual(CANDIDATES[index].video_id, "B")

    def test_short_play_does_not_count_as_qualifying_watch(self):
        events = [{"event_type": "video_playback", "video_id": "A", "watch_seconds": "5",
                   "timestamp": "2026-10-04T10:02:05"}]
        # No qualifying watch: seeded fallback chooses from the whole shortlist.
        self.assertEqual(choose_from_watches(CANDIDATES, events, sample_catalog(),
                                              "2026-10-08T10:01:00", random.Random(5)), 2)

    def test_later_playback_cannot_influence_earlier_choice(self):
        events = [{"event_type": "video_playback", "video_id": "A", "watch_seconds": "40",
                   "timestamp": "2026-10-08T10:03:00"}]
        index = choose_from_watches(CANDIDATES, events, sample_catalog(),
                                    "2026-10-08T10:01:00", random.Random(5))
        self.assertEqual(index, 2)

    def test_no_matching_topic_falls_back_to_shortlist(self):
        candidates = [Video("C", "sports", 75, True), Video("E", "music", 80, True)]
        events = [{"event_type": "video_playback", "video_id": "A", "watch_seconds": "40",
                   "timestamp": "2026-10-04T10:03:00"}]
        index = choose_from_watches(candidates, events, sample_catalog(),
                                    "2026-10-08T10:01:00", random.Random(7))
        self.assertIn(index, (0, 1))


if __name__ == "__main__":
    unittest.main()
