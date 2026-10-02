"""EDIT HERE: causal features. This file is inlined into the uploaded guest source.

previous/current contain only their own observation's declared market fields.
Return one finite float per FEATURE_NAMES entry, in exactly that order.
Never read future observations, labels, validation/OOS outcomes or external files.
"""

FEATURE_NAMES = ("last_mid_return_bps", "spread_bps", "level1_imbalance")
FEATURE_INPUT_FIELDS = ("Bp1", "Ap1", "Bq1", "Aq1")


def build_features(previous, current):
    previous_mid = (previous["Bp1"] + previous["Ap1"]) / 2
    mid = (current["Bp1"] + current["Ap1"]) / 2
    return [
        (mid / previous_mid - 1) * 10000,
        (current["Ap1"] - current["Bp1"]) / mid * 10000,
        (current["Bq1"] - current["Aq1"]) / (current["Bq1"] + current["Aq1"]),
    ]
