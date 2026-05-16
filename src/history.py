import sqlite3
import json
import pandas as pd
import streamlit as st
import os

# Constants
DB_PATH = "traffic.db"
LOCATIONS = [
    "Cầu Giấy - Trần Quý Kiên - C167.10-PTZ",
    "Cầu Giấy - Trần Đăng Ninh - C166.10-PTZ"
]

# Initialize the database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS traffic_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            time TEXT,
            video TEXT,
            counts TEXT,
            history TEXT
        )
    """)
    conn.commit()
    conn.close()

# Save log to database
def save_log(location, time_input, video, counts, history):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO traffic_logs (location, time, video, counts, history)
        VALUES (?, ?, ?, ?, ?)
    """, (
        location,
        time_input,
        video,
        json.dumps(counts),
        json.dumps(history)
    ))
    conn.commit()
    conn.close()

# Load logs from database
def load_logs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT location, time, video, counts, history FROM traffic_logs")
    rows = c.fetchall()
    conn.close()
    return rows

# Render the history tab
def render_history_tab(load_logs_fn, prepare_heatmap_data, bar_chart, line_chart, heatmap_chart, stacked_bar_chart):
    rows = load_logs_fn()
    if not rows:
        st.info("Chưa có dữ liệu lịch sử nào!")
        return
    # Selected location & date
    locations = sorted(list(set([r[0] for r in rows])))
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        selected_loc = st.selectbox("📍 Vị trí", locations, key="history_location_select")
    rows = [r for r in rows if r[0] == selected_loc]
    dates = sorted(list(set([pd.to_datetime(r[1]).date() for r in rows])))
    with col_info2:
        selected_date = st.date_input(
            "📅 Thời gian",
            value=dates[-1],
            min_value=dates[0],
            max_value=dates[-1],
            format="DD/MM/YYYY",
            key="history_date_select"
        )
    rows_day = [r for r in rows if pd.to_datetime(r[1]).date() == selected_date]
    grouped = {}
    for loc, t, video, counts, history in rows_day:
        grouped.setdefault(loc, []).append((t, video, counts, history))
    # Display sessions for each location
    for loc, sessions in grouped.items():
        sessions = sorted(sessions, reverse=True)
        # Display each session with video, table, and charts
        for idx, (t, video, counts, history) in enumerate(sessions):
            counts = json.loads(counts)
            history = json.loads(history)
            df = pd.DataFrame({
                "Vehicle Type": list(counts.keys()),
                "Count": list(counts.values())
            })
            # Use expander to show details for each session
            time_label = pd.to_datetime(t).strftime("%H:%M")
            with st.expander(f"🕒 {time_label} | 🚗 {sum(counts.values())} xe"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown("### 🎥 Video")
                    if video and os.path.exists(video):
                        st.video(video)
                with col2:
                    st.markdown("### 🚗 Bảng thống kê")
                    st.dataframe(df, use_container_width=True)
                    st.markdown(f"##### Tổng phương tiện: **{sum(counts.values())}**")
                # Display charts
                col3, col4 = st.columns(2)
                with col3:
                    st.markdown("### 📊 Phân bố phương tiện")
                    st.pyplot(bar_chart(df))
                with col4:
                    st.markdown("### 📈 Lưu lượng theo thời gian")
                    df_line = pd.DataFrame(history)
                    df_line["time"] = df_line["time"].astype(int)
                    df_line = df_line.groupby("time")[[
                        "car", "bus", "truck", "motorbike"
                    ]].mean().reset_index()
                    for col in ["car", "bus", "truck", "motorbike"]:
                        df_line[col] = df_line[col].rolling(5, min_periods=1).mean()
                    st.pyplot(line_chart(df_line))
                st.markdown("### 🔥 Mật độ theo thời gian")
                df_heat = prepare_heatmap_data(df_line)
                st.pyplot(heatmap_chart(df_heat))
                
        # Display stacked bar chart comparing sessions
        st.subheader(f"📊 So sánh các phiên ghi nhận")
        rows_all = []
        for loc, t, video, counts, history in rows:
            counts = json.loads(counts)
            rows_all.append({
                "time": t,
                "car": counts.get("car", 0),
                "bus": counts.get("bus", 0),
                "truck": counts.get("truck", 0),
                "motorbike": counts.get("motorbike", 0)
            })
        if rows_all:
            df_stack = pd.DataFrame(rows_all)
            df_stack = df_stack.sort_values("time")
            df_stack["time_label"] = pd.to_datetime(df_stack["time"]).dt.strftime("%d/%m/%Y\n%H:%M")
            st.pyplot(stacked_bar_chart(df_stack))  