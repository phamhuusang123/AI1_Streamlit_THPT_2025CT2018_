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
    # Khối A
    "A00": ["Toán", "Lí", "Hóa"],
    "A01": ["Toán", "Lí", "Tiếng Anh"],
    "A02": ["Toán", "Lí", "Sinh"],
    "A03": ["Toán", "Lí", "Sử"],
    "A04": ["Toán", "Lí", "Địa"],
    "A05": ["Toán", "Hóa", "Sử"],
    "A06": ["Toán", "Hóa", "Địa"],
    "A07": ["Toán", "Sử", "Địa"],
    "A08": ["Toán", "Sử", "Giáo dục kinh tế và pháp luật"],
    "A09": ["Toán", "Địa", "Giáo dục kinh tế và pháp luật"],
    "A10": ["Toán", "Lí", "Giáo dục kinh tế và pháp luật"],
    "A11": ["Toán", "Hóa", "Giáo dục kinh tế và pháp luật"],

    # Khối B
    "B00": ["Toán", "Hóa", "Sinh"],
    "B02": ["Toán", "Sinh", "Địa"],
    "B03": ["Toán", "Sinh", "Văn"],
    "B04": ["Toán", "Sinh", "Giáo dục kinh tế và pháp luật"],
    "B08": ["Toán", "Sinh", "Tiếng Anh"],

    # Khối C
    "C00": ["Văn", "Sử", "Địa"],
    "C01": ["Văn", "Toán", "Lí"],
    "C02": ["Văn", "Toán", "Hóa"],
    "C03": ["Văn", "Toán", "Sử"],
    "C04": ["Văn", "Toán", "Địa"],
    "C05": ["Văn", "Lí", "Hóa"],
    "C08": ["Văn", "Hóa", "Sinh"],
    "C12": ["Văn", "Sử", "Sinh"],
    "C13": ["Văn", "Sinh", "Địa"],
    "C14": ["Văn", "Toán", "Giáo dục kinh tế và pháp luật"],
    "C17": ["Văn", "Hóa", "Giáo dục kinh tế và pháp luật"],
    "C19": ["Văn", "Sử", "Giáo dục kinh tế và pháp luật"],
    "C20": ["Văn", "Địa", "Giáo dục kinh tế và pháp luật"],

    # Khối D
    "D01": ["Văn", "Toán", "Tiếng Anh"],
    "D02": ["Văn", "Toán", "Tiếng Nga"],
    "D03": ["Văn", "Toán", "Tiếng Pháp"],
    "D04": ["Văn", "Toán", "Tiếng Trung"],
    "D05": ["Văn", "Toán", "Tiếng Đức"],
    "D06": ["Văn", "Toán", "Tiếng Nhật"],
    "D07": ["Toán", "Hóa", "Tiếng Anh"],
    "D08": ["Toán", "Sinh", "Tiếng Anh"],
    "D09": ["Toán", "Sử", "Tiếng Anh"],
    "D10": ["Toán", "Địa", "Tiếng Anh"],
    "D11": ["Văn", "Lí", "Tiếng Anh"],
    "D12": ["Văn", "Hóa", "Tiếng Anh"],
    "D13": ["Văn", "Sinh", "Tiếng Anh"],
    "D14": ["Văn", "Sử", "Tiếng Anh"],
    "D15": ["Văn", "Địa", "Tiếng Anh"],
    "D20": ["Toán", "Địa", "Tiếng Trung"],
    "D21": ["Toán", "Hóa", "Tiếng Đức"],
    "D22": ["Toán", "Hóa", "Tiếng Nga"],
    "D23": ["Toán", "Hóa", "Tiếng Nhật"],
    "D24": ["Toán", "Hóa", "Tiếng Pháp"],
    "D25": ["Toán", "Hóa", "Tiếng Trung"],
    "D26": ["Toán", "Lí", "Tiếng Đức"],
    "D27": ["Toán", "Lí", "Tiếng Nga"],
    "D28": ["Toán", "Lí", "Tiếng Nhật"],
    "D29": ["Toán", "Lí", "Tiếng Pháp"],
    "D30": ["Toán", "Lí", "Tiếng Trung"],
    "D31": ["Toán", "Sinh", "Tiếng Đức"],
    "D32": ["Toán", "Sinh", "Tiếng Nga"],
    "D33": ["Toán", "Sinh", "Tiếng Nhật"],
    "D34": ["Toán", "Sinh", "Tiếng Pháp"],
    "D35": ["Toán", "Sinh", "Tiếng Trung"],
    "D42": ["Văn", "Địa", "Tiếng Nga"],
    "D43": ["Văn", "Địa", "Tiếng Nhật"],
    "D44": ["Văn", "Địa", "Tiếng Pháp"],
    "D45": ["Văn", "Địa", "Tiếng Trung"],
    "D55": ["Văn", "Lí", "Tiếng Trung"],
    "D63": ["Văn", "Sử", "Tiếng Nhật"],
    "D64": ["Văn", "Sử", "Tiếng Pháp"],
    "D65": ["Văn", "Sử", "Tiếng Trung"],
    "D66": ["Văn", "Giáo dục kinh tế và pháp luật", "Tiếng Anh"],
    "D68": ["Văn", "Giáo dục kinh tế và pháp luật", "Tiếng Nga"],
    "D70": ["Văn", "Giáo dục kinh tế và pháp luật", "Tiếng Pháp"],
    "D71": ["Văn", "Giáo dục kinh tế và pháp luật", "Tiếng Trung"],
    "D84": ["Toán", "Tiếng Anh", "Giáo dục kinh tế và pháp luật"],
}


MIN_STUDENTS_PER_BLOCK = 1
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
    min_value=0.0, max_value=30.0, value=21.0, step=0.01
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