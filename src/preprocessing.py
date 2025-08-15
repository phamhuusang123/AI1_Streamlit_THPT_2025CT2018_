from typing import List, Tuple

# Polars có sẵn theo dự án của bạn; nếu muốn phòng hờ thì có thể bọc try/except
import polars as pl
import pandas as pd

# Danh sách môn (giữ nguyên) + bổ sung N1..N7 để detect sau khi tách
ALL_SUBJECTS = [
    "Toán","Văn","Lí","Hóa","Sinh","Tin học","Sử","Địa",
    "Giáo dục kinh tế và pháp luật","Công nghệ","Công nghệ nông nghiệp",
    "Công nghệ công nghiệp","Ngoại ngữ",
    # 7 mã ngoại ngữ
    "N1","N2","N3","N4","N5","N6","N7",
]

# Map mã ngoại ngữ -> tên (nếu cần hiển thị)
FOREIGN_LANGUAGE_CODES = {
    "N1": "Tiếng Anh",
    "N2": "Tiếng Nga",
    "N3": "Tiếng Pháp",
    "N4": "Tiếng Trung",
    "N5": "Tiếng Đức",
    "N6": "Tiếng Nhật",
    "N7": "Tiếng Hàn",
}

def detect_subjects(columns) -> List[str]:
    cols = [str(c).strip() for c in columns]
    return [s for s in ALL_SUBJECTS if s in cols]

# --- Split cho Pandas: tạo cột N1..N7 từ "Ngoại ngữ" + "Mã môn ngoại ngữ" ---
def _split_foreign_language_pandas(df: pd.DataFrame) -> pd.DataFrame:
    if "Ngoại ngữ" not in df.columns or "Mã môn ngoại ngữ" not in df.columns:
        return df
    df = df.copy()
    mmnn = df["Mã môn ngoại ngữ"].astype(str).str.upper().str.strip()

    # tạo cột N1..N7 (numeric), chỉ nhận điểm từ "Ngoại ngữ" khi đúng mã
    for code in ["N1","N2","N3","N4","N5","N6","N7"]:
        if code not in df.columns:
            df[code] = pd.NA
        mask = mmnn.eq(code)
        if mask.any():
            df.loc[mask, code] = df.loc[mask, "Ngoại ngữ"]

    # ép kiểu số cho 7 cột mới
    for code in ["N1","N2","N3","N4","N5","N6","N7"]:
        df[code] = pd.to_numeric(df[code], errors="coerce")

    # tuỳ chọn: thêm cột tên môn ngoại ngữ (text) nếu bạn muốn dùng
    df["Tên môn ngoại ngữ"] = mmnn.map(FOREIGN_LANGUAGE_CODES)

    return df


def _split_foreign_language_polars(df: pl.DataFrame) -> pl.DataFrame:
    mapping = {
        "N1": "Tiếng Anh",
        "N2": "Tiếng Nga",
        "N3": "Tiếng Pháp",
        "N4": "Tiếng Trung",
        "N5": "Tiếng Đức",
        "N6": "Tiếng Nhật",
        "N7": "Tiếng Hàn"
    }

    # Thêm cột tên môn ngoại ngữ
    df = df.with_columns(
        pl.col("Mã môn ngoại ngữ").map_elements(lambda x: mapping.get(x, None), return_dtype=pl.String).alias("Tên môn ngoại ngữ")
    )

    # Tạo các cột điểm theo môn ngoại ngữ
    for code, subject in mapping.items():
        df = df.with_columns(
            pl.when(pl.col("Mã môn ngoại ngữ") == code)
              .then(pl.col("Ngoại ngữ"))
              .otherwise(None)
              .alias(subject)
        )

    return df


def preprocess(df, backend: str) -> Tuple[object, List[str], str]:
    """
    Chuẩn hoá tên cột, tách N1..N7, ép kiểu số cho các cột môn.
    Trả về: (df_processed, subjects, backend)
    """
    if backend == "polars":
        assert isinstance(df, pl.DataFrame)
        # chuẩn hoá tên cột
        df = df.rename({c: str(c).strip() for c in df.columns})
        # tách ngoại ngữ
        df = _split_foreign_language_polars(df)

        # detect môn sau khi đã có N1..N7
        subjects = detect_subjects(df.columns)

        # ép float cho tất cả cột môn tìm được (nếu tồn tại)
        for c in subjects:
            if c in df.columns:
                try:
                    df = df.with_columns(pl.col(c).cast(pl.Float64, strict=False).alias(c))
                except Exception:
                    # bỏ qua nếu cột không cast được
                    pass
        return df, subjects, "polars"

    else:
        assert isinstance(df, pd.DataFrame)
        df = df.copy()
        df.columns = [str(c).strip() for c in df.columns]
        df = _split_foreign_language_pandas(df)

        subjects = detect_subjects(df.columns)
        for c in subjects:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        return df, subjects, "pandas"

# --- API giữ nguyên để app.py gọi: tự nhận backend theo kiểu df ---
def filter_candidates(df, subjects):
    """
    Lọc chỉ giữ thí sinh có đủ điểm cho toàn bộ 'subjects'.
    Tự động dùng .drop_nulls (Polars) hoặc .dropna (Pandas).
    """
    if not subjects:
        # trả bản sao để tránh side-effect
        try:
            if isinstance(df, pl.DataFrame):
                return df.clone()
        except Exception:
            pass
        return df.copy()

    # Polars
    try:
        if isinstance(df, pl.DataFrame):
            return df.drop_nulls(subset=subjects)
    except Exception:
        pass

    # Pandas
    if isinstance(df, pd.DataFrame):
        return df.dropna(subset=subjects).copy()

    # fallback
    return df
