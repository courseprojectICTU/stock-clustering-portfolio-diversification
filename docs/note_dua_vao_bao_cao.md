# Ghi Chú Đề Tài: Phân Cụm Cổ Phiếu VN100 & Đa Dạng Hóa Danh Mục Đầu Tư

> **Môn học:** Học máy (Machine Learning) - HK7  
> **Mục đích:** Ghi chú ngắn gọn các quyết định kỹ thuật, công thức toán và số liệu thực nghiệm từ các notebook để thuận tiện mở rộng thành Báo cáo Tiểu luận hoàn chỉnh.

---

## 1. Tiến Trình Thực Hiện Đề Tài (Hiện Tại: Đã Hoàn Thành 6/10 Bước)

| Bước | Tên nhiệm vụ | Trạng thái | Sản phẩm / Kết quả đạt được |
| :---: | :--- | :---: | :--- |
| **01** | **Thu thập dữ liệu** | **Đã hoàn thành** | Dữ liệu thô 100 mã VN100 (`data/raw/*.csv`) và metadata phân ngành ICB (`vn100_symbols.csv`) |
| **02** | **Xác định đặc trưng & quy tắc tiền xử lý** | **Đã hoàn thành** | Chọn giá `adj_close`, xác định ngưỡng thiếu $\ge 90\%$, quy tắc bỏ ngày lễ, quy tắc Forward-fill |
| **03** | **Tiền xử lý dữ liệu** | **Đã hoàn thành** | Loại 2 mã thiếu (`VTP`, `NAB`), lọc 68 ngày nghỉ lễ, điền khuyết 48 ô $\to$ Ma trận sạch $1.187 \times 98$ |
| **04** | **Trích chọn đặc trưng** | **Đã hoàn thành** | Tính lợi suất logarit ($1.186 \times 98$), kiểm định đuôi béo Kurtosis = 3.86, tính 8 chỉ số tài chính |
| **05** | **Biểu diễn tương quan & khoảng cách** | **Đã hoàn thành** | Chỉ ra nhược điểm Euclid, tính Pearson $\rho \in [-1, 1]$ và khoảng cách Mantegna $d = \sqrt{2(1-\rho)}$ |
| **06** | **Phân chia dữ liệu Train / Test theo thời gian** | **Đã hoàn thành** | Chia In-Sample (2022-2024, 62.3%) / Out-of-Sample (2025-2026, 37.7%), xuất bản ma trận Train |
| **07** | **Huấn luyện phân cụm phân cấp trên tập Train** | *Bước tiếp theo* | Thử nghiệm 4 linkage (Single, Complete, Average, Ward), dựng Dendrogram, đo hệ số Cophenetic (CCC) |
| **08** | **Xác định số cụm tối ưu & Đối chứng** | *Kế hoạch* | Quét Silhouette Score $k \in [3, 15]$ chọn $k$ tối ưu, đối chứng với mô hình PCA + K-Means |
| **09** | **Đánh giá độ ổn định & Đối chiếu ngành** | *Kế hoạch* | Kiểm tra ổn định qua thời gian (chỉ số ARI các pha thị trường), đối chiếu cụm với 11 ngành ICB |
| **10** | **Ứng dụng đa dạng hóa danh mục & Backtest** | *Kế hoạch* | Chọn danh mục đại diện các cụm, kiểm thử lịch sử Out-of-Sample so với danh mục ngẫu nhiên và VN-Index |

- **Tiến độ tổng thể:** Đã hoàn thành 6/10 bước (đạt 60% khối lượng đề tài), hoàn tất toàn bộ giai đoạn chuẩn bị dữ liệu, biểu diễn khoảng cách và phân tách ranh giới Train / Test sạch sẽ.
- **Trọng tâm tiếp theo:** Chuyển sang giai đoạn huấn luyện các mô hình phân cụm trên tập Train (Bước 7 & 8) và thực nghiệm tài chính ứng dụng Backtest trên tập Test (Bước 9 & 10).

---

## 2. Dữ Liệu & Phạm Vi Nghiên Cứu (Chương 1 & 2)

- **Không gian mẫu nghiên cứu:**
  - Rổ chỉ số **VN100** trên sàn HOSE (gồm 30 mã VN30 và 70 mã VNMidCap).
  - Đại diện cho hơn 90% giá trị vốn hóa và thanh khoản toàn thị trường chứng khoán Việt Nam.
  - Nhãn phân ngành đối chứng: Chuẩn **ICB** (11 nhóm ngành cấp 1) lưu tại `data/metadata/vn100_symbols.csv`.
