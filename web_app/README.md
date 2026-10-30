# Web Application: VN100 Feature Extraction & Mantegna Relational Studio

> **Lưu ý phạm vi kiến trúc:** Thư mục `web_app/` chứa toàn bộ mã nguồn của hệ thống giao diện tương tác web (Web Studio). Đây là công cụ trực quan hóa hỗ trợ nằm ngoài phạm vi mô hình học máy chính của tiểu luận.

---

## 1. Mục Đích & Vai Trò
- Cho phép người dùng hoặc hội đồng đánh giá tương tác trực quan với kết quả của Bước 2 (Tiền xử lý) và Bước 3 (Trích chọn đặc trưng & Thiết lập không gian khoảng cách Mantegna).
- Cung cấp giao diện trực tiếp để:
  * Kiểm toán dữ liệu thô (Data Audit).
  * Chạy thử nghiệm quy trình làm sạch với các tham số tùy chọn (ngưỡng bao phủ, tỷ lệ lọc ngày lễ, phương pháp điền khuyết).
  * Tra cứu 8 chỉ số đặc trưng tài chính của 98 cổ phiếu (lợi suất, biến động, Sharpe, Skewness, Kurtosis).
  * Xem trực quan biểu đồ phân phối khoảng cách Mantegna ($0 \le d \le 2$).
  * Tương tác với Bản đồ nhiệt (Canvas Heatmap) chuyển đổi giữa Hệ số tương quan Pearson ($\rho$) và Khoảng cách Mantegna ($d$).
  * Tra cứu Top 10 cặp đồng pha nhất (cùng cụm) và Top 10 cặp trực giao phân kỳ (đa dạng hóa).

---

## 2. Cấu Trúc Thư Mục `web_app/`
```
web_app/
├── main.py              # Backend FastAPI server & API endpoints
├── templates/
│   └── index.html       # Giao diện người dùng đơn trang (Tailwind CSS, Chart.js, HTML5 Canvas)
└── README.md            # Tài liệu hướng dẫn sử dụng
```

---

## 3. Hướng Dẫn Khởi Chạy

Chạy lệnh sau từ thư mục gốc dự án:
```powershell
py -3.12 web_app/main.py
```

Sau đó mở trình duyệt tại:
**http://127.0.0.1:8000**

---

## 4. Các API Endpoints Chính
* `GET /`: Phục vụ giao diện dashboard người dùng.
* `GET /api/audit`: Trả về thống kê kiểm toán dữ liệu thô 100 mã.
* `POST /api/process`: Thực thi pipeline tiền xử lý và trích chọn đặc trưng.
* `GET /api/heatmap_sample`: Trả về ma trận tương quan và ma trận khoảng cách của 15 cổ phiếu trụ cột HOSE.
