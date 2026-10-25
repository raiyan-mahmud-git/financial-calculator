"""Home view: Overview and interactive directory of the Financial Calculator suite."""

import streamlit as st

from ui.components import get_current_currency


def show_home() -> None:
    """Render the homepage with quick links and architecture overview."""
    st.title("💰 Financial & Mathematical Calculator")
    st.markdown(
        """
        Welcome to the **Financial Calculator** suite — a production-grade, pure Python application
        providing high-precision financial modeling, growth simulations, and mathematical tools.
        """
    )

    curr = get_current_currency()

    st.info(
        f"💡 **Active Currency:** **{curr}**. You can change your preferred currency symbol anytime "
        "in the left sidebar. Scenarios and inputs across all tools can be bookmarked and shared via URL parameters."
    )

    st.subheader("Explore Calculators")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            ### 🏡 [Mortgage & Amortization](Mortgage_&_Loan)
            - Fixed-rate monthly mortgage calculations.
            - Month-by-month principal and interest amortization schedules.
            - Accelerated payoff and interest savings from extra monthly payments.
            - Download complete schedules as CSV.

            ### 📈 [Retirement Wealth Planner](Retirement_Planner)
            - Long-term compound investment trajectories.
            - Real-world adjustments: initial nest egg, annual salary/contribution raises.
            - Inflation discounting to calculate real future purchasing power.

            ### 🌱 [Compound Growth](Compound_Growth)
            - Discrete compounding ($n$ times/year) and continuous growth ($P e^{rt}$).
            - Exponential percent increase and asset depreciation.
            - Comparative charts across frequencies.

            ### ⏱️ [Doubling & Target Time](Doubling_&_Target_Time)
            - Calculate investment doubling duration via Continuous, Annual, and Rule of 72 models.
            - Solve exact time required to reach arbitrary financial goals.
            """
        )

    with col2:
        st.markdown(
            """
            ### 🧮 [Logarithm Solver](Logarithm_Solver)
            - Solve the full exponential/logarithmic relation: $\\log_b(x) = y \\iff b^y = x$.
            - Solve for $x$, solve for exponent $y$, or solve for base $b$.
            - Interactive curve visualization with solved coordinate points.

            ### 🔬 [Scientific Notation](Scientific_Notation)
            - High-precision conversion between real numbers and standard form ($m \\times 10^e$).
            - Fixes IEEE 754 log quirks and rounding rollover edge cases (e.g., $9.999 \\to 1.00 \\times 10^1$).
            - Flexible parser accepting `1.56 x 10^11`, `1.56*10^11`, `1.56e11`.

            ### 🧪 [pH Scale & Acidity](pH_Scale_&_Acidity)
            - Chemistry logarithmic concentration tool: $\\text{pH} = -\\log_{10}([H^+])$.
            - Instant pH, pOH, and acidity/alkalinity classification.
            - Full interactive visual pH color spectrum.
            """
        )

    st.divider()

    st.markdown("### 🛠️ Key Technical Highlights")
    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric("Architecture", "Pure Decoupled Core", "No UI coupling")
    with k2:
        st.metric("Test Coverage", "100% Core Passing", "55 Unit Tests")
    with k3:
        st.metric("Deployment", "Streamlit Cloud", "Python 3.10+")


if __name__ == "__main__":
    show_home()
