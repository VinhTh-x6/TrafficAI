import plotly.express as px

# style function
def style(fig):
    fig.update_layout(
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font=dict(color="white"),
        margin=dict(l=10, r=10, t=40, b=10)
    )
    return fig

# pie chart
def pie_chart(df):
    fig_pie = px.pie(
        df,
        names="Vehicle Type",
        values="Count",
        hole=0.6,
        color_discrete_sequence=["#38BDF8", "#22C55E", "#F97316", "#A855F7"]
    )
    fig_pie.update_traces(
        textinfo="percent",
        pull=[0.05] * len(df),
        marker=dict(line=dict(color="#111827", width=2))
    )
    return style(fig_pie)

# line chart
def line_chart(df):
    fig_line = px.line(
        df,
        x="time",
        y=["car", "bus", "truck", "motorbike"],
        color_discrete_sequence=["#38BDF8", "#22C55E", "#F97316", "#A855F7"]
    )
    fig_line.update_traces(line=dict(width=3))
    fig_line.update_layout(hovermode="x unified", legend_title_text="", xaxis_title="Thời gian", yaxis_title="Số phương tiện")
    return style(fig_line)

# bar chart
def bar_chart(df):
    fig_bar = px.bar(
        df,
        x="Vehicle Type",
        y="Count",
        text="Count",
        color="Vehicle Type",
        color_discrete_sequence=["#38BDF8", "#22C55E", "#F97316", "#A855F7"]
    )
    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(showlegend=False, xaxis_title="Loại phương tiện", yaxis_title="Số phương tiện")
    return style(fig_bar)

# stacked bar chart for history comparison
def stacked_bar_chart(df):
    fig = px.bar(
        df,
        x="time_label",
        y=["car", "bus", "truck", "motorbike"],
        color_discrete_sequence=["#38BDF8", "#22C55E", "#F97316", "#A855F7"],
        barmode="stack"
    )
    fig.update_traces(width=0.45)
    fig.update_layout(legend=dict(
        orientation="h", 
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=-0.03), 
        legend_title_text="",
        xaxis_title="Thời gian", yaxis_title="Số phương tiện")
    return style(fig)