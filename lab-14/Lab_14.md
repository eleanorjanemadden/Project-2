# Lab 14 — Portfolio Baselines

Eleanor Madden | October 20, 2026

## Explain to your partner first

Why can two risky assets together be less risky than either alone? 

This is because of diversification. When you combine the variances of 2 risky assets, it mathematically equates to overall less risk through creating a portfolio. If one goes up, the other might go down and the inverse is true. This action decreases overall volatility.  

## Define

What does each simple portfolio earn and risk — and does any of them meet the Meridian mandate?

None of the three baselines meets both the expected-return objective and reserve requirement. The benchmark earns enough on the training assumptions but has no eligible reserve. Equal weight and inverse volatility hold enough reserve assets but fall below the return objective. These results do not establish future returns or compliance with the unresolved calendar-year loss rule.

## Represent

These are annual **course-authored training values**, not market estimates. Returns and volatilities enter `portfolio.py` as decimals.

| Sleeve | Expected return | Volatility | Reserve-eligible? |
|---|---:|---:|---|
| Treasury bills | 3.5% | 0.5% | Yes |
| Treasury 10-year note | 4.3% | 7.0% | Yes |
| Investment-grade bond fund | 5.0% | 6.0% | No |
| Global equity index fund | 8.0% | 16.0% | No |

| Correlation | Bills | 10-year | IG bonds | Equity |
|---|---:|---:|---:|---:|
| Bills | 1.00 | 0.10 | 0.05 | 0.00 |
| 10-year | 0.10 | 1.00 | 0.80 | -0.10 |
| IG bonds | 0.05 | 0.80 | 1.00 | 0.25 |
| Equity | 0.00 | -0.10 | 0.25 | 1.00 |

The objective is CPI + 4% = **6.5%**, using a **2.5% CPI estimate**. The reserve minimum is four quarterly payouts of $0.75 million divided by $100 million, or **3%**. Training bills and the 10-year note qualify under Lab 13's rules. The objective is net of costs in the mandate; the exercise supplies no separate fee estimate, so meeting 6.5% here is an expected-return screen rather than proof of the rolling five-year net objective.

## Implement and run

