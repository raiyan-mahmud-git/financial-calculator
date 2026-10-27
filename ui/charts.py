"""Plotly visualizers for financial growth, amortization, retirement, and pH scales."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

DARK_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": "#E2E8F0", "family": "Inter, sans-serif"},
    "xaxis": {"gridcolor": "#334155", "zerolinecolor": "#475569"},
    "yaxis": {"gridcolor": "#334155", "zerolinecolor": "#475569"},
    "margin": {"l": 40, "r": 20, "t": 50, "b": 40},
}


def create_donut_chart(
    labels: list[str],
    values: list[float],
    title: str,
    colors: list[str] | None = None,
) -> go.Figure:
    """Create a sleek donut chart for split breakdowns (e.g. Principal vs Interest)."""
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                marker=dict(colors=colors or ["#3B82F6", "#EF4444", "#10B981"]),
                textinfo="label+percent",
                hoverinfo="label+value+percent",
            )
        ]
    )
    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=16)),
        showlegend=True,
        **DARK_LAYOUT,
    )
    return fig


def create_amortization_chart(df: pd.DataFrame) -> go.Figure:
    """Chart remaining loan balance and cumulative interest over payment periods."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["month"],
            y=df["ending_balance"],
            name="Remaining Balance",
            mode="lines",
            line=dict(color="#3B82F6", width=2.5),
            fill="tozeroy",
            fillcolor="rgba(59, 130, 246, 0.15)",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["month"],
            y=df["cumulative_interest"],
            name="Cumulative Interest",
            mode="lines",
            line=dict(color="#EF4444", width=2.5, dash="dash"),
        )
    )
    fig.update_layout(
        title=dict(text="Amortization Schedule: Balance & Cumulative Interest", x=0.5),
        xaxis_title="Month",
        yaxis_title="Amount",
        hovermode="x unified",
        **DARK_LAYOUT,
    )
    return fig


def create_retirement_chart(df: pd.DataFrame) -> go.Figure:
    """Chart retirement wealth growth: nominal balance, real purchasing power, and deposits."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["year"],
            y=df["ending_nominal_balance"],
            name="Nominal Balance",
            mode="lines+markers",
            line=dict(color="#10B981", width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["year"],
            y=df["ending_real_balance"],
            name="Real Purchasing Power",
            mode="lines",
            line=dict(color="#38BDF8", width=2.5, dash="dash"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["year"],
            y=df["cumulative_contributions"],
            name="Total Deposits",
            mode="lines",
            line=dict(color="#94A3B8", width=2),
            fill="tozeroy",
            fillcolor="rgba(148, 163, 184, 0.15)",
        )
    )
    fig.update_layout(
        title=dict(text="Retirement Wealth Accumulation Over Time", x=0.5),
        xaxis_title="Year",
        yaxis_title="Portfolio Value",
        hovermode="x unified",
        **DARK_LAYOUT,
    )
    return fig


def create_growth_comparison_chart(df: pd.DataFrame) -> go.Figure:
    """Compare multiple compounding models over a shared time horizon."""
    fig = px.line(
        df,
        x="Year",
        y="Balance",
        color="Compounding Type",
        title="Comparison of Growth Compounding Frequencies",
        color_discrete_sequence=["#3B82F6", "#8B5CF6", "#10B981", "#F59E0B"],
    )
    fig.update_layout(
        hovermode="x unified",
        **DARK_LAYOUT,
    )
    return fig


def create_ph_scale_chart(current_ph: float) -> go.Figure:
    """Render an intuitive visual pH scale spectrum (0 to 14) with current indicator."""
    fig = go.Figure()

    # pH color gradient zones
    zones = [
        (0, 3, "#EF4444", "Strongly Acidic"),
        (3, 6, "#F97316", "Weakly Acidic"),
        (6, 8, "#10B981", "Neutral"),
        (8, 11, "#06B6D4", "Weakly Basic"),
        (11, 14, "#8B5CF6", "Strongly Basic"),
    ]

    for start, end, color, label in zones:
        fig.add_trace(
            go.Bar(
                x=[end - start],
                y=["pH Scale"],
                base=start,
                orientation="h",
                name=label,
                marker=dict(color=color),
                hoverinfo="name",
                showlegend=True,
            )
        )

    # Indicator for current pH
    fig.add_vline(
        x=current_ph,
        line_width=4,
        line_color="#FFFFFF",
        annotation_text=f"pH {current_ph:.2f}",
        annotation_position="top",
        annotation_font=dict(size=14, color="#FFFFFF"),
    )

    layout_copy = dict(DARK_LAYOUT)
    layout_copy.pop("xaxis", None)
    layout_copy.pop("yaxis", None)

    fig.update_layout(
        title=dict(text=f"pH Scale Position ({current_ph:.2f})", x=0.5),
        barmode="stack",
        xaxis=dict(
            range=[0, 14],
            dtick=1,
            title="pH Level",
            gridcolor="#334155",
            zerolinecolor="#475569",
        ),
        yaxis=dict(showticklabels=False),
        height=260,
        **layout_copy,
    )
    return fig


def create_log_curve_chart(
    base: float,
    x_val: float,
    y_val: float,
) -> go.Figure:
    """Plot logarithmic and exponential curves showing inverse symmetry."""
    import numpy as np

    x_points = np.linspace(0.05, max(x_val * 1.5, 10.0), 300)
    y_log = [np.log(pt) / np.log(base) for pt in x_points]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x_points,
            y=y_log,
            mode="lines",
            name=f"y = log_{base}(x)",
            line=dict(color="#3B82F6", width=2.5),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[x_val],
            y=[y_val],
            mode="markers+text",
            name="Solution Point",
            text=[f"({x_val:.2f}, {y_val:.2f})"],
            textposition="top center",
            marker=dict(color="#EF4444", size=12, symbol="star"),
        )
    )
    fig.update_layout(
        title=dict(text=f"Logarithmic Function Curve (Base {base})", x=0.5),
        xaxis_title="x",
        yaxis_title="y = log_b(x)",
        **DARK_LAYOUT,
    )
    return fig
