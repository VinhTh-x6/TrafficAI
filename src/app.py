import streamlit as st
import tempfile
import cv2
import pandas as pd
import os
import plotly.io as pio
from layout import *
from track_count import tracking_counting
from charts import *
from history import render_history_tab, load_logs, init_db, save_log, LOCATIONS

# Streamlit page configuration and styling
st.set_page_config(page_title="TrafficAI", page_icon="🚦", layout="wide")
pio.templates.default = "plotly_dark"
render_ui_style()
render_header()
init_db()

# session state
for key in ["done", "history", "final_counts"]:
    if key not in st.session_state:
        st.session_state[key] = False if key == "done" else None if key == "final_counts" else []

# ------------------------------------------------------------------
# Sidebar — control panel: source, location, and detection settings
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown("#### 📁 Video Source")
    video_file = st.file_uploader("Choose file", type=["mp4"], label_visibility="collapsed")

    render_divider()

    st.markdown("#### 📍 Location &amp; Time")
    location = st.selectbox("Location", LOCATIONS)
    datetime_input = st.datetime_input("Time", value=pd.Timestamp.now().to_pydatetime())

    render_divider()

    st.markdown("#### ⚙️ Detection Settings")
    mode = st.radio("Counting Mode", ["Polygon", "Line"], horizontal=True)
    conf = st.slider(
        "Confidence", 0.1, 1.0, 0.25, 0.05,
        help="Low conf: detects more but is more error-prone.\nHigh conf: cleaner detection but may miss some."
    )
    show_region = st.checkbox(
        "Show " + ("Polygon" if mode == "Polygon" else "Line"), True
    )

    render_divider()
    run = st.button("🚀  Start Processing", use_container_width=True)

SAVED_VIDEOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_videos")
os.makedirs(SAVED_VIDEOS_DIR, exist_ok=True)

timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
output_video_path = os.path.join(SAVED_VIDEOS_DIR, f"traffic_{timestamp}.mp4")

tab_run, tab_history = st.tabs(["🚀 System", "📚 History"])

# ------------------------------------------------------------------
# Run tab
# ------------------------------------------------------------------
with tab_run:
    if run and not video_file:
        st.warning("⚠️ Please upload a video in the sidebar to start!")
        st.stop()

    if run:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(video_file.read())
        source = tfile.name
        cap = cv2.VideoCapture(source)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        col_video, col_table = st.columns([2, 1])
        history = []
        frame_id = 0
        with col_video:
            st.markdown("##### 🎥 Live Camera")
            video_box = st.empty()
            status_box = st.empty()
            progress_container = st.empty()
            progress_bar = progress_container.progress(0)
        with col_table:
            st.markdown("##### 🚗 Statistics")
            kpi_box = st.empty()

        generator = tracking_counting(
            source=source,
            model_path=r"models/best.pt",
            output_path=output_video_path,
            mode=mode.lower(),
            location=location,
            conf=conf,
            show_region=show_region
        )
        for frame, counts in generator:
            frame_id += 1
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            video_box.image(frame, use_container_width=True)

            with kpi_box.container():
                render_kpi_cards(counts)

            history.append({
                "time": round(frame_id / fps, 2),
                "car": counts.get("car", 0),
                "bus": counts.get("bus", 0),
                "truck": counts.get("truck", 0),
                "motorbike": counts.get("motorbike", 0)
            })

            percent = int((frame_id / total_frames) * 100) if total_frames else 0
            progress_bar.progress(min(percent, 100))
            status_box.markdown(
                f'<span class="status-pill">🚦 Processing — {percent}%</span>',
                unsafe_allow_html=True
            )

        progress_container.empty()
        # track_count.py already re-encodes the video to output_video_path as
        # H.264 (see the _reencode_to_h264 function in tracking_counting), so
        # there is no need to re-encode again here.
        status_box.markdown('<span class="status-pill">✅ Completed</span>', unsafe_allow_html=True)

        st.session_state.history = history
        st.session_state.final_counts = counts
        st.session_state.done = True
        if location:
            save_log(location.strip(), str(datetime_input), output_video_path, counts, history)

    # data visualization
    if st.session_state.done:
        render_divider()
        counts = st.session_state.final_counts
        df_final = pd.DataFrame({
            "Vehicle Type": list(counts.keys()),
            "Count": list(counts.values())
        })
        df_line = pd.DataFrame(st.session_state.history)
        df_line["time"] = df_line["time"].astype(int)
        df_line = df_line.groupby("time")[["car", "bus", "truck", "motorbike"]].mean().reset_index()
        for col in ["car", "bus", "truck", "motorbike"]:
            df_line[col] = df_line[col].rolling(5, min_periods=1).mean()

        col_bar, col_line = st.columns(2)
        with col_bar:
            st.markdown("##### 📊 Vehicle Distribution")
            with st.container(border=True):
                st.plotly_chart(bar_chart(df_final), use_container_width=True, config={"displayModeBar": False})
        with col_line:
            st.markdown("##### 📈 Traffic Flow Over Time")
            with st.container(border=True):
                st.plotly_chart(line_chart(df_line), use_container_width=True, config={"displayModeBar": False})

        st.markdown("##### 🔥 Density Over Time")
        df_heat = prepare_heatmap_data(df_line)
        with st.container(border=True):
            st.plotly_chart(heatmap_chart(df_heat), use_container_width=True, config={"displayModeBar": False})
    elif not run:
        empty_html = (
            '<div class="kpi-card" style="text-align:center; padding:2.5rem 1rem; --kpi-color:#2DD4BF;">'
            '<div style="font-size:2rem;">📡</div>'
            '<div style="margin-top:8px; color:#E8EAED; font-family:\'Space Grotesk\',sans-serif; font-weight:600;">'
            'No processing session yet</div>'
            '<div style="margin-top:4px; color:#7B8794; font-size:0.85rem;">'
            'Upload a video in the left sidebar and click "Start Processing" to begin monitoring.</div>'
            '</div>'
        )
        st.markdown(empty_html, unsafe_allow_html=True)

# ------------------------------------------------------------------
# History tab
# ------------------------------------------------------------------
with tab_history:
    render_history_tab(load_logs, prepare_heatmap_data, bar_chart, line_chart, heatmap_chart, stacked_bar_chart)