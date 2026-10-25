"""Reusable UI components and state management for the Financial Calculator."""

from __future__ import annotations

from typing import Any

import streamlit as st

from fincalc.formatting import CURRENCY_SYMBOLS, format_currency


def init_session_state() -> None:
    """Initialize global session state variables if not already present."""
    if "currency" not in st.session_state:
        st.session_state["currency"] = "USD"


def render_sidebar_currency_selector() -> str:
    """Render currency selector widget in the sidebar and persist in session state."""
    init_session_state()
    currencies = list(CURRENCY_SYMBOLS.keys())
    current_idx = currencies.index(st.session_state.get("currency", "USD"))

    selected = st.sidebar.selectbox(
        "💱 Currency Display",
        options=currencies,
        index=current_idx,
        format_func=lambda code: f"{code} ({CURRENCY_SYMBOLS[code]})",
        help="Select your preferred currency symbol for all monetary results.",
        key="global_currency_selector",
    )
    st.session_state["currency"] = selected
    return selected


def get_current_currency() -> str:
    """Return the currently active currency code from session state."""
    return st.session_state.get("currency", "USD")


def format_curr(amount: float, decimals: int = 2) -> str:
    """Format an amount using the currently selected global currency."""
    return format_currency(amount, currency=get_current_currency(), decimals=decimals)


def formula_expander(title: str, latex_formula: str, explanation: str) -> None:
    """Render a standardized formula expander using st.latex and explanation."""
    with st.expander(f"📐 How this is calculated: {title}"):
        st.latex(latex_formula)
        st.markdown(explanation)


def render_error(error: Exception | str) -> None:
    """Display domain error cleanly without exposing raw Python tracebacks."""
    message = str(error)
    st.error(f"⚠️ **Calculation Error:** {message}")


def get_query_param_float(key: str, default: float) -> float:
    """Retrieve a float parameter from st.query_params safely."""
    val = st.query_params.get(key)
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def get_query_param_int(key: str, default: int) -> int:
    """Retrieve an integer parameter from st.query_params safely."""
    val = st.query_params.get(key)
    if val is None:
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def get_query_param_str(key: str, default: str) -> str:
    """Retrieve a string parameter from st.query_params safely."""
    val = st.query_params.get(key)
    if val is None:
        return default
    return str(val)


def sync_query_params(**kwargs: Any) -> None:
    """Update current st.query_params with given key-value pairs."""
    for key, val in kwargs.items():
        if val is not None:
            st.query_params[key] = str(val)