python3 portfolio.py
python3 mandate.py
python3 validate.py
```

`portfolio.py` uses only the standard library. Its editable inputs are at the top, and calculations are separate importable functions. Inverse volatility divides each reciprocal volatility by the sum of all reciprocals. The engine forms covariance as correlation × volatility × volatility, then computes variance using all ordered sleeve pairs and takes its square root. It refuses out-of-range or asymmetric correlations before printing results.

The updated `mandate.py` copies my Lab 13 checker and adds candidate E. Candidates A–D and their rules are preserved; my original Lab 13 folder is unchanged. The local original checker matches the supplied GitHub repository's checker.

## Validate

| Portfolio | Weights: bills / 10-year / IG / equity (%) | Return | Volatility | Reserve-eligible | Meets 6.5%? |
|---|---|---:|---:|---:|---|
| Benchmark | 0.0 / 0.0 / 40.0 / 60.0 | 6.80% | 10.46% | 0.0% | Yes |
| Equal weight | 25.0 / 25.0 / 25.0 / 25.0 | 5.20% | 5.21% | 50.0% | No |
| Inverse volatility | 84.3 / 6.0 / 7.0 / 2.6 | 3.77% | 1.05% | 90.3% | No |

Every displayed value matches the lab's known answer. Inverse-volatility weights are calculated at full precision; the displayed weights sum to 99.9% because of rounding.

Executed evidence:

- [Original Lab 13 rerun](outputs/lab13_original_run.txt): A and D pass all implemented rules; B fails reserve, liquidity, and issuer limits; C fails reserve.
- [Baseline run](outputs/portfolio_run.txt): the three results above.
- [Mandate run](outputs/mandate_run.txt): E has 0.0% reserve, fails the 3% reserve rule, and passes the other implemented checks.
- [Validation run](outputs/validation_run.txt): all known values, symmetric 0.50 stress, 1.3 rejection, asymmetric-table rejection, restored inputs, E's failure, and price-file completeness.

`validate.py` creates temporary copies of the actual script and executes each changed version. At IG–equity correlation 0.50 in both cells, benchmark volatility rises to **11.00%**. At 1.3, the script exits unsuccessfully with a clear range error. Changing only one cell produces the symmetry error. The submitted script remains at 0.25.

The benchmark is not automatically suitable just because the client selected it for performance comparison. S4 is a benchmark, while S3 is a separate reserve constraint. Volatility also does not guarantee that calendar-year losses stay below 10%. Horizon, realized net returns, annual rebalancing, turnover, and S9 require information or clarification beyond this holdings checker.

## Diversification and calculation by hand

Diversification spreads investments across exposures that do not move exactly together. A correlation below +1 lowers the covariance term relative to perfect positive correlation, so some movements can offset. It can reduce issuer-specific risk, but shared market risks remain, and correlations can rise during stress.

For the benchmark:

- Expected return = 0.40 × 0.05 + 0.60 × 0.08 = 0.068 = **6.80%**.
- Bond–equity covariance = 0.25 × 0.06 × 0.16 = **0.0024**.
- Variance = (0.40² × 0.06²) + (0.60² × 0.16²) + (2 × 0.40 × 0.60 × 0.0024).
- Variance = 0.000576 + 0.009216 + 0.001152 = **0.010944**.
- Volatility = √0.010944 = 0.1046136 = **10.46%**.

If correlation were +1, volatility would be 0.40 × 6% + 0.60 × 16% = **12.00%**. The actual 10.46% is below that value and below equity's 16%, but above bonds' 6%. Two risky assets *can* be less risky together than either alone, depending on their weights and covariance; this benchmark is not an example of being below both. Omitting covariance gives √0.009792 = **9.90%**, which is incorrect here. At correlation 0.50, covariance is 0.0048 and variance is 0.012096, giving **11.00%** volatility.

## Explain the code — discussion preparation

The key block is `portfolio_variance`, followed by `portfolio_volatility`:

1. `range(len(weights))` visits each sleeve as `i` and each sleeve as `j`.
2. `weights[i] * weights[j] * covariance[i][j]` scales the covariance by both allocations.
3. `sum(...)` adds every ordered pair. Diagonal terms are each sleeve's own weighted variance. Off-diagonal terms appear twice, once in each order.
4. `portfolio_volatility` checks for negative variance, allows only tiny floating-point rounding at zero, and takes the square root to convert variance to volatility.

AI quiz for review: **Why does the code have no explicit factor of 2?**

Answer: The nested loops already include both the bonds–equity and equity–bonds terms. Multiplying the total by 2 would count them again.

Explanation to check after answering: Because the table is symmetric, the two off-diagonal contributions are equal. Adding both is equivalent to the two-asset formula's `2*w1*w2*covariance` term.

Partner question: **If the equity weight is zero, does equity still add risk through its correlations?** 
Answer: No. Every term involving equity contains its zero weight and contributes zero.


## Reflect — draft responses to revisit

**Why does inverse volatility pile into bills?** Bills have a volatility of only 0.5%, so their reciprocal volatility is 200. The other reciprocals are about 14.29, 16.67, and 6.25. Bills therefore receive 200 / 237.20, or about 84.3%. This method responds to standalone volatility rather than the return objective or the full correlation structure. Low volatility alone does not make the allocation right for Meridian.

**Which baseline would I show the CIO first?** I would show the benchmark first because it is already the client's reference point. It clears the expected-return screen but fails the reserve rule. That gives us a practical starting point for explaining why the actual portfolio needs to differ from the benchmark. I would show the other two next to make the return-versus-risk tradeoff clear, without lowering the objective to make them pass.

