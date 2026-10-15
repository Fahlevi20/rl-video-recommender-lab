import unittest
from pathlib import Path

from compare_d2 import compare_d2


LOG = Path(__file__).with_name("generated_two_visits.csv")


class CompareD2Test(unittest.TestCase):
    def test_same_history_and_shortlist_yield_different_choices_and_reactions(self):
        original = LOG.read_bytes()
        result = compare_d2(LOG)

        self.assertEqual(LOG.read_bytes(), original)
        self.assertEqual([event["event_id"] for event in result["history"]],
                         ["E1", "E2", "E3", "E4", "E5"])
        self.assertEqual([video.video_id for video in result["candidates"]],
                         ["B", "E", "C"])
        self.assertEqual(result["random"][0].video_id, "C")
        self.assertEqual(result["history_rule"][0].video_id, "B")
        self.assertEqual(result["random"][1].playback_seconds, 5)
        self.assertEqual(result["history_rule"][1].playback_seconds, 40)
        self.assertTrue(result["random"][1].clicked)
        self.assertTrue(result["history_rule"][1].clicked)


if __name__ == "__main__":
    unittest.main()
