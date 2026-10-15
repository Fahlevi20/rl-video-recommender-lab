"""Illustrative probability of a later app open given immediate playback.

These invented values are not estimates of how real people return.
"""


def returns_after_playback(playback_seconds, draw):
    if not 0 <= draw < 1:
        raise ValueError("Return draw must be in [0, 1)")
    if playback_seconds >= 30:
        probability = 0.70
    elif playback_seconds > 0:
        probability = 0.30
    else:
        probability = 0.10
    return draw < probability
