"""Meridian training baselines. Run: python3 portfolio.py (standard library only)."""
import math

# Course-authored annual training values; decimals, not market estimates.
SLEEVES = ["Treasury bills", "Treasury 10-year note",
           "Investment-grade bond fund", "Global equity index fund"]
RETURNS = [0.035, 0.043, 0.050, 0.080]
VOLATILITIES = [0.005, 0.070, 0.060, 0.160]
CORRELATIONS = [
    [1.00, 0.10, 0.05, 0.00],
    [0.10, 1.00, 0.80, -0.10],
    [0.05, 0.80, 1.00, 0.25],
    [0.00, -0.10, 0.25, 1.00],
]
CPI_ESTIMATE = 0.025  # Estimate for the exercise, not observed inflation.
OBJECTIVE = CPI_ESTIMATE + 0.04
RESERVE_ELIGIBLE = [True, True, False, False]


def validate_inputs(volatilities, correlations):
    n = len(volatilities)
    if len(correlations) != n or any(len(row) != n for row in correlations):
        raise ValueError("Correlation table must be square and match the sleeves.")
    if any(not math.isfinite(v) or v <= 0 for v in volatilities):
        raise ValueError("Volatilities must be finite and positive.")
    for i in range(n):
        for j in range(n):
            value = correlations[i][j]
            if not math.isfinite(value) or not -1 <= value <= 1:
                raise ValueError(f"Correlation [{i}][{j}] must be between -1 and 1.")
            if not math.isclose(value, correlations[j][i], abs_tol=1e-12):
                raise ValueError("Correlation table must be symmetric.")
        if not math.isclose(correlations[i][i], 1.0, abs_tol=1e-12):
            raise ValueError("Each diagonal correlation must equal 1.")


def covariance_matrix(volatilities, correlations):
    validate_inputs(volatilities, correlations)
    return [[correlations[i][j] * volatilities[i] * volatilities[j]
             for j in range(len(volatilities))] for i in range(len(volatilities))]


def equal_weights(n):
    return [1 / n] * n


def inverse_volatility_weights(volatilities):
    inverse = [1 / v for v in volatilities]
    return [value / sum(inverse) for value in inverse]


def expected_return(weights, returns):
    return sum(w * r for w, r in zip(weights, returns))


def portfolio_variance(weights, covariance):
    # All ordered pairs: i=j gives own risk; i!=j gives covariance twice per pair.
    return sum(weights[i] * weights[j] * covariance[i][j]
               for i in range(len(weights)) for j in range(len(weights)))


def portfolio_volatility(weights, covariance):
    variance = portfolio_variance(weights, covariance)
    if variance < -1e-12:
        raise ValueError("Negative portfolio variance; check the correlation assumptions.")
    return math.sqrt(max(0.0, variance))


def reserve_weight(weights, eligible):
    return sum(w for w, allowed in zip(weights, eligible) if allowed)


def meets_objective(value, objective):
    return value >= objective


def baseline_weights():
    return {"Benchmark": [0, 0, 0.4, 0.6],
            "Equal weight": equal_weights(len(SLEEVES)),
            "Inverse volatility": inverse_volatility_weights(VOLATILITIES)}


def main():
    covariance = covariance_matrix(VOLATILITIES, CORRELATIONS)
    print("Meridian baselines: annual course-authored training inputs")
    print(f"Objective: {OBJECTIVE:.2%}; CPI estimate: {CPI_ESTIMATE:.1%}")
    print("Weight order: " + " / ".join(SLEEVES))
    for name, weights in baseline_weights().items():
        result = expected_return(weights, RETURNS)
        print(f"\n{name}")
        print("  Weights (%): " + " / ".join(f"{w * 100:.1f}" for w in weights))
        print(f"  Expected return: {result:.2%}")
        print(f"  Volatility: {portfolio_volatility(weights, covariance):.2%}")
        print(f"  Reserve-eligible: {reserve_weight(weights, RESERVE_ELIGIBLE):.1%}")
        print(f"  Meets {OBJECTIVE:.1%} objective: {'yes' if meets_objective(result, OBJECTIVE) else 'no'}")


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        raise SystemExit(f"Input error: {error}")
