"""Run: python3 -m streamlit run app.py."""
import hashlib
import importlib
import io
from pathlib import Path
import streamlit as st
import gs10
import mandate
import portfolio

# Reload the engine so a browser rerun picks up saved training-input changes.
importlib.reload(portfolio)

def portfolio_comparison(current, estimates, eligible, objective, minimum,
                         constrained, is_training, additional_cost):
    assets = current["assets"]
    covariance = portfolio.covariance_matrix(current["volatilities"], current["correlations"])
    equal = portfolio.equal_weights(len(assets))
    inverse = portfolio.inverse_volatility_weights(current["volatilities"])
    labels = [
        *(f"{asset} weight" for asset in assets),
        "Annual return before additional cost", "Annual return after additional cost",
        "Estimated annual volatility", "Reserve-eligible weight",
        "Fully invested (100%)", "Long-only weights",
        f"After-cost return screen (≥ {objective:.2%})",
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
        after_cost = estimate - additional_cost
        reserve = portfolio.reserve_weight(weights, eligible)
        volatility = portfolio.portfolio_volatility(weights, covariance)
        checks = [
            abs(sum(weights) - 1) <= tolerance,
            min(weights) >= -tolerance,
            after_cost >= objective - tolerance,
            reserve >= minimum - tolerance,
            all(asset in allowed_assets for asset, weight in zip(assets, weights)
                if weight > tolerance),
        ]
        verdicts = ["Pass" if passed else "Fail" for passed in checks]
        if is_training:
            verdicts[-1] = unresolved
        comparison[name] = [
            *(f"{weight:.2%}" for weight in weights),
            f"{estimate:.2%}", f"{after_cost:.2%}", f"{volatility:.2%}", f"{reserve:.2%}",
            *verdicts, *([unresolved] * 4),
        ]

    return comparison


def show_portfolio_comparison(comparison, constrained, objective, cost_bps):
    st.subheader("Portfolio comparison — selected inputs")
    st.caption(f"Annual additional cost assumption: {cost_bps:g} bps. Enter only costs beyond "
               "fund expenses already reflected in adjusted-price returns.")
    st.caption("All three use the selected window, current return estimates, covariance, "
               "reserve eligibility, additional cost and thresholds. The two baselines keep their formula "
               "weights even when they fail a rule.")
    st.dataframe(comparison, hide_index=True, row_height=34,
                 height=34 * (len(comparison["Measure or rule"]) + 1) + 3)
    if constrained is None:
        st.error(f"No constrained mix meets the {objective:.2%} after-cost screen "
                 "and reserve minimum on the five-point grid. Stop the paper pilot "
                 "and return to committee under the agreed settings.")
    st.caption("The universe check flags any positive weight outside the draft ETF list, "
               "using the ticker labels supplied in the data. "
               "Meridian uses course training sleeves. The reserve check uses the selected "
               "eligibility assumptions. Actual redemption terms, issuer exposures and "
               "exemptions, and live implementation restrictions require separate verification.")
    st.caption("The return screen compares an after-cost annual estimate with a numerical threshold. "
               "The rolling five-year net CPI + 4% objective remains unresolved. The model "
               "does not evaluate rolling net outcomes with realized inflation and costs.")


def show_gs10_monitor():
    st.subheader("GS10 point-in-time monitoring")
    st.caption("Monitoring only. The monthly 10-year Treasury yield gives context for "
               "interest-rate exposure in IEF and LQD. It does not enter the ETF return "
               "estimates, mandate screens or allocation search. This cutoff applies only to GS10.")
    try:
        vintages = gs10.saved_vintages()
        if not vintages:
            st.warning("GS10 is unresolved because no dated vintage is recorded.")
            return
        cutoff = st.selectbox("Decision cutoff (saved vintage date)", sorted(vintages))
        record = vintages[cutoff]
        observations = gs10.read_vintage(cutoff)
        if not observations:
            st.warning("GS10 is unresolved because the saved vintage has no usable observation.")
            return
        latest = max(observations)
    except (OSError, ValueError, ArithmeticError, KeyError) as error:
        st.warning(f"GS10 is unresolved because the saved evidence could not be read: {error}")
        return

    st.markdown(f"**Decision cutoff:** {cutoff}  \n"
                f"**Latest observation in the cutoff vintage:** {latest:%B %Y}  \n"
                f"**Signal value:** {observations[latest]:.2f}% per annum "
                "(monthly average, not seasonally adjusted)  \n"
                f"**ALFRED vintage date:** {cutoff}")
    evidence_url = ("https://github.com/eleanorjanemadden/Project-2/blob/main/"
                    "evidence/lab-17/")
    st.markdown("Source: Federal Reserve Board, H.15 Selected Interest Rates, "
                f"via [ALFRED vintage download]({record['url']}). "
                f"[Bundled GS10 data card]({evidence_url}Lab_17.md#r--represent-my-data-card) · "
                f"[Download manifest]({evidence_url}data/download_manifest.json)")
    st.caption("The observation month identifies the period measured. The dated ALFRED "
               "snapshot establishes availability at date level, and contains the version "
               "used here. Later releases and revisions are kept separate, and missing "
               "values are skipped without filling. For a decision at the opening, use "
               "the prior calendar day's vintage or verify the publication timestamp "
               "before trading. Same-day pre-trade availability is unresolved.")


st.set_page_config(page_title="Portfolio stability", layout="wide")
st.title("Portfolio stability")
st.caption("Built with AI help, a learning demonstration, not investment advice.")
st.subheader("Paper-pilot decision and stop condition")
st.write("Stop the paper pilot and return to committee if the agreed reserve rule or "
         "after-cost return screen becomes infeasible. A weight shift above five percentage "
         "points keeps live adoption deferred.")
st.caption("Bundled snapshot, zero-additional-cost reference: 60% BIL / 40% VT. "
           "Original window and return stresses: 55–85% BIL, 15–45% VT, and 0% IEF/LQD. "
           "Illustrative cost stresses across both windows: 45–85% BIL, 15–55% VT, "
           "0% IEF, and 0–5% LQD.")
objective = st.sidebar.number_input("Objective (%)", value=6.5, step=0.1) / 100
minimum = st.sidebar.number_input("Reserve minimum (%)", min_value=0.0,
                                  max_value=100.0, value=3.0, step=1.0) / 100
cost_bps = st.sidebar.number_input(
    "Annual additional cost assumption (bps)", min_value=0.0, value=0.0, step=5.0,
    help="Illustrative portfolio-level costs such as trading or advisory fees. Include only "
         "costs beyond fund expenses already reflected in adjusted-price returns.",
)
additional_cost = cost_bps / 10_000
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
    st.subheader("Edit annual returns before additional cost and reserve eligibility")
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
               loaded["correlations"], objective, default_eligible, minimum,
               additional_cost=additional_cost)
    def search_current(cost):
        return portfolio.search_portfolio(estimates, current["volatilities"],
                                          current["correlations"], objective, eligible, minimum,
                                          additional_cost=cost)

    answer = search_current(additional_cost)
    comparison = portfolio_comparison(current, estimates, eligible, objective, minimum,
                                      answer, raw is None, additional_cost)
    show_portfolio_comparison(comparison, answer, objective, cost_bps)

    with st.expander("Illustrative annual cost stress — 0, 25, 50, and 100 bps"):
        st.caption("These scenarios use the current inputs and fixed cost assumptions. "
                   "Actual costs require separate evidence. The constrained search reruns at "
                   "each cost, with the same numerical threshold and reserve minimum.")
        scenarios = []
        for bps in (0, 25, 50, 100):
            cost = bps / 10_000
            solution = answer if cost == additional_cost else search_current(cost)
            stress = portfolio_comparison(current, estimates, eligible, objective, minimum,
                                          solution, raw is None, cost)
            measures = stress.pop("Measure or rule")
            for name, values in stress.items():
                row = dict(zip(measures, values))
                no_mix = name == "Constrained portfolio" and solution is None
                scenarios.append({
                    "Annual cost (bps)": bps,
                    "Portfolio": name,
                    "Weights": "No feasible mix" if no_mix else ", ".join(
                        f"{asset} {row[f'{asset} weight']}" for asset in current["assets"]),
                    "Return before cost": row["Annual return before additional cost"],
                    "Return after cost": row["Annual return after additional cost"],
                    "Volatility": row["Estimated annual volatility"],
                    "Reserve weight": row["Reserve-eligible weight"],
                    "After-cost screen": "Infeasible" if no_mix else
                    row[f"After-cost return screen (≥ {objective:.2%})"],
                })
        st.dataframe(scenarios, hide_index=True)

    st.subheader("Sensitivity — as loaded versus current inputs")

    def display_result(title, result):
        st.markdown(f"**{title}**")
        if result is None:
            st.warning(f"No mix meets the {objective:.2%} after-cost screen and reserve minimum.")
            return
        st.table({"Asset": loaded["assets"],
                  "Weight (%)": [f"{w * 100:.2f}" for w in result["weights"]]})
        st.write(f"Annual return before additional cost: {result['return']:.2%}")
        st.write(f"Annual return after additional cost: {result['return'] - additional_cost:.2%}")
        st.write(f"Annual volatility: {result['volatility']:.2%}")
        st.write(f"Reserve-eligible weight: {result['reserve']:.2%}")

    left, right = st.columns(2)
    with left:
        display_result("Current lowest-risk mix", answer)
    with right:
        display_result("As loaded — all months" if raw is not None else
                       "As loaded — Meridian training inputs", as_loaded)
    st.caption("Both searches use the current sidebar objective, reserve minimum, and additional cost. "
               "As loaded keeps "
               "the original returns, risk estimates and default eligibility.")
    if answer is not None and as_loaded is not None:
        change = max(abs(a-b) for a, b in zip(answer["weights"], as_loaded["weights"])) * 100
        st.metric("Largest weight change (percentage points)", f"{change:.2f}")
    else:
        st.info("Largest weight change: N/A when either search has no feasible mix.")
    st.caption("The constrained search minimizes estimated volatility on a five-percentage-point "
               "grid of fully invested, long-only mixes that clear the after-cost return and reserve screens. "
               "Losses remain possible.")
except (ValueError, UnicodeError, OSError) as error:
    st.error(f"Input error: {error}")


show_gs10_monitor()
