"""
visualizations.py - Simple, Layman-Friendly Bar Charts for Cola Next SMO KPI Analyzer
Focuses strictly on easy-to-understand bar charts with clear legends and zero complicated charts.
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple

COLA_NAVY = "#0b1e36"
COLA_CRIMSON = "#d8232a"
COLA_EMERALD = "#10b981"
COLA_AMBER = "#f59e0b"
COLA_SLATE = "#64748b"
COLA_LIGHT_GRAY = "#e2e8f0"


def get_base_layout():
    """Clean, distraction-free chart layout."""
    return dict(
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#334155"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=30, t=40, b=30),
        hoverlabel=dict(
            bgcolor="#0b1e36",
            font_size=12,
            font_family="Plus Jakarta Sans, sans-serif",
            font_color="#ffffff"
        )
    )


def create_smo_kpi_bar_chart(smo_row: pd.Series, thresholds: Dict[str, Tuple[float, float]]) -> go.Figure:
    """
    Simple horizontal bar chart showing the selected SMO's scores across all 5 percentage KPIs.
    Each bar is colored Green, Yellow, or Red based on their score.
    """
    kpis = [
        ("Achievement %", float(smo_row.get("Ach.%", 0) or 0), *thresholds.get("Achievement", (100.0, 85.0))),
        ("Call Completion %", float(smo_row.get("Call Comp. %", 0) or 0), *thresholds.get("Call Completion", (95.0, 85.0))),
        ("GPS Accuracy %", float(smo_row.get("GPS Accuracy % (PJP)", 0) or 0), *thresholds.get("GPS Accuracy", (90.0, 75.0))),
        ("Delivered Cases %", float(smo_row.get("Delivered Cases %", 0) or 0), *thresholds.get("Delivered Cases", (90.0, 80.0))),
        ("Strike Rate %", float(smo_row.get("Strike Rate %", 0) or 0), *thresholds.get("Strike Rate", (80.0, 65.0))),
        ("Productive Outlets %", float(smo_row.get("Productive Unique Outlets %", 0) or 0), 60.0, 40.0)
    ]

    labels = [k[0] for k in kpis]
    values = [k[1] for k in kpis]
    colors = []
    
    for _, val, g, y in kpis:
        if val >= g:
            colors.append(COLA_EMERALD)  # Green
        elif val >= y:
            colors.append(COLA_AMBER)    # Yellow
        else:
            colors.append(COLA_CRIMSON)  # Red

    fig = go.Figure(go.Bar(
        y=labels,
        x=values,
        orientation="h",
        marker=dict(color=colors, line=dict(color="#ffffff", width=1.5)),
        text=[f"<b>{v:.1f}%</b>" for v in values],
        textposition="outside",
        cliponaxis=False
    ))

    # Add a target line at 100%
    fig.add_vline(
        x=100,
        line_dash="dash",
        line_color="#64748b",
        annotation_text="100% Standard Goal",
        annotation_position="top right",
        annotation_font=dict(size=11, color="#64748b")
    )

    layout = get_base_layout()
    layout.update(
        title=dict(
            text=f"<b>Performance Scorecard for {smo_row.get('SMO Name', 'SMO')}</b>",
            font=dict(size=14, color="#0b1e36")
        ),
        xaxis=dict(
            title="Score (%)",
            range=[0, max(120, max(values) + 15)],
            gridcolor="#f1f5f9"
        ),
        yaxis=dict(
            title="",
            autorange="reversed" # top KPI at the top
        ),
        height=360
    )
    fig.update_layout(layout)
    return fig


def create_top_performers_bar(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """
    Simple horizontal bar chart showing the highest performing SMOs by Achievement %.
    """
    clean_df = df.dropna(subset=["Ach.%"]).sort_values(by="Ach.%", ascending=True).tail(top_n)

    # Color code bars: Green for >=100%, Yellow for >=85%, Red for <85%
    colors = []
    for val in clean_df["Ach.%"]:
        if val >= 100.0:
            colors.append(COLA_EMERALD)
        elif val >= 85.0:
            colors.append(COLA_AMBER)
        else:
            colors.append(COLA_CRIMSON)

    fig = go.Figure(go.Bar(
        y=clean_df["SMO Name"] + " (" + clean_df["Route Name"].astype(str) + ")",
        x=clean_df["Ach.%"],
        orientation="h",
        marker=dict(color=colors),
        text=clean_df["Ach.%"].apply(lambda v: f"<b>{v:.1f}%</b>"),
        textposition="outside",
        cliponaxis=False
    ))

    # Add 100% Target reference line
    fig.add_vline(x=100, line_dash="dash", line_color="#0b1e36", annotation_text="100% Target", annotation_position="top right")

    layout = get_base_layout()
    layout.update(
        title=dict(text="<b>Top SMOs by Sales Achievement %</b>", font=dict(size=14, color="#0b1e36")),
        xaxis=dict(title="Achievement % (Target = 100%)", gridcolor="#f1f5f9", range=[0, max(120, clean_df["Ach.%"].max() + 15)]),
        yaxis=dict(title=""),
        height=max(360, len(clean_df) * 32)
    )
    fig.update_layout(layout)
    return fig


def create_bottom_performers_bar(df: pd.DataFrame, bot_n: int = 10) -> go.Figure:
    """
    Simple horizontal bar chart showing the lowest performing SMOs needing coaching.
    """
    clean_df = df.dropna(subset=["Ach.%"]).sort_values(by="Ach.%", ascending=False).tail(bot_n)

    fig = go.Figure(go.Bar(
        y=clean_df["SMO Name"] + " (" + clean_df["Route Name"].astype(str) + ")",
        x=clean_df["Ach.%"],
        orientation="h",
        marker=dict(color=COLA_CRIMSON),
        text=clean_df["Ach.%"].apply(lambda v: f"<b>{v:.1f}%</b>"),
        textposition="outside",
        cliponaxis=False
    ))

    fig.add_vline(x=85, line_dash="dash", line_color=COLA_AMBER, annotation_text="85% Minimum Pass", annotation_position="top right")

    layout = get_base_layout()
    layout.update(
        title=dict(text="<b>SMOs Needing Support & Coaching (Lowest Achievement %)</b>", font=dict(size=14, color="#0b1e36")),
        xaxis=dict(title="Achievement %", gridcolor="#f1f5f9", range=[0, 100]),
        yaxis=dict(title="", autorange="reversed"),
        height=max(360, len(clean_df) * 32)
    )
    fig.update_layout(layout)
    return fig


def create_target_vs_sales_bar(df: pd.DataFrame) -> go.Figure:
    """
    Simple grouped bar chart comparing Target Cases vs Actual Sales Cases by Distributor / Zone.
    """
    group_col = "Distribution Name" if "Distribution Name" in df.columns and df["Distribution Name"].nunique() > 1 else "Zone"
    if group_col not in df.columns or df[group_col].nunique() == 0:
        group_col = "Route Name"

    grouped = df.groupby(group_col).agg({
        "Target": "sum",
        "Route Sale": "sum"
    }).reset_index().sort_values(by="Target", ascending=True)

    fig = go.Figure()

    # Target Bar (Gray)
    fig.add_trace(go.Bar(
        y=grouped[group_col],
        x=grouped["Target"],
        name="Target Cases (Goal)",
        orientation="h",
        marker=dict(color=COLA_LIGHT_GRAY, line=dict(color="#cbd5e1", width=1)),
        text=grouped["Target"].apply(lambda v: f"{v:,.0f}"),
        textposition="auto"
    ))

    # Actual Sales Bar (Navy Blue)
    fig.add_trace(go.Bar(
        y=grouped[group_col],
        x=grouped["Route Sale"],
        name="Actual Sales (Delivered/Sold)",
        orientation="h",
        marker=dict(color=COLA_NAVY),
        text=grouped["Route Sale"].apply(lambda v: f"{v:,.0f}"),
        textposition="auto"
    ))

    layout = get_base_layout()
    layout.update(
        title=dict(text=f"<b>Target vs Actual Sales by {group_col}</b>", font=dict(size=14, color="#0b1e36")),
        barmode="group",
        xaxis=dict(title="Number of Cases (Bottles/Boxes)", gridcolor="#f1f5f9"),
        yaxis=dict(title=""),
        height=max(320, len(grouped) * 45),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    fig.update_layout(layout)
    return fig


def create_zone_health_bar(team_stats: Dict[str, Any]) -> go.Figure:
    """
    Simple 3-bar chart showing how many SMOs are in Green, Yellow, and Red zones.
    """
    categories = ["Green (Met Goal)", "Yellow (Average)", "Red (Action Needed)"]
    counts = [
        team_stats.get("green_count", 0),
        team_stats.get("yellow_count", 0),
        team_stats.get("red_count", 0)
    ]
    colors = [COLA_EMERALD, COLA_AMBER, COLA_CRIMSON]

    fig = go.Figure(go.Bar(
        x=categories,
        y=counts,
        marker=dict(color=colors),
        text=[f"<b>{c} SMOs</b>" for c in counts],
        textposition="outside",
        cliponaxis=False
    ))

    layout = get_base_layout()
    layout.update(
        title=dict(text="<b>Overall Team Performance Health (SMO Count)</b>", font=dict(size=14, color="#0b1e36")),
        xaxis=dict(title=""),
        yaxis=dict(title="Number of Sales Officers (SMOs)", gridcolor="#f1f5f9", range=[0, max(counts) + 5 if counts else 10]),
        height=320
    )
    fig.update_layout(layout)
    return fig


def create_order_delivery_bar(smo_row: pd.Series) -> go.Figure:
    """
    Simple 3-bar chart for an individual SMO showing:
    1. Ordered Cases
    2. Delivered Cases
    3. Undelivered Cases
    """
    categories = ["Ordered Cases", "Delivered Cases", "Un-Delivered Cases"]
    values = [
        float(smo_row.get("No. of Ordered Cases", 0) or 0),
        float(smo_row.get("No. of Delivered Cases", 0) or 0),
        float(smo_row.get("No. of Un-Delivered Cases", 0) or 0)
    ]
    colors = [COLA_NAVY, COLA_EMERALD, COLA_CRIMSON]

    fig = go.Figure(go.Bar(
        x=categories,
        y=values,
        marker=dict(color=colors),
        text=[f"<b>{v:,.0f} cases</b>" for v in values],
        textposition="outside",
        cliponaxis=False
    ))

    layout = get_base_layout()
    layout.update(
        title=dict(text="<b>Order vs Delivery Fulfillment Breakdown</b>", font=dict(size=14, color="#0b1e36")),
        xaxis=dict(title=""),
        yaxis=dict(title="Cases", gridcolor="#f1f5f9", range=[0, max(values) * 1.18 if max(values) > 0 else 10]),
        height=320
    )
    fig.update_layout(layout)
    return fig


def create_calls_bar(smo_row: pd.Series) -> go.Figure:
    """
    Simple bar chart comparing Planned Calls vs Actual Calls Made vs Productive Calls (where order was taken).
    """
    categories = ["Planned Shop Visits", "Actual Shop Visits", "Visits with Orders (Productive)"]
    values = [
        float(smo_row.get("Plan Calls MTD", 0) or 0),
        float(smo_row.get("Actual Calls MTD", 0) or 0),
        float(smo_row.get("No. of Productive Calls MTD", 0) or 0)
    ]
    colors = [COLA_LIGHT_GRAY, COLA_NAVY, COLA_EMERALD]

    fig = go.Figure(go.Bar(
        x=categories,
        y=values,
        marker=dict(color=colors, line=dict(color="#cbd5e1", width=1)),
        text=[f"<b>{v:,.0f} visits</b>" for v in values],
        textposition="outside",
        cliponaxis=False
    ))

    layout = get_base_layout()
    layout.update(
        title=dict(text="<b>Route Shop Visits (Calls) Conversion</b>", font=dict(size=14, color="#0b1e36")),
        xaxis=dict(title=""),
        yaxis=dict(title="Number of Visits (Calls)", gridcolor="#f1f5f9", range=[0, max(values) * 1.18 if max(values) > 0 else 10]),
        height=320
    )
    fig.update_layout(layout)
    return fig
