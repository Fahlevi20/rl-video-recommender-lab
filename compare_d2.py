"""Compare two D2 policies on the same recorded history and synthetic response draw."""

import random
from pathlib import Path

from candidate_generator import generate_candidates, sample_catalog
from event_history import events_known_before_decision
from history_baseline import choose_from_watches
from random_baseline import choose_random_video
from viewer_reaction import react_to_video


LOG = Path(__file__).with_name("generated_two_visits.csv")
D2_TIME = "2026-10-08T10:01:00"


def compare_d2(log_path=LOG):
    catalog = sample_catalog()
    candidate_rng = random.Random(42)
    generate_candidates(catalog, candidate_rng)  # Reproduce D1's candidate draw.
    candidates = generate_candidates(catalog, candidate_rng)
    history = events_known_before_decision(log_path, "D2")

    # Independent policy seeds give different D2 choices; both face the same candidates.
    random_index = choose_random_video(candidates, random.Random(5))
    history_index = choose_from_watches(candidates, history, catalog, D2_TIME, random.Random(7))

    # Reset the response draw for each hypothetical choice (same random percentile).
    random_video, history_video = candidates[random_index], candidates[history_index]
    random_response = react_to_video(random_video, "cooking", random.Random(10))
    history_response = react_to_video(history_video, "cooking", random.Random(10))
    return {
        "history": history,
        "candidates": candidates,
        "random": (random_video, random_response),
        "history_rule": (history_video, history_response),
    }


def main():
    result = compare_d2()
    print("Same U1 history before D2:")
    for event in result["history"]:
        print(f"  {event['event_id']}: {event['event_type']} "
              f"video={event['video_id'] or '-'} playback={event['watch_seconds'] or '-'}")
    print("Same D2 shortlist:")
    for index, video in enumerate(result["candidates"]):
        print(f"  {index}: {video.video_id} ({video.topic})")
    print("Same synthetic response draw; simulator privately models cooking interest.")
    for label, reason in (("random", "ignores history"),
                          ("history_rule", "uses recorded 40s watch of cooking A")):
        video, response = result[label]
        print(f"  {label} ({reason}): show {video.video_id} ({video.topic}); "
              f"clicked={response.clicked}, playback={response.playback_seconds}s")
    print("These are two hypothetical D2 reactions, not observed events. No CSV was changed.")
    print("D2 in the saved log was selected with different random seeds and remains B/ignored.")
    print("Return timing is independent of the video: this is not a return-lift or RL comparison.")


if __name__ == "__main__":
    main()
