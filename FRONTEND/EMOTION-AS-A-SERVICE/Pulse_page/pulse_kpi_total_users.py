# -*- coding: utf-8 -*-
"""Total users KPI for Fan Pulse."""

import plotly.graph_objects as go

from pulse_data import format_compact_number, get_total_user_count

CHART_BACKGROUND = "#1A1A2E"
CHART_BORDER = "#3A3A55"
CHART_TEXT = "#F5F5F5"


def get_total_users():
    """Return unique users from the full tweet metrics provider."""
    return get_total_user_count()


def display_total_users():
    """Return the total users KPI card and raw value."""
    total_users = get_total_users()
    figure = _create_kpi_card("Total Users", format_compact_number(total_users))
    return figure, total_users


def _create_kpi_card(label, value):
    figure = go.Figure()

    figure.add_annotation(
        text=label,
        x=0.05,
        y=0.78,
        xref="paper",
        yref="paper",
        showarrow=False,
        align="left",
        font=dict(size=20, color=CHART_TEXT),
    )
    figure.add_annotation(
        text=f"<b>{value}</b>",
        x=0.05,
        y=0.35,
        xref="paper",
        yref="paper",
        showarrow=False,
        align="left",
        font=dict(size=42, color=CHART_TEXT),
    )
    figure.update_layout(
        width=320,
        height=170,
        paper_bgcolor=CHART_BACKGROUND,
        plot_bgcolor=CHART_BACKGROUND,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        shapes=[
            dict(
                type="rect",
                x0=0,
                y0=0,
                x1=1,
                y1=1,
                xref="paper",
                yref="paper",
                line=dict(color=CHART_BORDER, width=1),
                fillcolor=CHART_BACKGROUND,
            )
        ],
    )

    return figure


if __name__ == "__main__":
    kpi_figure, total_value = display_total_users()
    kpi_figure.show(config={"displayModeBar": False})
    print(f"Total unique users: {total_value:,}")
