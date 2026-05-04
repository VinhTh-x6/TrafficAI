import matplotlib.pyplot as plt
import seaborn as sns

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

def create_ax(figsize=(7, 4)):
    sns.set_theme(style="white")
    fig, ax = plt.subplots(figsize=figsize, dpi=120)
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

# pie
def pie_chart(df):
    fig, ax = create_ax((2, 1))
    labels = df["Vehicle Type"]
    values = df["Count"]
    colors = [COLORS[x.lower()] for x in labels]
    wedges, _, autotexts = ax.pie(
        values,
        startangle=90,
        colors=colors,
        autopct=lambda p: f"{p:.0f}%",
        pctdistance=0.72,
        radius=0.85,
        center=(-0.22, 0),
        wedgeprops=dict(
            width=0.40,
            edgecolor=PANEL,
            linewidth=2.2
        )
    )
    for t in autotexts:
        t.set_color("white")
        t.set_fontsize(8)
        t.set_fontweight("bold")
    ax.legend(
        labels,
        loc="center left",
        bbox_to_anchor=(0.88, 0.5),
        frameon=False,
        labelcolor=SUBTLE,
        fontsize=6
    )
    ax.set_aspect("equal")
    fig.tight_layout(pad=0.8)
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
    ax.set_xlabel("Thời gian", fontsize=25)
    ax.set_ylabel("Số phương tiện", fontsize=25)
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
    ax.set_xlabel("Số phương tiện", fontsize=25)
    ax.set_ylabel("")
    ax.tick_params(labelsize=25)
    fig.tight_layout(pad=1.4)
    return fig

# stacked bar
def stacked_bar_chart(df):
    fig, ax = create_ax((5, 2.5))
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