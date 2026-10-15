"""Compute a descriptive seven-day engaged-return label from timestamped events."""

import csv
from datetime import datetime, timedelta
from pathlib import Path


WINDOW = timedelta(days=7)


def engaged_return_status(events, decision_id, as_of, observed_through=None):
    impressions = [event for event in events if event["decision_id"] == decision_id
                   and event["event_type"] == "video_shown"]
    if len(impressions) != 1:
        raise ValueError(f"Unknown decision or duplicate impression: {decision_id}")
    impression = impressions[0]
    shown_at = datetime.fromisoformat(impression["timestamp"])
    deadline = shown_at + WINDOW
    observed_through = as_of if observed_through is None else observed_through
    cutoff = min(as_of, observed_through)

    for visit in events:
        if visit["viewer_id"] != impression["viewer_id"] or visit["event_type"] != "visit_started":
            continue
        visit_at = datetime.fromisoformat(visit["timestamp"])
        if not shown_at < visit_at <= cutoff:
            continue
        for playback in events:
            if (playback["viewer_id"] == impression["viewer_id"]
                    and playback["visit_id"] == visit["visit_id"]
                    and playback["event_type"] in ("video_playback", "video_watched")
                    and int(playback["watch_seconds"]) >= 30
                    and visit_at <= datetime.fromisoformat(playback["timestamp"])
                    <= min(deadline, cutoff)):
                return "yes"
    return "no" if cutoff >= deadline else "pending"


def main():
    path = Path(__file__).with_name("generated_two_visits.csv")
    with path.open(newline="", encoding="utf-8") as events_file:
        events = list(csv.DictReader(events_file))
    for time in (datetime(2026, 10, 8, 11), datetime(2026, 10, 11, 10, 1)):
        print(f"D1 as of {time.isoformat()}: {engaged_return_status(events, 'D1', time)}")
    print("V2 opened the app but had no 30-second playback; no RL reward is calculated.")


if __name__ == "__main__":
    main()
