import contextlib
import io
import random
import unittest

from candidate_generator import Video
from random_baseline import choose_random_video, main


class RandomBaselineTest(unittest.TestCase):
    def test_selects_one_video_from_current_candidates(self):
        candidates = [
            Video("A", "cooking", 90, True),
            Video("C", "sports", 75, True),
            Video("E", "music", 80, True),
        ]
        index = choose_random_video(candidates, random.Random(42))
        self.assertIn(index, range(len(candidates)))
        self.assertIn(candidates[index], candidates)

    def test_same_seed_reproduces_choices(self):
        candidates = [
            Video("A", "cooking", 90, True),
            Video("C", "sports", 75, True),
            Video("E", "music", 80, True),
        ]
        first = random.Random(42)
        second = random.Random(42)
        self.assertEqual(
            [choose_random_video(candidates, first) for _ in range(5)],
            [choose_random_video(candidates, second) for _ in range(5)],
        )

    def test_demo_prints_each_step_as_a_log(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            main()
        log = output.getvalue()
        self.assertIn("[STEP 1] Filter the catalog", log)
        self.assertIn("[STEP 2] Build the three-video shortlist", log)
        self.assertIn("[STEP 3] Random baseline chooses index", log)
        self.assertIn("[STEP 4] Selected video", log)
        self.assertIn("No watch or return was simulated", log)

    def test_rejects_empty_shortlist(self):
        with self.assertRaisesRegex(ValueError, "empty shortlist"):
            choose_random_video([], random.Random(42))


if __name__ == "__main__":
    unittest.main()
