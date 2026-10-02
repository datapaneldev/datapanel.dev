"""Four real training inputs, including an explicitly requested second book level."""

FEATURE_NAMES = ("last_mid_return_bps", "spread_bps", "level1_imbalance", "level2_imbalance")
FEATURE_INPUT_FIELDS = ("Bp1", "Ap1", "Bq1", "Aq1", "Bq2", "Aq2")


def build_features(previous, current):
    mid = (current["Bp1"] + current["Ap1"]) / 2
    previous_mid = (previous["Bp1"] + previous["Ap1"]) / 2
    denominator = current["Bq2"] + current["Aq2"]
    # A zero-size second level is handled explicitly, not silently filled by the loader.
    level2 = (current["Bq2"] - current["Aq2"]) / denominator if denominator > 0 else 0.0
    return [
        (mid / previous_mid - 1) * 10000,
        (current["Ap1"] - current["Bp1"]) / mid * 10000,
        (current["Bq1"] - current["Aq1"]) / (current["Bq1"] + current["Aq1"]),
        level2,
    ]
