"""A simple policy that chooses one video from an existing shortlist."""

import random

from candidate_generator import generate_candidates, sample_catalog


def choose_random_video(candidates, rng):
    if not candidates:
        raise ValueError("Cannot choose from an empty shortlist")
    return rng.randrange(len(candidates))


def main():
    catalog = sample_catalog()
    candidate_rng = random.Random(42)
    policy_rng = random.Random(7)
    print("Demo only: the entries below explain a selection, not real event logs.")
    print("Candidate seed: 42; random-baseline seed: 7.")
    print("The baseline does not use viewer profile or playback history.\n")
    print("[STEP 1] Filter the catalog:")
    for video in catalog:
        status = "keep" if video.eligible and video.duration_seconds >= 30 else "exclude"
        print(f"  video {video.video_id}: topic={video.topic}, duration={video.duration_seconds}s, "
              f"eligible={video.eligible} -> {status}")

    for example in range(1, 3):
        print(f"\n--- Selection example {example} ---")
        candidates = generate_candidates(catalog, candidate_rng)
        print("[STEP 2] Build the three-video shortlist:")
        for index, video in enumerate(candidates):
            print(f"  index {index}: video {video.video_id} ({video.topic}, {video.duration_seconds}s)")
        choice = choose_random_video(candidates, policy_rng)
        selected = candidates[choice]
        print(f"[STEP 3] Random baseline chooses index {choice} (ignores topic/history).")
        print(f"[STEP 4] Selected video: {selected.video_id} ({selected.topic}).")
        print("No watch or return was simulated; this example stops at the video choice.")


if __name__ == "__main__":
    main()
