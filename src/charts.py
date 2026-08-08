import pandas as pd
import numpy as np
import plotly.graph_objects as go

# theme (aligned with layout.py design tokens: night-asphalt dashboard)
# Charts are built with Plotly instead of matplotlib/seaborn: Plotly renders in the
# browser (SVG/Canvas), so it actually picks up the same web fonts layout.py already
# @imports (Inter / JetBrains Mono) instead of falling back to server-side matplotlib
# fonts — and it blends into the dark UI natively instead of shipping a static PNG.
PANEL_2 = "#161B26"   # matches layout.py's BG_PANEL_2 — the bordered-card background
GRID = "#242B38"
TEXT = "#E8EAED"
SUBTLE = "#7B8794"
AMBER = "#FFB020"
TEAL = "#2DD4BF"
COLORS = {
    "car": "#22c55e",
    "bus": "#FFB020",
    "truck": "#FF5470",
    "motorbike": "#2DD4BF"
}

FONT_SANS = "Inter, 'Space Grotesk', sans-serif"
FONT_MONO = "'JetBrains Mono', Consolas, monospace"


def _base_layout(height=320, showlegend=False):
    """Shared layout: transparent background (blends into the card container),
    Inter for general text, gridlines matching the dashboard's border color."""
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_SANS, color=SUBTLE, size=12),
        margin=dict(l=10, r=20, t=10, b=10),
        height=height,
        showlegend=showlegend,
        legend=dict(
            orientation="v",
            font=dict(family=FONT_SANS, color=SUBTLE, size=12),
            bgcolor="rgba(0,0,0,0)",
        ),
        hoverlabel=dict(
            bgcolor=PANEL_2,
            font_family=FONT_MONO,
            font_color=TEXT,
            bordercolor=GRID,
        ),
    )


# heatmap data (unchanged — pure pandas, independent of the plotting library)
def prepare_heatmap_data(df, n_bins=10):
    df_heat = df.copy()
    if len(df_heat) <= 1:
        return df_heat
    n_bins = min(n_bins, len(df_heat))
    bins = np.linspace(
        df_heat["time"].min(),
        df_heat["time"].max(),
        n_bins + 1
    )
    df_heat["bucket"] = pd.cut(
        df_heat["time"],
        bins=bins,
        include_lowest=True,
        labels=False
    )
    df_heat = (
        df_heat.groupby("bucket")[["time", "car", "bus", "truck", "motorbike"]]
        .mean()
        .reset_index(drop=True)
    )
    df_heat["time"] = (
        df_heat["time"]
        .round()
        .astype(int)
        .astype(str) + "s"
    )
    return df_heat


# heatmap
def heatmap_chart(df):
    raw = df[["car", "bus", "truck", "motorbike"]].T.values.astype(float)
    # global log1p scale: compresses the dominant type (e.g. motorbike ~100)
    # while still separating small counts (1 vs 2 vs 3) on low-volume rows.
    # Per-row normalization was tried but it amplifies noise — a single
    # stray count on a near-zero row (e.g. truck) gets divided by its own
    # tiny max and turns into a false "Peak" block across many cells.
    z_log = np.log1p(raw)
    peak = raw.max()
    if peak <= 0:
        tick_vals = [0]
        zmax = 1
    else:
        candidates = [0, 1, max(2, round(peak * 0.1)), max(3, round(peak * 0.4)), round(peak)]
        tick_vals = sorted(set(v for v in candidates if v <= peak))
        zmax = np.log1p(peak)

    fig = go.Figure(
        go.Heatmap(
            z=z_log,
            x=df["time"],
            y=["Car", "Bus", "Truck", "Motorbike"],
            customdata=raw,
            colorscale=[[0, PANEL_2], [0.5, TEAL], [1, AMBER]],
            zmin=0,
            zmax=zmax,
            hovertemplate="%{y} · %{x}<br>%{customdata:.0f} vehicles<extra></extra>",
            colorbar=dict(
                thickness=10,
                outlinewidth=0,
                tickvals=[np.log1p(v) for v in tick_vals],
                ticktext=[str(int(v)) for v in tick_vals],
                tickfont=dict(family=FONT_MONO, size=10, color=SUBTLE),
            ),
        )
    )
    fig.update_layout(**_base_layout(height=220))
    fig.update_xaxes(
        title=dict(text="Time", font=dict(family=FONT_SANS, size=12, color=TEXT)),
        tickfont=dict(family=FONT_MONO, size=10, color=SUBTLE),
        showgrid=False,
    )
    fig.update_yaxes(
        tickfont=dict(family=FONT_SANS, size=11, color=SUBTLE),
        showgrid=False,
    )
    return fig