- **Giai đoạn thu thập:**
  - Từ **01/01/2022 đến 23/10/2026 (~5 năm)**.
  - Bao quát đầy đủ các chu kỳ thị trường: giảm mạnh (2022), phục hồi (2023 - 2024), đi ngang tích lũy (2025 - 2026).
  - Thuận lợi để kiểm tra tính ổn định của các cụm qua thời gian bằng chỉ số Adjusted Rand Index (ARI).
- **Loại giá sử dụng:**
  - Bắt buộc dùng **giá đóng cửa điều chỉnh (`adj_close`)** để tính lợi suất.
  - Lý do: Đã loại trừ tác động chia tách cổ phiếu, phát hành thêm và trả cổ tức. Giá đóng cửa thô (`close`) chứa các bước nhảy giá giả tạo, làm sai lệch kết quả mô hình.

---

## 3. Tiền Xử Lý Dữ Liệu (Notebook 02 - Chương 2)

- **Thu thập ban đầu:** 100/100 mã cổ phiếu với 1.255 mốc thời gian theo lịch dương (`data/raw/`).
- **Lọc mã thiếu dữ liệu (ngưỡng chấp nhận $\ge 90\%$):**
  - Loại bỏ 2 mã: `VTP` (chỉ có 42.6% phiên) và `NAB` (chỉ có 87.6% phiên) do mới chuyển sàn/niêm yết trên HOSE đầu năm 2024.
  - Giữ lại: **98 mã cổ phiếu** có dữ liệu liên tục từ 98% đến 100%.
- **Lọc bỏ 68 ngày nghỉ lễ sàn HOSE:**
  - Sàn đóng cửa các dịp lễ Tết (Tết Nguyên Đán, Giỗ tổ Hùng Vương, 30/4 - 1/5, 2/9) -> Tổng khối lượng toàn sàn bằng 0.
  - Loại bỏ các ngày này giúp đưa dữ liệu về đúng **1.187 phiên giao dịch thực tế**.
- **Điền khuyết bằng Forward-fill:**
  - Toàn bộ ma trận chỉ còn 48 ô trống rải rác ở 3 mã: `CTR` (27 ô), `EVF` (11 ô), `HHV` (10 ô) do mới lên sàn đầu năm 2022 hoặc tạm dừng giao dịch ngắn ngày.
  - Sử dụng **Forward-fill (`ffill`)**: Lấy giá đóng cửa phiên liền trước điền cho phiên bị thiếu.
  - Lý do chọn: Phù hợp với logic nắm giữ tài sản của nhà đầu tư, không gây nhìn trước tương lai (Look-ahead bias) như phép nội suy hay Backward-fill.
- **Kết quả đầu ra:** Ma trận giá sạch $1.187 \text{ phiên} \times 98 \text{ mã}$ tại [`data/processed/adj_close_clean.csv`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/data/processed/adj_close_clean.csv).

---

## 4. Trích Chọn Đặc Trưng Lợi Suất Logarit (Notebook 03 - Chương 3)

- **Công thức tính lợi suất logarit:**
  $$r_{i, t} = \ln\left(\frac{P_{i, t}}{P_{i, t-1}}\right) = \ln(P_{i, t}) - \ln(P_{i, t-1})$$
- **3 lý do sử dụng lợi suất logarit thay cho giá thô:**
  - *Tính dừng (Stationarity):* Giá cổ phiếu có xu hướng tăng giảm dài hạn (không dừng). Lợi suất dao động quanh mức kỳ vọng 0 với phương sai hữu hạn, thích hợp cho mô hình học máy.
  - *Khử chênh lệch mệnh giá (Scale-invariance):* Triệt tiêu khoảng cách thị giá giữa cổ phiếu giá cao (100.000đ) và giá thấp (10.000đ), đưa mọi dao động về cùng thang đo phần trăm biến động.
  - *Tính cộng dồn theo thời gian:* Lợi suất tích lũy qua nhiều phiên đơn giản là tổng các lợi suất ngày: $r_{0 \to k} = \sum_{t=1}^k r_t$.
