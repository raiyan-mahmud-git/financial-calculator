"""Retirement wealth planning view with inflation adjustments and contribution growth."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from fincalc.core import retirement_projection
from fincalc.errors import FinCalcError
from ui.charts import create_donut_chart, create_retirement_chart
from ui.components import (
    format_curr,
    formula_expander,
    get_query_param_float,
    get_query_param_int,
    render_error,
    sync_query_params,
)


def show_retirement() -> None:
    """Render the Retirement Wealth Planner page."""
    st.title("📈 Retirement Investment Planner")
    st.markdown(
        "Model your wealth accumulation trajectory over time with realistic parameters: "
        "annual career contribution increases and inflation-adjusted purchasing power."
    )

    tab_calc, tab_compare = st.tabs(["📊 Portfolio Planner", "⚖️ Compare Strategies"])

    with tab_calc:
        # Default query params
        default_start = get_query_param_float("start", 10000.0)
        default_monthly = get_query_param_float("monthly", 500.0)
        default_rate = get_query_param_float("rate", 7.0)
        default_years = get_query_param_int("years", 30)
        default_increase = get_query_param_float("increase", 2.0)
        default_inflation = get_query_param_float("inflation", 2.5)

        with st.form("retirement_form"):
            col1, col2 = st.columns(2)
            with col1:
                starting_balance = st.number_input(
                    "Current Nest Egg (Starting Balance)",
                    min_value=0.0,
                    max_value=10000000.0,
                    value=float(default_start),
                    step=1000.0,
                    help="Money already saved or invested today.",
                )
                monthly_contribution = st.number_input(
                    "Initial Monthly Contribution",
                    min_value=0.0,
                    max_value=100000.0,
                    value=float(default_monthly),
                    step=50.0,
                    help="Amount you invest each month.",
                )
                annual_rate_pct = st.number_input(
                    "Expected Annual Investment Return (%)",
                    min_value=0.0,
                    max_value=30.0,
                    value=float(default_rate),
                    step=0.25,
                    format="%.2f",
                    help="Expected average annual nominal return (e.g., 7% for S&P 500 average).",
                )

            with col2:
                years = st.number_input(
                    "Investment Horizon (Years)",
                    min_value=1,
                    max_value=60,
                    value=int(default_years),
                    step=1,
                    help="Years until retirement.",
                )
                annual_increase_pct = st.number_input(
                    "Annual Contribution Growth (%)",
                    min_value=0.0,
                    max_value=20.0,
                    value=float(default_increase),
                    step=0.5,
                    format="%.2f",
                    help="Percentage you increase your monthly savings each year as your income grows.",
                )
                inflation_rate_pct = st.number_input(
                    "Expected Annual Inflation Rate (%)",
                    min_value=0.0,
                    max_value=15.0,
                    value=float(default_inflation),
                    step=0.25,
                    format="%.2f",
                    help="Used to calculate future purchasing power in today's dollars.",
                )

            st.form_submit_button("Simulate Wealth Growth", type="primary")

        sync_query_params(
            start=starting_balance,
            monthly=monthly_contribution,
            rate=annual_rate_pct,
            years=years,
            increase=annual_increase_pct,
            inflation=inflation_rate_pct,
        )

        try:
            res = retirement_projection(
                starting_balance=starting_balance,
                monthly_contribution=monthly_contribution,
                annual_rate=annual_rate_pct / 100.0,
                years=int(years),
                annual_contribution_increase=annual_increase_pct / 100.0,
                inflation_rate=inflation_rate_pct / 100.0,
            )

            st.divider()
            st.subheader("Retirement Milestones")

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric(
                    "Final Nominal Wealth",
                    format_curr(res.final_nominal_balance),
                    help="Total account balance at retirement before inflation adjustment.",
                )
            with m2:
                st.metric(
                    "Real Purchasing Power",
                    format_curr(res.final_real_balance),
                    help="What your nest egg will feel like in terms of today's dollars.",
                )
            with m3:
                st.metric(
                    "Your Out-of-Pocket Deposits",
                    format_curr(res.total_contributions),
                    help="Total principal invested by you.",
                )
            with m4:
                st.metric(
                    "Compound Growth Earned",
                    format_curr(res.total_interest),
                    help="Free money generated by compound returns.",
                )

            # Charts
            st.subheader("Visual Growth Projections")
            c1, c2 = st.columns([2, 1])

            df_sched = pd.DataFrame([vars(r) for r in res.schedule])

            with c1:
                st.plotly_chart(create_retirement_chart(df_sched), use_container_width=True)

            with c2:
                donut = create_donut_chart(
                    labels=["Your Contributions", "Investment Growth"],
                    values=[res.total_contributions, res.total_interest],
                    title="Wealth Source Breakdown",
                    colors=["#94A3B8", "#10B981"],
                )
                st.plotly_chart(donut, use_container_width=True)

            # Year-by-Year Table
            st.subheader("Year-by-Year Wealth Progression")
            disp_df = df_sched[
                [
                    "year",
                    "starting_balance",
                    "annual_contributions",
                    "annual_interest",
                    "ending_nominal_balance",
                    "ending_real_balance",
                ]
            ].copy()
            disp_df.columns = [
                "Year",
                "Start Balance",
                "Deposits",
                "Interest Earned",
                "Ending Balance (Nominal)",
                "Ending Balance (Real)",
            ]

            st.dataframe(
                disp_df.style.format(
                    {
                        "Start Balance": "{:,.2f}",
                        "Deposits": "{:,.2f}",
                        "Interest Earned": "{:,.2f}",
                        "Ending Balance (Nominal)": "{:,.2f}",
                        "Ending Balance (Real)": "{:,.2f}",
                    }
                ),
                use_container_width=True,
                height=350,
            )

        except FinCalcError as err:
            render_error(err)

    with tab_compare:
        st.subheader("Compare Conservative vs Aggressive Asset Allocations")
        c_col1, c_col2 = st.columns(2)

        with c_col1:
            st.markdown("#### Portfolio A: Conservative (Bonds / Fixed Income)")
            start_a = st.number_input("Start Balance A", value=10000.0, step=1000.0, key="ret_sa")
            dep_a = st.number_input("Monthly Contribution A", value=500.0, step=50.0, key="ret_da")
            ret_a = st.number_input("Return A (%)", value=4.5, step=0.25, key="ret_ra")
            yr_a = st.number_input("Years A", value=30, step=1, key="ret_ya")

        with c_col2:
            st.markdown("#### Portfolio B: Growth / Equities (Index Funds)")
            start_b = st.number_input("Start Balance B", value=10000.0, step=1000.0, key="ret_sb")
            dep_b = st.number_input("Monthly Contribution B", value=500.0, step=50.0, key="ret_db")
            ret_b = st.number_input("Return B (%)", value=8.5, step=0.25, key="ret_rb")
            yr_b = st.number_input("Years B", value=30, step=1, key="ret_yb")

        res_a = retirement_projection(
            start_a, dep_a, ret_a / 100.0, int(yr_a), inflation_rate=0.025
        )
        res_b = retirement_projection(
            start_b, dep_b, ret_b / 100.0, int(yr_b), inflation_rate=0.025
        )

        st.divider()
        out1, out2 = st.columns(2)
        with out1:
            st.info("📌 **Conservative Portfolio (4.5%)**")
            st.write(f"Nominal Ending Balance: **{format_curr(res_a.final_nominal_balance)}**")
            st.write(f"Real Purchasing Power: **{format_curr(res_a.final_real_balance)}**")
            st.write(f"Compound Growth: **{format_curr(res_a.total_interest)}**")

        with out2:
            st.info("📌 **Growth Portfolio (8.5%)**")
            st.write(f"Nominal Ending Balance: **{format_curr(res_b.final_nominal_balance)}**")
            st.write(f"Real Purchasing Power: **{format_curr(res_b.final_real_balance)}**")
            st.write(f"Compound Growth: **{format_curr(res_b.total_interest)}**")

        diff = res_b.final_nominal_balance - res_a.final_nominal_balance
        st.success(
            f"🚀 **The Growth Portfolio generates {format_curr(diff)} more wealth "
            f"({diff / res_a.final_nominal_balance * 100:.1f}% higher!)**"
        )

    formula_expander(
        title="Retirement Accumulation & Purchasing Power",
        latex_formula=r"\text{Real Balance}_y = \frac{\text{Nominal Balance}_y}{(1 + r_{\text{inflation}})^y}",
        explanation=(
            "- **Monthly Deposits**: Added each month, earning compounding interest.\n"
            "- **Contribution Escalation**: Monthly savings increase each year by $g$ ($C_y = C_0(1+g)^{y-1}$).\n"
            "- **Real Purchasing Power**: Future nominal dollars lose purchasing power due to inflation; "
            "this discount formula gives true equivalent value in today's currency."
        ),
    )


if __name__ == "__main__":
    show_retirement()
