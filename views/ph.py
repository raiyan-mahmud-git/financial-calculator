"""pH scale and acidity calculator view."""

from __future__ import annotations

import streamlit as st

from fincalc.core import ph_from_concentration
from fincalc.errors import FinCalcError
from ui.charts import create_ph_scale_chart
from ui.components import formula_expander, render_error


def show_ph() -> None:
    """Render the pH Scale and Hydrogen Ion Concentration page."""
    st.title("🧪 pH Scale & Hydrogen Ion Concentration")
    st.markdown(
        "Calculate the acidity or alkalinity of an aqueous solution from its hydrogen ion "
        r"concentration $[H^+]$: $$\text{pH} = -\log_{10}([H^+])$$"
    )

    st.subheader("Common Sample Presets")
    preset_cols = st.columns(5)
    preset_val = None

    with preset_cols[0]:
        if st.button("Stomach Acid (0.01 M)", use_container_width=True):
            preset_val = 0.01
    with preset_cols[1]:
        if st.button("Coffee (1e-5 M)", use_container_width=True):
            preset_val = 1e-5
    with preset_cols[2]:
        if st.button("Pure Water (1e-7 M)", use_container_width=True):
            preset_val = 1e-7
    with preset_cols[3]:
        if st.button("Baking Soda (1e-9 M)", use_container_width=True):
            preset_val = 1e-9
    with preset_cols[4]:
        if st.button("Bleach (1e-13 M)", use_container_width=True):
            preset_val = 1e-13

    if preset_val is not None:
        st.session_state["ph_conc_input"] = str(preset_val)

    current_input = st.session_state.get("ph_conc_input", "0.007")

    conc_str = st.text_input(
        "Hydrogen Ion Concentration $[H^+]$ in moles/liter (mol/L):",
        value=current_input,
        help="Enter as decimal (e.g. 0.007) or scientific notation (e.g. 1e-7).",
        key="ph_text_box",
    )

    try:
        conc = float(conc_str)
        res = ph_from_concentration(conc)

        st.divider()
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("pH Value", f"{res.ph:.2f}")
        with m2:
            st.metric("pOH Value", f"{res.poh:.2f}")
        with m3:
            st.metric("Classification", res.classification)

        st.plotly_chart(create_ph_scale_chart(res.ph), use_container_width=True)

        if res.classification == "Acidic":
            st.info(f"🔴 Solution is **Acidic** with $[H^+] = {conc:.2e}$ mol/L.")
        elif res.classification == "Neutral":
            st.success(
                "🟢 Solution is **Neutral** (pH 7.00, $[H^+] = 1.00 \\times 10^{-7}$ mol/L)."
            )
        else:
            st.info(f"🔵 Solution is **Basic (Alkaline)** with $[H^+] = {conc:.2e}$ mol/L.")

    except ValueError:
        st.error(
            "⚠️ Please enter a valid decimal number or scientific notation string (e.g. 0.007 or 1e-7)."
        )
    except FinCalcError as err:
        render_error(err)

    formula_expander(
        title="pH Scale & Self-Ionization of Water",
        latex_formula=r"\text{pH} = -\log_{10}([H^+]), \quad \text{pOH} = -\log_{10}([OH^-]), \quad \text{pH} + \text{pOH} = 14.0",
        explanation=(
            "- **Logarithmic Nature**: Because pH is base-10 logarithmic, each whole pH unit represents a **10-fold** change in $[H^+]$. "
            "A solution with pH 3 is 10 times more acidic than pH 4, and 1,000 times more acidic than pH 6.\n"
            "- **Water Equilibrium**: At 25°C, $[H^+][OH^-] = 1.0 \\times 10^{-14}$, establishing the sum $\\text{pH} + \\text{pOH} = 14$."
        ),
    )


if __name__ == "__main__":
    show_ph()