- **Đặc trưng thống kê thị trường (98 mã, 1.186 phiên lợi suất):**
  - Lợi suất trung bình năm: $\bar{\mu}_{ann} = -3.65\%/\text{năm}$.
  - Độ biến động trung bình năm: $\bar{\sigma}_{ann} = 38.54\%/\text{năm}$.
  - Tỷ số Sharpe trung bình: $-0.222$ (lãi suất phi rủi ro $r_f = 4.5\%$).
  - Độ lệch (Skewness): Lệch âm nhẹ, phản ánh thị trường có rủi ro giảm giá nhanh và sâu.
  - Độ nhọn (Excess Kurtosis): Trung bình đạt $3.86 > 0$, kiểm định Jarque-Bera có $p < 0.001$.
  - Ý nghĩa thực tế: Lợi suất cổ phiếu thực tế có hiện tượng **đuôi béo (Fat-tails)** rất rõ rệt. Các phiên biến động chạm trần/sàn diễn ra với tần suất cao hơn nhiều so với giả định phân phối chuẩn.
- **Kết quả đầu ra:**
  - Ma trận lợi suất: $1.186 \text{ phiên} \times 98 \text{ mã}$ tại [`data/processed/log_returns.csv`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/data/processed/log_returns.csv).
  - Bảng đặc trưng tài chính 98 mã tại [`data/processed/stock_financial_features.csv`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/data/processed/stock_financial_features.csv).

---

## 5. Đo Lường Tương Quan & Khoảng Cách Mantegna (Notebook 04 - Chương 3)

- **Nhược điểm của khoảng cách Euclid trên chuỗi lợi suất:**
  - *Phụ thuộc biên độ biến động:* Hai mã đi cùng chiều 100% nhưng biên độ khác nhau ($\pm 7\%$ vs $\pm 2\%$) vẫn bị Euclid tính khoảng cách lớn $\to$ bị tách cụm sai.
  - *Không phân biệt được chiều dao động:* Hai mã đi ngược chiều nhau nhưng biên độ dao động rất nhỏ quanh 0 vẫn bị Euclid tính khoảng cách gần $\to$ bị gom nhầm cụm.
  - *Nhiễu do số chiều lớn ($1.186$ phiên):* Khoảng cách giữa các điểm có xu hướng co cụm lại, giảm độ phân biệt.
- **Hệ số tương quan Pearson ($\rho \in [-1, 1]$):**
  - Đo độ đồng pha tuyến tính giữa 2 chuỗi lợi suất, khử hoàn toàn ảnh hưởng của biên độ giá và độ lệch chuẩn.
  - Hạn chế: $\rho$ là độ đo tương đồng, không phải khoảng cách (có giá trị âm, trùng nhau thì $\rho=1 \ne 0$). Nếu lấy đơn giản $1-\rho$ thì vi phạm bất đẳng thức tam giác, khi dựng cây phân cụm phân cấp sẽ gây ra lỗi đảo nhánh (inversion).
- **Khoảng cách Mantegna ($d \in [0, 2]$):**
  - Công thức chuyển đổi:
    $$d(i, j) = \sqrt{2(1 - \rho_{i, j})}$$
  - Bản chất hình học: Khoảng cách Euclid giữa 2 vector lợi suất sau khi đã chuẩn hóa về mặt cầu đơn vị.
  - Thỏa mãn đầy đủ 4 tiên đề khoảng cách mêtric: Không âm, đồng nhất ($d=0 \iff \rho=1$), đối xứng, và bất đẳng thức tam giác.
  - Các mốc giá trị thực tế:
    - $\rho = 1 \implies d = 0$: Biến động giống hệt nhau, gom chung cụm.
    - $\rho = 0 \implies d = \sqrt{2} \approx 1.414$: Độc lập với nhau, thích hợp cho đa dạng hóa danh mục.
    - $\rho = -1 \implies d = 2.0$: Biến động trái ngược hoàn toàn, giúp phòng hộ rủi ro tối đa.
- **Số liệu thực nghiệm toàn kỳ trên 98 mã VN100:**
  - Tương quan Pearson trung bình: $\bar{\rho} = 0.3168$.
  - Khoảng cách Mantegna trung bình: $\bar{d} = 1.1541$.
  - Kiểm tra 20.000 bộ ba ngẫu nhiên: 100% thỏa mãn bất đẳng thức tam giác (0 trường hợp vi phạm).
  - Cặp cổ phiếu đồng pha mạnh nhất: `HSG - NKG` ($d = 0.4747$), `DCM - DPM` ($d = 0.5244$), `SSI - VCI` ($d = 0.6004$).
  - Cặp cổ phiếu độc lập nhất: `KOS - PET` ($d = 1.4248$), `KOS - MSB` ($d = 1.4237$).
