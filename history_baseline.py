"""Favor a candidate matching the topic of the latest recorded qualifying watch."""

import random

from candidate_generator import generate_candidates, sample_catalog
from event_history import events_known_before_decision


def choose_from_watches(candidates, history, catalog, decision_time, rng):
    if not candidates:
        raise ValueError("Cannot choose from an empty shortlist")

    catalog_by_id = {video.video_id: video for video in catalog}
    watches = [event for event in history
               if event["event_type"] == "video_playback"
               and event["timestamp"] < decision_time
               and int(event["watch_seconds"]) >= 30
               and event["video_id"] in catalog_by_id]
    if watches:
        latest = max(watches, key=lambda event: event["timestamp"])
        topic = catalog_by_id[latest["video_id"]].topic
        matches = [index for index, video in enumerate(candidates) if video.topic == topic]
        if matches:
            return rng.choice(matches)
    return rng.choice(list(range(len(candidates))))


def main():
    catalog = sample_catalog()
    candidate_rng = random.Random(42)
    generate_candidates(catalog, candidate_rng)  # D1's shortlist consumes the first draw.
    d2_candidates = generate_candidates(catalog, candidate_rng)
    history = events_known_before_decision("generated_two_visits.csv", "D2")
    print("D2 demonstration using the existing two-visit log (no CSV is changed).")
    print("D1 was originally selected by the random baseline; only D2 is reconsidered here.")
    print("[STEP 1] Recorded events available before D2:")
    for event in history:
        print(f"  {event['event_id']} {event['timestamp']} {event['event_type']} "
              f"video={event['video_id'] or '-'} playback={event['watch_seconds'] or '-'}")
    qualifying = [event for event in history if event["event_type"] == "video_playback"
                  and int(event["watch_seconds"]) >= 30]
    last_watch = max(qualifying, key=lambda event: event["timestamp"])
    topic = next(video.topic for video in catalog if video.video_id == last_watch["video_id"])
    print(f"[STEP 2] {last_watch['event_id']}: watched video {last_watch['video_id']} "
          f"for {last_watch['watch_seconds']}s; catalog topic = {topic}.")
    print("[STEP 3] D2's seeded candidate shortlist:")
    for index, video in enumerate(d2_candidates):
        print(f"  index {index}: video {video.video_id} ({video.topic})")
    index = choose_from_watches(d2_candidates, history, catalog, "2026-10-08T10:01:00",
                                random.Random(7))
    video = d2_candidates[index]
    print(f"[STEP 4] History rule selects index {index}: video {video.video_id} ({video.topic}).")
    print("Existing D2 also showed B, but its random baseline picked B by chance, not from E4.")
    print("This is a counterfactual rule demonstration, not a new simulated response, RL, or return lift.")


if __name__ == "__main__":
    main()
