import contextlib
import io
import random
import unittest

from candidate_generator import Video
from profile_baseline import choose_profile_video, main


class ProfileBaselineTest(unittest.TestCase):
    def setUp(self):
        self.candidates = [
            Video("A", "cooking", 90, True),
            Video("B", "cooking", 120, True),
            Video("C", "sports", 75, True),
        ]

    def test_chooses_matching_topic(self):
        choice = choose_profile_video(self.candidates, "sports", random.Random(7))
        self.assertEqual(self.candidates[choice].video_id, "C")

    def test_tie_selects_one_matching_video_reproducibly(self):
        first = random.Random(7)
        second = random.Random(7)
        choices = [choose_profile_video(self.candidates, "cooking", first) for _ in range(5)]
        self.assertEqual(choices, [choose_profile_video(self.candidates, "cooking", second) for _ in range(5)])
        self.assertTrue(all(self.candidates[index].topic == "cooking" for index in choices))

    def test_no_matching_topic_still_selects_a_candidate(self):
        choice = choose_profile_video(self.candidates, "music", random.Random(7))
        self.assertIn(choice, range(len(self.candidates)))

    def test_no_recorded_interest_still_selects_a_candidate(self):
        choice = choose_profile_video(self.candidates, None, random.Random(7))
        self.assertIn(choice, range(len(self.candidates)))

    def test_empty_shortlist_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "empty shortlist"):
            choose_profile_video([], "cooking", random.Random(7))

    def test_demo_prints_profile_match_and_tie(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            main()
        log = output.getvalue()
        self.assertIn("Recorded interest: cooking", log)
        self.assertIn("two cooking videos", log)
        self.assertIn("matches", log)
        self.assertIn("Selected video", log)
        self.assertIn("No watch or return was simulated", log)


if __name__ == "__main__":
    unittest.main()