- **Kết quả đầu ra:**
  - Ma trận tương quan toàn kỳ: [`data/processed/correlation_matrix.csv`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/data/processed/correlation_matrix.csv).
  - Ma trận khoảng cách toàn kỳ: [`data/processed/mantegna_distance_matrix.csv`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/data/processed/mantegna_distance_matrix.csv).

---

## 6. Phân Chia Tập Dữ Liệu Train / Test Theo Thời Gian (Notebook 05 - Chương 2 & 3)

### 6.1. Phương pháp luận & Nguồn tham khảo học thuật
- **Bản chất bài toán:**
  - Đối tượng phân cụm là **98 cổ phiếu**. Tuyệt đối không chia theo cổ phiếu (không bỏ bớt mã nào) vì sẽ không thể phân cụm hay đa dạng hóa cho các mã bị loại.
  - Đặc trưng của mỗi cổ phiếu là **chuỗi thời gian $1.186$ phiên giao dịch**. Bắt buộc phải chia theo **trục thời gian (Chronological Split: In-Sample vs Out-of-Sample)** để loại bỏ rủi ro nhìn trước tương lai (Look-ahead bias / Information Leakage).
- **3 nguồn tham khảo học thuật uy tín:**
  1. **Marcos López de Prado (2018)** – *Advances in Financial Machine Learning* (Chương 7 & 8): Nguyên tắc cấm dùng K-Fold xáo trộn ngẫu nhiên trên chuỗi thời gian tài chính có tự tương quan; thiết kế khung kiểm định Out-of-Sample chuẩn mực.
  2. **Rosario N. Mantegna (1999)** – *Hierarchical structure in financial markets*: Khẳng định chuỗi dữ liệu cần độ dài $T$ tối thiểu từ 2 đến 3 năm để ma trận tương quan ổn định, phản ánh đúng quan hệ ngành.
  3. **Lý thuyết Ma trận Ngẫu nhiên (Random Matrix Theory - RMT)** của Bouchaud & Potters (2000), Laloux et al. (1999): Tỷ số $Q = T/N$ phải lớn hơn 1 rất nhiều ($Q \ge 3 - 5$) để ma trận tương quan không bị nhiễu loạn bởi phân phối Marchenko-Pastur.

### 6.2. So sánh phản biện các phương pháp chia dữ liệu

| Phương pháp | Cách thực hiện | Nhược điểm & Lý do đánh giá |
| :--- | :--- | :--- |
| **K-Fold thông thường (Random Shuffle)** | Xáo trộn ngẫu nhiên ngày giao dịch | **Vi phạm nguyên tắc chuỗi thời gian (Look-ahead bias):** Dùng dữ liệu tương lai để dự đoán quá khứ, phá hủy toàn bộ cấu trúc tự tương quan và tính chu kỳ thị trường. |
| **Chia tỷ lệ 80/20 cơ học** | 80% thời gian đầu làm Train, 20% sau làm Test | Nếu lấy 80% ($948$ phiên), tập Train kéo dài đến tháng 08/2025, khiến tập Test chỉ còn **chưa đầy 10 tháng** (238 phiên), không đủ một chu kỳ kinh doanh 4 quý để đánh giá danh mục. |
| **Cửa sổ trượt (Rolling Window)** | Cửa sổ trượt 6 tháng train, 1 tháng test | Phù hợp trading lướt sóng ngắn hạn, **không phù hợp với Đa dạng hóa danh mục Markowitz** do phí giao dịch bào mòn lợi nhuận khi đảo danh mục liên tục; đồng thời $T \approx 125$ phiên quá nhỏ làm ma trận tương quan $98 \times 98$ bị nhiễu loạn nặng. |
| **Chia theo chu kỳ (Regime-based Split)** | **Train 3 năm (2022-2024) / Test 1.8 năm (2025-2026)** | **Lựa chọn tối ưu:** Vừa đủ số phiên khử nhiễu ($T \gg N$), vừa trải qua đầy đủ các pha thị trường thực tế. |

