# Video recommender RL — discussion notes

*Learning notes, 14 October 2026. Design discussion only; no simulator, model, real user logs, or measured business results exist yet.*

## What we want to build

A **realistic end-to-end learning workflow using synthetic, timestamped event logs**. The purpose is to understand how a recommendation decision, later user activity, feedback, training, and evaluation fit together before attempting anything for a client. Synthetic results cannot establish that a real client would gain users or revenue. We will progress in stages rather than generating the full project at once.

## One recommendation decision

When a viewer opens the app, a candidate generator presents some videos. The policy receives **one observation** containing (a) information known about the viewer up to that instant, (b) current context, and (c) the features of the available videos. It outputs an **action** selecting a video. Only **after** the action do we learn whether the viewer clicks and whether they visit and watch again later.

```text
Past behavior + current context + candidate-video features  →  policy
Policy  →  choose a candidate video
Later event logs  →  clicks, watches, new visits, and learning feedback
```

The observation can be one structured record or a numerical array with many fields: **one observation does not mean one number**. The candidate videos are available choices, but their *features* must also be visible to the policy so it can compare them. A video embedding is a numerical representation of video features; a policy can learn which embeddings lead to better outcomes for different viewers, but this does not imply human-like understanding of a video's meaning. Embeddings are **not required** to lie between −1 and 1. An action index such as `1` means “choose candidate 1 in the current shortlist,” not “one input value.”

