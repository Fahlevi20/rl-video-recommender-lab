import contextlib
import io
import random
import unittest
from datetime import datetime, timedelta

from visit_timing import next_visit_time, main


class VisitTimingTest(unittest.TestCase):
    def test_next_visit_has_one_of_the_example_day_gaps(self):
        previous = datetime.fromisoformat("2026-10-04T10:00:00")
        gap = next_visit_time(previous, random.Random(7)) - previous
        self.assertIn(gap, [timedelta(days=day) for day in (1, 2, 4, 8)])

    def test_fixed_seed_reproduces_visit_sequence(self):
        start = datetime.fromisoformat("2026-10-04T10:00:00")
        def timeline():
            now = start
            rng = random.Random(42)
            visits = []
            for _ in range(4):
                now = next_visit_time(now, rng)
                visits.append(now)
            return visits
        first = timeline()
        second = timeline()
        self.assertEqual(first, second)
        self.assertEqual(first[0], datetime.fromisoformat("2026-10-05T10:00:00"))
        self.assertTrue(all(later > earlier for earlier, later in zip([start] + first, first)))

    def test_demo_prints_timestamps_and_scope(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            main()
        log = output.getvalue()
        self.assertIn("2026-10-04T10:00:00", log)
        self.assertIn("next visit", log)
        self.assertIn("not affected by the video", log)
        self.assertIn("not an event log", log)


if __name__ == "__main__":
    unittest.main()
