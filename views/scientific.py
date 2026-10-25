"""Scientific notation converter view with round-trip verification and error resilience."""

from __future__ import annotations

import streamlit as st

from fincalc.core import from_scientific, to_scientific
from fincalc.errors import FinCalcError
from ui.components import formula_expander, render_error


def show_scientific() -> None:
    """Render the Scientific Notation Conversion page."""
    st.title("🔬 Scientific Notation Converter")
    st.markdown(
        "Convert very large or very small real numbers into normalized scientific notation ($m \\times 10^e$) "
        "and parse strings formatted in multiple notation conventions."
    )

    tab_to, tab_from = st.tabs(
        ["➡️ Number to Scientific Notation", "⬅️ Scientific Notation to Number"]
    )

    with tab_to:
        st.subheader("Convert Real Number to Standard Scientific Form")
        col1, col2 = st.columns([3, 1])

        with col1:
            raw_input_str = st.text_input(
                "Enter any real number (e.g. 156000000000, 0.000000000413, -42000, 9.999):",
                value="156000000000",
                key="sci_num_in",
            )
        with col2:
            precision = st.number_input(
                "Decimal Precision", min_value=0, max_value=12, value=2, step=1
            )

        try:
            num = float(raw_input_str.replace(",", "").strip())
            sci_result = to_scientific(num, precision=precision)

            st.divider()
            st.success(f"### Standard Form: **`{sci_result}`**")

            # Mathematical breakdown
            if num != 0:
                parts = sci_result.split(" x 10^")
                mantissa = parts[0]
                exp = parts[1]
                st.markdown(
                    f"- **Mantissa ($m$):** `{mantissa}` (where $1 \\le |m| < 10$)\n"
                    f"- **Exponent ($e$):** `{exp}`\n"
                    f"- **Verification:** `{mantissa} * 10^({exp}) = {float(mantissa) * (10 ** int(exp)):,}`"
                )
            else:
                st.markdown("- **Zero Edge Case:** Number is identically zero (`0.00 x 10^0`).")

        except ValueError:
            st.error("⚠️ Please enter a valid numerical input.")
        except FinCalcError as err:
            render_error(err)

    with tab_from:
        st.subheader("Parse Scientific Notation String to Real Number")
        sci_input = st.text_input(
            "Enter scientific string (e.g. '1.56 x 10^11', '1.56*10^11', '4.13 x 10^-10', '1.56e11'):",
            value="1.56 x 10^11",
            key="sci_str_in",
        )

        try:
            parsed_val = from_scientific(sci_input)
            st.divider()
            st.success(f"### Computed Real Value: **`{parsed_val:,.10g}`**")
            st.write(f"Standard Python float representation: `{parsed_val}`")

            # Round trip confirmation
            re_sci = to_scientific(parsed_val)
            st.info(f"🔄 **Round-trip check:** Reparsing to scientific yields `{re_sci}`")

        except FinCalcError as err:
            render_error(err)

    formula_expander(
        title="Scientific Notation & Base-10 Exponents",
        latex_formula=r"x = m \times 10^e \quad (1 \le |m| < 10, \quad e \in \mathbb{Z})",
        explanation=(
            "- **Exponent Calculation**: $e = \\lfloor \\log_{10}(|x|) \\rfloor$.\n"
            "- **Mantissa Calculation**: $m = x \\cdot 10^{-e}$.\n"
            "- **Rounding Edge Case**: If rounding the mantissa pushes $|m|$ to $10.0$ (e.g., $9.999 \\to 10.00$), "
            "the system correctly resets $m = 1.00$ and increments exponent $e \\leftarrow e + 1$."
        ),
    )


if __name__ == "__main__":
    show_scientific()
