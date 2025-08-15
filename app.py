import streamlit as st
import pandas as pd
import polars as pl

from src.data_loader import load_data
from src.preprocessing import preprocess, filter_candidates
from src.analysis import compute_totals, build_percentile_table, percentile_of_score, rank_of_score, counts_at_thresholds
from src.conversion import convert_score_via_percentile
from src.plots import histogram_with_score
from src.ui import render_header, render_stat_cards

st.set_page_config(page_title="Tra cứu điểm THPT 2025", layout="wide")

# ---------- helpers ----------
def df_len(df_obj):
    if isinstance(df_obj, pl.DataFrame):
        return df_obj.height
    return len(df_obj)

def count_non_null(df_obj, col, backend):
    if backend == "polars":
        return int(df_obj.select(pl.col(col).is_not_null().sum()).item())
    else:
        return int(df_obj[col].notna().sum())

def df_copy(df_obj, backend):
    return df_obj.clone() if backend == "polars" else df_obj.copy()

# --- Header ---
render_header()
st.write("")

# --- Load data ---
DATA_PATH = "data/diem_2018.csv"
try:
    df_raw, backend = load_data(DATA_PATH, use_polars_if_possible=True)
except Exception as e:
    st.error(f"Lỗi khi đọc dữ liệu: {e}")
    st.stop()

# --- Preprocess ---
df_proc, subjects, backend = preprocess(df_raw, backend)
if len(subjects) == 0:
    st.error("Không tìm thấy cột môn hợp lệ trong file dữ liệu.")
    st.stop()

# --- Build blocks ---
BLOCKS = {
    "A00": ["Toán","Lí","Hóa"],
    "A01": ["Toán","Lí","Ngoại ngữ"],
    "B00": ["Toán","Hóa","Sinh"],
    "C00": ["Văn","Sử","Địa"],
    "D01": ["Văn","Toán","Ngoại ngữ"],
    "D15": ["Văn","Địa","Ngoại ngữ"],

    # Biến thể ngoại ngữ theo mã N1..N7
    "A01_N1": ["Toán","Lí","N1"], "A01_N2": ["Toán","Lí","N2"], "A01_N3": ["Toán","Lí","N3"],
    "A01_N4": ["Toán","Lí","N4"], "A01_N5": ["Toán","Lí","N5"], "A01_N6": ["Toán","Lí","N6"], "A01_N7": ["Toán","Lí","N7"],

    "B04_N1": ["Toán","Sinh","N1"], "B04_N2": ["Toán","Sinh","N2"], "B04_N3": ["Toán","Sinh","N3"],
    "B04_N4": ["Toán","Sinh","N4"], "B04_N5": ["Toán","Sinh","N5"], "B04_N6": ["Toán","Sinh","N6"], "B04_N7": ["Toán","Sinh","N7"],

    "D01_N1": ["Văn","Toán","N1"], "D01_N2": ["Văn","Toán","N2"], "D01_N3": ["Văn","Toán","N3"],
    "D01_N4": ["Văn","Toán","N4"], "D01_N5": ["Văn","Toán","N5"], "D01_N6": ["Văn","Toán","N6"], "D01_N7": ["Văn","Toán","N7"],

    "D15_N1": ["Văn","Địa","N1"], "D15_N2": ["Văn","Địa","N2"], "D15_N3": ["Văn","Địa","N3"],
    "D15_N4": ["Văn","Địa","N4"], "D15_N5": ["Văn","Địa","N5"], "D15_N6": ["Văn","Địa","N6"], "D15_N7": ["Văn","Địa","N7"],

    # Một số khối bổ sung
    "A02": ["Toán","Lí","Sinh"],
    "A03": ["Toán","Lí","Sử"],
    "A04": ["Toán","Lí","Địa"],
    "A05": ["Toán","Hóa","Sử"],
    "A06": ["Toán","Hóa","Địa"],
    "A07": ["Toán","Sử","Địa"],
    "B01": ["Toán","Sinh","Sử"],
    "B02": ["Toán","Sinh","Địa"],
    "B03": ["Toán","Sinh","Giáo dục kinh tế và pháp luật"],
    "C01": ["Văn","Toán","Lí"],
    "C02": ["Văn","Toán","Hóa"],
    "C03": ["Văn","Toán","Sử"],
    "C04": ["Văn","Toán","Địa"],
    "C05": ["Văn","Hóa","Sử"],
    "C06": ["Văn","Hóa","Địa"],
    "C07": ["Văn","Sử","Sinh"],
    "C08": ["Văn","Hóa","Giáo dục kinh tế và pháp luật"],
    "C09": ["Văn","Lí","Giáo dục kinh tế và pháp luật"],
    "C10": ["Văn","Hóa","Tin học"],
    "C12": ["Văn","Sinh","Tin học"],
}


MIN_STUDENTS_PER_BLOCK = 500
available_blocks = []

for code, subs in BLOCKS.items():
    if all(sub in subjects for sub in subs):
        valid_students = filter_candidates(df_proc, subs)
        if df_len(valid_students) >= MIN_STUDENTS_PER_BLOCK:
            available_blocks.append(code)

for subj in subjects:
    try:
        cnt = count_non_null(df_proc, subj, backend)
        if cnt >= MIN_STUDENTS_PER_BLOCK:
            available_blocks.append(subj)
    except Exception:
        pass

