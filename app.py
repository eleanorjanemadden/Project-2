"""Run: python3 -m streamlit run app.py."""
import hashlib
import importlib
import io
from pathlib import Path
import streamlit as st
import mandate
import portfolio

# Reload the engine so a browser rerun picks up saved training-input changes.
importlib.reload(portfolio)

def show_portfolio_comparison(current, estimates, eligible, objective, minimum,
                              constrained, is_training):
    assets = current["assets"]
    covariance = portfolio.covariance_matrix(current["volatilities"], current["correlations"])
    equal = portfolio.equal_weights(len(assets))
    inverse = portfolio.inverse_volatility_weights(current["volatilities"])
    labels = [
        *(f"{asset} weight" for asset in assets),
        "Estimated annual return", "Estimated annual volatility", "Reserve-eligible weight",
        "Fully invested (100%)", "Long-only weights",
        f"Numerical return screen (≥ {objective:.2%})",
        f"Reserve allocation (≥ {minimum:.2%})",
        "Project 2 universe (BIL, IEF, LQD, VT)",
        f"Liquidity (≥ {mandate.MINIMUM_LIQUID_SHARE}% within "
        f"{mandate.LIQUIDITY_WINDOW} business days)",
        f"Company issuer limit (≤ {mandate.ISSUER_LIMIT}%, subject to exemptions)",
        "Live borrowing, short sales and derivatives restrictions",
        "Rolling five-year net return objective (CPI + 4%)",
    ]
    comparison = {"Measure or rule": labels}
    unresolved = "Unresolved"
    allowed_assets = {"BIL", "IEF", "LQD", "VT"}
    tolerance = 1e-12

    for name, weights in (
        ("Equal-weight baseline", equal),
        ("Inverse-volatility baseline", inverse),
        ("Constrained portfolio", None if constrained is None else constrained["weights"]),
    ):
        if weights is None:
            comparison[name] = ["N/A"] * len(labels)
            continue
        estimate = portfolio.expected_return(weights, estimates)
        reserve = portfolio.reserve_weight(weights, eligible)
        volatility = portfolio.portfolio_volatility(weights, covariance)
        checks = [
            abs(sum(weights) - 1) <= tolerance,
            min(weights) >= -tolerance,
            estimate >= objective - tolerance,
            reserve >= minimum - tolerance,
            all(asset in allowed_assets for asset, weight in zip(assets, weights)
                if weight > tolerance),
        ]
        verdicts = ["Pass" if passed else "Fail" for passed in checks]
        if is_training:
            verdicts[-1] = unresolved
        comparison[name] = [
            *(f"{weight:.2%}" for weight in weights),
            f"{estimate:.2%}", f"{volatility:.2%}", f"{reserve:.2%}",
            *verdicts, *([unresolved] * 4),
        ]

    st.subheader("Portfolio comparison — selected inputs")
    st.caption("All three use the selected window, current return estimates, covariance, "
               "reserve eligibility and thresholds. The two baselines keep their formula "
               "weights even when they fail a rule.")
    st.dataframe(comparison, hide_index=True, row_height=34, height=34 * (len(labels) + 1) + 3)
    if constrained is None:
        st.info("The constrained comparison has no feasible mix on the five-point grid.")
    st.caption("The universe check flags any positive weight outside the draft ETF list, "
               "using the ticker labels supplied in the data. "
               "Meridian uses course training sleeves. The reserve check uses the selected "
               "eligibility assumptions. Actual redemption terms, issuer exposures and "
               "exemptions, and live implementation restrictions require separate verification.")
    st.caption("The return screen compares an annual estimate with a numerical threshold. "
               "The rolling five-year net CPI + 4% objective remains unresolved. The model "
               "does not evaluate rolling net outcomes with realized inflation and costs.")


st.set_page_config(page_title="Portfolio stability", layout="wide")
st.title("Portfolio stability")
st.caption("Built with AI help, a learning demonstration, not investment advice.")
objective = st.sidebar.number_input("Objective (%)", value=6.5, step=0.1) / 100
minimum = st.sidebar.number_input("Reserve minimum (%)", min_value=0.0,
                                  max_value=100.0, value=3.0, step=1.0) / 100
