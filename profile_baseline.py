"""Choose a shortlisted video using a recorded topic interest when available."""

import random

from candidate_generator import Video


def choose_profile_video(candidates, recorded_interest, rng):
    if not candidates:
        raise ValueError("Cannot choose from an empty shortlist")

    matches = [index for index, video in enumerate(candidates)
               if video.topic == recorded_interest]
    possible = matches if matches else list(range(len(candidates)))
    return rng.choice(possible)


def main():
    candidates = [
        Video("A", "cooking", 90, True),
        Video("B", "cooking", 120, True),
        Video("C", "sports", 75, True),
    ]
    interest = "cooking"  # Illustrative interest supplied by U1, not hidden simulator state.
    rng = random.Random(7)

    print("Demo only: no synthetic visit or response event is generated.")
    print(f"[STEP 1] Recorded interest: {interest} (U1 stated this before selection).")
    print("[STEP 2] Candidate generator supplies this illustrative shortlist:")
    for index, video in enumerate(candidates):
        label = "matches" if video.topic == interest else "does not match"
        print(f"  index {index}: video {video.video_id} ({video.topic}) -> {label}")

    matches = [video for video in candidates if video.topic == interest]
    print(f"[STEP 3] There are {len(matches)} matching candidates: "
          "two cooking videos have the same topic-match score.")
    choice = choose_profile_video(candidates, interest, rng)
    selected = candidates[choice]
    print(f"[STEP 4] Seeded tie-break chooses index {choice}. Selected video: "
          f"{selected.video_id} ({selected.topic}).")
    print("No watch or return was simulated; this rule does not use playback history or learn from data.")


if __name__ == "__main__":
    main()
