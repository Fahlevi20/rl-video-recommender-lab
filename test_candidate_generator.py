import random
import unittest

from candidate_generator import Video, generate_candidates, sample_catalog


class CandidateGeneratorTest(unittest.TestCase):
    def test_filters_ineligible_and_short_videos(self):
        catalog = [
            Video("A", "cooking", 60, True),
            Video("B", "sports", 60, True),
            Video("C", "music", 60, True),
            Video("D", "music", 29, True),
            Video("E", "sports", 90, False),
        ]
        candidates = generate_candidates(catalog, random.Random(7))
        self.assertEqual({video.video_id for video in candidates}, {"A", "B", "C"})
        self.assertEqual(len(candidates), 3)

    def test_prefers_distinct_topics_when_available(self):
        candidates = generate_candidates(sample_catalog(), random.Random(7))
        self.assertEqual(len(candidates), 3)
        self.assertEqual(len({video.video_id for video in candidates}), 3)
        self.assertEqual(len({video.topic for video in candidates}), 3)

    def test_repeats_topic_using_different_videos_when_needed(self):
        catalog = [
            Video("A", "cooking", 60, True),
            Video("B", "cooking", 60, True),
            Video("C", "sports", 60, True),
        ]
        candidates = generate_candidates(catalog, random.Random(7))
        self.assertEqual({video.video_id for video in candidates}, {"A", "B", "C"})

    def test_fixed_seed_reproduces_sequence(self):
        catalog = sample_catalog()
        first = random.Random(42)
        second = random.Random(42)
        self.assertEqual(
            [generate_candidates(catalog, first) for _ in range(3)],
            [generate_candidates(catalog, second) for _ in range(3)],
        )


if __name__ == "__main__":
    unittest.main()
