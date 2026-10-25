"""Financial Calculator - Streamlit Web Application Entrypoint.

Provides multipage navigation, shared sidebar configuration, and app initialization.
"""

from __future__ import annotations

import streamlit as st

from ui.components import init_session_state, render_sidebar_currency_selector

# Initialize application layout and configuration
st.set_page_config(
    page_title="Financial Calculator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_state()

# Navigation setup using modern Streamlit Page routing
pages = {
    "Overview": [
        st.Page("views/home.py", title="Home", icon="🏠", default=True),
    ],
    "Calculators": [
        st.Page("views/mortgage.py", title="Mortgage & Loan", icon="🏡"),
        st.Page("views/retirement.py", title="Retirement Planner", icon="📈"),
        st.Page("views/growth.py", title="Compound Growth", icon="🌱"),
        st.Page("views/doubling.py", title="Doubling & Target Time", icon="⏱️"),
        st.Page("views/logarithms.py", title="Logarithm Solver", icon="🧮"),
        st.Page("views/scientific.py", title="Scientific Notation", icon="🔬"),
        st.Page("views/ph.py", title="pH Scale & Acidity", icon="🧪"),
    ],
}

pg = st.navigation(pages)

# Global sidebar settings
with st.sidebar:
    st.markdown("### ⚙️ Settings & Options")
    render_sidebar_currency_selector()

    st.divider()
    st.markdown(
        """
        ### 📚 Documentation
        - [Formulas & Derivations](https://github.com/raiyan-mahmud-git/financial-calculator/blob/main/docs/FORMULAS.md)
        - [Learning Notes & Architecture](https://github.com/raiyan-mahmud-git/financial-calculator/blob/main/docs/LEARNING_NOTES.md)

        ---
        **Source Repository:**  
        [raiyan-mahmud-git/financial-calculator](https://github.com/raiyan-mahmud-git/financial-calculator)
        """
    )

pg.run()
