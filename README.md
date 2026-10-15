# Video recommender RL — learning project

**Status:** early prototype: a candidate generator, random, profile-based, and recorded-watch-history recommendation baselines, one-video synthetic reaction sampler, independent visit-gap sampler, one- and two-visit timestamped log examples, a separate hypothetical video-dependent return illustration, and a descriptive seven-day label calculator exist, but no validated return simulator, trained model, real viewer logs, or measured results exist yet. We will build a realistic *workflow* using synthetic timestamped events, one stage at a time; this is not YouTube's implementation or a production service. See [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md) for the flow and [DISCUSSION_NOTES.md](DISCUSSION_NOTES.md) for decisions and open questions.

## What decision does the model make?

**When a viewer opens the app**, a candidate generator supplies three eligible videos. The policy sees what is known **before** the recommendation: the viewer's recorded history and visit context, plus features of the three candidates. It chooses **one candidate index** (`0`, `1`, or `2`). The simulator will later generate the viewer's response and possible future visits.

```text
Current observation (history + time context + candidate features)
    → policy → action: choose one of the three candidates
    → show video → log impression and any immediate click/watch
    → later visits, if any, create new observations and decisions
```

A video embedding could eventually be one set of candidate features; it is not itself RL. Cosine similarity could help shortlist candidates, but the RL policy is the *decision maker* that learns from subsequent feedback. Three candidates is a teaching-size shortlist, **not** an RL requirement.

**First shortlist prototype:** [candidate_generator.py](candidate_generator.py) holds a tiny synthetic catalog, keeps videos marked eligible and at least 30 seconds long, then supplies three **distinct** actual videos with different topics when available—for example, one cooking, one sports, and one music video. It uses seeded random selection so an experiment can be reproduced. If fewer than three topics are available, it fills the remaining slots from **different** eligible videos; topics may repeat (e.g., cooking A, cooking B, sports C). A fixed seed reproduces the sequence, **not** necessarily the same shortlist every visit. This is only the menu: no recommendation rule chooses a video yet. A cooking video can be chosen only if one is in the current shortlist. The function raises `ValueError` if fewer than three eligible videos exist; production behavior for that case remains to be designed.

**Illustrative D1 → D2 example (not a field in the current sample log):** The synthetic simulator may privately represent viewer U1 as interested in cooking to generate plausible behavior. At decision D1, the model does **not** receive that private preference; it chooses cooking video A using only the available history, context, and candidate features. If U1 then watches A, that watch is logged **after** D1. When U1 later visits for decision D2, the same model can use the recorded watch of A as history and may choose a *different* cooking video from D2's candidates. It cannot use D2's future watch or read the simulator's private preference. This is an example of how we could generate synthetic behavior, not a finalized viewer-response rule.

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

## Try the candidate generator

From this project directory, run `python candidate_generator.py` to print the catalog, why each video is kept or excluded, two visit shortlists, and a fallback example with two cooking videos. Run `python -m unittest discover -p "test*.py"` to test eligibility, distinct videos, topic diversity, and seed reproducibility alongside the event-history checks. The printed visits are **shortlist examples only**: no viewer response, visit event, or model recommendation is generated.

## Try the random recommendation baseline

Run `python random_baseline.py` from this project directory. It prints `[STEP 1]` catalog filtering, `[STEP 2]` each three-video shortlist, `[STEP 3]` the seeded random index, and `[STEP 4]` the **one selected video** for two examples. The generator and baseline use separate random-number streams so each has a reproducible sequence. This baseline **does not use U1's profile, the earlier 5-second play, or any other viewer history**; it is a comparison rule, not a trained RL model. The two printed examples do not simulate visits, impressions, or feedback.

## Try the profile-based baseline

Run `python profile_baseline.py` to see a step-by-step example: a **stated, recorded** cooking interest, two cooking candidates plus one sports candidate, and a seeded tie-break that selects **one** cooking video. `choose_profile_video(candidates, recorded_interest, rng)` returns the selected candidate index. If there is no recorded interest or no matching candidate, it chooses randomly among the current shortlist; an empty shortlist raises an error. This rule **does not** read a private simulator preference or the earlier 5-second playback, and it is **not trained**. The printed example uses an illustrative shortlist rather than generating it from the catalog; no visit or viewer-response events are simulated.

