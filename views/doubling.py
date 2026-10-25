"""Doubling time and time-to-target financial milestones view."""

from __future__ import annotations

import streamlit as st

from fincalc.core import doubling_time, time_to_reach_target
from fincalc.errors import FinCalcError
from ui.components import (
    format_curr,
    formula_expander,
    get_query_param_float,
    render_error,
    sync_query_params,
)


def show_doubling() -> None:
    """Render the Doubling Time & Milestone Calculator page."""
    st.title("⏱️ Doubling Time & Financial Goals")
    st.markdown(
        "Determine how long it takes for your investment to double in purchasing power or grow "
        "to a specific financial target."
    )

    tab_double, tab_target = st.tabs(["2️⃣ Doubling Time", "🎯 Target Accumulation Time"])

    with tab_double:
        st.subheader("How Long to Double Your Money?")
        def_rate = get_query_param_float("double_r", 7.0)

        rate_pct = st.number_input(
            "Annual Rate of Return (%)",
            min_value=0.1,
            max_value=100.0,
            value=float(def_rate),
            step=0.25,
            format="%.2f",
            key="input_double_rate",
            help="Expected annual rate of return.",
        )

        sync_query_params(double_r=rate_pct)

        try:
            r = rate_pct / 100.0
            t_cont = doubling_time(r, method="continuous")
            t_annual = doubling_time(r, method="annual")
            t_rule72 = doubling_time(r, method="rule_of_72")

            st.divider()
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Continuous Compounding", f"{t_cont:.2f} Years", help="Exact: ln(2) / r")
            with m2:
                st.metric(
                    "Annual Compounding", f"{t_annual:.2f} Years", help="Exact: ln(2) / ln(1+r)"
                )
            with m3:
                st.metric(
                    "Rule of 72 Approximation",
                    f"{t_rule72:.2f} Years",
                    help="Shortcut: 72 / (r*100)",
                )

            st.info(
                f"At a **{rate_pct:.2f}%** return, your money will double in approximately "
                f"**{t_annual:.1f} years** (or **{t_annual * 12:.0f} months**)."
            )

        except FinCalcError as err:
            render_error(err)

    with tab_target:
        st.subheader("Time Required to Reach a Specific Target")
        tc1, tc2 = st.columns(2)

        with tc1:
            curr_p = st.number_input(
                "Starting Principal", min_value=100.0, value=10000.0, step=1000.0, key="targ_p"
            )
            target_goal = st.number_input(
                "Target Amount", min_value=100.0, value=50000.0, step=5000.0, key="targ_goal"
            )

        with tc2:
            target_r = st.number_input(
                "Growth Rate (%)", min_value=0.1, value=8.0, step=0.25, key="targ_r"
            )
            is_cont = st.checkbox("Use Continuous Compounding", value=False, key="targ_cont")

        try:
            needed_years = time_to_reach_target(
                principal=curr_p,
                target=target_goal,
                annual_rate=target_r / 100.0,
                continuous=is_cont,
            )
            st.divider()
            st.success(
                f"🎯 Growing from **{format_curr(curr_p)}** to **{format_curr(target_goal)}** at "
                f"**{target_r:.2f}%** requires **{needed_years:.2f} years** ({needed_years * 12:.0f} months)."
            )

        except FinCalcError as err:
            render_error(err)

    formula_expander(
        title="Doubling Time & Rule of 72",
        latex_formula=r"t_{\text{cont}} = \frac{\ln(2)}{r}, \quad t_{\text{discrete}} = \frac{\ln(2)}{\ln(1 + r)}, \quad t_{\text{Rule 72}} \approx \frac{72}{r \times 100}",
        explanation=(
            "- **Continuous Derivation**: Setting $P e^{rt} = 2P \\implies e^{rt} = 2 \\implies rt = \\ln(2) \\implies t = \\frac{\\ln(2)}{r}$.\n"
            "- **Rule of 72**: A celebrated mental arithmetic rule. Since $\\ln(2) \\approx 0.693$, dividing 72 (which has many integer factors) "
            "by the percentage rate provides a remarkably close estimate for typical interest rates (5% - 12%)."
        ),
    )


if __name__ == "__main__":
    show_doubling()
