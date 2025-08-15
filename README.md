# 📊 Tra cứu & Phân tích điểm thi THPT 2025

Ứng dụng **Streamlit** hỗ trợ tra cứu vị trí của thí sinh trong phân phối điểm toàn quốc, xem phổ điểm, bảng mốc, xếp hạng ước tính và **quy đổi điểm giữa các khối** dựa trên phương pháp percentile.

---

## 🎯 Mục tiêu

- **Tra cứu**: Xác định vị trí điểm số của bạn so với toàn quốc theo từng khối/môn.
- **Phân tích**: Xem phổ điểm, bảng số lượng theo mốc và phần trăm trên/dưới.
- **Quy đổi**: Chuyển đổi điểm giữa các khối dựa trên nguyên tắc bảo toàn percentile.
- **Trực quan**: Hiển thị biểu đồ tương tác với Plotly.

---

## 📂 Cấu trúc dự án

```
.
├─ app.py                  # Ứng dụng Streamlit chính
├─ data/
│  └─ diem_2018.csv        # Dữ liệu mẫu
├─ src/
│  ├─ analysis.py          # Tính toán điểm, percentile, xếp hạng
│  ├─ conversion.py        # Quy đổi điểm giữa các khối
│  ├─ data_loader.py       # Tải dữ liệu CSV/XLSX
│  ├─ plots.py             # Vẽ biểu đồ phổ điểm, biểu đồ trung bình
│  ├─ preprocessing.py     # Tiền xử lý, tách môn ngoại ngữ, lọc dữ liệu
│  └─ ui.py                # Thành phần UI tái sử dụng
├─ requirements.txt        # Thư viện cần thiết
└─ README.md               # File hướng dẫn này
```

---

## ⚙️ Cài đặt

Yêu cầu:
- Python 3.10+
- pip

Bước cài đặt:

```bash
# Tạo môi trường ảo
python -m venv .venv
# Kích hoạt venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# Cài đặt thư viện
pip install --upgrade pip
pip install -r requirements.txt
```

Nội dung `requirements.txt` gợi ý:

```txt
streamlit>=1.35
numpy>=1.26
pandas>=2.0
polars>=0.20
plotly>=5.20
```

---


## ▶️ Chạy ứng dụng

```bash
streamlit run app.py
```

Sau khi chạy, mở trình duyệt tại **http://localhost:8501**.

---

## 🖱️ Cách sử dụng

1. **Chọn khối hoặc môn** trong sidebar.
2. **Nhập tổng điểm** (0–30, bước 0.01).
3. Bấm **"🔎 Tra cứu ngay"**.
4. Xem kết quả:
   - Thẻ chỉ số: điểm, Top %, xếp hạng.
   - Phổ điểm có đánh dấu vị trí của bạn.
   - Bảng số thí sinh theo mốc điểm.
   - Công cụ quy đổi điểm sang khối/môn khác.
5. Thử thay đổi khối/môn đích để so sánh tương quan.

---

## 📌 Ghi chú kỹ thuật

- **Backend dữ liệu**: 
  - CSV: ưu tiên đọc bằng Polars (nhanh hơn), fallback Pandas.
  - Excel: đọc bằng Pandas.
- **Tiền xử lý**:
  - Chuẩn hóa tên cột.
  - Tách "Ngoại ngữ" thành N1..N7 dựa trên "Mã môn ngoại ngữ".
- **Ngưỡng dữ liệu tối thiểu**: Chỉ hiển thị khối/môn có >= 500 thí sinh đủ dữ liệu.
- **Quy đổi điểm**: Dựa trên bảng percentile, nội suy tuyến tính.

---


## 🤝 Đóng góp

Rất hoan nghênh các ý tưởng mới, báo lỗi hoặc pull request.  
Bạn có thể:
- Mở issue nếu gặp lỗi hoặc muốn yêu cầu tính năng.
- Gửi PR cải thiện code, giao diện hoặc tài liệu.

