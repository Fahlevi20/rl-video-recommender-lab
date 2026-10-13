# Video recommender RL: stage 1 — define the decision

This is a **synthetic learning project**, not a real video service or a copy of YouTube's implementation. This first stage defines what one recommendation decision means. There is no simulator or trained model yet.

## One decision, in plain language

A simple candidate generator has already shortlisted three videos. The agent must pick **one** to show to a synthetic viewer. Before choosing, it can inspect a summary of recent behavior and the attributes of all three candidates. It cannot see whether the viewer *will* click or return later.

| Concept | Toy definition |
| --- | --- |
| **Viewer's hidden preference** | The simulator knows which topic this synthetic viewer genuinely likes. The agent **does not receive this value directly**; it must use observed behavior as clues. |
| **Observed viewer state** | Recent topic-watch counts, recent skips, and current day (normalized if passed to a model). These describe the viewer's history and context, not their true hidden preference. |
| **Candidate features** | For each of three shortlisted videos: topic, sensationalism/clickbait level, and an **estimated immediate-click score** from a separate, simple candidate generator. These describe the possible choices, not the viewer's state. |
| **Observation to the policy** | The viewer-state features **together with** the three candidates' features and scores. These can be encoded as one array later, but their roles remain different. No future click or return is included. |
| **Action** | Integer `0`, `1`, or `2`: show the corresponding shortlisted video. The action is a shortlist *index*, not a permanent video ID. |
| **Outcome and reward** | After showing the video, the simulator generates an immediate click response and, separately, whether the viewer returns for the next opportunity. For learning, a possible objective is `click_reward + 2 × return_reward`, where each term is 0 or 1. The factor 2 is a **teaching choice** to be tested, not a real business value. A click does **not** automatically cause a return. |
| **Next observation** | An updated history: what was shown, whether it was clicked/skipped, and the next opportunity's shortlist, **if** the viewer returns. If they do not return, the episode ends. |
| **Episode** | Up to 10 recommendation opportunities for one synthetic viewer, ending earlier if the simulated viewer leaves. Ten is a toy limit, not a production time horizon. |

The *baseline* is a non-RL rule: select the candidate with the highest **estimated immediate-click score**. A future RL policy would select among the **same three candidates**, but learn which choices yield better cumulative reward over the episode. We will compare both fairly after building the simulator.

## Worked two-decision example (illustrative, not measured)

At day 1, the observed history says the viewer watched two cooking videos and skipped one sports video. Their genuine topic preference is **hidden**. The candidate generator supplies:

| Action index | Video | Estimated immediate-click score |
| ---: | --- | ---: |
| 0 | Sensational sports clip | 0.9 |
| 1 | Helpful cooking lesson | 0.6 |
| 2 | Short travel clip | 0.4 |

The click-score baseline picks **action 0**. Suppose this viewer clicks, but does **not** return: click `1`, return `0`, reward `1 + 2×0 = 1`; the episode stops. This is **one possible synthetic outcome**, not something the agent knew before acting.

To illustrate a *different possible trajectory from the same starting point*, suppose another policy picks **action 1**. The viewer clicks and returns: click `1`, return `1`, reward `1 + 2×1 = 3`. On day 2, the observation now includes the day-1 cooking click, and the next three candidate videos. If the agent picks a good day-2 video and the viewer clicks but does not return, the second reward is `1`, so that trajectory totals `3 + 1 = 4`. The two trajectories are **hypothetical**: they do not prove that a cooking video caused the return or that RL is better. The later simulator must specify and test how outcomes are generated.

**Reacher connection:** a single fingertip-to-target pass did not mean the arm stayed close. Likewise, a single video click does not mean a viewer will come back. In both cases, the objective, the reward, and the evaluation metric need to be defined separately.

## What comes next

Only after we agree on this definition will we build a tiny Gymnasium environment, inspect a few manual episodes, compare simple baselines, train an RL model, and finally evaluate it. We will do **one stage at a time**, not generate the entire system now.

### Reading

- [Google's SlateQ paper](https://ar5iv.labs.arxiv.org/html/1905.12767) illustrates a published long-term recommendation objective; this toy setup is **not** its actual state representation or architecture.
- [Gymnasium guide to custom environments](https://gymnasium.farama.org/introduction/create_custom_env/) explains the observation/action/reward/next-observation interface we will implement later.
