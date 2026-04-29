import streamlit as st
import tempfile
import cv2
import pandas as pd
import os
import plotly.express as px
import plotly.io as pio
import time
from layout import *
from track_count import tracking_counting
from charts import *

# Streamlit page configuration and styling
st.set_page_config(page_title="TrafficAI", layout="wide")
pio.templates.default = "plotly_dark"
# render header and UI style
render_header()
render_ui_style()

# session state
for key in ["done", "history", "final_counts"]:
    if key not in st.session_state:
        st.session_state[key] = False if key == "done" else None if key == "final_counts" else []

# input source
st.subheader("📡 Input Source")
source_type = st.radio("Choose source type", ["Upload Video", "Phone Camera"])
video_file = None
camera_url = None
# set parameters based on source type
if source_type == "Upload Video":
    st.markdown("### 📁 Upload your video")
    count_mode = "region"
    video_file = st.file_uploader("Choose file", type=["mp4"])
elif source_type == "Phone Camera":
    st.markdown("### 📱 Connect your phone camera")
    count_mode = "Line"
    camera_url = st.text_input("Enter camera URL", "http://192.168.1.222:8080/video")
run = st.button("🚀 Run System")
start_time = time.time()
output_video_path = os.path.join(tempfile.gettempdir(), "output.mp4")

# process video
if run:
    # set parameters based on source type
    total_frames = 1000
    fps = 25
    if source_type == "Upload Video":
        if not video_file:
            st.warning("Please upload video")
            st.stop()
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(video_file.read())
        source = tfile.name
        cap = cv2.VideoCapture(source)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        source_type_run = "upload"
        mode = "polygon"
    else:
        source = camera_url
        source_type_run = "camera"
        mode = "line"
        region = None

    col_video, col_table = st.columns([2, 1])
    history = []
    frame_id = 0
    # UI containers
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
    # run tracking and counting
    generator = tracking_counting(
        source=source,
        model_path=r"D:\TrafficAI\runs\detect\train\weights\best.pt",
        output_path=output_video_path,
        source_type=source_type_run,
        mode=mode
    )
    for frame, counts in generator:
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
        # update progress/status
        if source_type == "Upload Video":
            percent = int((frame_id / total_frames) * 100)
            progress_bar.progress(percent)
            status_box.markdown(f"🚦 Processing... **{percent}%**")
        else:
            elapsed = time.time() - start_time
            status_box.markdown(f"📡 Live Camera | ⏱ {elapsed:.1f}s")

    progress_container.empty()
    # final status update
    if source_type == "Upload Video":
        status_box.markdown("✅ Completed")
    else:
        elapsed = time.time() - start_time
        status_box.markdown(f"📹 Camera session finished | ⏱ Total time: {elapsed:.2f}s")
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

# data visualization
if st.session_state.done:
    st.markdown("---")
    # final counts for pie and bar charts
    counts = st.session_state.final_counts
    df_final = pd.DataFrame({
        "Vehicle Type": list(counts.keys()),
        "Count": list(counts.values())
    })
    # prepare line chart data
    df_line = pd.DataFrame(st.session_state.history)
    df_line["time"] = df_line["time"].astype(int)
    df_line = df_line.groupby("time")[[
        "car", "bus", "truck", "motorbike"
    ]].mean().reset_index()
    for col in ["car", "bus", "truck", "motorbike"]:
        df_line[col] = df_line[col].rolling(5, min_periods=1).mean()

    col_pie, col_line = st.columns(2)
    # pie chart
    with col_pie:
        st.subheader("🟠 Vehicle Ratio")
        st.plotly_chart(pie_chart(df_final), use_container_width=True)

    # line chart
    with col_line:
        st.subheader("📈 Traffic Over Time")
        st.plotly_chart(line_chart(df_line), use_container_width=True)

    # bar chart
    st.subheader("📊 Vehicle Distribution")
    st.plotly_chart(bar_chart(df_final), use_container_width=True) 