if not available_blocks:
    available_blocks = subjects

default_block = "A00" if all(s in subjects for s in ["Toán","Lí","Hóa"]) else subjects[0]

# --- FIX 1: Giữ state cho sel_block ---
if "sel_block" not in st.session_state:
    st.session_state.sel_block = default_block

st.session_state.sel_block = st.sidebar.selectbox(
    "Chọn khối/môn",
    available_blocks,
    index=available_blocks.index(st.session_state.sel_block),
    key="sel_block_select"
)
sel_block = st.session_state.sel_block

user_score = st.sidebar.number_input(
    "Nhập tổng điểm",
    min_value=0.0, max_value=30.0, value=21.0, step=0.25
)

# --- FIX 2: Cờ submitted ---
if "submitted" not in st.session_state:
    st.session_state.submitted = False

if st.sidebar.button("🔎 Tra cứu ngay"):
    st.session_state.submitted = True

show_results = st.session_state.submitted

# --- Tính totals ---
if sel_block in BLOCKS:
    subs = [s for s in BLOCKS[sel_block] if s in subjects]
    df_filtered = filter_candidates(df_proc, subs)
    totals_arr = compute_totals(df_filtered, subs, backend=backend)
elif sel_block in subjects:
    df_filtered = filter_candidates(df_proc, [sel_block])
    totals_arr = compute_totals(df_filtered, [sel_block], backend=backend)
else:
    df_filtered = df_copy(df_proc, backend)
    totals_arr = compute_totals(df_filtered, subjects[:3], backend=backend)

st.sidebar.markdown(f"**Số thí sinh được tính:** {len(totals_arr):,}")

# --- Hiển thị kết quả ---
if show_results:
    if len(totals_arr) == 0:
        st.warning("Không có đủ dữ liệu để tính cho lựa chọn này.")
    else:
        pct = percentile_of_score(totals_arr, user_score)
        rank = rank_of_score(totals_arr, user_score)
        top_pct = round(100.0 - pct, 2)

        cards = {
            f"Điểm (khối {sel_block})": f"{user_score:.2f}",
            "Top % (toàn quốc)": f"{top_pct}%",
            "Xếp hạng (ước tính)": f"#{rank:,}",
        }
        render_stat_cards(cards)

        st.plotly_chart(
            histogram_with_score(
                totals_arr, user_score, bin_min=0, bin_max=30, bin_step=1,
                title=f"Phổ điểm - Khối {sel_block} (toàn quốc)"
            ),
            use_container_width=True
        )

        thr_df = pd.DataFrame(counts_at_thresholds(totals_arr)).rename(
            columns={"moc": "Từ mốc", "count": "Số thí sinh >= mốc", "pct": "% tổng"}
        )
        st.markdown("### Bảng số thí sinh theo mốc điểm (>= mốc)")
        st.dataframe(thr_df, use_container_width=True)

        # ---- Quy đổi điểm ----
        st.markdown("### Quy đổi điểm (theo percentiles)")

        # --- FIX 3: Giữ state cho target_block ---
        if "target_block" not in st.session_state:
            st.session_state.target_block = available_blocks[0]

        if st.session_state.target_block not in available_blocks:
            st.session_state.target_block = available_blocks[0]

        st.session_state.target_block = st.selectbox(
            "Chọn khối đích để quy đổi",
            available_blocks,
            index=available_blocks.index(st.session_state.target_block),
            key="target_block_select"
        )
        target_block = st.session_state.target_block

        if target_block in BLOCKS:
            dst_subjs = [s for s in BLOCKS[target_block] if s in subjects]
        elif target_block in subjects:
            dst_subjs = [target_block]
        else:
            dst_subjs = subjects[:3]

        if dst_subjs:
            df_dst = filter_candidates(df_proc, dst_subjs)
            dst_totals = compute_totals(df_dst, dst_subjs, backend=backend)
        else:
            dst_totals = compute_totals(df_proc, dst_subjs, backend=backend)

        if target_block == sel_block:
            converted = user_score
        else:
            if len(totals_arr) == 0 or len(dst_totals) == 0:
                st.warning("Không đủ dữ liệu để quy đổi giữa hai khối.")
                converted = float("nan")
            else:
                src_table = build_percentile_table(totals_arr)
                dst_table = build_percentile_table(dst_totals)
                converted = convert_score_via_percentile(src_table, dst_table, user_score)

        if pd.isna(converted):
            st.markdown("- Không thể quy đổi do thiếu dữ liệu.")
        else:
            st.markdown(
                f"- Điểm **{user_score:.2f}** (khối {sel_block}) "
                f"≈ **{converted:.2f}** (khối {target_block}) theo percentiles"
            )

        equals_same = int((totals_arr == user_score).sum())
        above_same = int((totals_arr > user_score).sum())
        st.markdown(f"- Tổng thí sinh trong dữ liệu (được tính): **{len(totals_arr):,}**")
        st.markdown(f"- Số thí sinh điểm cao hơn bạn: **{above_same:,}**")
        st.markdown(f"- Số thí sinh cùng điểm: **{max(equals_same-1, 0):,}**")
else:
    st.info("Nhấn 'Tra cứu ngay' trong sidebar để bắt đầu.")