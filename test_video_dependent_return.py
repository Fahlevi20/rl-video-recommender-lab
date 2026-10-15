import unittest

from video_dependent_return import returns_after_playback


class DependentReturnTest(unittest.TestCase):
    def test_invented_return_probabilities_include_short_play(self):
        for playback, probability in [(0, 0.10), (5, 0.30), (40, 0.70)]:
            with self.subTest(playback=playback):
                self.assertTrue(returns_after_playback(playback, probability - 0.001))
                self.assertFalse(returns_after_playback(playback, probability))

    def test_draw_must_be_a_percentile(self):
        for draw in (-0.01, 1.0):
            with self.assertRaises(ValueError):
                returns_after_playback(40, draw)


if __name__ == "__main__":
    unittest.main()
