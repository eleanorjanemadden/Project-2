"""Check reserve portfolio candidates using editable percentage weights."""

# Editable inputs. Weights and limits use percent units (e.g., 8 means 8%).
# Holding, issuer, business days to redeem, reserve-eligible
HOLDINGS = [
    ("Cash", "none", 0, True),
    ("Treasury bills", "U.S. Treasury", 1, True),
    ("Treasury 10-year note", "U.S. Treasury", 1, True),
    ("Global equity index fund", "diversified fund", 2, False),
    ("Investment-grade bond fund", "diversified fund", 3, False),
    ("Private real estate fund", "diversified fund", 90, False),
    ("Acme Corp bonds", "Acme Corp", 4, False),
    ("Acme Corp stock", "Acme Corp", 1, False),
]

# Each row contains weights for candidates A, B, C, and D.
WEIGHTS = {
    "Cash": (2, 1, 1, 0),
    "Treasury bills": (2, 0, 1, 0),
    "Treasury 10-year note": (10, 0, 0, 100),
    "Global equity index fund": (60, 55, 70, 0),
    "Investment-grade bond fund": (26, 20, 20, 0),
    "Private real estate fund": (0, 15, 0, 0),
    "Acme Corp bonds": (0, 5, 0, 0),
    "Acme Corp stock": (0, 4, 8, 0),
}
CANDIDATES = ("A", "B", "C", "D")
RESERVE_SIZE = 100  # USD millions
QUARTERLY_DISTRIBUTION = 0.75  # USD millions
QUARTERS_TO_COVER = 4
LIQUIDITY_WINDOW = 5  # Business days
MINIMUM_LIQUID_SHARE = 90  # Percent
ISSUER_LIMIT = 8  # Percent
EXEMPT_ISSUERS = {"none", "U.S. Treasury", "diversified fund"}


def main():
    reserve_minimum = QUARTERS_TO_COVER * QUARTERLY_DISTRIBUTION / RESERVE_SIZE * 100
    print(f"Reserve minimum: {reserve_minimum:.1f}%")

    for index, candidate in enumerate(CANDIDATES):
        weights = [WEIGHTS[holding][index] for holding, _, _, _ in HOLDINGS]
        eligible_weight = 0
        liquid_weight = 0
        company_weights = {}
        for (holding, issuer, days, eligible), weight in zip(HOLDINGS, weights):
            if eligible:
                eligible_weight += weight
            if days <= LIQUIDITY_WINDOW:
                liquid_weight += weight
            if issuer not in EXEMPT_ISSUERS:
                company_weights[issuer] = company_weights.get(issuer, 0) + weight

        total = sum(weights)
        lowest = min(weights)
        largest_company = max(company_weights.values(), default=0)
        # Small tolerance avoids failures caused only by floating-point rounding.
        tolerance = 1e-9
        checks = [
            ("Weights sum to 100", total, abs(total - 100) <= tolerance),
            ("Lowest weight (long-only)", lowest, lowest >= -tolerance),
            ("Reserve-eligible weight", eligible_weight,
             eligible_weight >= reserve_minimum - tolerance),
            (f"Weight redeemable within {LIQUIDITY_WINDOW} business days", liquid_weight,
             liquid_weight >= MINIMUM_LIQUID_SHARE - tolerance),
            ("Largest single company", largest_company,
             largest_company <= ISSUER_LIMIT + tolerance),
        ]

        print(f"\nCandidate {candidate}")
        for label, value, passed in checks:
            print(f"  {label}: {value:.1f}% — {'pass' if passed else 'FAIL'}")
        print("  Calendar-year loss rule: requires CIO clarification")
        failures = sum(not passed for _, _, passed in checks)
        print("  passes every checkable rule" if failures == 0
              else f"  fails {failures} rule(s)")


if __name__ == "__main__":
    main()