### 6.3. Chi tiết Phương án 1 (Lựa chọn chính thức của đề tài)
- **Tập Train (In-Sample): Từ `04/01/2022` đến `31/12/2024` (3 năm tròn)**
  - Gồm **740 phiên giá / 739 phiên lợi suất** (chiếm **62.31%** dữ liệu).
  - Tỷ số $Q_{train} = T_{train} / N = 739 / 98 \approx 7.54 \gg 1$ (thỏa mãn hoàn hảo tiêu chuẩn RMT, khử sạch nhiễu ngẫu nhiên).
  - Bao quát trọn vẹn cả 2 pha thị trường khốc liệt: Pha Downtrend giảm sâu (2022) và Pha Phục hồi tái tích lũy (2023 - 2024). Giúp mô hình học được mối quan hệ giữa các cổ phiếu trong cả lúc thị trường hoảng loạn lẫn hưng phấn.
  - Toàn bộ quá trình huấn luyện mô hình phân cụm phân cấp và lựa chọn danh mục đại diện bắt buộc chỉ được sử dụng dữ liệu trong tập Train này.
- **Tập Test (Out-of-Sample): Từ `02/01/2025` đến `23/10/2026` (~1.8 năm)**
  - Gồm **447 phiên giao dịch** (chiếm **37.69%** dữ liệu).
  - Là pha thị trường hoàn toàn mới (đi ngang tích lũy, phân hóa sâu theo kết quả kinh doanh từng mã).
  - Đóng vai trò môi trường kiểm thử tương lai độc lập (Out-of-Sample Backtesting), đo lường xem danh mục đa dạng hóa có thực sự vượt trội hơn chỉ số thị trường VN-Index hay không.
- **Số liệu ma trận trên tập Train (739 phiên x 98 mã):**
  - Tương quan Pearson trung bình: $\bar{\rho}_{train} = 0.3697$ (cao hơn toàn kỳ do năm 2022 giảm mạnh toàn sàn có độ đồng pha cao).
  - Khoảng cách Mantegna trung bình: $\bar{d}_{train} = 1.1156$.
  - Kiểm tra 20.000 bộ ba ngẫu nhiên: 100% thỏa mãn bất đẳng thức tam giác (0 trường hợp vi phạm).
- **Kết quả đầu ra:**
  - Thư mục huấn luyện In-Sample [`data/processed/train/`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/data/processed/train/):
    - [`train_adj_close.csv`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/data/processed/train/train_adj_close.csv) ($740 \times 98$): Giá đóng cửa điều chỉnh tập Train.
    - [`train_log_returns.csv`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/data/processed/train/train_log_returns.csv) ($739 \times 98$): Lợi suất logarit tập Train.
    - [`train_correlation_matrix.csv`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/data/processed/train/train_correlation_matrix.csv) ($98 \times 98$): Ma trận tương quan Pearson tập Train.
    - [`train_mantegna_distance_matrix.csv`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/data/processed/train/train_mantegna_distance_matrix.csv) ($98 \times 98$): Ma trận khoảng cách Mantegna tập Train.
  - Thư mục kiểm thử Out-of-Sample [`data/processed/test/`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/data/processed/test/):
    - [`test_adj_close.csv`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/data/processed/test/test_adj_close.csv) ($447 \times 98$): Giá đóng cửa điều chỉnh tập Test.
    - [`test_log_returns.csv`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/data/processed/test/test_log_returns.csv) ($447 \times 98$): Lợi suất logarit tập Test.

---

## 7. So Sánh Các Phương Pháp Đo Khoảng Cách

| Phương pháp | Cách tính toán | Ý nghĩa cốt lõi | Nhược điểm trong bài toán tài chính | Đánh giá sử dụng |
| :--- | :--- | :--- | :--- | :---: |
| **Euclidean** | $\sqrt{\sum (r_{1t} - r_{2t})^2}$ | Đo khoảng cách hình học | Bị ảnh hưởng bởi biên độ dao động, không đo được quan hệ đồng pha/ngược pha | **Không dùng** |
| **Manhattan ($L_1$)** | $\sum \|r_{1t} - r_{2t}\|$ | Tổng độ lệch tuyệt đối | Vẫn phụ thuộc biên độ, không phản ánh được mức độ biến động cùng chiều | **Không dùng** |
| **DTW** | Co giãn trục thời gian | So khớp sóng lệch pha | Không phù hợp tài chính vì thông tin thị trường tác động đồng thời theo từng ngày | **Không dùng** |
| **Cosine Similarity** | $\frac{u \cdot v}{\|u\| \|v\|}$ | Góc giữa hai vector | Chưa chuẩn hóa trừ kỳ vọng trung bình, bị chi phối bởi xu hướng chung thị trường | **Không dùng** |
| **Spearman** | Tương quan trên thứ hạng | Đo quan hệ đơn điệu | Làm mất thông tin độ lớn lợi suất, không tương thích với lý thuyết phương sai Markowitz | **Tham khảo** |
| **Pearson ($\rho$)** | $\frac{\text{Cov}(X, Y)}{\sigma_X \sigma_Y}$ | Đo độ đồng pha tuyến tính | Là độ đo tương đồng $[-1, 1]$, không phải mêtric khoảng cách | **Bước trung gian** |
| **Mantegna ($d$)** | $\sqrt{2(1 - \rho)}$ | Đổi $\rho$ thành độ dài mêtric | Thỏa mãn 4 tiên đề khoảng cách, chống lỗi đảo nhánh cây phân cấp | **Lựa chọn tối ưu** |

