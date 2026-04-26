import streamlit as st
import tempfile
import cv2
import pandas as pd
from track_count import tracking_counting
import plotly.express as px

st.set_page_config(page_title="TrafficAI", layout="wide")
st.markdown(
    """
    <h1 style='text-align:center; color:#00C2FF;'>🚦 TrafficAI System</h1>
    <p style='text-align:center; color:gray;'>Real-time Vehicle Detection & Counting System</p>
    """,
    unsafe_allow_html=True
)

video_file = st.file_uploader("Upload video", type=["mp4"])
run = st.button("🚀 Run System")

if "done" not in st.session_state:
    st.session_state.done = False
if "history" not in st.session_state:
    st.session_state.history = []
if "final_counts" not in st.session_state:
    st.session_state.final_counts = None

if video_file and run:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tfile:
        tfile.write(video_file.read())
        video_path = tfile.name

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    col_video, col_table = st.columns([2, 1])
    history = [] 
    frame_id = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    with col_video:
        st.markdown("### 🎥 Video Stream")
        video_box = st.empty()
        status_box = st.empty()
        progress_container = st.empty()
        progress_bar = progress_container.progress(0)
    with col_table:
        st.markdown("### 🚗 Vehicle Count Table")
        table_box = st.empty()
        kpi_box = st.empty()
    
    for frame, counts in tracking_counting(
        video_path,
        r"D:\TrafficAI\runs\detect\train\weights\best.pt"
    ):
        frame_id += 1
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_box.image(frame, use_container_width=True)
        df = pd.DataFrame({
            "Vehicle Type": list(counts.keys()),
            "Count": list(counts.values())
        })

        table_box.dataframe(df, use_container_width=True)
        total = sum(counts.values())
        kpi_box.markdown(f"##### Total Vehicles: {total}")
        history.append({
            "time": round(frame_id / fps, 2),
            "car": counts.get("car", 0),
            "bus": counts.get("bus", 0),
            "truck": counts.get("truck", 0),
            "motorbike": counts.get("motorbike", 0)
        })
        percent = int((frame_id / total_frames) * 100)
        progress_bar.progress(percent)
        status_box.markdown(f"""🚦 Processing... **{percent}%**""")

    progress_container.empty()
    status_box.markdown("✅ Completed")
    st.session_state.history = history
    st.session_state.final_counts = counts
    st.session_state.done = True

if st.session_state.done:
    st.markdown("---")
    counts = st.session_state.final_counts
    df_final = pd.DataFrame({
        "Vehicle Type": list(counts.keys()),
        "Count": list(counts.values())
    })
    col_pie, col_line = st.columns(2)

    # PIE CHART
    with col_pie:
        st.subheader("🟠 Vehicle Ratio")
        fig_pie = px.pie(
            df_final,
            names="Vehicle Type",
            values="Count",
            hole=0.4
        )

        st.plotly_chart(fig_pie, use_container_width=True)

    # LINE CHART 
    with col_line:
        st.subheader("📈 Traffic Over Time")
        df_line = pd.DataFrame(st.session_state.history)
        df_line["time"] = df_line["time"].astype(int)
        df_line = df_line.groupby("time")[[
            "car", "bus", "truck", "motorbike"
        ]].mean().reset_index()

        df_line["car"] = df_line["car"].rolling(3, min_periods=1).mean()
        df_line["bus"] = df_line["bus"].rolling(3, min_periods=1).mean()
        df_line["truck"] = df_line["truck"].rolling(3, min_periods=1).mean()
        df_line["motorbike"] = df_line["motorbike"].rolling(3, min_periods=1).mean()

        fig_line = px.line(
            df_line,
            x="time",
            y=["car", "bus", "truck", "motorbike"],
        )

        st.plotly_chart(fig_line, use_container_width=True)

    # BAR CHART
    st.subheader("📊 Vehicle Distribution")
    fig_bar = px.bar(
        df_final,
        x="Vehicle Type",
        y="Count",
        text="Count"
    )

    fig_bar.update_traces(textposition="outside")

    fig_bar.update_layout(
        height=450,
        template="plotly_dark",
        margin=dict(l=20, r=20, t=30, b=20)
    )

    st.plotly_chart(fig_bar, use_container_width=True)