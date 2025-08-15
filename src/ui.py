# src/ui.py
import streamlit as st

def render_header():
    st.markdown("""
    <div style="border-radius:12px;padding:22px;background:linear-gradient(90deg,#6a8ef6,#8f4fcf);box-shadow:0 8px 30px rgba(0,0,0,0.08);">
      <h1 style="color:white;margin:0;font-size:28px;">Tra cứu & phân tích điểm thi THPT 2025</h1>
      <div style="color:rgba(255,255,255,0.9);margin-top:6px;">Tra cứu vị trí của bạn theo dữ liệu toàn quốc </div>
    </div>
    """, unsafe_allow_html=True)

def sidebar_controls(blocks, default_block, default_score=21.0):
    st.sidebar.title("Thiết lập tra cứu")
    block = st.sidebar.selectbox("Chọn khối/môn", blocks, index=blocks.index(default_block) if default_block in blocks else 0)
    score = st.sidebar.number_input("Nhập tổng điểm", min_value=0.0, max_value=30.0, value=float(default_score), step=0.25)
    do = st.sidebar.button("🔎 Tra cứu ngay")
    return block, score, do

def render_stat_cards(cards: dict):
    cols = st.columns(len(cards))
    for col, (k, v) in zip(cols, cards.items()):
        with col:
            st.markdown(f"<div style='background:#fff;padding:14px;border-radius:10px;box-shadow:0 6px 18px rgba(0,0,0,0.04)'><div style='color:#666'>{k}</div><div style='font-size:22px;font-weight:700'>{v}</div></div>", unsafe_allow_html=True)