---

## 8. Định Hướng Phân Cụm Phân Cấp (Notebook 06 - Chương 4)

- **Thuật toán chính:** Agglomerative Hierarchical Clustering thực thi trên ma trận khoảng cách `data/processed/train/mantegna_distance_matrix.csv`.
- **So sánh 4 tiêu chí liên kết (Linkage):**
  - *Single Linkage:* Nối theo khoảng cách nhỏ nhất giữa 2 cụm. Dễ bị hiệu ứng dây chuyền (chaining), cụm kéo dài và lỏng lẻo.
  - *Complete Linkage:* Nối theo khoảng cách lớn nhất giữa 2 cụm. Cụm tròn chặt nhưng dễ bị ảnh hưởng bởi điểm ngoại lai.
  - *Average Linkage (UPGMA):* Nối theo khoảng cách trung bình của tất cả các cặp điểm. Ổn định cao, bảo toàn tốt cấu trúc khoảng cách gốc.
  - *Ward's Linkage:* Tối thiểu hóa mức tăng phương sai nội cụm khi gộp. Tạo các cụm đồng đều về số lượng, rất phù hợp cho việc phân bổ vốn.
- **Tiêu chí đánh giá và chọn số cụm $k$:**
  - Cây phả hệ Dendrogram và bản đồ nhiệt Clustermap trên tập Train.
  - Hệ số tương quan Cophenetic (Cophenetic Correlation Coefficient - CCC) để chọn tiêu chí liên kết bảo toàn khoảng cách gốc tốt nhất.
  - Phân tích chỉ số Silhouette Score để tìm số cụm $k$ tối ưu (quét $k \in [3, 15]$).
- **Mô hình đối chứng (Baseline):** Sử dụng PCA (giữ $\ge 80\%$ phương sai) kết hợp K-Means để đối chiếu hiệu quả phân cụm.

---

## 9. Ứng Dụng Đa Dạng Hóa Danh Mục & Out-of-Sample Backtest (Notebook 09 - Chương 6)

- **Nguyên lý lý thuyết danh mục Markowitz:**
  - Rủi ro danh mục phụ thuộc lớn vào hiệp phương sai giữa các cổ phiếu nắm giữ.
  - Phân cụm giúp gom các mã có độ đồng biến động cao vào cùng nhóm.
- **Quy tắc chọn cổ phiếu từ kết quả phân cụm (hoàn toàn dựa trên tập Train):**
  - Tránh chọn nhiều mã trong cùng một cụm ($d \to 0$): Rủi ro phi hệ thống trùng lặp, không có tác dụng giảm thiểu rủi ro.
  - Chọn các mã đại diện từ các cụm khác nhau ($d \ge 1.414$): Triệt tiêu rủi ro riêng lẻ giữa các nhóm cổ phiếu.
  - Ưu tiên chọn mã có tỷ số Sharpe cao nhất hoặc thanh khoản tốt nhất trong từng cụm làm đại diện.
- **Đánh giá hiệu quả trên tập Test (Out-of-Sample Backtest):**
  - Giữ nguyên danh mục đã chọn từ tập Train, đưa vào chạy mô phỏng trên $447$ phiên của tập Test (2025 - 2026).
  - So sánh Danh mục Đa dạng hóa theo Cụm với:
    1. Danh mục chọn ngẫu nhiên các mã (1.000 mẫu Monte Carlo).
    2. Danh mục thị trường (VN-Index hoặc VN100 trọng số đều).
  - Các chỉ số đo lường: Lợi suất tích lũy (Cumulative Return), Độ biến động năm (Annualized Volatility), Tỷ số Sharpe và Mức sụt giảm tối đa (MDD).

