"""Build a reproducible three-video shortlist from a synthetic catalog."""

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Video:
    video_id: str
    topic: str
    duration_seconds: int
    eligible: bool


def sample_catalog():
    return [
        Video("A", "cooking", 90, True),
        Video("B", "cooking", 120, True),
        Video("C", "sports", 75, True),
        Video("D", "sports", 100, True),
        Video("E", "music", 80, True),
        Video("F", "music", 29, True),
        Video("G", "cooking", 60, False),
    ]


def generate_candidates(catalog, rng):
    eligible = [video for video in catalog if video.eligible and video.duration_seconds >= 30]
    if len(eligible) < 3:
        raise ValueError("Need at least three distinct eligible videos")

    topics = list(dict.fromkeys(video.topic for video in eligible))
    chosen_topics = rng.sample(topics, min(3, len(topics)))
    candidates = [
        rng.choice([video for video in eligible if video.topic == topic])
        for topic in chosen_topics
    ]
    if len(candidates) < 3:
        remaining = [video for video in eligible if video not in candidates]
        candidates.extend(rng.sample(remaining, 3 - len(candidates)))
    return candidates


def main():
    catalog = sample_catalog()
    rng = random.Random(42)
    print("Synthetic catalog:")
    for video in catalog:
        status = "keep" if video.eligible and video.duration_seconds >= 30 else "exclude"
        print(f"  {video.video_id}: {video.topic}, {video.duration_seconds}s, eligible={video.eligible} -> {status}")

    for visit in range(1, 3):
        candidates = generate_candidates(catalog, rng)
        print(f"\nVisit {visit}: candidate generator supplies this shortlist:")
        for index, video in enumerate(candidates):
            print(f"  {index}: video {video.video_id} ({video.topic}, {video.duration_seconds}s)")
        print("  No recommendation selected: a model/baseline would choose one of 0, 1, or 2 later.")

    limited_catalog = [video for video in catalog if video.video_id in {"A", "B", "C"}]
    print("\nFallback example: only cooking A, cooking B, and sports C are eligible:")
    for index, video in enumerate(generate_candidates(limited_catalog, rng)):
        print(f"  {index}: video {video.video_id} ({video.topic}, {video.duration_seconds}s)")
    print("  Topics may repeat; video IDs remain distinct. No model decision yet.")


if __name__ == "__main__":
    main()
