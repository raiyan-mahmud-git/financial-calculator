"""Logarithm and exponential equation solver view."""

from __future__ import annotations

import streamlit as st

from fincalc.core import solve_log
from fincalc.errors import FinCalcError
from ui.charts import create_log_curve_chart
from ui.components import formula_expander, render_error


def show_logarithms() -> None:
    """Render the Logarithmic Equation Solver page."""
    st.title("🧮 Logarithm Equation Solver")
    st.markdown(
        "Solve the fundamental inverse relation between exponential and logarithmic functions: "
        r"$$\log_b(x) = y \iff b^y = x$$"
    )

    mode = st.radio(
        "Select which variable you want to solve for:",
        options=[
            "Solve for Result x (x = b^y)",
            "Solve for Exponent y (y = log_b(x))",
            "Solve for Base b (b = x^(1/y))",
        ],
        index=0,
    )

    st.divider()

    try:
        if "Result x" in mode:
            st.subheader("Solve for x: x = b^y")
            col1, col2 = st.columns(2)
            with col1:
                b = st.number_input("Base (b)", min_value=0.01, value=2.0, step=0.5, key="log_b1")
            with col2:
                y = st.number_input("Exponent (y)", value=4.0, step=0.5, key="log_y1")

            sol_x = solve_log(base=b, exponent=y)
            st.success(f"### Solution: **x = {sol_x:,.4f}**")
            st.write(f"Verification: $\\log_{{{b}}}({sol_x:,.4f}) = {y}$")

            if b > 1 and sol_x > 0:
                st.plotly_chart(create_log_curve_chart(b, sol_x, y), use_container_width=True)

        elif "Exponent y" in mode:
            st.subheader("Solve for Exponent y: y = log_b(x)")
            col1, col2 = st.columns(2)
            with col1:
                b = st.number_input("Base (b)", min_value=0.01, value=2.0, step=0.5, key="log_b2")
            with col2:
                x = st.number_input(
                    "Argument x", min_value=0.0001, value=16.0, step=1.0, key="log_x2"
                )

            sol_y = solve_log(base=b, x=x)
            st.success(f"### Solution: **Exponent y = {sol_y:,.4f}**")
            st.write(f"Verification: ${b}^{{{sol_y:,.4f}}} = {x}$")

            if b > 1 and x > 0:
                st.plotly_chart(create_log_curve_chart(b, x, sol_y), use_container_width=True)

        else:
            st.subheader("Solve for Base b: b = x^(1/y)")
            col1, col2 = st.columns(2)
            with col1:
                x = st.number_input(
                    "Argument x", min_value=0.0001, value=16.0, step=1.0, key="log_x3"
                )
            with col2:
                y = st.number_input("Exponent y", value=4.0, step=0.5, key="log_y3")

            sol_b = solve_log(x=x, exponent=y)
            st.success(f"### Solution: **Base b = {sol_b:,.4f}**")
            st.write(f"Verification: ${sol_b:,.4f}^{{{y}}} = {x}$")

            if sol_b > 1 and x > 0:
                st.plotly_chart(create_log_curve_chart(sol_b, x, y), use_container_width=True)

    except FinCalcError as err:
        render_error(err)

    formula_expander(
        title="Logarithmic Inverses & Change of Base",
        latex_formula=r"\log_b(x) = \frac{\ln(x)}{\ln(b)}, \quad b^y = x, \quad b = x^{1/y}",
        explanation=(
            "- **Inverse Relationship**: Logarithms answer the question: *'To what power must I raise base $b$ to obtain $x$?'*\n"
            "- **Domain Restrictions**: Base $b > 0$ and $b \neq 1$. Argument $x > 0$."
        ),
    )


if __name__ == "__main__":
    show_logarithms()