upload = st.sidebar.file_uploader("Upload prices.csv", type="csv")
bundled = st.sidebar.checkbox("Use included Project 2 prices.csv", value=True)
last_36 = st.sidebar.checkbox("Last 36 months", value=False)

try:
    raw = upload.getvalue() if upload is not None else (
        Path(__file__).with_name("prices.csv").read_bytes() if bundled else None)
    if raw is None:
        loaded = {"assets": portfolio.SLEEVES, "returns": portfolio.RETURNS,
                  "volatilities": portfolio.VOLATILITIES,
                  "correlations": portfolio.CORRELATIONS}
        current = loaded
        default_eligible = portfolio.RESERVE_ELIGIBLE
        dataset = "meridian"
        st.write("Meridian — annual course-authored training values")
        if last_36:
            st.info("The 36-month switch applies to CSV prices; Meridian has fixed training inputs.")
    else:
        text = raw.decode("utf-8-sig")
        loaded = portfolio.estimate_from_csv(io.StringIO(text))
        current = portfolio.estimate_from_csv(io.StringIO(text), last_36=last_36)
        default_eligible = [ticker in {"BIL", "IEF"} for ticker in loaded["assets"]]
        dataset = hashlib.sha256(raw).hexdigest()[:12]
        st.write(f"Monthly-price estimates — {current['months']} monthly returns, "
                 f"{current['first_return_month']} through {current['last_return_month']}")
        st.caption("Historical arithmetic estimates, not forecasts. BIL and IEF count for the "
                   "draft mandate; review reserve eligibility for other uploads.")
    st.subheader("Edit annual expected returns and reserve eligibility")
    estimates, eligible = [], []
    for index, asset in enumerate(current["assets"]):
        left, right = st.columns([3, 2])
        # A different window gets its own controls initialized to that window's estimates.
        estimates.append(left.number_input(f"{asset} return estimate (%)",
                         value=current["returns"][index] * 100, step=0.1,
                         key=f"return_{dataset}_{last_36}_{index}") / 100)
        eligible.append(right.checkbox(f"{asset} reserve-eligible",
                        value=default_eligible[index], key=f"reserve_{dataset}_{index}"))

    as_loaded = portfolio.search_portfolio(loaded["returns"], loaded["volatilities"],
               loaded["correlations"], objective, default_eligible, minimum)
    answer = portfolio.search_portfolio(estimates, current["volatilities"],
             current["correlations"], objective, eligible, minimum)

    show_portfolio_comparison(current, estimates, eligible, objective, minimum, answer,
                              is_training=raw is None)

    st.subheader("Sensitivity — as loaded versus current inputs")

    def display_result(title, result):
        st.markdown(f"**{title}**")
        if result is None:
            st.warning("no mix meets the objective")
            return
        st.table({"Asset": loaded["assets"],
                  "Weight (%)": [f"{w * 100:.2f}" for w in result["weights"]]})
        st.write(f"Expected return estimate: {result['return']:.2%}")
        st.write(f"Annual volatility: {result['volatility']:.2%}")
        st.write(f"Reserve-eligible weight: {result['reserve']:.2%}")

    left, right = st.columns(2)
    with left:
        display_result("Current lowest-risk mix", answer)
    with right:
        display_result("As loaded — all months" if raw is not None else
                       "As loaded — Meridian training inputs", as_loaded)
    st.caption("Both searches use the current sidebar objective and minimum. As loaded keeps "
               "the original returns, risk estimates and default eligibility.")
    if answer is not None and as_loaded is not None:
        change = max(abs(a-b) for a, b in zip(answer["weights"], as_loaded["weights"])) * 100
        st.metric("Largest weight change (percentage points)", f"{change:.2f}")
    else:
        st.info("Largest weight change: N/A when either search has no feasible mix.")
    st.caption("The constrained search minimizes estimated volatility on a five-percentage-point "
               "grid of fully invested, long-only mixes that clear the return and reserve screens. "
               "Losses remain possible.")
except (ValueError, UnicodeError, OSError) as error:
    st.error(f"Input error: {error}")
