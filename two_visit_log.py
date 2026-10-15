"""Generate two synthetic visits with separate recommendation decisions."""

import random
from datetime import datetime, timedelta
from pathlib import Path

from candidate_generator import generate_candidates, sample_catalog
from event_history import events_known_before_decision
from one_visit_log import FIELDNAMES, write_events
from random_baseline import choose_random_video
from viewer_reaction import react_to_video
from visit_timing import next_visit_time


def generate_two_visits(start, candidate_rng, policy_rng, reaction_rng, visit_rng):
    rows = []
    selections = {}
    visit_start = start
    catalog = sample_catalog()
    for number in (1, 2):
        visit_id = f"V{number}"
        decision_id = f"D{number}"

        def record(at, event_type, video_id="", source="", watch_seconds="",
                   decision=""):
            values = [f"E{len(rows) + 1}", at.isoformat(), "U1", visit_id,
                      decision, video_id, event_type, source, watch_seconds]
            rows.append(dict(zip(FIELDNAMES, values)))

        record(visit_start, "visit_started")
        candidates = generate_candidates(catalog, candidate_rng)
        chosen_index = choose_random_video(candidates, policy_rng)
        video = candidates[chosen_index]
        selections[decision_id] = video.video_id
        shown = visit_start + timedelta(minutes=1)
        record(shown, "video_shown", video.video_id, "random_baseline", decision=decision_id)
        response = react_to_video(video, "cooking", reaction_rng)
        if response.clicked:
            clicked = shown + timedelta(minutes=1)
            record(clicked, "video_clicked", video.video_id, "random_baseline", decision=decision_id)
            record(clicked + timedelta(seconds=response.playback_seconds), "video_playback",
                   video.video_id, "random_baseline", str(response.playback_seconds), decision_id)
        if number == 1:
            visit_start = next_visit_time(visit_start, visit_rng)
    return rows, selections


def main():
    start = datetime.fromisoformat("2026-10-04T10:00:00")
    rows, selections = generate_two_visits(
        start, random.Random(42), random.Random(7), random.Random(42), random.Random(5)
    )
    print("Two synthetic visits: fixed seeds; return time independent of recommendations.")
    print("The random baseline ignores prior playback when choosing D2.")
    for row in rows:
        print(f"{row['event_id']} {row['timestamp']} {row['visit_id']} {row['decision_id'] or '-'} "
              f"{row['event_type']} video={row['video_id'] or '-'} "
              f"playback={row['watch_seconds'] or '-'}")
    print(f"Selections: {selections}")
    destination = Path(__file__).with_name("generated_two_visits.csv")
    try:
        write_events(destination, rows)
    except FileExistsError:
        print(f"File already exists: {destination.name}; left unchanged.")
    else:
        print(f"Saved {len(rows)} rows to {destination.name}.")
    history = events_known_before_decision(destination, "D2")
    print("History available before D2:", [row["event_id"] for row in history])
    print("No seven-day label or RL reward is calculated yet; the return gap is independent of video choice.")


if __name__ == "__main__":
    main()
