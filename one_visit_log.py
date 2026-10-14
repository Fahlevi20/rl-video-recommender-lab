"""Connect shortlist, random choice, and reaction for one synthetic visit."""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

from candidate_generator import generate_candidates, sample_catalog
from random_baseline import choose_random_video
from viewer_reaction import react_to_video


FIELDNAMES = ["event_id", "timestamp", "viewer_id", "visit_id", "decision_id",
              "video_id", "event_type", "source", "watch_seconds"]


def generate_one_visit(start, candidate_rng, policy_rng, response_rng):
    candidates = generate_candidates(sample_catalog(), candidate_rng)
    chosen_index = choose_random_video(candidates, policy_rng)
    video = candidates[chosen_index]
    response = react_to_video(video, "cooking", response_rng)

    def row(event_id, time, event_type, video_id="", decision_id="", source="",
            watch_seconds=""):
        return dict(zip(FIELDNAMES, [event_id, time.isoformat(), "U1", "V1", decision_id,
                                     video_id, event_type, source, watch_seconds]))

    shown = start + timedelta(minutes=1)
    rows = [row("E1", start, "visit_started"),
            row("E2", shown, "video_shown", video.video_id, "D1", "random_baseline")]
    if response.clicked:
        clicked = shown + timedelta(minutes=1)
        rows.append(row("E3", clicked, "video_clicked", video.video_id, "D1", "random_baseline"))
        rows.append(row("E4", clicked + timedelta(seconds=response.playback_seconds),
                        "video_playback", video.video_id, "D1", "random_baseline",
                        str(response.playback_seconds)))
    return rows, candidates, chosen_index, response


def write_events(path, rows):
    with Path(path).open("x", newline="", encoding="utf-8") as events_file:
        writer = csv.DictWriter(events_file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main():
    start = datetime.fromisoformat("2026-10-04T10:00:00")
    rows, candidates, chosen_index, response = generate_one_visit(
        start, random.Random(42), random.Random(7), random.Random(42)
    )
    print("One synthetic visit only: seeded example, not real viewer data.")
    print("[STEP 1] Viewer U1 opens the app at", start.isoformat())
    print("[STEP 2] Candidate generator supplies:")
    for index, video in enumerate(candidates):
        print(f"  {index}: video {video.video_id} ({video.topic})")
    print(f"[STEP 3] Random baseline selects index {chosen_index}; "
          f"video {candidates[chosen_index].video_id} is shown.")
    print(f"[STEP 4] Simulator response: clicked={response.clicked}, "
          f"playback_seconds={response.playback_seconds}; "
          f"qualifying watch={response.playback_seconds >= 30}.")
    print("[STEP 5] Generated event rows:")
    for event in rows:
        print(f"  {event['event_id']} {event['timestamp']} {event['event_type']} "
              f"video={event['video_id'] or '-'} playback={event['watch_seconds'] or '-'}")
    destination = Path(__file__).with_name("generated_one_visit.csv")
    try:
        write_events(destination, rows)
    except FileExistsError:
        print(f"File already exists: {destination.name}. Left unchanged; remove or rename it to regenerate.")
    else:
        print(f"Saved {len(rows)} rows to {destination.name}; sample_events.csv was not modified.")
    print("No later visit, seven-day label, or RL reward is generated.")


if __name__ == "__main__":
    main()
