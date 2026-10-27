# Ghi chú tổng hợp nội dung phục vụ Báo cáo Tiểu luận

> **Đề tài:** Phân nhóm cổ phiếu theo mức độ đồng biến động giá phục vụ đa dạng hóa danh mục đầu tư  
> **Mục đích file:** Ghi chép siêu ngắn gọn các quyết định, cơ sở dữ liệu và kết quả thực hiện để đưa vào các chương của báo cáo tiểu luận.

---

## 1. Xác định đề tài & Phạm vi nghiên cứu (Đưa vào Chương 1: Mở đầu)
- **Thị trường mục tiêu:** Thị trường Chứng khoán Việt Nam (Sàn HOSE).
- **Không gian cổ phiếu:** Rổ chỉ số **VN100** (gồm 30 mã VN30 + 70 mã VNMidCap đại diện vốn hóa và thanh khoản cao nhất thị trường).
- **Khung thời gian nghiên cứu:** **01/01/2022 – 23/10/2026 (~5 năm)**.
  - *Ý nghĩa khoa học:* Trải qua trọn vẹn chu kỳ thị trường: Downtrend mạnh (2022), Tích lũy/Phục hồi (2023–2024) và Ổn định (2025–2026), là điều kiện lý tưởng để kiểm định độ ổn định của các cụm qua thời gian (Adjusted Rand Index - ARI).

---

## 2. Nguồn gốc dữ liệu & Chuẩn hóa (Đưa vào Chương 2: Thu thập Dữ liệu)
- **Nguồn cấp dữ liệu gốc:** Sở Giao dịch Chứng khoán TP.HCM (HOSE) thông qua hệ thống tài chính toàn cầu **Yahoo Finance** (định danh mã `.VN`) và API nội địa (TCBS / VCI).
- **Cấu trúc trường dữ liệu thô:** Gồm 8 trường chuẩn: `date`, `open`, `high`, `low`, `close`, `adj_close`, `volume`, `symbol`.
- **Cơ sở khoa học về giá:** Bắt buộc sử dụng **`adj_close` (Giá đóng cửa điều chỉnh)** thay vì `close` danh nghĩa để tính chuỗi lợi suất logarit $r_t = \ln(P_t / P_{t-1})$.
  - *Lý do:* `adj_close` đã chiết khấu toàn bộ sự kiện quyền (cổ tức tiền mặt, cổ phiếu thưởng, phát hành thêm), loại bỏ biến động giá giả tạo.
- **Dữ liệu đối chứng ngành (Ground Truth):** Chuẩn phân ngành quốc tế **ICB (Industry Classification Benchmark)** được chuẩn hóa về cấp 1 & cấp 2 (11 nhóm ngành lớn: Ngân hàng, Bất động sản, Thép, Dịch vụ tài chính, Bán lẻ, Công nghệ, Năng lượng...) lưu tại `data/metadata/vn100_symbols.csv`.

---

## 3. Kiến trúc kỹ thuật & Kết quả thu thập (Đưa vào Chương 2 hoặc Phụ lục)
- **Cấu trúc pipeline:**
  - `src/data_loader.py`: Module đa nguồn (Multi-backend), sử dụng dynamic import (`importlib`) chống lỗi phụ thuộc phiên bản.
  - `scripts/crawl_vn100.py`: Script tự động hóa với tính năng Resume (tự động bỏ qua mã đã cào thành công nếu mất mạng).
- **Kết quả thu thập thô (Phase 1):** Đạt **100/100 mã cổ phiếu** được lưu trữ độc lập tại `data/raw/{symbol}.csv`.

---

## 4. Phát hiện thực tế làm đầu vào Tiền xử lý (Đưa vào Chương 3: Tiền xử lý)
- **Hiện tượng dữ liệu khuyết:** Một số cổ phiếu chuyển sàn hoặc niêm yết muộn trong giai đoạn 2022–2026 (tiêu biểu như `VTP` chuyển sang HOSE từ 12/03/2024 chỉ có ~686 phiên thay vì ~1200 phiên).
- **Định hướng xử lý tiếp theo:**
  - Căn chỉnh lịch giao dịch chung (Trading Calendar Alignment).
  - Thiết lập ngưỡng chấp nhận dữ liệu lịch sử tối thiểu (Threshold Filtering) hoặc nội suy để đảm bảo ma trận tương quan không bị lệch chuỗi thời gian.

---

## 5. Khung sườn đề cương các chương tiếp theo của Báo cáo
1. **Chương 1: Tổng quan bài toán & Cơ sở lý thuyết** (Đồng biến động giá, Khoảng cách Mantegna $d = \sqrt{2(1-\rho)}$, 4 tiêu chí liên kết Single, Complete, Average, Ward, Giảm chiều PCA + K-Means).
2. **Chương 2: Dữ liệu & Tiền xử lý** (Rổ VN100, Giá điều chỉnh, Căn chỉnh chuỗi lợi suất logarit, Xử lý missing).
3. **Chương 3: Thực nghiệm Phân cụm & Lựa chọn số cụm tối ưu** (Dendrogram, Clustermap, Silhouette Score, So sánh Agglomerative vs K-Means/PCA).
4. **Chương 4: Đánh giá độ ổn định & Đối chiếu Nhóm ngành** (Chỉ số ARI qua các chu kỳ 2022-2026, Đối chiếu ma trận nhầm lẫn Cụm vs Ngành ICB).
5. **Chương 5: Ứng dụng Đa dạng hóa Danh mục Đầu tư** (Chiến lược chọn 1 mã đại diện/cụm, Backtest hiệu suất so với Random Portfolio & Thị trường: Sharpe, Volatility, MDD).
6. **Chương 6: Kết luận & Hướng phát triển**.
