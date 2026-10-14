"""Sample illustrative visit gaps, independently of recommendations."""

import random
from datetime import datetime, timedelta


DAY_GAPS = (1, 2, 4, 8)


def next_visit_time(previous_visit, rng):
    return previous_visit + timedelta(days=rng.choice(DAY_GAPS))


def main():
    rng = random.Random(42)
    previous_visit = datetime.fromisoformat("2026-10-04T10:00:00")
    print("Synthetic logging exercise (seed=42), not an event log or a real viewer forecast.")
    print("Available gaps: 1, 2, 4, 8 days, each equally likely.")
    print("These gaps are not affected by the video or playback response.")
    print(f"Visit 1: {previous_visit.isoformat()}")

    for visit_number in range(2, 6):
        next_visit = next_visit_time(previous_visit, rng)
        print(f"Visit {visit_number}: next visit at {next_visit.isoformat()} "
              f"({(next_visit - previous_visit).days} days after Visit {visit_number - 1})")
        previous_visit = next_visit
    print("No recommendations, watches, seven-day labels, or RL reward are generated here.")


if __name__ == "__main__":
    main()