## Try one synthetic viewer reaction

Run `python viewer_reaction.py` to print example responses **after** a video is shown. The simulator privately treats U1 as interested in cooking. For a matching topic the invented outcomes are 20% ignore, 20% click and play 5 seconds, 60% click and play 40 seconds; for a nonmatching topic they are 50%, 30%, and 20% respectively. A fixed seed reproduces the examples; individual responses are **not guaranteed** by topic. These invented numbers are for teaching, **not observations about real people**. The policy must not receive the simulator's private interest; a viewer's separately stated profile interest is a different, recorded input. Playback under 30 seconds is still feedback, but not a qualifying watch. This small sampler does **not** generate timestamped event logs, later visits, seven-day labels, or a training reward.

## Try synthetic return times (logging exercise only)

Run `python visit_timing.py` to print a starting visit timestamp and four later visit timestamps. It uses a fixed seed and independently picks a gap of **1, 2, 4, or 8 days**, each with equal chance. This is an invented rule for practicing irregular visits, **not** a realistic estimate or a trained return predictor. The choice of video and its playback do **not** affect these gaps; consequently this rule cannot teach a policy to improve returns through recommendations. It generates **no** timestamped event rows, video decisions, watches, engaged-return labels, or RL reward. We must design video-dependent return behavior separately before training an RL policy on a long-term objective.

## Generate one visit's event rows

Run `python one_visit_log.py` from this project directory. It connects the candidate generator, **random baseline**, and response sampler for one synthetic U1 visit, then prints each step and writes [generated_one_visit.csv](generated_one_visit.csv). The file records `visit_started`, `video_shown`, and—if clicked—`video_clicked` and `video_playback` with the playback duration. `source=random_baseline` identifies the selection rule on recommendation-related rows; the visit-start row has no selector. These are **practice timestamps and seeded responses**, not observed real behavior. The script does not overwrite an existing file: to regenerate after inspecting it, rename or remove only `generated_one_visit.csv` first. [sample_events.csv](sample_events.csv) remains the separate hand-written teaching example. This first generated log contains **no later visit, engaged-return label, or RL training reward**. The candidate shortlist and private simulator preference are not columns in this event CSV; they need separate contracts before policy training.

## Generate two visits (logging exercise)

Run `python two_visit_log.py` to print U1's first and later visit and write [generated_two_visits.csv](generated_two_visits.csv). Each visit gets one new shortlist and decision ID (D1, D2). The seeded gap between visit starts comes from the **independent** visit-time sampler; the random baseline chooses one video per visit and ignores history. The simulator logs immediate clicks/playback only if they happen. The output prints the event IDs available before D2, including D1's feedback and the new app open but **not** D2's future response. The script will not overwrite an existing output file; [sample_events.csv](sample_events.csv) and [generated_one_visit.csv](generated_one_visit.csv) remain untouched. We have **not** implemented a personalized later decision or a video-dependent return rule, so this exercise cannot show that D1 caused U1 to return.

## Try a watch-history recommendation rule

Run `python history_baseline.py` to **reconsider D2 only**, without editing `generated_two_visits.csv`. The printed history stops before D2: E4 records 40 seconds of video A, whose catalog topic is cooking. The rule takes the **latest recorded playback of at least 30 seconds**, looks up its topic in the catalog, and selects a matching video from D2's actual three-video shortlist (B cooking, E music, C sports). Here it selects **B because of E4**. The original two-visit CSV also shows B, but that B was selected **by chance** using the random baseline; the new rule is a separate demonstration and does not pretend to resimulate D2's response. If no qualifying prior watch or matching candidate exists, the rule picks randomly from the shortlist; equal-topic candidates are tied randomly. A 5-second playback is still logged, but this simple rule does not use it to infer a preferred topic. This hand-written rule cannot see the simulator's private preference or a playback at or after D2, and it is **not RL or evidence of improved returns**. Run `python -m unittest discover -p "test*.py"` to check these cases.

## Compare two D2 choices and immediate reactions

