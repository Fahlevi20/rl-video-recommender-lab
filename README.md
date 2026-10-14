# Video recommender RL — learning project

**Status:** design only. No simulator, trained model, real viewer logs, or measured results exist yet. We will build a realistic *workflow* using synthetic timestamped events, one stage at a time; this is not YouTube's implementation or a production service. See [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md) for the flow and [DISCUSSION_NOTES.md](DISCUSSION_NOTES.md) for decisions and open questions.

## What decision does the model make?

**When a viewer opens the app**, a candidate generator supplies three eligible videos. The policy sees what is known **before** the recommendation: the viewer's recorded history and visit context, plus features of the three candidates. It chooses **one candidate index** (`0`, `1`, or `2`). The simulator will later generate the viewer's response and possible future visits.

```text
Current observation (history + time context + candidate features)
    → policy → action: choose one of the three candidates
    → show video → log impression and any immediate click/watch
    → later visits, if any, create new observations and decisions
```

A video embedding could eventually be one set of candidate features; it is not itself RL. Cosine similarity could help shortlist candidates, but the RL policy is the *decision maker* that learns from subsequent feedback. Three candidates is a teaching-size shortlist, **not** an RL requirement.

## What does “engaged return within seven days” mean?

Our agreed **measurement outcome** for a recommendation is: **the viewer returns to the same app within seven days and watches any video**. The later video may be from another channel; it need not be the originally recommended video. Clicking or watching the recommended video *now* is a **separate immediate outcome**. A **watch** means at least **30 seconds of playback**: a click followed by 5 seconds counts as a click, not a watch. This is our agreed synthetic-project rule, not a universal standard; we will use videos long enough for the threshold to be achievable. The seven-day window is **7 × 24 hours after the recommendation's impression timestamp**. A return visit must begin after that impression, and its qualifying 30 seconds of playback must be completed **no later than** the deadline. For example, if video A was shown Oct 4 at 10:00, the deadline is Oct 11 at 10:00; a qualifying watch completed at 10:01 is too late for A's label, although the visit and watch are still logged. A new recommendation on Oct 11 would have its own window. If the viewer returns and watches within the windows of several **earlier** recommendations, each may receive a descriptive **yes** label; the app still records **one** return event, not several. A video shown *during* the returning visit stays **pending** until a subsequent engaged visit. These labels do not establish which prior video caused the return or settle the training reward. Seven days is our project choice, not a number prescribed by a paper.

A simplified event timeline:

| Day | Recorded event | Status for the day-4 recommendation |
| ---: | --- | --- |
| 4 | Viewer visits; recommended video A is shown and clicked | Immediate click = yes; engaged return = **pending** |
| 5–7 | Viewer does not open the app | No recommendation action; engaged return still **pending** |
| 8 | Viewer opens the app and watches video B, possibly from another channel | Engaged return = **yes** |
| 11 | Seven-day window ends | If no qualifying return-and-watch occurred, mark **no**; do not change an earlier **yes** |

One visit can include **multiple watched videos**. **First version:** the app asks the **same model once per visit** to recommend one video. In a later extension, the app may ask that same model again within a visit; that would be a **second decision**, not a second model or a return. The viewer can also find a video through search or their own choice; log that watch without pretending the model picked it. A return visit with one or several qualifying watches still counts as **one engaged visit** at viewer level; a person may also make several separate visits on the same day. Video B may or may not have been recommended on day 8. The watch is an app-level event, not evidence that the viewer watched video A again. **Log the app open even when nothing is watched**, so the visit is not lost; merely opening the app without watching does **not** satisfy the engaged-return measure. An earlier pending label remains pending until a qualifying watch on a later visit or until its seven-day window closes. A missing visit on day 5 does **not** end the viewer's episode or count as skipping a video; they could return on day 8. Day 8 would also be a **new** recommendation decision with a new observation, if that visit includes a recommendation opportunity. The day-8 watch is not available to the day-4 policy when it chooses video A.

If our recorded data stops before day 11, an unresolved day-4 outcome is **not yet known**; it must not automatically be labeled “no.” And observing the day-8 visit after showing A does **not** prove A caused the return. A fair policy comparison would be needed to investigate that.

## What are we optimizing?

Engaged return is the **agreed measurement**, not yet a finalized training reward. An older example proposed `click + 2 × return`; that bonus was arbitrary and **is not our chosen rule**. We will define precisely how the policy learns from delayed events and how to handle multiple intervening decisions before coding. We will report immediate clicks, watches, engaged returns, and potential negative user outcomes separately, rather than claim that a synthetic reward is business impact.

## Learning stages

1. **Now:** finalize event definitions, time windows, attribution, and training reward with one worked viewer timeline.
2. Generate seeded, timestamped synthetic visits, impressions, clicks, and watches; inspect the logs.
3. Test simple baselines before training an RL policy.
4. Train a policy in a validated simulator; evaluate saved models on different seeds and inspect failures.
5. Connect simulated measurements to what a real client would need: authorized logs, valid comparisons, user-experience safeguards, and an actual business outcome. Synthetic results alone cannot establish a revenue or retention lift.

## Research context

The [SlateQ paper](https://ar5iv.labs.arxiv.org/html/1905.12767) describes long-term recommendation value and consecutive *visits* that may be spaced apart in time. It does not publish our toy observation schema, our seven-day return definition, or a specific seven-day history lookback. [Gymnasium's custom-environment guide](https://gymnasium.farama.org/introduction/create_custom_env/) describes the `reset`/`step` interface we may implement after the rules are agreed.