The earlier three-video shortlist is just a teaching-size example, **not an RL requirement**. It means our toy policy chooses one of three options. The [SlateQ paper](https://ar5iv.labs.arxiv.org/html/1905.12767) studies recommending a *slate* of items: one simulation chooses three from ten candidates, while its YouTube experiment works with a much larger candidate set. Our design does not reproduce that system.

## Visits, days, and what the model can know

**One visit is not one calendar day.** If a viewer opens the app on day 4, stays away on days 5–7, and returns on day 8, there are recommendation decisions on **day 4 and day 8**, not on the days with no visit. A missing visit is **not** a skipped video.

| Day | Event | New video decision? |
| ---: | --- | :---: |
| 4 | Viewer visits; video shown | Yes |
| 5–7 | No visit | No |
| 8 | Viewer visits again | Yes |

On day 4, the policy cannot see the future day-8 visit. On day 8, it may use the history recorded through day 8 **before selecting the day-8 video**: for example, what happened on day 4, the elapsed time since the prior visit, and today's candidates. If the viewer returns again on day 9, it can also use what happened on day 8. We must distinguish `visit_number` from calendar time and from a history window. `days_since_last_visit = 1` on day 9 does **not** imply that only one day of older history is available. Proposed features such as `days_since_last_visit`, `days_since_last_click`, and past-week counts are **our design choices**, not published SlateQ field names.

The [SlateQ paper, §§3 and 9](https://ar5iv.labs.arxiv.org/html/1905.12767) describes summaries of earlier behavior and accounts for the time elapsed between consecutive *observed* visits. Those visits can be days apart. It does **not** disclose a fixed seven-day feature lookback or an exact live input schema. Its forward-looking engagement horizon is a **different concept** from how much past history is supplied to the model.

## Synthetic logs and the agreed outcome

We do **not** have an authorized real interaction dataset. We will first generate synthetic, timestamped events, including visits, recommendation impressions, clicks, and watches. A later visit becomes known **when it occurs**, not when the earlier video is recommended. Logs allow us to join later activity to an earlier decision for training and analysis; merely seeing a later visit does **not prove** the earlier video caused it.

Our agreed **measurement outcome** is an **engaged return within seven days**: a viewer comes back within seven days of a recommendation **and watches something**. **Record every return visit**, even if the viewer watches nothing; a visit with no qualifying watch is not engaged, and does not turn a pending earlier decision into yes or no while its window remains open. The seven-day window is **our proposed project definition**, not a rule from SlateQ. Track immediate clicks separately. We agreed that a **watch requires at least 30 seconds of playback**; a click with less playback is not a watch. This is a toy-project rule, not a universal standard, and candidate videos must be long enough for it to apply. We agreed the window begins at a recommendation's impression timestamp and ends **7 × 24 hours later**, including the deadline instant: a return visit must start after the impression and a 30-second watch must be completed by the deadline. A later return is still logged but means **no engaged return within seven days** for that earlier decision; the clock does not reset, and a new recommendation has its own window. For **descriptive decision labels**, we agreed a qualifying later engaged visit can mark **yes** for every recommendation shown *before that visit* whose own seven-day window contains the completed watch. Count the underlying visit only **once** in viewer-level results; a video first shown during that visit stays pending for its own later return. This is temporal association, not causal attribution or automatic double RL reward. We still need to finalize the event schema, training-credit rule, and how to handle windows extending beyond the available observation period. In particular, **“no visit tomorrow” must not end the episode automatically**; someone may come back several days later.

**Do not confuse a measurement outcome with a training reward.** An earlier draft proposed `click + 2 × return`; that `2` was arbitrary, not research-based, and we discussed replacing that bonus. One simple RL reward idea is `+1` for a click and no immediate return bonus, so a returning viewer gives the policy opportunities to earn rewards on later visits. But that idea does **not automatically optimize** our agreed seven-day *engaged-return* metric: a separate reward/credit-assignment design is still needed and should be settled before implementation. The [README](README.md) and [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md) now mark the older illustrative click-plus-return proposal as **not agreed**; neither a click-only nor a return-bonus reward has been finalized.

**Multiple videos per visit (agreed):** A viewer can watch more than one video in one app visit and may have more than one visit in a calendar day. Record each watch, but count a later visit containing at least one 30-second watch as **one** engaged visit in viewer-level metrics, not one per watched video. If the app requests another recommendation during the same visit, the model may make another action; this is **not** a return. If the viewer finds a video through search or chooses it without a model recommendation, still log the watch but do not claim the model selected it. Earlier recommendations may independently receive descriptive yes labels within their own windows; this does not duplicate the real visit event.

## Baseline, RL, and evaluation

A simple baseline can use current user/candidate features to favor the highest estimated immediate-click score. A separate RL policy would choose from the same eligible candidates but learn from the defined reward and later state transitions. Cosine similarity can help retrieve or score candidates; **cosine similarity is not itself an RL algorithm**. We should test the simulator and the baseline before training PPO or another RL model. A more complex RL policy is justified only if it improves the chosen objective over simpler approaches without unacceptable side effects.

For the synthetic exercise, evaluate policies in the same documented simulator under reproducible conditions, inspect individual trajectories, and compare **clicks, engaged returns, and user-experience guardrails** separately. A policy can change which future visits occur, so identical initial seeds do not force identical later observations. For a real client, historical data alone may lack outcomes for options never shown; valid offline policy evaluation requires appropriate logging (including chosen-action probabilities and sufficient action coverage), followed by carefully controlled online evaluation. A simulated lift is **not** a measured live lift.

## Why a client might care

The possible business pathway is:

```text
Better recommendations → more useful later visits → potentially better
customer retention or more ad opportunities → potentially more revenue
```

**Each arrow is a hypothesis to test, not a guarantee.** For a subscription service, longer-term satisfaction might improve renewal; for an ad-supported service, useful extra visits might create ad opportunities. We would also measure costs and negative effects such as skips, complaints, opt-outs, or time spent without satisfaction. A client claim would be: “We will test whether a policy raises **engaged seven-day returns** without hurting user experience, then measure whether that change improves *your* business metric.” Our synthetic project cannot promise a revenue gain.

The [SlateQ paper](https://ar5iv.labs.arxiv.org/html/1905.12767) reports improved engagement in a YouTube live experiment, **not a disclosed revenue impact**. A different [Microsoft Decision Service paper](https://arxiv.org/html/1606.03966) reports an 18% revenue lift for a particular landing-page application versus a non-contextual bandit; that **contextual-bandit case is not an estimate for this video recommender**.

## Next design checkpoint

Before coding, revise the [system design](SYSTEM_DESIGN.md) to match the agreed realistic direction: irregular visit times, timestamped synthetic event logs, a precisely defined seven-day engaged-return *measurement*, and a separately specified reward and attribution rule. Then build one stage at a time: event definitions → baseline logs → simulator and tests → learning → evaluation. No real-user data or production deployment is part of the current project.
