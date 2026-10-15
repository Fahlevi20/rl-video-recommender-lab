"""Show a separate, illustrative engaged-return yes case."""

import csv
from datetime import datetime
from pathlib import Path

from engaged_return import engaged_return_status


EXISTING_LOG = Path(__file__).with_name("generated_two_visits.csv")


def build_yes_example():
    with EXISTING_LOG.open(newline="", encoding="utf-8") as events_file:
        rows = list(csv.DictReader(events_file))
    return rows + [{**rows[-1],
                    "event_id": f"E{len(rows) + 1}",
                    "timestamp": "2026-10-08T10:03:40",
                    "decision_id": "",
                    "video_id": "C",
                    "event_type": "video_playback",
                    "source": "search",
                    "watch_seconds": "40"}]


def main():
    rows = build_yes_example()
    print("Illustrative yes example: copied rows plus one V2 watch found by search.")
    print("The original generated_two_visits.csv remains unchanged; no new CSV is written.")
    for row in rows:
        print(f"{row['event_id']} {row['timestamp']} {row['visit_id']} "
              f"{row['event_type']} video={row['video_id'] or '-'} "
              f"source={row['source'] or '-'} playback={row['watch_seconds'] or '-'}")
    now = datetime(2026, 10, 8, 11)
    for decision_id in ("D1", "D2"):
        print(f"{decision_id} as of {now.isoformat()}: "
              f"{engaged_return_status(rows, decision_id, now)}")
    print("D1's label is descriptive, not evidence that video A caused the return or an RL reward.")


if __name__ == "__main__":
    main()
