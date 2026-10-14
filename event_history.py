"""Read the events available before a recommendation decision."""

import csv


def events_known_before_decision(csv_path, decision_id):
    with open(csv_path, newline="", encoding="utf-8") as events_file:
        events = list(csv.DictReader(events_file))

    decisions = [
        event for event in events
        if event["decision_id"] == decision_id and event["event_type"] == "video_shown"
    ]
    if len(decisions) != 1:
        raise ValueError(f"Unknown decision or duplicate impression: {decision_id}")

    decision = decisions[0]
    return [
        event for event in events
        if event["viewer_id"] == decision["viewer_id"]
        and event["timestamp"] < decision["timestamp"]
    ]