Run `python compare_d2.py`. Both hypothetical policies receive the **same** recorded history (E1–E5) and D2 shortlist (B cooking, E music, C sports). With separate fixed policy seeds, random chooses C and the watch-history rule chooses B. Both choices receive the **same seeded synthetic response percentile**: C gets a 5-second play, B a 40-second play, because the invented reaction probabilities differ by topic. This is **one illustrative draw**, not a performance estimate or proof that history usually wins. The private cooking interest is given only to the reaction simulator, never to either policy. Nothing is appended to the saved event CSV; its original D2 was B/ignored under another seed. Visit timing still ignores video choice, so this comparison cannot measure improved returns or train RL. Tests: `python -m unittest discover -p "test*.py"`.

## See a possible return depend on the recommendation

Run `python compare_return_journeys.py` to extend the two hypothetical D2 choices to a *possible later V3*. The return simulator assumes invented chances of opening the app again: 10% after 0 seconds of D2 playback, 30% after 5 seconds, and 70% after 40 seconds. With the same illustrative return draw (0.45), random C gets a 5-second play and no V3; history-based B gets a 40-second play and a V3 on Oct 10. On V3, a separately sampled D3 response produces a 40-second watch, so **D2's** descriptive seven-day engaged-return label is `yes`; without V3, the random branch's D2 remains `pending` until its window closes Oct 15, then becomes `no` with complete observation. An app open *without* a 30-second watch would not qualify, and D3's own return label remains pending. The already-recorded V2 start happened **before D2**, so it cannot be caused by D2. This is one pair of **assumed synthetic** journeys, not evidence about real return probabilities, a causal estimate, or a settled training reward. Branch logs exist only in memory; `generated_two_visits.csv` and the older independent `visit_timing.py` exercise remain unchanged.

## Check the seven-day engaged-return label

Run `python engaged_return.py` to read `generated_two_visits.csv` and print D1's **descriptive** status at two observation times. The Oct 8 return without a 30-second playback leaves D1 **pending**; after D1's Oct 11 10:01 deadline, given a log observed through that time, it becomes **no**. The calculator also supports **yes** when a later visit starts after the impression and any video has at least 30 seconds of playback completed by the deadline (inclusive). A 5-second play or a watch on the original visit is not a qualifying *return*. If the log ends before the deadline, pass `observed_through` so the unresolved label stays pending rather than becoming a false no. The timestamps in this exercise are illustrative and the descriptive label **is not an RL training reward or causal attribution**.

## Inspect an engaged-return `yes` example

Run `python yes_return_example.py` to see a separate, **illustrative** V2 watch. It reads `generated_two_visits.csv` and adds one playback row **in memory**: U1 finds video C through search and completes 40 seconds at Oct 8 10:03:40. It prints D1 = `yes` because this is a later engaged visit within D1's window, while D2 = `pending` because D2 was first shown **during** V2 and needs a subsequent visit. It does **not** change either CSV or assert that D1 caused U1's return. This is a deliberately added example, not an extra response sampled by the viewer simulator and not an RL reward.

## First hand-written event log

The small [sample_events.csv](sample_events.csv) contains four visits by one synthetic viewer. On visit V3, a recommended video is clicked and played for **5 seconds**, recorded as `video_playback` with `watch_seconds=5`. This is logged playback but **not** a qualifying watch under our 30-second rule. A later decision D4 can use that recorded short playback as history—for example, alongside other past clicks and watches to learn patterns—but D3 cannot use it before showing the video. We have not yet built the numerical features or trained a model to learn such patterns. `event_history.py` reads the rows known **strictly before** the timestamp of a model decision; `test_event_history.py` checks that later responses and return events cannot enter an earlier decision's input. To inspect it locally, run `python -m unittest discover -p "test*.py"` from this directory. This is a **leakage check for the hand-written log**, not a completed observation builder, generated dataset, RL reward, or trained model. The full candidate set and prior preference features are not present in this first log; they must be designed before a policy can choose among videos. Event times are ISO-formatted practice timestamps, not real user data.

## Research context

The [SlateQ paper](https://ar5iv.labs.arxiv.org/html/1905.12767) describes long-term recommendation value and consecutive *visits* that may be spaced apart in time. It does not publish our toy observation schema, our seven-day return definition, or a specific seven-day history lookback. [Gymnasium's custom-environment guide](https://gymnasium.farama.org/introduction/create_custom_env/) describes the `reset`/`step` interface we may implement after the rules are agreed.
