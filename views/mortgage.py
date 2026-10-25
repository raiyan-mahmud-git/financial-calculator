"""Mortgage and loan amortization view with extra payment acceleration and scenario comparison."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from fincalc.core import amortization_schedule
from fincalc.errors import FinCalcError
from ui.charts import create_amortization_chart, create_donut_chart
from ui.components import (
    format_curr,
    formula_expander,
    get_query_param_float,
    get_query_param_int,
    render_error,
    sync_query_params,
)


def show_mortgage() -> None:
    """Render the Mortgage & Amortization Calculator page."""
    st.title("🏡 Mortgage & Loan Amortization")
    st.markdown(
        "Calculate monthly mortgage payments, explore full amortization schedules, "
        "and determine how much time and interest you save by making extra monthly principal payments."
    )

    tab_calc, tab_compare = st.tabs(["📊 Loan Calculator", "⚖️ Compare Two Scenarios"])

    with tab_calc:
        # Default values read from query params or sensible standards
        default_principal = get_query_param_float("principal", 200000.0)
        default_rate = get_query_param_float("rate", 6.0)
        default_years = get_query_param_int("years", 30)
        default_extra = get_query_param_float("extra", 100.0)

        with st.form("mortgage_form"):
            col1, col2 = st.columns(2)
            with col1:
                principal = st.number_input(
                    "Loan Principal Amount",
                    min_value=1000.0,
                    max_value=10000000.0,
                    value=float(default_principal),
                    step=5000.0,
                    help="The initial borrowed amount.",
                )
                annual_rate_pct = st.number_input(
                    "Annual Interest Rate (%)",
                    min_value=0.0,
                    max_value=50.0,
                    value=float(default_rate),
                    step=0.125,
                    format="%.3f",
                    help="Annual nominal interest rate (e.g. 6.0 for 6%).",
                )

            with col2:
                years = st.number_input(
                    "Loan Term (Years)",
                    min_value=1,
                    max_value=50,
                    value=int(default_years),
                    step=1,
                    help="Duration of the loan in years (typically 15 or 30).",
                )
                extra_monthly = st.number_input(
                    "Optional Extra Monthly Principal Payment",
                    min_value=0.0,
                    max_value=20000.0,
                    value=float(default_extra),
                    step=50.0,
                    help="Additional principal paid each month to accelerate loan payoff.",
                )

            st.form_submit_button("Calculate Schedule", type="primary")

        # Sync URL query parameters
        sync_query_params(
            principal=principal,
            rate=annual_rate_pct,
            years=years,
            extra=extra_monthly,
        )

        try:
            annual_rate = annual_rate_pct / 100.0
            result = amortization_schedule(
                principal=principal,
                annual_rate=annual_rate,
                years=int(years),
                extra_monthly_payment=extra_monthly,
            )

            st.divider()
            st.subheader("Key Loan Metrics")

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Base Monthly Payment", format_curr(result.base_monthly_payment))
            with m2:
                st.metric("Total Interest Paid", format_curr(result.total_interest))
            with m3:
                st.metric("Total Loan Cost", format_curr(result.total_paid))
            with m4:
                st.metric(
                    "Payoff Time", f"{result.payoff_years:.1f} yrs ({result.payoff_months} mo)"
                )

            if extra_monthly > 0:
                s1, s2 = st.columns(2)
                with s1:
                    st.success(
                        f"🎉 **Total Interest Saved:** **{format_curr(result.interest_saved)}**"
                    )
                with s2:
                    st.success(
                        f"⏳ **Time Saved:** **{result.months_saved} months** "
                        f"({result.months_saved / 12:.1f} years sooner!)"
                    )

            # Visualizations
            st.subheader("Visual Breakdown")
            chart_col1, chart_col2 = st.columns([1, 2])

            with chart_col1:
                donut_fig = create_donut_chart(
                    labels=["Principal", "Total Interest"],
                    values=[result.total_principal, result.total_interest],
                    title="Principal vs Interest Breakdown",
                    colors=["#3B82F6", "#EF4444"],
                )
                st.plotly_chart(donut_fig, use_container_width=True)

            with chart_col2:
                # Convert schedule to pandas DataFrame
                df_schedule = pd.DataFrame([vars(r) for r in result.schedule])
                area_fig = create_amortization_chart(df_schedule)
                st.plotly_chart(area_fig, use_container_width=True)

            # Interactive Schedule Table
            st.subheader("Complete Amortization Schedule")
            display_df = df_schedule[
                [
                    "month",
                    "beginning_balance",
                    "payment",
                    "principal_paid",
                    "interest_paid",
                    "ending_balance",
                ]
            ].copy()
            display_df.columns = [
                "Month",
                "Beginning Balance",
                "Payment",
                "Principal Paid",
                "Interest Paid",
                "Ending Balance",
            ]

            st.dataframe(
                display_df.style.format(
                    {
                        "Beginning Balance": "{:,.2f}",
                        "Payment": "{:,.2f}",
                        "Principal Paid": "{:,.2f}",
                        "Interest Paid": "{:,.2f}",
                        "Ending Balance": "{:,.2f}",
                    }
                ),
                use_container_width=True,
                height=350,
            )

            # Download CSV Button
            csv_data = display_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Amortization Schedule (CSV)",
                data=csv_data,
                file_name=f"amortization_schedule_{int(principal)}_{int(annual_rate_pct)}pct_{years}yr.csv",
                mime="text/csv",
            )

        except FinCalcError as err:
            render_error(err)

    with tab_compare:
        st.subheader("Compare Two Mortgage Scenarios Side-by-Side")
        scol1, scol2 = st.columns(2)

        with scol1:
            st.markdown("#### Scenario A (e.g. 30-Year Fixed)")
            p_a = st.number_input("Principal A", value=200000.0, step=5000.0, key="cmp_pa")
            r_a = st.number_input("Rate A (%)", value=6.5, step=0.125, key="cmp_ra")
            y_a = st.number_input("Term A (Years)", value=30, step=1, key="cmp_ya")
            ext_a = st.number_input("Extra Monthly A", value=0.0, step=50.0, key="cmp_exta")

        with scol2:
            st.markdown("#### Scenario B (e.g. 15-Year Fixed or Refinance)")
            p_b = st.number_input("Principal B", value=200000.0, step=5000.0, key="cmp_pb")
            r_b = st.number_input("Rate B (%)", value=5.5, step=0.125, key="cmp_rb")
            y_b = st.number_input("Term B (Years)", value=15, step=1, key="cmp_yb")
            ext_b = st.number_input("Extra Monthly B", value=0.0, step=50.0, key="cmp_extb")

        res_a = amortization_schedule(p_a, r_a / 100.0, int(y_a), ext_a)
        res_b = amortization_schedule(p_b, r_b / 100.0, int(y_b), ext_b)

        st.divider()
        st.markdown("### Comparison Results")
        cmp_col1, cmp_col2 = st.columns(2)

        with cmp_col1:
            st.info("📌 **Scenario A**")
            st.write(f"Monthly Payment: **{format_curr(res_a.actual_monthly_payment)}**")
            st.write(f"Total Interest: **{format_curr(res_a.total_interest)}**")
            st.write(f"Total Cost: **{format_curr(res_a.total_paid)}**")
            st.write(f"Payoff Duration: **{res_a.payoff_years:.1f} years**")

        with cmp_col2:
            st.info("📌 **Scenario B**")
            st.write(f"Monthly Payment: **{format_curr(res_b.actual_monthly_payment)}**")
            st.write(f"Total Interest: **{format_curr(res_b.total_interest)}**")
            st.write(f"Total Cost: **{format_curr(res_b.total_paid)}**")
            st.write(f"Payoff Duration: **{res_b.payoff_years:.1f} years**")

        interest_diff = res_a.total_interest - res_b.total_interest
        if interest_diff > 0:
            st.success(
                f"💡 **Scenario B saves you {format_curr(interest_diff)} in total interest!**"
            )
        elif interest_diff < 0:
            st.success(
                f"💡 **Scenario A saves you {format_curr(abs(interest_diff))} in total interest!**"
            )

    formula_expander(
        title="Fixed-Rate Mortgage Payment & Amortization",
        latex_formula=r"PMT = P \left[\frac{i(1 + i)^N}{(1 + i)^N - 1}\right]",
        explanation=(
            "- **$P$**: Principal borrowed amount.\n"
            "- **$i$**: Periodic monthly interest rate ($r / 12$).\n"
            "- **$N$**: Total scheduled monthly payments ($12 \\times \\text{years}$).\n"
            "- **Amortization Breakdown**: Each month, interest charged is $\\text{Balance} \\times i$. "
            "The remaining portion of payment goes to principal, reducing the next month's interest."
        ),
    )


if __name__ == "__main__":
    show_mortgage()
