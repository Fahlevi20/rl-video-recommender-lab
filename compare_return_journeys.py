"""Compare hypothetical D2 choices, later app opens, and engaged-return labels."""

import random
from datetime import datetime, timedelta

from candidate_generator import generate_candidates, sample_catalog
from compare_d2 import D2_TIME, compare_d2
from engaged_return import engaged_return_status
from history_baseline import choose_from_watches
from one_visit_log import FIELDNAMES
from random_baseline import choose_random_video
from video_dependent_return import returns_after_playback
from viewer_reaction import react_to_video


V3_START = datetime(2026, 10, 10, 10)
D2_DEADLINE = datetime(2026, 10, 15, 10, 1)


def compare_return_journeys(return_draw=0.45, v3_response_seed=42):
    comparison = compare_d2()
    catalog = sample_catalog()
    candidate_rng = random.Random(42)
    for _ in range(2):
        generate_candidates(catalog, candidate_rng)
    v3_candidates = generate_candidates(catalog, candidate_rng)
    journeys = {}

    for policy in ("random", "history_rule"):
        rows = [event.copy() for event in comparison["history"]]

        def record(at, visit_id, decision_id, video_id, event_type, source="", seconds=""):
            values = [f"E{len(rows) + 1}", at.isoformat(), "U1", visit_id,
                      decision_id, video_id, event_type, source, seconds]
            rows.append(dict(zip(FIELDNAMES, values)))

        def record_decision(at, visit_id, decision_id, video, response):
            record(at, visit_id, decision_id, video.video_id, "video_shown", policy)
            if response.clicked:
                clicked = at + timedelta(minutes=1)
                record(clicked, visit_id, decision_id, video.video_id, "video_clicked", policy)
                record(clicked + timedelta(seconds=response.playback_seconds), visit_id,
                       decision_id, video.video_id, "video_playback", policy,
                       str(response.playback_seconds))

        d2_video, d2_response = comparison[policy]
        record_decision(datetime.fromisoformat(D2_TIME), "V2", "D2", d2_video, d2_response)
        if returns_after_playback(d2_response.playback_seconds, return_draw):
            record(V3_START, "V3", "", "", "visit_started")
            d3_shown = V3_START + timedelta(minutes=1)
            prior = [row for row in rows if row["timestamp"] < d3_shown.isoformat()]
            if policy == "random":
                index = choose_random_video(v3_candidates, random.Random(5))
            else:
                index = choose_from_watches(v3_candidates, prior, catalog,
                                            d3_shown.isoformat(), random.Random(7))
            d3_video = v3_candidates[index]
            d3_response = react_to_video(d3_video, "cooking", random.Random(v3_response_seed))
            record_decision(d3_shown, "V3", "D3", d3_video, d3_response)
        journeys[policy] = rows
    return journeys


def main():
    comparison = compare_d2()
    journeys = compare_return_journeys()
    print("Invented simulator: chance of V3 app open is 10% after 0s, 30% after 5s, 70% after 40s.")
    print("Both branches share return draw 0.45, but future visits depend on their own D2 response.")
    print("Both start with the same recorded U1 history E1-E5 and D2 shortlist:")
    for index, video in enumerate(comparison["candidates"]):
        print(f"  {index}: {video.video_id} ({video.topic})")
    for policy in ("random", "history_rule"):
        print(f"\n--- Hypothetical {policy} journey ---")
        for row in journeys[policy][5:]:
            print(f"  {row['event_id']} {row['timestamp']} {row['visit_id']} "
                  f"{row['event_type']} video={row['video_id'] or '-'} "
                  f"playback={row['watch_seconds'] or '-'}")
        v3 = any(row["visit_id"] == "V3" for row in journeys[policy])
        print(f"  V3 app open: {'yes' if v3 else 'no'}")
        for time in (datetime(2026, 10, 12), D2_DEADLINE):
            print(f"  D2 engaged return as of {time.isoformat()} with complete observation: "
                  f"{engaged_return_status(journeys[policy], 'D2', time)}")
        if v3:
            print("  D3 is still pending on V3: it needs a later, separate engaged visit.")
    print("No CSV is written. This one invented paired draw is not a causal estimate or RL reward.")
    print("The original V2 return predates D2 and cannot be attributed to either D2 choice.")


if __name__ == "__main__":
    main()