# line
def line_chart(df):
    fig = go.Figure()
    for vehicle in ["car", "bus", "truck", "motorbike"]:
        fig.add_trace(
            go.Scatter(
                x=df["time"],
                y=df[vehicle],
                name=vehicle.capitalize(),
                mode="lines",
                line=dict(color=COLORS[vehicle], width=3, shape="spline", smoothing=0.4),
                hovertemplate=f"{vehicle.capitalize()}: " + "%{y:.1f}<extra></extra>",
            )
        )
    fig.update_layout(**_base_layout(height=300, showlegend=True))
    fig.update_layout(hovermode="x unified")
    fig.update_xaxes(
        title=dict(text="Time", font=dict(family=FONT_SANS, size=13, color=TEXT)),
        tickfont=dict(family=FONT_MONO, size=11, color=SUBTLE),
        showgrid=False,
        showspikes=True,
        spikemode="across",
        spikedash="dot",
        spikecolor=SUBTLE,
        spikethickness=1,
    )
    fig.update_yaxes(
        title=dict(text="Vehicles", font=dict(family=FONT_SANS, size=13, color=TEXT)),
        tickfont=dict(family=FONT_MONO, size=11, color=SUBTLE),
        showgrid=True,
        gridcolor=GRID,
        zeroline=False,
    )
    return fig


# horizontal bar
def bar_chart(df):
    df_sorted = df.sort_values("Count", ascending=True)
    colors = [COLORS.get(v.lower(), AMBER) for v in df_sorted["Vehicle Type"]]
    fig = go.Figure(
        go.Bar(
            x=df_sorted["Count"],
            y=df_sorted["Vehicle Type"],
            orientation="h",
            marker=dict(color=colors),
            text=df_sorted["Count"],
            texttemplate="%{text}",
            textposition="outside",
            textfont=dict(family=FONT_MONO, size=13, color=TEXT),
            hovertemplate="%{y}: %{x}<extra></extra>",
        )
    )
    max_count = df["Count"].max()
    fig.update_layout(**_base_layout(height=300))
    fig.update_layout(bargap=0.35)
    fig.update_traces(marker=dict(color=colors, cornerradius=6), selector=dict(type="bar"))
    fig.update_xaxes(
        title=dict(text="Vehicles", font=dict(family=FONT_SANS, size=12, color=TEXT)),
        tickfont=dict(family=FONT_MONO, size=11, color=SUBTLE),
        range=[0, max_count * 1.18],
        nticks=5,
        showgrid=True,
        gridcolor=GRID,
        zeroline=False,
    )
    fig.update_yaxes(
        tickfont=dict(family=FONT_SANS, size=12, color=SUBTLE),
        showgrid=False,
    )
    return fig


# stacked bar (with a total line overlay)
def stacked_bar_chart(df):
    df = df.copy()
    df["time_label"] = pd.to_datetime(df["time"]).dt.strftime("%H:%M")
    totals = df[["car", "bus", "truck", "motorbike"]].sum(axis=1)

    fig = go.Figure()
    for vehicle in ["car", "bus", "truck", "motorbike"]:
        fig.add_trace(
            go.Bar(
                x=df["time_label"],
                y=df[vehicle],
                name=vehicle.capitalize(),
                marker=dict(color=COLORS[vehicle], cornerradius=4),
                width=0.35,
                hovertemplate=f"{vehicle.capitalize()}: " + "%{y}<extra></extra>",
            )
        )
    fig.add_trace(
        go.Scatter(
            x=df["time_label"],
            y=totals,
            mode="lines+markers+text",
            text=totals.astype(int).astype(str),
            textposition="top center",
            textfont=dict(family=FONT_MONO, size=10, color=TEXT),
            line=dict(color="white", width=1.5),
            marker=dict(size=6, color="white", line=dict(width=1, color=PANEL_2)),
            name="Total",
            hovertemplate="Total: %{y}<extra></extra>",
        )
    )
    fig.update_layout(barmode="stack", **_base_layout(height=300, showlegend=True))
    fig.update_xaxes(
        title=dict(text="Time", font=dict(family=FONT_SANS, size=12, color=TEXT)),
        tickfont=dict(family=FONT_MONO, size=10, color=SUBTLE),
        showgrid=False,
    )
    fig.update_yaxes(
        title=dict(text="Vehicles", font=dict(family=FONT_SANS, size=12, color=TEXT)),
        tickfont=dict(family=FONT_MONO, size=10, color=SUBTLE),
        showgrid=True,
        gridcolor=GRID,
        zeroline=False,
    )
    return fig