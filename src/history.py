import sqlite3
import json
import pandas as pd
import streamlit as st
import os
from layout import VEHICLE_ICON, VEHICLE_COLOR, render_kpi_cards, render_divider

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
    c.execute("SELECT id, location, time, video, counts, history FROM traffic_logs")
    rows = c.fetchall()
    conn.close()
    return rows


# Delete logs (DB record + corresponding video file, if it still exists)
def delete_log(log_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT video FROM traffic_logs WHERE id=?", (log_id,))
    row = c.fetchone()
    if row and row[0] and os.path.exists(row[0]):
        try:
            os.remove(row[0])
        except OSError:
            pass

    c.execute("DELETE FROM traffic_logs WHERE id=?", (log_id,))
    conn.commit()
    conn.close()


# inline badge strip: icon + count per vehicle type, used on the collapsed session row
def _render_badge_strip(counts: dict):
    badges = ""
    for vt, count in counts.items():
        color = VEHICLE_COLOR.get(vt, "#7B8794")
        icon = VEHICLE_ICON.get(vt, "🚘")
        badges += (
            f'<span style="display:inline-flex;align-items:center;gap:4px;'
            f'font-family:\'JetBrains Mono\',monospace;font-size:0.78rem;'
            f'color:#E8EAED;background:rgba(255,255,255,0.03);'
            f'border:1px solid {color}55;border-radius:999px;'
            f'padding:2px 10px;margin-right:6px;">'
            f'{icon}&nbsp;{count}</span>'
        )
    st.markdown(badges, unsafe_allow_html=True)


# empty state, matching the run tab's idle card
def _render_empty_state():
    empty_html = (
        '<div class="kpi-card" style="text-align:center; padding:2.5rem 1rem; --kpi-color:#2DD4BF;">'
        '<div style="font-size:2rem;">🗂️</div>'
        '<div style="margin-top:8px; color:#E8EAED; font-family:\'Space Grotesk\',sans-serif; font-weight:600;">'
        'No history data yet</div>'
        '<div style="margin-top:4px; color:#7B8794; font-size:0.85rem;">'
        'Saved processing sessions will appear here.</div>'
        '</div>'
    )
    st.markdown(empty_html, unsafe_allow_html=True)


# Render the history tab
def render_history_tab(load_logs_fn, prepare_heatmap_data, bar_chart, line_chart, heatmap_chart, stacked_bar_chart):
    rows = load_logs_fn()
    if not rows:
        _render_empty_state()
        return

    # Selected location & date
    locations = sorted(list(set([r[1] for r in rows])))

    col_info1, col_info2 = st.columns(2)
    with col_info1:
        selected_loc = st.selectbox("📍 Location", locations, key="history_location_select")
    rows = [r for r in rows if r[1] == selected_loc]
    dates = sorted(list(set([pd.to_datetime(r[2]).date() for r in rows])))

    with col_info2:
        selected_date = st.date_input(
            "📅 Time",
            value=dates[-1],
            min_value=dates[0],
            max_value=dates[-1],
            format="DD/MM/YYYY",
            key="history_date_select"
        )
    rows_day = [r for r in rows if pd.to_datetime(r[2]).date() == selected_date]
    rows_day = sorted(rows_day, key=lambda x: x[2], reverse=True)

    render_divider()

    if not rows_day:
        _render_empty_state()
        return

    # Session list
    for idx, (log_id, loc, t, video, counts, history) in enumerate(rows_day):
        counts = json.loads(counts)
        history = json.loads(history)
        total = sum(counts.values())
        time_label = pd.to_datetime(t).strftime("%H:%M")

        with st.container(border=True):
            col_time, col_badges, col_btn, col_delete = st.columns([1.3, 3.7, 1.8, 0.9])
            with col_time:
                time_html = (
                    '<div style="font-family:\'JetBrains Mono\',monospace;">'
                    '<div style="color:#7B8794;font-size:0.7rem;">SESSION</div>'
                    f'<div style="color:#FFB020;font-weight:600;font-size:1rem;">🕒 {time_label}</div>'
                    '</div>'
                )
                st.markdown(time_html, unsafe_allow_html=True)
            with col_badges:
                st.markdown(f"<div style='color:#7B8794;font-size:0.7rem;margin-bottom:4px;'>TOTAL: {total} vehicles</div>", unsafe_allow_html=True)
                _render_badge_strip(counts)
            with col_btn:
                show_detail = st.toggle("Details", key=f"detail_{idx}")
            with col_delete:
                if st.button("🗑️", key=f"del_{log_id}", help="Delete this session"):
                    st.session_state[f"cf_{log_id}"] = True

            if st.session_state.get(f"cf_{log_id}"):
                confirm_html = (
                    '<div style="background:rgba(255,84,112,0.08);border:1px solid rgba(255,84,112,0.35);'
                    'border-radius:10px;padding:10px 14px;margin-top:8px;">'
                    '<span style="color:#FF5470;font-weight:600;">'
                    '⚠️ Delete this session? This action cannot be undone.</span>'
                    '</div>'
                )
                st.markdown(confirm_html, unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ Confirm delete", key=f"y_{log_id}", use_container_width=True):
                        delete_log(log_id)
                        st.session_state[f"cf_{log_id}"] = False
                        st.rerun()
                with c2:
                    if st.button("Cancel", key=f"n_{log_id}", use_container_width=True):
                        st.session_state[f"cf_{log_id}"] = False
                        st.rerun()

            # Detail
            if show_detail:
                render_divider()
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown("##### 🎥 Video")
                    if video and os.path.exists(video):
                        st.video(video)
                    else:
                        st.caption("Saved video file not found.")

                with col2:
                    st.markdown("##### 🚗 Statistics")
                    render_kpi_cards(counts)

                # Data line
                df_line = pd.DataFrame(history)
                df_line["time"] = df_line["time"].astype(int)
                df_line = df_line.groupby("time")[[
                    "car", "bus", "truck", "motorbike"
                ]].mean().reset_index()

                for col in ["car", "bus", "truck", "motorbike"]:
                    df_line[col] = (
                        df_line[col]
                        .rolling(5, min_periods=1)
                        .mean()
                    )

                df = pd.DataFrame({
                    "Vehicle Type": list(counts.keys()),
                    "Count": list(counts.values())
                })

                with st.expander("📋 Analysis Report"):
                    col3, col4 = st.columns(2)
                    with col3:
                        st.markdown("##### 📊 Vehicle Distribution")
                        with st.container(border=True):
                            st.plotly_chart(bar_chart(df), use_container_width=True, config={"displayModeBar": False})

                    with col4:
                        st.markdown("##### 📈 Traffic Flow Over Time")
                        with st.container(border=True):
                            st.plotly_chart(line_chart(df_line), use_container_width=True, config={"displayModeBar": False})

                    st.markdown("##### 🔥 Density Over Time")
                    df_heat = prepare_heatmap_data(df_line)
                    with st.container(border=True):
                        st.plotly_chart(heatmap_chart(df_heat), use_container_width=True, config={"displayModeBar": False})

    # Display stacked bar chart comparing sessions
    render_divider()
    st.markdown("##### 📊 Daily Overview")
    rows_all = []
    for log_id, loc, t, video, counts, history in rows_day:
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
        with st.container(border=True):
            st.plotly_chart(stacked_bar_chart(df_stack), use_container_width=True, config={"displayModeBar": False})