---

## 10. Khung Đề Cương 7 Chương Báo Cáo Tiểu Luận

1. **Chương 1: Mở đầu & Cơ sở lý thuyết**
   - Bài toán đa dạng hóa danh mục đầu tư và lý thuyết Markowitz.
   - Hạn chế của khoảng cách Euclid, cơ sở hệ số tương quan Pearson và khoảng cách Mantegna.
   - Thuật toán phân cụm phân cấp (Hierarchical Clustering) và phương pháp đối chứng PCA + K-Means.
2. **Chương 2: Thu thập & Tiền xử lý dữ liệu**
   - Thu thập 100 mã rổ VN100 giai đoạn 2022 - 2026.
   - Lọc mã thiếu dữ liệu (loại VTP, NAB), khử 68 ngày nghỉ lễ sàn HOSE, xử lý giá trị khuyết bằng Forward-fill.
3. **Chương 3: Trích chọn đặc trưng, Thiết lập mêtric & Phân chia Train/Test**
   - Tính lợi suất logarit, kiểm định tính dừng và hiện tượng đuôi béo (Jarque-Bera, Kurtosis).
   - Xây dựng ma trận tương quan Pearson và ma trận khoảng cách Mantegna, kiểm định bất đẳng thức tam giác.
   - Cơ sở lý thuyết phân chia Chronological Split (Marcos López de Prado, RMT), phân tách Train (2022 - 2024) và Test (2025 - 2026).
4. **Chương 4: Thực nghiệm phân cụm & Đánh giá mô hình**
   - Dựng cây Dendrogram với 4 tiêu chí liên kết (Single, Complete, Average, Ward) trên tập Train.
   - Đánh giá hệ số Cophenetic (CCC) và tìm số cụm $k$ tối ưu bằng Silhouette Score.
   - So sánh kết quả phân cụm phân cấp với mô hình PCA + K-Means.
5. **Chương 5: Đánh giá độ ổn định & Đối chiếu phân ngành ICB**
   - Kiểm tra tính ổn định của cụm qua các giai đoạn thị trường bằng chỉ số Adjusted Rand Index (ARI).
   - So sánh các cụm tìm được với 11 nhóm ngành thực tế theo chuẩn ICB.
6. **Chương 6: Ứng dụng đa dạng hóa danh mục đầu tư & Kiểm thử lịch sử**
   - Xây dựng danh mục phân bổ đều từ các đại diện cụm trên tập Train.
   - Out-of-Sample Backtest trên tập Test (2025 - 2026) so với danh mục ngẫu nhiên và VN-Index.
7. **Chương 7: Kết luận & Hướng phát triển**
   - Tổng kết đóng góp của đề tài và các hạn chế cần hoàn thiện thêm.

---

## 11. Danh Mục Tệp Thực Nghiệm & Phân Định Hệ Thống

- **Hệ thống 5 Notebook thực nghiệm:**
  - [`01_data_collection_prep.ipynb`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/notebooks/01_data_collection_prep.ipynb): Thu thập dữ liệu thô 100 mã VN100.
  - [`02_data_preprocessing.ipynb`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/notebooks/02_data_preprocessing.ipynb): Lọc mã thiếu, khử ngày nghỉ lễ, điền khuyết Forward-fill ($1.187 \times 98$).
  - [`03_feature_extraction_returns.ipynb`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/notebooks/03_feature_extraction_returns.ipynb): Trích chọn lợi suất logarit ($1.186 \times 98$), kiểm định thống kê đuôi béo.
  - [`04_correlation_distance.ipynb`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/notebooks/04_correlation_distance.ipynb): Tính tương quan Pearson và khoảng cách Mantegna toàn kỳ ($98 \times 98$).
  - [`05_train_test_split.ipynb`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/notebooks/05_train_test_split.ipynb): Phân chia Train (2022-2024, 62.3%) / Test (2025-2026, 37.7%) và xuất bản ma trận Train phục vụ phân cụm.
- **Phân định kiến trúc phụ trợ:**
  - Thư mục [`web_app/`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/web_app/): Công cụ giao diện web tương tác độc lập (dùng để kiểm toán dữ liệu và xem bản đồ nhiệt).
  - Toàn bộ pipeline phân tích và mô hình học máy phục vụ báo cáo nằm độc lập trong `src/` và `notebooks/`.

