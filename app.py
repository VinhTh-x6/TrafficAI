import streamlit as st
import tempfile
import cv2
import pandas as pd
import os
import plotly.io as pio
import time
from layout import *
from track_count import tracking_counting
from charts import *
from history import render_history_tab, load_logs, init_db, save_log, LOCATIONS

# Streamlit page configuration and styling
st.set_page_config(page_title="TrafficAI", layout="wide")
pio.templates.default = "plotly_dark"
# render header and apply UI styles
render_header()
render_ui_style()
init_db()  

# session state
for key in ["done", "history", "final_counts"]:
    if key not in st.session_state:
        st.session_state[key] = False if key == "done" else None if key == "final_counts" else []
tab_run, tab_history = st.tabs(["🚀 Hệ thống", "📚 Xem lại"])
# Run tab
with tab_run:
    # input source
    st.markdown("### 📁 Tải video lên")
    video_file = st.file_uploader("Chọn file", type=["mp4"])
    location = st.selectbox("📍 Vị trí", LOCATIONS)
    datetime_input = st.datetime_input("📅 Thời gian", value=pd.Timestamp.now().to_pydatetime())
    run = st.button("🚀 Bắt đầu xử lý")
    output_video_path = os.path.join(tempfile.gettempdir(), "output.mp4")

    # process video
    if run:
        # set parameters based on source type
        if not video_file:
            st.warning("Vui lòng tải video lên để bắt đầu!")
            st.stop()
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(video_file.read())
        source = tfile.name
        cap = cv2.VideoCapture(source)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        col_video, col_table = st.columns([2, 1])
        history = []
        frame_id = 0
        # UI containers
        with col_video:
            st.markdown("### 🎥 Video hiển thị")
            video_box = st.empty()
            status_box = st.empty()
            progress_container = st.empty()
            progress_bar = progress_container.progress(0)
        with col_table:
            st.markdown("### 🚗 Bảng thống kê")
            table_box = st.empty()
            kpi_box = st.empty()
        # run tracking and counting
        generator = tracking_counting(
            source=source,
            model_path=r"D:\TrafficAI\runs\detect\train\weights\best.pt",
            output_path=output_video_path,
            mode="polygon",
            location=location
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
            kpi_box.markdown(f"##### Tổng phương tiện: **{total}**")
            # history for line chart
            history.append({
                "time": round(frame_id / fps, 2),
                "car": counts.get("car", 0),
                "bus": counts.get("bus", 0),
                "truck": counts.get("truck", 0),
                "motorbike": counts.get("motorbike", 0)
            })
            # update progress/status
            percent = int((frame_id / total_frames) * 100)
            progress_bar.progress(percent)
            status_box.markdown(f"🚦 Đang xử lý... **{percent}%**")

        progress_container.empty()
        # final status update
        status_box.markdown("✅ Hoàn thành")
        # save history and final counts to session state for visualization
        st.session_state.history = history
        st.session_state.final_counts = counts
        st.session_state.done = True
        if location:
            save_log(
                location.strip(),
                str(datetime_input),
                output_video_path,
                counts,
                history
            )

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

        col_pie, col_bar = st.columns(2)
        # bar chart
        with col_pie:
            st.subheader("📊 Phân bố phương tiện")
            st.pyplot(bar_chart(df))
        # line chart
        with col_bar:
            st.subheader("📈 Lưu lượng theo thời gian")
            st.pyplot(line_chart(df_line))
        # pie chart
        st.subheader("🟠 Tỷ lệ phương tiện")
        st.pyplot(pie_chart(df))
    

# History tab
with tab_history:
    render_history_tab(load_logs, pie_chart, bar_chart, line_chart, stacked_bar_chart)