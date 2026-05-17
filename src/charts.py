import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# theme
BG = "#0f172a"
PANEL = "#111827"
GRID = "#334155"
TEXT = "#e5e7eb"
SUBTLE = "#94a3b8"
COLORS = {
    "car": "#22c55e",
    "bus": "#f59e0b",
    "truck": "#ef4444",
    "motorbike": "#38bdf8"
}

# style
def create_ax(figsize=(7, 4)):
    sns.set_theme(style="white")
    fig, ax = plt.subplots(figsize=figsize, dpi=200)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(PANEL)
    ax.grid(axis="y", color=GRID, alpha=0.16, linewidth=0.8)
    ax.grid(axis="x", visible=False)

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.tick_params(colors=SUBTLE, labelsize=6)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)
    return fig, ax

# heatmap data
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
    fig, ax = create_ax((4, 2))
    heat_df = (
        df.set_index("time")[["car", "bus", "truck", "motorbike"]]
        .T
    )
    sns.heatmap(
        heat_df,
        ax=ax,
        cmap="YlGnBu",
        square=True,      
        linewidths=0.6,    
        linecolor=BG,
        cbar_kws={
            "pad": 0.15,
            "fraction": 0.03,
            "shrink": 0.6       
        }
    )
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize=5, colors=SUBTLE)
    ax.set_xlabel("Thời gian", fontsize=6, color=TEXT, labelpad=2)
    ax.set_ylabel("")
    ax.set_yticklabels(
        ["Car", "Bus", "Truck", "Motorbike"],
        rotation=0,
        fontsize=5,        
        color=SUBTLE
    )
    # ax.set_xticks(range(len(heat_df.columns)))
    ax.set_xticklabels(
        [str(x) for x in heat_df.columns],
        rotation=0,
        fontsize=5,        
        color=SUBTLE
    )
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout(pad=0.3)  
    return fig

# line
def line_chart(df):
    fig, ax = create_ax((15, 8))
    for vehicle in ["car", "bus", "truck", "motorbike"]:
        ax.plot(
            df["time"],
            df[vehicle],
            linewidth=5,
            label=vehicle.capitalize(),
            color=COLORS[vehicle]
        )
    ax.set_xlabel("Thời gian", fontsize=26)
    ax.set_ylabel("Số phương tiện", fontsize=26)
    ax.legend(
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        frameon=False,
        labelcolor=SUBTLE,
        fontsize=25
    )
    ax.grid(axis="y", color=GRID, alpha=0.16, linewidth=5)
    ax.tick_params(labelsize=25)
    fig.tight_layout(pad=0.8)
    return fig

# horizontal bar 
def bar_chart(df):
    fig, ax = create_ax((15, 8))
    df_sorted = df.sort_values("Count", ascending=True)
    bars = ax.barh(
        df_sorted["Vehicle Type"],
        df_sorted["Count"],
        color=[COLORS[v.lower()] for v in df_sorted["Vehicle Type"]],
        height=0.72,
        linewidth=2
    )
    max_count = df["Count"].max()
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + max_count * 0.015,
            bar.get_y() + bar.get_height() / 2,
            f"{int(width)}",
            va="center",
            color=TEXT,
            fontsize=25
        )
    ax.grid(axis="y", color=GRID, alpha=0.16, linewidth=5)
    ax.set_xlim(0, max_count * 1.12)
    ax.set_xlabel("Số phương tiện", fontsize=26)
    ax.set_ylabel("")
    ax.tick_params(labelsize=25)
    fig.tight_layout(pad=1.4)
    return fig

# stacked bar
def stacked_bar_chart(df):
    fig, ax = create_ax((max(6, len(df) * 0.6), 2.5))
    df["time_label"] = pd.to_datetime(df["time"]).dt.strftime("%H:%M")
    x = df["time_label"]
    bottom = [0] * len(df)
    for vehicle in ["car", "bus", "truck", "motorbike"]:
        ax.bar(
            x,
            df[vehicle],
            bottom=bottom,
            label=vehicle.capitalize(),
            color=COLORS[vehicle],
            width=0.5,
            linewidth=0.4
        )
        bottom = [b + v for b, v in zip(bottom, df[vehicle])]
    totals = df[["car", "bus", "truck", "motorbike"]].sum(axis=1)
    ax.plot(
        x,
        totals,
        linewidth=1,
        marker="o",
        markersize=2,
        color="white",
        label="Total"
    )
    for i, total in enumerate(totals):
        ax.text(
            i,
            total + 3,  
            str(int(total)),
            ha="center",
            va="bottom",
            fontsize=6,
            color=TEXT
        )
    ax.set_xlabel("Thời gian", fontsize=7)
    ax.set_ylabel("Số phương tiện", fontsize=7)
    ax.legend(
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        frameon=False,
        labelcolor=SUBTLE,
        fontsize=6
    )
    fig.tight_layout(pad=0.8)
    return fig