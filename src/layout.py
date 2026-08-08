import streamlit as st

BG_BASE = "#0A0E14"
BG_PANEL = "#10141C"
BG_PANEL_2 = "#161B26"
BORDER = "#242B38"
AMBER = "#FFB020"
TEAL = "#2DD4BF"
DANGER = "#FF5470"
TEXT = "#E8EAED"
MUTED = "#7B8794"

VEHICLE_ICON = {
    "motorbike": "🏍️",
    "car": "🚗",
    "bus": "🚌",
    "truck": "🚚",
}
VEHICLE_LABEL_VI = {
    "motorbike": "Motorbike",
    "car": "Car",
    "bus": "Bus",
    "truck": "Truck",
}
VEHICLE_COLOR = {
    "motorbike": TEAL,
    "car": "#22C55E",
    "bus": AMBER,
    "truck": DANGER,
}

# header
def render_header():
    header_html = (
        '<div class="ta-header">'
        '<div class="ta-header-badge">● LIVE VISION SYSTEM</div>'
        '<h1 class="ta-title">Traffic<span>AI</span></h1>'
        '<p class="ta-subtitle">Real-time vehicle detection &amp; counting system</p>'
        '</div>'
        '<div class="lane-divider"></div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)


# global styles
def render_ui_style():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;600&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        .stApp {{
            background: radial-gradient(120% 100% at 50% 0%, #0D1119 0%, {BG_BASE} 55%, #070A0F 100%);
            color: {TEXT};
        }}

        .block-container {{
            padding-top: 3.2rem;
            padding-bottom: 2.5rem;
            max-width: 1300px;
        }}

        /* ---------- Header ---------- */
        .ta-header {{ text-align: center; padding: 0.75rem 0 0.25rem 0; }}
        .ta-header-badge {{
            display: inline-block;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem;
            letter-spacing: 0.12em;
            color: {DANGER};
            background: rgba(255, 84, 112, 0.08);
            border: 1px solid rgba(255, 84, 112, 0.35);
            padding: 3px 10px;
            border-radius: 999px;
            margin-bottom: 10px;
        }}
        .ta-title {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 2.6rem;
            letter-spacing: -0.02em;
            color: {TEXT};
            margin: 0;
        }}
        .ta-title span {{
            background: linear-gradient(90deg, {AMBER}, {TEAL});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .ta-subtitle {{
            font-size: 0.95rem;
            color: {MUTED};
            margin-top: 4px;
        }}

        /* Neon glow signature divider */
        .lane-divider {{
            height: 0.5px;
            margin: 22px 0 26px 0;
            background: linear-gradient(
                90deg,
                transparent 0%,
                {TEAL} 15%,
                {AMBER} 50%,
                {TEAL} 85%,
                transparent 100%
            );
            box-shadow:
                0 0 5px rgba(255, 176, 32, 0.4),
                0 0 10px rgba(45, 212, 191, 0.25);
        }}

        /* ---------- Sidebar (control panel) ---------- */
        section[data-testid="stSidebar"] {{
            background: {BG_PANEL};
            border-right: 1px solid {BORDER};
        }}
        section[data-testid="stSidebar"] .block-container {{ padding-top: 1.5rem; }}

        /* ---------- Section labels ---------- */
        h3, h4 {{
            font-family: 'Space Grotesk', sans-serif !important;
            letter-spacing: -0.01em;
        }}

        /* ---------- Tabs ---------- */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 4px;
            border-bottom: 1px solid {BORDER};
        }}
        .stTabs [data-baseweb="tab"] {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 600;
            color: {MUTED};
            background: transparent;
            border-radius: 8px 8px 0 0;
            padding: 8px 18px;
        }}
        .stTabs [aria-selected="true"] {{
            color: {AMBER} !important;
            background: rgba(255, 176, 32, 0.08) !important;
            border-bottom: 2px solid {AMBER};
        }}

        /* ---------- Buttons ---------- */
        div.stButton > button {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 600;
            letter-spacing: 0.01em;
            color: #0A0E14;
            background: linear-gradient(90deg, {AMBER}, #FFCB66);
            border: none;
            border-radius: 10px;
            padding: 0.55rem 1.3rem;
            box-shadow: 0 6px 18px rgba(255, 176, 32, 0.22);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}
        div.stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 10px 24px rgba(255, 176, 32, 0.32);
            color: #0A0E14;
        }}
        div.stButton > button p {{ color: #0A0E14 !important; font-weight: 600; }}

        /* ---------- Inputs ---------- */
        div[data-baseweb="select"] > div,
        .stTextInput input, .stDateInput input, .stTimeInput input {{
            background: {BG_PANEL_2} !important;
            border: 1px solid {BORDER} !important;
            border-radius: 8px !important;
            color: {TEXT} !important;
        }}
        div[data-testid="stFileUploaderDropzone"] {{
            background: {BG_PANEL_2};
            border: 1.5px dashed {BORDER};
            border-radius: 12px;
        }}
        .stSlider [data-baseweb="slider"] div[role="slider"] {{
            background-color: {AMBER} !important;
            box-shadow: 0 0 0 4px rgba(255,176,32,0.18);
        }}
        .stSlider [data-testid="stTickBar"] {{ display: none; }}
        div[data-baseweb="slider"] > div > div {{ background: {TEAL} !important; }}

        .stRadio [role="radiogroup"] label {{
            background: {BG_PANEL_2};
            border: 1px solid {BORDER};
            border-radius: 8px;
            padding: 4px 12px;
            margin-right: 6px;
        }}

        /* ---------- Video / camera frame ---------- */
        div[data-testid="stImage"] {{
            position: relative;
            border-radius: 14px;
            border: 1px solid {BORDER};
            background: #05070B;
            padding: 8px;
            box-shadow: 0 0 0 1px rgba(45,212,191,0.06), 0 20px 40px rgba(0,0,0,0.45);
        }}

        /* ---------- Dataframe / table ---------- */
        div[data-testid="stDataFrame"] {{
            border-radius: 14px;
            overflow: hidden;
            background: {BG_PANEL_2};
            border: 1px solid {BORDER};
        }}

        /* ---------- Containers used as cards (history sessions) ---------- */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background: {BG_PANEL_2};
            border: 1px solid {BORDER} !important;
            border-radius: 12px;
        }}

        /* ---------- KPI cards ---------- */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin: 6px 0 4px 0;
        }}
        .kpi-card {{
            background: {BG_PANEL_2};
            border: 1px solid {BORDER};
            border-top: 3px solid var(--kpi-color, {AMBER});
            border-radius: 12px;
            padding: 14px 16px 12px 16px;
        }}
        .kpi-card .kpi-icon {{ font-size: 1.3rem; }}
        .kpi-card .kpi-label {{
            font-size: 0.74rem;
            color: {MUTED};
            margin-top: 4px;
        }}
        .kpi-card .kpi-value {{
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
            font-size: 1.7rem;
            color: {TEXT};
            margin-top: 2px;
        }}
        .kpi-total {{
            background: linear-gradient(120deg, rgba(255,176,32,0.10), rgba(45,212,191,0.06));
            border: 1px solid rgba(255,176,32,0.35);
            border-radius: 12px;
            padding: 14px 16px;
            margin-bottom: 10px;
        }}
        .kpi-total .kpi-label {{ font-size: 0.75rem; color: {MUTED}; letter-spacing: 0.04em; }}
        .kpi-total .kpi-value {{
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            font-size: 2rem;
            color: {AMBER};
        }}

        /* ---------- Status pill ---------- */
        .status-pill {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            color: {TEAL};
            background: rgba(45,212,191,0.08);
            border: 1px solid rgba(45,212,191,0.3);
            padding: 4px 12px;
            border-radius: 999px;
        }}

        /* ---------- Progress bar ---------- */
        div[data-testid="stProgress"] div[role="progressbar"] > div {{
            background: linear-gradient(90deg, {TEAL}, {AMBER});
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# reusable dashed lane divider used between sections instead of st.markdown("---")
def render_divider():
    st.markdown('<div class="lane-divider"></div>', unsafe_allow_html=True)


def render_kpi_cards(counts: dict):
    total = sum(counts.values())
    total_html = (
        '<div class="kpi-total">'
        '<div class="kpi-label">TOTAL VEHICLES</div>'
        f'<div class="kpi-value">{total}</div>'
        '</div>'
    )
    st.markdown(total_html, unsafe_allow_html=True)

    card_parts = []
    for vt, count in counts.items():
        color = VEHICLE_COLOR.get(vt, AMBER)
        icon = VEHICLE_ICON.get(vt, "🚘")
        label = VEHICLE_LABEL_VI.get(vt, vt.capitalize())
        card_parts.append(
            f'<div class="kpi-card" style="--kpi-color:{color};">'
            f'<div class="kpi-icon">{icon}</div>'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{count}</div>'
            '</div>'
        )
    grid_html = '<div class="kpi-grid">' + ''.join(card_parts) + '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)


def render_status_pill(text: str):
    st.markdown(f'<span class="status-pill">{text}</span>', unsafe_allow_html=True)