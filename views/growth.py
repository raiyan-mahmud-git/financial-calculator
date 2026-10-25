"""Compound growth, continuous growth, annuities, and percent change view."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from fincalc.core import (
    annuity_future_value,
    compound_interest,
    continuous_growth,
    percent_decrease,
    percent_increase,
)
from fincalc.errors import FinCalcError
from ui.charts import create_growth_comparison_chart
from ui.components import (
    format_curr,
    formula_expander,
    get_query_param_float,
    get_query_param_int,
    render_error,
    sync_query_params,
)


def show_growth() -> None:
    """Render the Compound Growth & Annuity Calculator page."""
    st.title("🌱 Compound Growth & Annuities")
    st.markdown(
        "Explore how investments grow across different compounding intervals — from annual to continuous compounding — "
        "as well as annuity cash flow streams and exponential depreciation."
    )

    tab_lump, tab_annuity, tab_change = st.tabs(
        ["💵 Lump Sum Compounding", "🔄 Annuity Cash Flows", "📉 Percent Increase & Decrease"]
    )

    with tab_lump:
        st.subheader("Lump Sum Investment Compounding")
        col1, col2 = st.columns(2)

        def_principal = get_query_param_float("p", 10000.0)
        def_rate = get_query_param_float("r", 8.0)
        def_years = get_query_param_int("t", 10)

        with col1:
            principal = st.number_input(
                "Initial Principal Amount",
                min_value=0.0,
                max_value=10000000.0,
                value=float(def_principal),
                step=500.0,
                key="growth_p",
            )
            rate_pct = st.number_input(
                "Annual Interest Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(def_rate),
                step=0.25,
                key="growth_r",
            )

        with col2:
            years = st.number_input(
                "Investment Horizon (Years)",
                min_value=1,
                max_value=50,
                value=int(def_years),
                step=1,
                key="growth_t",
            )
            custom_n = st.selectbox(
                "Custom Compounding Frequency",
                options=[1, 2, 4, 12, 365],
                format_func=lambda n: {
                    1: "Annually (1/yr)",
                    2: "Semi-Annually (2/yr)",
                    4: "Quarterly (4/yr)",
                    12: "Monthly (12/yr)",
                    365: "Daily (365/yr)",
                }[n],
                index=3,
                key="growth_n",
            )

        sync_query_params(p=principal, r=rate_pct, t=years)

        try:
            rate_dec = rate_pct / 100.0
            fv_annual = compound_interest(principal, rate_dec, years, compounds_per_year=1)
            fv_custom = compound_interest(principal, rate_dec, years, compounds_per_year=custom_n)
            fv_cont = continuous_growth(principal, rate_dec, years)

            st.divider()
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Compounded Annually (n=1)", format_curr(fv_annual))
            with m2:
                st.metric(f"Compounded {custom_n}×/Year", format_curr(fv_custom))
            with m3:
                st.metric("Compounded Continuously", format_curr(fv_cont))

            # Build year-by-year curve across all compounding models
            records = []
            for y in range(1, int(years) + 1):
                records.append(
                    {
                        "Year": y,
                        "Balance": compound_interest(principal, rate_dec, y, 1),
                        "Compounding Type": "Annual (n=1)",
                    }
                )
                records.append(
                    {
                        "Year": y,
                        "Balance": compound_interest(principal, rate_dec, y, 4),
                        "Compounding Type": "Quarterly (n=4)",
                    }
                )
                records.append(
                    {
                        "Year": y,
                        "Balance": compound_interest(principal, rate_dec, y, 12),
                        "Compounding Type": "Monthly (n=12)",
                    }
                )
                records.append(
                    {
                        "Year": y,
                        "Balance": continuous_growth(principal, rate_dec, y),
                        "Compounding Type": "Continuous",
                    }
                )

            df_comp = pd.DataFrame(records)
            st.plotly_chart(create_growth_comparison_chart(df_comp), use_container_width=True)

        except FinCalcError as err:
            render_error(err)

    with tab_annuity:
        st.subheader("Recurring Annuity Streams")
        st.markdown("Calculate future value for equal deposits made every month or period.")

        ac1, ac2 = st.columns(2)
        with ac1:
            pmt = st.number_input("Periodic Deposit Amount", value=300.0, step=50.0, key="ann_pmt")
            ann_rate = st.number_input(
                "Annual Interest Rate (%)", value=10.0, step=0.25, key="ann_r"
            )
        with ac2:
            ann_years = st.number_input("Duration (Years)", value=3.0, step=0.5, key="ann_t")
            ann_freq = st.selectbox(
                "Deposit Frequency",
                options=[12, 4, 1],
                format_func=lambda f: {
                    12: "Monthly (12/yr)",
                    4: "Quarterly (4/yr)",
                    1: "Annually (1/yr)",
                }[f],
                key="ann_freq",
            )

        due_toggle = st.checkbox("Annuity Due (Deposits at beginning of each period)", value=False)
        rate_dec = ann_rate / 100.0

        fv_ord = annuity_future_value(
            pmt, rate_dec, ann_years, compounds_per_year=ann_freq, annuity_due=due_toggle
        )
        fv_cont_ann = annuity_future_value(
            pmt, rate_dec, ann_years, compounds_per_year=ann_freq, continuous=True
        )

        total_paid_in = pmt * ann_freq * ann_years
        st.divider()
        am1, am2, am3 = st.columns(3)
        with am1:
            st.metric("Total Deposits Made", format_curr(total_paid_in))
        with am2:
            st.metric("Discrete Future Value", format_curr(fv_ord))
        with am3:
            st.metric("Continuous Cash Flow FV", format_curr(fv_cont_ann))

    with tab_change:
        st.subheader("Exponential Percent Increase & Depreciation")
        pc1, pc2 = st.columns(2)
        with pc1:
            st.markdown("#### Percent Growth")
            inc_val = st.number_input("Initial Amount", value=100.0, step=10.0, key="inc_val")
            inc_pct = st.number_input("Rate of Increase (%)", value=10.0, step=1.0, key="inc_pct")
            inc_t = st.number_input("Time Periods", value=2.0, step=1.0, key="inc_t")
            inc_res = percent_increase(inc_val, inc_pct / 100.0, inc_t)
            st.write(f"Resulting Value: **{inc_res:,.2f}** (Growth: +{inc_res - inc_val:,.2f})")

        with pc2:
            st.markdown("#### Percent Depreciation / Decay")
            dec_val = st.number_input("Initial Asset Value", value=100.0, step=10.0, key="dec_val")
            dec_pct = st.number_input("Depreciation Rate (%)", value=10.0, step=1.0, key="dec_pct")
            dec_t = st.number_input("Time Periods (Years)", value=2.0, step=1.0, key="dec_t")
            dec_res = percent_decrease(dec_val, dec_pct / 100.0, dec_t)
            st.write(f"Depreciated Value: **{dec_res:,.2f}** (Loss: -{dec_val - dec_res:,.2f})")

    formula_expander(
        title="Compound & Continuous Compounding",
        latex_formula=r"A_{\text{discrete}} = P \left(1 + \frac{r}{n}\right)^{nt}, \quad A_{\text{continuous}} = P e^{rt}",
        explanation=(
            "- **Discrete Formula**: Compounding $n$ times per year multiplies principal by $(1 + r/n)$ every period.\n"
            "- **Continuous Formula**: As compounding frequency approaches infinity ($n \\to \\infty$), "
            "growth converges to the natural exponential function $e^{rt}$."
        ),
    )


if __name__ == "__main__":
    show_growth()
