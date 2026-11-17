"""Meridian training baselines"""
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



def search_portfolio(returns, volatilities, correlations, objective,
                     eligible, reserve_minimum):
    """Exhaust every fully invested long-only 5-percentage-point mix."""
    n = len(returns)
    if not 3 <= n <= 6 or len(volatilities) != n or len(eligible) != n:
        raise ValueError("Use three to six assets with matching input lengths.")
    if not all(math.isfinite(r) for r in returns) or not math.isfinite(objective):
        raise ValueError("Return estimates and objective must be finite.")
    if not math.isfinite(reserve_minimum) or not 0 <= reserve_minimum <= 1:
        raise ValueError("Reserve minimum must be between 0 and 100%.")
    covariance = covariance_matrix(volatilities, correlations)

    def mixes(remaining, slots):
        # Integer units avoid a floating-point weight-sum problem: 20 units = 100%.
        if slots == 1:
            yield [remaining / 20]
        else:
            for units in range(remaining + 1):
                for rest in mixes(remaining - units, slots - 1):
                    yield [units / 20] + rest

    best = None
    for weights in mixes(20, n):
        result = expected_return(weights, returns)
        reserve = reserve_weight(weights, eligible)
        if result < objective - 1e-12 or reserve < reserve_minimum - 1e-12:
            continue
        volatility = portfolio_volatility(weights, covariance)
        if best is None or volatility < best["volatility"] - 1e-12:
            best = {"weights": weights, "return": result,
                    "volatility": volatility, "reserve": reserve}
    return best


def estimate_from_csv(source, last_36=False):
    """Annual estimates from simple monthly returns; sample SD, not CAGR."""
    import csv
    import datetime as dt
    import statistics
    from pathlib import Path

    if isinstance(source, (str, Path)):
        with open(source, newline="", encoding="utf-8-sig") as file:
            return estimate_from_csv(file, last_36)
    rows = list(csv.reader(source))
    if not rows or not 4 <= len(rows[0]) <= 7:
        raise ValueError("CSV needs a date column and three to six ticker columns.")
    tickers = [name.strip() for name in rows[0][1:]]
    if len(set(tickers)) != len(tickers) or not all(tickers):
        raise ValueError("Tickers must be nonempty and unique.")
    dates, prices = [], []
    for row in rows[1:]:
        if len(row) != len(tickers) + 1:
            raise ValueError("Every CSV row must have a date and a price for every ticker.")
        try:
            date = dt.date.fromisoformat(row[0])
            values = [float(value) for value in row[1:]]
        except ValueError as error:
            raise ValueError("Use ISO dates YYYY-MM-DD and numeric prices.") from error
        if any(not math.isfinite(v) or v <= 0 for v in values):
            raise ValueError("Prices must be finite and positive; no missing values.")
        month = date.year * 12 + date.month
        if dates and month != dates[-1].year * 12 + dates[-1].month + 1:
            raise ValueError("Prices must be consecutive monthly rows, oldest first.")
        dates.append(date)
        prices.append(values)
    if len(prices) < 3 or (last_36 and len(prices) < 37):
        raise ValueError("Need at least three prices, or 37 prices for 36 monthly returns.")
    monthly = [[prices[t][i] / prices[t-1][i] - 1 for i in range(len(tickers))]
               for t in range(1, len(prices))]
    used_dates = dates[1:]
    if last_36:
        monthly, used_dates = monthly[-36:], used_dates[-36:]
    columns = list(zip(*monthly))
    returns = [statistics.mean(column) * 12 for column in columns]
    vols = [statistics.stdev(column) * math.sqrt(12) for column in columns]
    if any(v <= 0 for v in vols):
        raise ValueError("Each asset needs nonzero historical volatility.")
    correlations = [[max(-1.0, min(1.0, statistics.correlation(a, b)))
                     for b in columns] for a in columns]
    return {"assets": tickers, "returns": returns, "volatilities": vols,
            "correlations": correlations, "months": len(monthly),
            "first_return_month": used_dates[0].isoformat(),
            "last_return_month": used_dates[-1].isoformat()}


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
