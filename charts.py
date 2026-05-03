import plotly.express as px

# style function
def style(fig):
    fig.update_layout(
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font=dict(color="white"),
        margin=dict(l=10, r=50, t=70, b=40)
    )
    return fig

# pie chart
def pie_chart(df):
    fig_pie = px.pie(
        df,
        names="Vehicle Type",
        values="Count",
        hole=0.5,
        color_discrete_sequence=["#00BFFF", "#66CD00", "#EEAD0E", "#FF4040"]
    )
    fig_pie.update_traces(
        textinfo="percent",
        marker=dict(line=dict(color="#111827", width=2)),
        domain=dict(x=[0.0, 0.85])
    )
    fig_pie.update_layout(legend=dict(
            yanchor="top",
            y=1,
            xanchor="left",
            x=0.84
        ))
    return style(fig_pie)

# line chart
def line_chart(df):
    fig_line = px.line(
        df,
        x="time",
        y=["car", "bus", "truck", "motorbike"],
        color_discrete_sequence=["#66CD00", "#EEAD0E", "#FF4040", "#00BFFF"]
    )
    fig_line.update_traces(line=dict(width=3))
    fig_line.update_layout(hovermode="x unified",
        legend=dict(
            x=0.93,
            xanchor="left",
            y=0.8,
            yanchor="middle"
        ),
        xaxis=dict(domain=[0.0, 0.9]), xaxis_title="Thời gian", yaxis_title="Số phương tiện", legend_title_text="")
    return style(fig_line)

# bar chart
def bar_chart(df):
    max_count = df["Count"].max()
    fig_bar = px.bar(
        df,
        y="Vehicle Type",
        x="Count",
        text="Count",
        color="Vehicle Type",
        orientation="h",
        color_discrete_sequence=["#00BFFF", "#66CD00", "#EEAD0E", "#FF4040"]
    )
    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(showlegend=False, yaxis_title="Loại phương tiện", xaxis_title="Số phương tiện")
    fig_bar.update_xaxes(range=[0, max_count * 1.2])
    return style(fig_bar)

# stacked bar chart for history comparison
def stacked_bar_chart(df):
    fig = px.bar(
        df,
        x="time_label",
        y=["car", "bus", "truck", "motorbike"],
        color_discrete_sequence=["#66CD00", "#EEAD0E", "#FF4040", "#00BFFF"],
        barmode="stack"
    )
    fig.update_traces(width=0.45)
    fig.update_layout(
        legend=dict(
            x=0.93,
            xanchor="left",
            y=0.8,
            yanchor="middle"
        ),
    xaxis=dict(domain=[0.0, 0.9]), xaxis_title="Thời gian", yaxis_title="Số phương tiện", legend_title_text="")
    return style(fig)