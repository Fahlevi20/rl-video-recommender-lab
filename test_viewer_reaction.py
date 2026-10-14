import contextlib
import io
import random
import unittest

from candidate_generator import Video
from viewer_reaction import react_to_video, main


class ViewerReactionTest(unittest.TestCase):
    def setUp(self):
        self.cooking = Video("A", "cooking", 90, True)
        self.sports = Video("C", "sports", 75, True)

    def test_matching_video_uses_agreed_outcome_ranges(self):
        for draw, expected in [(0.19, (False, 0)), (0.20, (True, 5)),
                               (0.39, (True, 5)), (0.40, (True, 40)),
                               (0.99, (True, 40))]:
            with self.subTest(draw=draw):
                rng = random.Random()
                rng.random = lambda: draw
                response = react_to_video(self.cooking, "cooking", rng)
                self.assertEqual((response.clicked, response.playback_seconds), expected)
                self.assertEqual(response.playback_seconds >= 30, draw >= 0.40)

    def test_nonmatching_video_uses_agreed_outcome_ranges(self):
        for draw, expected in [(0.49, (False, 0)), (0.50, (True, 5)),
                               (0.79, (True, 5)), (0.80, (True, 40))]:
            with self.subTest(draw=draw):
                rng = random.Random()
                rng.random = lambda: draw
                response = react_to_video(self.sports, "cooking", rng)
                self.assertEqual((response.clicked, response.playback_seconds), expected)

    def test_same_seed_reproduces_a_sequence_of_responses(self):
        first = random.Random(42)
        second = random.Random(42)
        self.assertEqual(
            [react_to_video(self.cooking, "cooking", first) for _ in range(10)],
            [react_to_video(self.cooking, "cooking", second) for _ in range(10)],
        )

    def test_demo_prints_private_state_and_observed_response_separately(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            main()
        log = output.getvalue()
        self.assertIn("Private simulator interest", log)
        self.assertIn("Outcome", log)
        self.assertIn("not provided to the recommendation policy", log)
        self.assertIn("No later visit", log)


if __name__ == "__main__":
    unittest.main()
