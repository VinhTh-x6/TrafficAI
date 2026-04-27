import streamlit as st
import tempfile
import cv2
import pandas as pd
import os
import plotly.express as px
import plotly.io as pio
from track_count import tracking_counting

st.set_page_config(page_title="TrafficAI", layout="wide")
pio.templates.default = "plotly_dark"

# header
st.markdown("""
<h1 style='text-align:center; color:#00C2FF;'>🚦 TrafficAI System</h1>
<p style='text-align:center; color:gray;'>Real-time Vehicle Detection & Counting System</p>
""", unsafe_allow_html=True)

# UI style
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}
/* Plotly */
div[data-testid="stPlotlyChart"] {
    background: #111827;
    border-radius: 14px;
    padding: 10px;
    box-shadow: 0px 6px 25px rgba(0,0,0,0.5);
}
/* Image */
div[data-testid="stImage"] {
    border-radius: 16px;
    border: 1px solid #38BDF8;
    box-shadow: 0 0 20px rgba(56,189,248,0.4);
    background: rgba(17,24,39,0.8);
    padding: 6px;
}
/* Table */
div[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
    background: #0B1220;
    border: 1px solid #38BDF8;
    box-shadow: 0 10px 30px rgba(56,189,248,0.25);
    padding: 8px;
}
div[data-testid="stDataFrame"] table tbody tr:hover {
    background-color: rgba(56,189,248,0.08);
    transition: 0.2s;
}
</style>
""", unsafe_allow_html=True)
# session state
for key in ["done", "history", "final_counts"]:
    if key not in st.session_state:
        st.session_state[key] = False if key == "done" else None if key == "final_counts" else []

# input
video_file = st.file_uploader("Upload video", type=["mp4"])
run = st.button("🚀 Run System")
output_video_path = os.path.join(tempfile.gettempdir(), "output.mp4")

# process video
if video_file and run:
    # save uploaded video to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tfile:
        tfile.write(video_file.read())
        video_path = tfile.name
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    col_video, col_table = st.columns([2, 1])
    history = []
    frame_id = 0
    # stream video & update table in real-time
    with col_video:
        st.markdown("### 🎥 Video Stream")
        video_box = st.empty()
        status_box = st.empty()
        progress_container = st.empty()
        progress_bar = progress_container.progress(0)
        download_video = st.empty()
    with col_table:
        st.markdown("### 🚗 Vehicle Counts Table")
        table_box = st.empty()
        kpi_box = st.empty()
        download_csv = st.empty()
    # loop through video frames and update UI
    for frame, counts in tracking_counting(
        video_path,
        r"D:\TrafficAI\runs\detect\train\weights\best.pt",
        output_video_path
    ):
        frame_id += 1
        # convert BGR to RGB for display
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_box.image(frame, use_container_width=True)

        df = pd.DataFrame({
            "Vehicle Type": list(counts.keys()),
            "Count": list(counts.values())
        })
        # update table & KPI
        table_box.dataframe(df, use_container_width=True)
        total = sum(counts.values())
        kpi_box.markdown(f"##### Total Vehicles: **{total}**")
        # history for line chart
        history.append({
            "time": round(frame_id / fps, 2),
            "car": counts.get("car", 0),
            "bus": counts.get("bus", 0),
            "truck": counts.get("truck", 0),
            "motorbike": counts.get("motorbike", 0)
        })
        # update progress
        percent = int((frame_id / total_frames) * 100)
        progress_bar.progress(percent)
        status_box.markdown(f"🚦 Processing... **{percent}%**")

    progress_container.empty()
    status_box.markdown("✅ Completed")
    # download video & csv
    with download_video:
        with open(output_video_path, "rb") as f:
            st.download_button("📥 Download Video", f, "traffic_result.mp4", on_click='ignore')
    with download_csv:
        st.download_button(
            "📥 Download CSV",
            df.to_csv(index=False),
            "vehicle_count.csv",
            on_click='ignore'
        )
    # save history and final counts to session state for visualization
    st.session_state.history = history
    st.session_state.final_counts = counts
    st.session_state.done = True

# style function
def style(fig):
    fig.update_layout(
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font=dict(color="white"),
        margin=dict(l=10, r=10, t=40, b=10)
    )
    return fig

# data visualization
if st.session_state.done:
    st.markdown("---")
    counts = st.session_state.final_counts
    df_final = pd.DataFrame({
        "Vehicle Type": list(counts.keys()),
        "Count": list(counts.values())
    })
    col_pie, col_line = st.columns(2)

    # pie chart
    with col_pie:
        st.subheader("🟠 Vehicle Ratio")
        fig_pie = px.pie(
            df_final,
            names="Vehicle Type",
            values="Count",
            hole=0.6,
            color_discrete_sequence=["#38BDF8", "#22C55E", "#F97316", "#A855F7"]
        )
        fig_pie.update_traces(
            textinfo="percent",
            pull=[0.05] * len(df_final),
            marker=dict(line=dict(color="#111827", width=2))
        )
        st.plotly_chart(style(fig_pie), use_container_width=True)

    # line chart
    with col_line:
        st.subheader("📈 Traffic Over Time")
        df_line = pd.DataFrame(st.session_state.history)
        df_line["time"] = df_line["time"].astype(int)
        df_line = df_line.groupby("time")[[
            "car", "bus", "truck", "motorbike"
        ]].mean().reset_index()

        for col in ["car", "bus", "truck", "motorbike"]:
            df_line[col] = df_line[col].rolling(5, min_periods=1).mean()
        fig_line = px.line(
            df_line,
            x="time",
            y=["car", "bus", "truck", "motorbike"],
            color_discrete_sequence=["#38BDF8", "#22C55E", "#F97316", "#A855F7"]
        )

        fig_line.update_traces(line=dict(width=3))
        fig_line.update_layout(hovermode="x unified", xaxis_title="Time (s)", yaxis_title="Vehicle  Count")
        st.plotly_chart(style(fig_line), use_container_width=True)

    # bar chart
    st.subheader("📊 Vehicle Distribution")
    fig_bar = px.bar(
        df_final,
        x="Vehicle Type",
        y="Count",
        text="Count",
        color="Vehicle Type",
        color_discrete_sequence=["#38BDF8", "#22C55E", "#F97316", "#A855F7"]
    )
    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(showlegend=False, yaxis_title="Vehicle  Count")
    st.plotly_chart(style(fig_bar), use_container_width=True)