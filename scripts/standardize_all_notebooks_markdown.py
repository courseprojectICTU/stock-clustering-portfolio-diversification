import json
import os

# ==============================================================================
# NOTEBOOK 01 MARKDOWN REPLACEMENTS
# ==============================================================================
NB01_REPLACEMENTS = {
    0: """# Notebook 01: Thu thập Dữ liệu Lịch sử VN100 (2022–2026)

- **Mục tiêu:** Thu thập dữ liệu giao dịch lịch sử của 100 cổ phiếu thuộc rổ VN100 và thông tin phân ngành chuẩn ICB.
- **Thời gian:** 01/01/2022 đến 23/10/2026 (gần 5 năm, bao gồm các chu kỳ giảm 2022, tích lũy 2023, phục hồi 2024–2026).
- **Nguồn dữ liệu:** Thư viện `vnstock3` (nguồn dữ liệu thị trường chứng khoán Việt Nam).

### Các bước thực hiện:
1. Lấy danh sách 100 mã cổ phiếu rổ VN100 và bảng phân ngành ICB cấp 1.
2. Tải chuỗi giá OHLCV theo ngày cho từng mã và lưu vào thư mục `data/raw/`.
3. Kiểm tra tính toàn vẹn và cấu trúc dữ liệu thô ban đầu.""",

    2: """### 1. Lấy danh sách rổ cổ phiếu VN100 và Phân ngành ICB
- Rổ VN100 gồm 30 mã VN30 (vốn hóa lớn nhất) và 70 mã VNMidCap (vốn hóa trung bình, thanh khoản cao), đại diện cho hơn 90% vốn hóa thị trường HOSE.
- Metadata phân ngành ICB được lưu lại để phục vụ đối chiếu với các cụm thuật toán tìm được ở Mốc 2 và Mốc 3.""",

    4: """### 2. Thu thập dữ liệu giá OHLCV từng mã (2022–2026)
- Thu thập dữ liệu theo ngày từ `2022-01-01` đến `2026-10-23`.
- Mỗi mã được lưu thành một tệp CSV độc lập trong `data/raw/{symbol}.csv` để tránh rủi ro mất dữ liệu nếu đường truyền bị gián đoạn.""",

    6: """### 3. Kiểm tra mẫu dữ liệu thô
- Đọc thử dữ liệu của một cổ phiếu tiêu biểu (HPG) để xác minh định dạng cột (`date, open, high, low, close, volume, adj_close`) trước khi tiến hành tiền xử lý.""",

    8: """## Tổng kết Notebook 01

### Câu hỏi & Trả lời
- **Tại sao chọn rổ VN100 làm không gian nghiên cứu?** VN100 đại diện cho hơn 90% vốn hóa và thanh khoản của sàn HOSE, bao quát các ngành kinh tế trọng yếu và tránh được các cổ phiếu thanh khoản kém (penny/rác).
- **Dữ liệu thô thu thập gồm những gì?** Gồm 100 tệp CSV độc lập trong `data/raw/` với 7 trường thông tin giá và khối lượng, cùng tệp metadata phân ngành `data/metadata/vn100_symbols.csv`.

### Kết quả phân tích dữ liệu chính
- **Quy mô dữ liệu:** Đã thu thập đủ 100 mã cổ phiếu với tối đa 1.255 mốc thời gian theo lịch dương từ đầu năm 2022 đến tháng 10/2026.
- **Tính toàn vẹn ban đầu:** Các cổ phiếu niêm yết lâu năm (như HPG, VCB, FPT) có đủ dữ liệu; một số mã mới chào sàn có số phiên ít hơn và cần xử lý ở bước sau.

### Nhận định & Hướng đi tiếp theo
- **Notebook 02:** Ghép 100 file thành ma trận giá đóng cửa điều chỉnh (`adj_close`), loại bỏ ngày nghỉ lễ của HOSE, lọc mã thiếu dữ liệu $\\ge 90\\%$ và điền khuyết bằng Forward-fill."""
}

# ==============================================================================
# NOTEBOOK 02 MARKDOWN REPLACEMENTS
# ==============================================================================
NB02_REPLACEMENTS = {
    0: """# Notebook 02: Tiền xử lý và Làm sạch Dữ liệu Giá VN100

- **Mục tiêu:** Chuyển đổi 100 file giá thô thành một ma trận giá đóng cửa điều chỉnh (`adj_close`) đồng bộ, sạch 100% giá trị thiếu.
- **Dữ liệu vào:** 100 tệp CSV thô tại `data/raw/` (1.255 ngày lịch dương).
- **Dữ liệu ra:** Ma trận giá sạch `data/processed/adj_close_clean.csv` ($1.187 \\text{ phiên} \\times 98 \\text{ mã}$).

### Các bước thực hiện:
1. **Ghép ma trận giá:** Gom cột `adj_close` của 100 mã theo trục ngày giao dịch.
2. **Kiểm tra độ đầy đủ (Coverage):** Lọc bỏ các mã có tỷ lệ dữ liệu $< 90\\%$.
3. **Loại bỏ ngày nghỉ lễ:** Lọc 68 ngày sàn HOSE không giao dịch (khối lượng bằng 0).
4. **Điền khuyết (Imputation):** Xử lý 48 ô trống cục bộ bằng giá phiên trước (Forward-fill).
5. **Xuất bản dữ liệu:** Lưu ma trận giá sạch phục vụ tính lợi suất ở Notebook 03.""",

    2: """### 1. Nạp và ghép dữ liệu giá điều chỉnh (adj_close)
- Chọn cột `adj_close` (giá đóng cửa đã điều chỉnh sau chia tách cổ phiếu, thưởng và trả cổ tức) thay vì giá `close` thô.
- Lý do kỹ thuật: Giá `close` thô chứa các bước nhảy giá giả tạo ($\\pm 20\\% - 30\\%$) vào ngày giao dịch không hưởng quyền, làm sai lệch hoàn toàn độ biến động và tương quan.""",

    4: """### Nhận xét dữ liệu thô ban đầu:
- Ma trận ban đầu có 1.255 ngày lịch dương và 100 mã cổ phiếu, chứa hơn 16.000 ô trống (NaN).
- Nguyên nhân: Các ngày nghỉ cuối tuần/lễ tết vẫn có dòng ngày, và một số mã mới niêm yết trong giai đoạn 2022–2026 nên thiếu dữ liệu những năm đầu.""",

    5: """### 2. Kiểm tra tỷ lệ dữ liệu và lọc mã cổ phiếu
- Áp dụng ngưỡng chấp nhận tối thiểu **90% số phiên**: Các mã thiếu nhiều hơn 10% sẽ làm méo ma trận tương quan và làm sai lệch thuật toán phân cụm.""",

    7: """### Đánh giá kết quả lọc mã:
- **VTP (Viettel Post):** Chào sàn HOSE tháng 03/2024, chỉ có 42.6% số phiên (thiếu hơn nửa chu kỳ nghiên cứu).
- **NAB (Nam A Bank):** Chuyển sang HOSE tháng 03/2024, chỉ đạt 87.6% số phiên.
- **Kết luận:** Loại bỏ VTP và NAB. Giữ lại **98 mã cổ phiếu** có độ đầy đủ từ 98% đến 100%.""",

    8: """### 3. Loại bỏ 68 ngày nghỉ lễ của sàn HOSE
- Sàn HOSE đóng cửa vào các dịp lễ tết (Tết Nguyên Đán, Giỗ tổ Hùng Vương, 30/4 - 1/5, Quốc khánh 2/9).
- Tại các ngày này, khối lượng giao dịch thị trường bằng 0. Hệ thống Yahoo Finance tự động sao chép giá cũ tạo các phiên giá đi ngang giả tạo. Ta lọc bỏ 68 ngày này để đưa dữ liệu về đúng **1.187 phiên giao dịch thực tế**.""",

    10: """### 4. Xử lý giá trị khuyết bằng Forward-fill
- Sau khi loại 68 ngày nghỉ lễ, toàn bộ ma trận 98 mã chỉ còn đúng 48 ô trống (NaN).""",

    12: """### Phương pháp xử lý giá trị khuyết:
- 48 ô thiếu tập trung ở 3 mã: CTR (27 ô), EVF (11 ô), HHV (10 ô) do mới lên sàn đầu năm 2022 hoặc tạm ngừng giao dịch ngắn ngày.
- **Áp dụng Forward-fill (`ffill`):** Điền bằng giá đóng cửa phiên gần nhất trước đó.
- Lý do: Phù hợp với thực tế tài chính (nhà đầu tư nắm giữ tài sản qua ngày dừng giao dịch vẫn chịu giá tham chiếu cũ), không gây rò rỉ dữ liệu tương lai (Look-ahead bias) như phép nội suy hay backward-fill.
- Sau khi điền, ma trận sạch hoàn toàn (0 ô NaN).""",

    13: """### 5. Trực quan hóa chuỗi giá sau làm sạch
- Kiểm tra trực quan đường giá của 6 mã tiêu biểu: Nhóm vốn hóa lớn (VCB, HPG, FPT) và nhóm có xử lý điền khuyết (CTR, EVF, HHV).""",

    15: """### 6. Xuất bản ma trận giá sạch
- Lưu bảng giá đã làm sạch vào file `data/processed/adj_close_clean.csv`.""",

    17: """## Tổng kết Notebook 02

### Câu hỏi & Trả lời
- **Tại sao bắt buộc dùng giá đóng cửa điều chỉnh (adj_close)?** Giá điều chỉnh đã khử toàn bộ các bước nhảy giá kỹ thuật do chia cổ tức và phát hành thêm cổ phiếu. Nếu dùng giá thô, mức biến động và tương quan sẽ bị sai lệch nghiêm trọng.
- **Phương pháp điền khuyết nào được chọn và tại sao?** Chọn Forward-fill (`ffill`) vì bảo toàn tính nhân quả thời gian (không dùng dữ liệu tương lai) và phản ánh đúng giá trị tham chiếu khi cổ phiếu tạm dừng giao dịch.

### Kết quả phân tích dữ liệu chính
- **Lọc mã:** Loại 2 mã `VTP` (42.6%) và `NAB` (87.6%); giữ lại **98 mã cổ phiếu** đạt độ đầy đủ $\\ge 90\\%$.
- **Lọc ngày:** Loại 68 ngày nghỉ lễ sàn HOSE; chuẩn hóa chuỗi thời gian về **1.187 phiên giao dịch thực tế**.
- **Xử lý khuyết:** Điền 48 ô NaN cục bộ bằng Forward-fill; ma trận đạt trạng thái sạch hoàn toàn ($1.187 \\times 98$, 0 ô trống).

### Nhận định & Hướng đi tiếp theo
- **Notebook 03:** Dùng ma trận giá sạch $1.187 \\times 98$ để tính chuỗi lợi suất logarit ($1.186 \\times 98$), kiểm định hiện tượng đuôi béo (Jarque-Bera) và trích xuất các chỉ số rủi ro tài chính."""
}

# ==============================================================================
# NOTEBOOK 03 MARKDOWN REPLACEMENTS
# ==============================================================================
NB03_REPLACEMENTS = {
    0: """# Notebook 03: Trích chọn Đặc trưng - Chuỗi Lợi suất Logarit và Thống kê Rủi ro

- **Mục tiêu:** Chuyển đổi ma trận giá sạch thành chuỗi lợi suất logarit và trích xuất các đặc trưng tài chính mô tả rủi ro của 98 cổ phiếu VN100.
- **Dữ liệu vào:** Ma trận giá sạch `data/processed/adj_close_clean.csv` ($1.187 \\text{ phiên} \\times 98 \\text{ mã}$).
- **Dữ liệu ra:** Ma trận lợi suất `data/processed/log_returns.csv` ($1.186 \\text{ phiên} \\times 98 \\text{ mã}$) và bảng đặc trưng `data/processed/stock_financial_features.csv`.

### Các bước thực hiện:
1. **Chuyển đổi lợi suất logarit:** Chuyển chuỗi giá thành chuỗi lợi suất liên tục.
2. **Trích chọn đặc trưng tài chính:** Tính lợi suất năm hóa, độ biến động năm hóa, tỷ số Sharpe, Skewness, Kurtosis.
3. **Kiểm định phân phối chuẩn:** Thực hiện kiểm định Jarque-Bera đánh giá hiện tượng đuôi béo (Fat-tails).
4. **Phân tích không gian Lợi suất - Rủi ro:** Khảo sát tương quan giữa mức sinh lời và rủi ro.
5. **Cơ sở cho bước tiếp theo:** Phân tích hạn chế của khoảng cách Euclid trên chuỗi lợi suất.""",

    2: """### 1. Cơ sở toán học của Lợi suất Logarit
- **Tính dừng (Stationarity):** Chuỗi giá $P_t$ không dừng và chứa xu hướng dài hạn. Chuỗi lợi suất logarit $r_t = \\ln(P_t / P_{t-1})$ mang tính dừng, phù hợp làm đầu vào cho các thuật toán phân cụm.
- **Khử thiên lệch quy mô (Scale Bias):** Lợi suất đo mức thay đổi tương đối (%) thay vì giá trị tuyệt đối, giúp so sánh bình đẳng giữa cổ phiếu thị giá cao (100.000 đ) và thị giá thấp (10.000 đ).
- **Tính cộng dồn qua thời gian:** Lợi suất logarit lũy kế sau $k$ phiên bằng tổng đại số các lợi suất ngày:
  $$r_{0 \\to k} = \\ln(P_k / P_0) = \\sum_{t=1}^k r_t$$""",

    4: """### 2. Trích chọn các chỉ số thống kê tài chính
- **Lợi suất năm hóa:** $\\mu_{ann} = \\mu_{daily} \\times 252$
- **Độ biến động năm hóa:** $\\sigma_{ann} = \\sigma_{daily} \\times \\sqrt{252}$
- **Tỷ số Sharpe:** $\\text{Sharpe} = (\\mu_{ann} - r_f) / \\sigma_{ann}$ (với lãi suất phi rủi ro $r_f = 4.5\\%/\\text{năm}$).
- **Độ lệch (Skewness):** Đo tính bất đối xứng của phân phối. Giá trị âm phản ánh rủi ro giảm giá đột ngột.
- **Độ nhọn (Excess Kurtosis):** Đo độ dày của đuôi phân phối. Giá trị $> 0$ phản ánh hiện tượng đuôi béo (Fat-tails).
- **Kiểm định Jarque-Bera:** Kiểm tra giả thuyết phân phối chuẩn của chuỗi lợi suất.""",

    6: """### Đánh giá kết quả thống kê mô tả:
- **Độ biến động phân hóa:** Độ biến động năm trung bình đạt $38.5\\%$. Nhóm phòng thủ (VNM, GAS) biến động thấp nhất ($20\\% - 24\\%$), trong khi nhóm bất động sản đầu cơ (DIG, NVL, PDR) biến động mạnh nhất ($> 50\\%$).
- **Đuôi béo rõ rệt:** 100% cổ phiếu có Excess Kurtosis $> 1.0$ (trung bình $3.86$). Kiểm định Jarque-Bera cho p-value $< 0.001$ trên tất cả các mã, bác bỏ giả định phân phối chuẩn.""",

    7: """### 3. Kiểm định trực quan hiện tượng Đuôi béo (Fat-Tails)
- So sánh phân phối thực nghiệm của 4 mã đại diện ngành (VCB, HPG, FPT, SSI) với đường cong chuẩn Gauss có cùng kỳ vọng và độ lệch chuẩn.""",

    9: """### Đánh giá hiện tượng đuôi béo:
- Phân phối thực tế có đỉnh nhọn hơn và hai đuôi dày hơn đáng kể so với phân phối chuẩn.
- Tần suất xuất hiện các phiên tăng trần (+7%) hoặc giảm sàn (-7%) cao hơn nhiều so với lý thuyết phân phối Gauss.
- Do đó, việc đo lường rủi ro danh mục cần dựa trên ma trận đồng biến động thực nghiệm thay vì các giả định phân phối đơn giản.""",

    10: """### 4. Không gian Lợi suất và Rủi ro (Risk - Return Profile)
- Biểu đồ phân tán giữa Độ biến động năm hóa ($\\sigma_{ann}$) và Lợi suất năm hóa ($\\mu_{ann}$) của 98 mã cổ phiếu giai đoạn 2022–2026.""",

    13: """### 5. Xuất bản dữ liệu
- Lưu chuỗi lợi suất vào `data/processed/log_returns.csv` ($1.186 \\times 98$) và bảng đặc trưng vào `data/processed/stock_financial_features.csv`.""",

    15: """## Tổng kết Notebook 03

### Câu hỏi & Trả lời
- **Tại sao bắt buộc dùng lợi suất logarit thay vì giá cổ phiếu thô?** Chuỗi giá không dừng và bị phụ thuộc vào mệnh giá. Lợi suất logarit có tính dừng, chuẩn hóa biến động về tỷ lệ phần trăm và có tính chất cộng dồn qua thời gian.
- **Thị trường chứng khoán Việt Nam có tuân theo phân phối chuẩn không?** Không. 100% cổ phiếu VN100 đều có hiện tượng đuôi béo (Kurtosis trung bình 3.86, Jarque-Bera $p < 0.001$), các phiên biên độ lớn ($\\pm 7\\%$) xuất hiện thường xuyên hơn nhiều so với phân phối Gauss.

### Kết quả phân tích dữ liệu chính
- **Chuỗi lợi suất:** Đã chuyển đổi thành công 1.187 phiên giá sạch thành **1.186 phiên lợi suất logarit liên tục** của 98 mã.
- **Đặc trưng rủi ro:** Độ biến động bình quân thị trường là 38.5%/năm; nhóm phòng thủ dao động 20–24%, nhóm đầu cơ trên 50%.
- **Vấn đề kỹ thuật cho bước gom cụm:** Khoảng cách Euclid trên chuỗi lợi suất bị bẫy biên độ dao động (scale effect) và bẫy ngược pha quanh 0, do đó cần một không gian khoảng cách dựa trên tương quan.

### Nhận định & Hướng đi tiếp theo
- **Notebook 04:** Xây dựng ma trận tương quan Pearson $\\rho \\in [-1, 1]$ và chuyển đổi sang khoảng cách mêtric Mantegna $d = \\sqrt{2(1-\\rho)} \\in [0, 2]$ để chuẩn bị dữ liệu đầu vào chuẩn cho phân cụm phân cấp."""
}

# ==============================================================================
# NOTEBOOK 04 MARKDOWN REPLACEMENTS
# ==============================================================================
NB04_REPLACEMENTS = {
    0: """# Notebook 04: Biểu diễn Quan hệ Tương quan và Khoảng cách Mantegna

- **Mục tiêu:** Xây dựng không gian khoảng cách mêtric dựa trên tương quan đồng biến động giá giữa 98 cổ phiếu VN100.
- **Dữ liệu vào:** Ma trận lợi suất logarit `data/processed/log_returns.csv` ($1.186 \\text{ phiên} \\times 98 \\text{ mã}$).
- **Dữ liệu ra:** Ma trận tương quan `correlation_matrix.csv` ($98 \\times 98$) và ma trận khoảng cách Mantegna `mantegna_distance_matrix.csv` ($98 \\times 98$).

### Các bước thực hiện:
1. **Phân tích hạn chế của khoảng cách Euclid:** Chỉ ra các trường hợp sai lệch khi gom cụm trực tiếp chuỗi lợi suất.
2. **Tính toán ma trận tương quan Pearson ($\\rho \\in [-1, 1]$):** Đo lường mức độ đồng pha tuyến tính.
3. **Chuyển đổi sang khoảng cách Mantegna ($d = \\sqrt{2(1 - \\rho)}$):** Thiết lập không gian mêtric chuẩn trong đoạn $[0, 2]$.
4. **Kiểm tra 4 tiên đề mêtric:** Kiểm chứng thực nghiệm bất đẳng thức tam giác trên 20.000 bộ ba cổ phiếu.
5. **Khảo sát các cặp cổ phiếu tiêu biểu:** Xác định các cặp đồng pha nhất (cùng cụm) và độc lập nhất (tối ưu đa dạng hóa).""",

    2: """### 1. Hạn chế của Khoảng cách Euclid trên Chuỗi Lợi suất
- Khoảng cách Euclid hình học: $d_{Euclid}(\\mathbf{r}_i, \\mathbf{r}_j) = \\sqrt{\\sum_{t=1}^T (r_{i, t} - r_{j, t})^2}$.
- **Hai sai lầm cốt lõi khi áp dụng vào tài chính:**
  1. *Bẫy biên độ dao động (Scale bias):* Hai cổ phiếu đồng pha 100% nhưng một mã dao động $\\pm 7\\%$ và một mã phòng thủ $\\pm 1\\%$ sẽ bị Euclid tính khoảng cách lớn và tách thành hai cụm khác nhau.
  2. *Bẫy ngược pha quanh 0:* Hai cổ phiếu ngược pha 100% nhưng dao động nhỏ quanh $0.5\\%$ lại bị Euclid tính khoảng cách bé và gom nhầm vào một cụm.""",

    4: """### 2. Bộ đôi Tương quan Pearson và Khoảng cách Mantegna
- **Hệ số tương quan Pearson ($\\rho \\in [-1, 1]$):** Khử hoàn toàn ảnh hưởng của độ lệch biên độ, đo đúng mức độ đồng biến động. Tuy nhiên, $\\rho$ là độ tương đồng, không phải khoảng cách (có giá trị âm, trùng nhau $\\rho=1 \\ne 0$).
- **Khoảng cách Mantegna ($d \\in [0, 2]$):** Được Rosario N. Mantegna (1999) đề xuất:
  $$d(i, j) = \\sqrt{2(1 - \\rho_{i, j})}$$
- **Ý nghĩa hình học:** Khi chuẩn hóa chuỗi lợi suất thành vector đơn vị trên mặt cầu $\\mathbb{S}^{T-1}$, khoảng cách Mantegna chính là độ dài dây cung nối hai vector. Nó thỏa mãn trọn vẹn 4 tiên đề mêtric:
  1. Không âm: $d(i, j) \\ge 0$.
  2. Đồng nhất: $d(i, j) = 0 \\iff \\rho_{i, j} = 1$.
  3. Đối xứng: $d(i, j) = d(j, i)$.
  4. Bất đẳng thức tam giác: $d(i, k) \\le d(i, j) + d(j, k)$ (đảm bảo cây phân cấp Dendrogram không bị đảo ngược nhánh).""",

    6: """### 3. Thực nghiệm trên 98 Cổ phiếu VN100 (2022–2026)
- Tính toán ma trận tương quan $\\mathbf{C}$ ($98 \\times 98$) và ma trận khoảng cách Mantegna $\\mathbf{D}$ ($98 \\times 98$).
- Kiểm chứng thực nghiệm bất đẳng thức tam giác trên 20.000 bộ ba cổ phiếu ngẫu nhiên.""",

    8: """### 4. So sánh Heatmap Khoảng cách Euclid và Mantegna
- Trực quan hóa ma trận khoảng cách của 15 cổ phiếu đại diện các ngành trụ cột (Ngân hàng, Thép, Bất động sản, Bán lẻ, Công nghệ, Tiêu dùng).""",

    10: """### 5. Khảo sát các Cặp cổ phiếu Cùng ngành và Độc lập
- Xác định các cặp có khoảng cách nhỏ nhất (đồng biến động mạnh, cùng ngành) và các cặp có khoảng cách lớn nhất (độc lập, thích hợp giảm thiểu tương quan danh mục).""",

    12: """## Tổng kết Notebook 04

### Câu hỏi & Trả lời
- **Tại sao không thể gom cụm trực tiếp bằng khoảng cách Euclid?** Khoảng cách Euclid bị phụ thuộc vào độ lớn biên độ dao động và bị nhầm lẫn giữa hai chuỗi ngược pha có biên độ nhỏ.
- **Khoảng cách Mantegna giải quyết vấn đề gì?** Chuyển đổi hệ số tương quan $\\rho \\in [-1, 1]$ thành khoảng cách mêtric $d \\in [0, 2]$ thỏa mãn 100% bất đẳng thức tam giác, giúp cây Dendrogram không bị lỗi đảo nhánh.

### Kết quả phân tích dữ liệu chính
- **Kiểm định mêtric:** Kiểm tra 20.000 bộ ba ngẫu nhiên cho thấy 100% thỏa mãn bất đẳng thức tam giác (0 vi phạm).
- **Cấu trúc đồng pha:** Các cổ phiếu cùng ngành có khoảng cách Mantegna rất nhỏ ($d \\approx 0.45 - 0.55$, tương đương $\\rho \\approx 0.70 - 0.85$, như cặp Thép `HPG - HSG` hay Chứng khoán `SSI - VND`).
- **Cấu trúc độc lập:** Các cổ phiếu ngành phòng thủ hoặc tiêu dùng thiết yếu có khoảng cách lớn ($d \\approx 1.30 - 1.45$, tương đương $\\rho \\approx 0$), thích hợp cho việc đa dạng hóa danh mục.

### Nhận định & Hướng đi tiếp theo
- **Notebook 05:** Phân chia tập dữ liệu theo trục thời gian (Train 2022–2024 / Test 2025–2026) theo nguyên tắc chống rò rỉ dữ liệu (No Look-ahead bias) và tính ma trận khoảng cách riêng cho tập Train."""
}

# ==============================================================================
# NOTEBOOK 05 MARKDOWN REPLACEMENTS
# ==============================================================================
NB05_REPLACEMENTS = {
    0: """# Notebook 05: Phân chia Dữ liệu Train / Test theo Chu kỳ Thời gian

- **Mục tiêu:** Phân chia dữ liệu theo trục thời gian (In-Sample Train vs Out-of-Sample Test) nhằm chống nhìn trước tương lai (Look-ahead bias) và chuẩn bị dữ liệu cho khâu phân cụm.
- **Nguyên tắc phân chia:** Giữ nguyên toàn bộ 98 cổ phiếu; phân chia tuần tự theo trục thời gian (Chronological Split) thay vì xáo trộn ngẫu nhiên.
- **Dữ liệu vào:** `adj_close_clean.csv` ($1.187 \\times 98$) và `log_returns.csv` ($1.186 \\times 98$).
- **Dữ liệu ra:** Thư mục độc lập `data/processed/train/` (2022–2024) và `data/processed/test/` (2025–2026).

### Các bước thực hiện:
1. Phân tích cơ sở lý thuyết chia dữ liệu trong học máy tài chính (López de Prado, 2018 và Lý thuyết Ma trận Ngẫu nhiên RMT).
2. Thiết lập ranh giới phân tách: Train (2022–2024, 62.3% số phiên) và Test (2025–2026, 37.7% số phiên).
3. Trực quan hóa chuỗi thời gian toàn thị trường và ranh giới phân chia.
4. Tính toán ma trận tương quan và ma trận khoảng cách Mantegna riêng cho tập Train ($739 \\text{ phiên} \\times 98 \\text{ mã}$).
5. Xuất bản các bộ dữ liệu độc lập vào 2 thư mục `train/` và `test/`.""",

    2: """### 1. Nạp dữ liệu giá sạch và chuỗi lợi suất
- Nạp hai bảng dữ liệu hoàn chỉnh từ Notebook 02 và 03: `adj_close_clean.csv` ($1.187 \\times 98$) và `log_returns.csv` ($1.186 \\times 98$).""",

    4: """### 2. Cơ sở lý thuyết phân chia dữ liệu trong tài chính
- **Tại sao chia theo thời gian mà không chia theo cổ phiếu?**
  - Đối tượng phân cụm là toàn bộ 98 cổ phiếu. Nếu chia 70 mã để train và 28 mã để test thì không thể gom cụm hay xây dựng danh mục cho 28 mã đó. Do đó, toàn bộ 98 mã luôn được giữ nguyên.
  - Phân chia bắt buộc phải thực hiện trên **trục thời gian (Temporal Split)**.
- **So sánh các phương pháp phân chia:**
  - *K-Fold ngẫu nhiên:* Vi phạm tính nhân quả thời gian, gây rò rỉ dữ liệu tương lai vào quá khứ (Look-ahead bias).
  - *Chia 80/20 cơ học:* Tập Test chỉ còn chưa đầy 10 tháng (238 phiên), không đủ một chu kỳ kinh doanh 4 quý để đánh giá danh mục.
  - *Chia theo chu kỳ (Regime-based):* **Train 3 năm (2022–2024, 739 phiên) / Test ~1.8 năm (2025–2026, 447 phiên)**. Đây là phương án tối ưu, đảm bảo tập Train bao quát đủ các pha thị trường (giảm, tích lũy, hồi phục) và tập Test đủ dài để backtest.
- **Tiêu chuẩn Lý thuyết Ma trận Ngẫu nhiên (RMT):**
  - Tỷ số quan sát trên số chiều: $Q = T/N = 739 / 98 \\approx 7.54 \\gg 1$.
  - Tỷ số $Q > 3 - 5$ đảm bảo ma trận tương quan tập Train khử sạch nhiễu ngẫu nhiên Marchenko-Pastur, phản ánh đúng tương quan tài chính thực tế.""",

    5: """### 3. Thực hiện phân chia tập Train và Test
- **Tập Train (In-Sample):** Từ `2022-01-04` đến `2024-12-31` (740 phiên giá / 739 phiên lợi suất, chiếm 62.31%).
- **Tập Test (Out-of-Sample):** Từ `2025-01-02` đến `2026-10-23` (447 phiên giá / 447 phiên lợi suất, chiếm 37.69%).""",

    7: """### 4. Trực quan hóa ranh giới chuỗi thời gian
- Xây dựng chỉ số đại diện VN100 Equal-Weighted Index (lấy mốc 100 điểm tại phiên đầu tiên) để quan sát diễn biến chu kỳ thị trường qua hai tập dữ liệu.""",

    9: """### 5. Tính ma trận Tương quan và Khoảng cách Mantegna trên tập Train
- Tuân thủ nguyên tắc không rò rỉ thông tin: Toàn bộ quá trình chọn thuật toán, quét số cụm và chọn cổ phiếu đại diện chỉ dùng dữ liệu tập Train ($739 \\text{ phiên}$).
- Tập Test hoàn toàn độc lập, chỉ dùng ở bước kiểm định hiệu quả danh mục sau này (Notebook 09).""",

    11: """### 6. So sánh phân phối tương quan tập Train và Toàn kỳ
- So sánh phân phối hệ số tương quan $\\rho$ giữa tập Train (2022–2024) và Toàn kỳ (2022–2026) để kiểm tra tính đại diện của dữ liệu huấn luyện.""",

    13: """### 7. Xuất bản dữ liệu vào hai thư mục Train và Test
- Lưu trữ độc lập vào `data/processed/train/` và `data/processed/test/` nhằm quản lý dữ liệu chặt chẽ và ngăn ngừa rò rỉ thông tin ngoài mẫu.""",

    15: """## Tổng kết Notebook 05

### Câu hỏi & Trả lời
- **Tại sao không dùng K-Fold ngẫu nhiên trong bài toán này?** K-Fold làm xáo trộn thứ tự thời gian, khiến mô hình học trước dữ liệu tương lai và phá hủy tính tự tương quan của chuỗi tài chính.
- **Tỷ số $Q = T/N \\approx 7.54$ có ý nghĩa gì?** Theo Lý thuyết Ma trận Ngẫu nhiên (RMT), tỷ số $T/N > 3 - 5$ đảm bảo các giá trị riêng của ma trận tương quan không bị lẫn trong dải nhiễu Marchenko-Pastur, giúp kết quả gom cụm có ý nghĩa kinh tế thực chất.

### Kết quả phân tích dữ liệu chính
- **Phân chia chu kỳ:** Tập Train gồm 739 phiên lợi suất (2022–2024, 62.3%); tập Test gồm 447 phiên lợi suất (2025–2026, 37.7%).
- **Cách ly dữ liệu:** Đã lưu độc lập các tệp dữ liệu vào hai thư mục `train/` và `test/`.
- **Dữ liệu sẵn sàng:** Ma trận khoảng cách Mantegna tập Train (`train_mantegna_distance_matrix.csv`, $98 \\times 98$) đã sẵn sàng cho bước lựa chọn thuật toán ở Mốc 2.

### Nhận định & Hướng đi tiếp theo
- **Notebook 06:** Đưa 3 trường phái phân cụm (K-Means phẳng, Phân cấp Top-Down, Phân cấp Bottom-Up) lên bàn cân thực nghiệm trên tập Train để chọn mô hình đề xuất chính và mô hình cơ sở."""
}

# ==============================================================================
# NOTEBOOK 06 MARKDOWN REPLACEMENTS
# ==============================================================================
NB06_REPLACEMENTS = {
    0: """# Notebook 06: Lựa chọn Thuật toán - K-Means, Phân cấp Top-Down và Bottom-Up

- **Mục tiêu:** Quyết định 6 — Thực nghiệm đối chứng khách quan giữa 3 trường phái phân cụm nhằm xác định mô hình đề xuất chính (Proposed Model) và mô hình cơ sở (Baseline Model).
- **Dữ liệu vào:** Dữ liệu tập Train 2022–2024 (`train_log_returns.csv`, `train_correlation_matrix.csv`, `train_mantegna_distance_matrix.csv`) từ Notebook 05.
- **Trường phái khảo sát:**
  - Phân hoạch phẳng: K-Means (Euclidean) và K-Means (PCA 5D).
  - Phân cấp chia dần (Top-Down): Bisecting K-Means và DIANA.
  - Phân cấp gộp dần (Bottom-Up): Agglomerative Hierarchical (Single, Complete, Average, Ward).

### Các bước thực nghiệm:
1. So sánh lý thuyết về hàm mục tiêu, không gian đầu vào và độ phức tạp tính toán giữa 3 trường phái.
2. Đo độ ổn định tái lập qua 30 random seeds bằng chỉ số Adjusted Rand Index (ARI).
3. Đo khả năng phân tách tương quan nội cụm vs liên cụm ($\\Delta = \\bar{\\rho}_{\\text{intra}} - \\bar{\\rho}_{\\text{inter}}$) và kiểm tra hiện tượng dồn cụm ngoại lai.
4. Tổng kết bảng đối chứng đa tiêu chí và đưa ra quyết định kỹ thuật số 6.""",

    2: """### 1. Nạp Dữ liệu Huấn luyện (In-Sample Train Data)
- Tuân thủ nguyên tắc chống rò rỉ dữ liệu (López de Prado, 2018), toàn bộ quá trình so sánh và lựa chọn thuật toán chỉ sử dụng tập **Train (2022–2024)**.
- Nạp 3 tệp dữ liệu từ `data/processed/train/`:
  - `train_log_returns.csv`: Chuỗi lợi suất logarit ($739 \\text{ phiên} \\times 98 \\text{ mã}$).
  - `train_correlation_matrix.csv`: Ma trận tương quan Pearson $\\rho \\in [-1, 1]$ ($98 \\times 98$).
  - `train_mantegna_distance_matrix.csv`: Ma trận khoảng cách Mantegna $d = \\sqrt{2(1-\\rho)} \\in [0, 2]$ ($98 \\times 98$).""",

    4: """### 2. So sánh Lý thuyết giữa 3 Trường phái Phân cụm
*(Theo Bài giảng Bài 8 mục 8.1.3 & 8.1.4 — Thầy Nguyễn Tuấn Anh)*

| Tiêu chí | Phân hoạch phẳng (K-Means) | Phân cấp Chia dần (Top-Down) | Phân cấp Gộp dần (Bottom-Up) |
| :--- | :--- | :--- | :--- |
| **Cơ chế tối ưu** | Cực tiểu hóa sai số nội cụm: $\\mathcal{L} = \\sum \\|\\mathbf{x}_i - \\boldsymbol{\\mu}_{c_i}\\|^2$ | Bắt đầu từ 1 cụm lớn, chia đôi đệ quy (Bisecting, DIANA) | Bắt đầu từ các điểm đơn lẻ, gộp dần từng cặp gần nhất lên cây |
| **Không gian đầu vào** | Vector Euclid $\\mathbb{R}^d$ (tính tâm $\\boldsymbol{\\mu}$). Không nhận ma trận khoảng cách | Thường dùng vector Euclid (Bisecting) hoặc khoảng cách (DIANA) | Nhận trực tiếp ma trận khoảng cách siêu mêtric Mantegna |
| **Tính tất định** | Phụ thuộc seed khởi tạo, dễ kẹt ở cực tiểu địa phương | Bisecting vẫn nhạy cảm seed; DIANA tất định | Tất định 100% (cùng dữ liệu luôn cho cùng 1 kết quả) |
| **Rủi ro tài chính** | Bẫy biên độ dao động và bẫy ngược pha | Dễ dính bẫy lột vỏ ngoại lai (Outlier Peeling Trap) làm lệch cụm | Nhìn từ vi mô: Khóa chặt các cặp cổ phiếu đồng ngành trước |
| **Độ phức tạp** | $O(NKd)$ — tối ưu cho Big Data | $O(K \\cdot NKd)$ (Bisecting) hoặc $O(N^2)$ | Bộ nhớ $O(N^2)$, tính toán $O(N^2) \\to O(N^3)$ (chạy $< 0.05$s với $N=98$) |""",

    5: """### 3. Thiết kế Thực nghiệm Đối chứng
- Khảo sát đồng thời cả 3 trường phái tại số cụm thử nghiệm $K = 6$:
  1. *Trường phái phẳng:* K-Means trên chuỗi lợi suất gốc (Euclidean) và trên không gian PCA 5D.
  2. *Trường phái Top-Down:* Bisecting K-Means và DIANA (Divisive Analysis) trên khoảng cách Mantegna.
  3. *Trường phái Bottom-Up:* Khảo sát 4 tiêu chí liên kết (*Single, Complete, Average, Ward*) trên ma trận Mantegna.""",

    7: """### Thực nghiệm 1: Đánh giá Độ ổn định Tái lập (Stability)
- **K-Means phẳng ($ARI = 0.4722 \\pm 0.1272$):** Bất ổn định lớn. Khi thay đổi seed khởi tạo, hơn 50% số mã bị chuyển sang cụm khác do thuật toán rơi vào các cực tiểu địa phương khác nhau.
- **Top-Down Bisecting ($ARI = 0.5517 \\pm 0.0883$):** Cấu trúc cây giúp cải thiện đôi chút, nhưng mỗi bước phân nhánh vẫn dùng 2-Means ngẫu nhiên nên kết quả gán cụm vẫn dao động.
- **Bottom-Up Hierarchical ($ARI = 1.0000 \\pm 0.0000$):** Tất định tuyệt đối. Kết quả tái lập 100%, không đổi cụm khi đổi seed, giúp danh mục đầu tư không bị đảo hàng liên tục gây tốn phí giao dịch.""",

    9: """### Thực nghiệm 2: Khả năng Phân tách Tương quan và Bẫy Ngoại lai
- **K-Means phẳng:** $\\Delta \\approx +0.0136$ (Euclid) và $\\Delta = -0.0222$ (PCA 5D). Giá trị $\\Delta \\le 0$ cho thấy cổ phiếu cùng cụm có tương quan không khác biệt so với khác cụm.
- **Top-Down Bisecting K-Means:** $\\Delta = +0.0428$ (tốt hơn K-Means phẳng nhưng vẫn kém hơn Bottom-Up).
- **Top-Down DIANA (Bẫy lột vỏ ngoại lai):** Thuật toán chia từ trên xuống bằng cách bóc các mã dị biệt trước, dẫn đến việc dồn **90 cổ phiếu** vào 1 cụm khổng lồ và tạo ra 4 cụm đơn lẻ 1 mã (`[90, 4, 1, 1, 1, 1]`), không thể dùng để đa dạng hóa danh mục.
- **Bottom-Up Hierarchical:** Mọi linkage đều đạt $\\Delta > 0$ rõ rệt ($+0.0932 \\to +0.2210$). Đặc biệt, Ward tạo phân bố kích thước cụm đồng đều nhất (`[33, 21, 14, 13, 10, 7]`), thuận lợi nhất cho việc chọn đại diện danh mục.""",

    12: """## Tổng kết Notebook 06

### Câu hỏi & Trả lời
- **Tại sao chọn Phân cụm phân cấp Gộp dần (Bottom-Up) làm mô hình chính?**
  - Tính tất định tuyệt đối ($ARI = 1.0000$ qua 30 seeds), không đổi nhãn cụm ngẫu nhiên.
  - Nhận trực tiếp ma trận khoảng cách Mantegna, khử bẫy biên độ và bẫy ngược pha của Euclid.
  - Độ phân tách tương quan $\\Delta = +0.0932$ vượt trội và kích thước cụm cân bằng, bảo toàn tốt các hạt nhân ngành từ đáy cây.
- **Mô hình nào được chọn làm Baseline đối chứng?**
  - **K-Means trên không gian PCA 5D** được chọn làm Mô hình cơ sở (Baseline Model) theo đúng Tiêu chí 2 của Bài kiểm tra 2.

### Kết quả phân tích dữ liệu chính
- **Độ ổn định:** Bottom-Up đạt ARI = 1.0000 tuyệt đối vs K-Means phẳng (0.4722) và Bisecting K-Means (0.5517).
- **Phân tách tương quan:** Bottom-Up đạt $\\Delta$ từ $+0.0932$ đến $+0.2210$, trong khi K-Means chỉ đạt quanh 0.
- **Bẫy ngoại lai của DIANA:** Phân cấp Top-Down dồn 90 mã vào một siêu cụm (`[90, 4, 1, 1, 1, 1]`), không đáp ứng yêu cầu phân bổ vốn danh mục.

### Nhận định & Hướng đi tiếp theo
- **Notebook 07:** So sánh chi tiết 4 tiêu chí liên kết (*Single, Complete, Average, Ward*) trong Bottom-Up, đo hệ số Cophenetic (CCC), quét số cụm $K \\in [3, 15]$ và chốt cấu hình tối ưu $K^*$ cho bài toán đầu tư."""
}

ALL_NOTEBOOKS_TO_STANDARDIZE = {
    "notebooks/01_data_collection_prep.ipynb": NB01_REPLACEMENTS,
    "notebooks/02_data_preprocessing.ipynb": NB02_REPLACEMENTS,
    "notebooks/03_feature_extraction_returns.ipynb": NB03_REPLACEMENTS,
    "notebooks/04_correlation_distance.ipynb": NB04_REPLACEMENTS,
    "notebooks/05_train_test_split.ipynb": NB05_REPLACEMENTS,
    "notebooks/06_algorithm_selection_hierarchical_vs_kmeans.ipynb": NB06_REPLACEMENTS,
}

def apply_replacements(nb_path, replacements):
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    code_cells_before = [c for c in nb["cells"] if c["cell_type"] == "code"]
    errs_before = [o for c in code_cells_before for o in c.get("outputs", []) if o.get("output_type") == "error"]

    modified = 0
    for idx, new_text in replacements.items():
        if idx < len(nb["cells"]):
            cell = nb["cells"][idx]
            if cell["cell_type"] == "markdown":
                lines = [line + "\n" for line in new_text.split("\n")]
                if lines:
                    lines[-1] = lines[-1].rstrip("\n")
                cell["source"] = lines
                modified += 1
            else:
                print(f"  [WARN] Cell {idx} in {nb_path} is {cell['cell_type']}, not markdown!")
        else:
            print(f"  [WARN] Index {idx} out of range in {nb_path}")

    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)

    code_cells_after = [c for c in nb["cells"] if c["cell_type"] == "code"]
    errs_after = [o for c in code_cells_after for o in c.get("outputs", []) if o.get("output_type") == "error"]

    print(f"[OK] {nb_path}: refined {modified} MD cells. Code cells: {len(code_cells_after)}, Error outputs: {len(errs_after)}.")

def main():
    print("Standardizing markdown narratives across Notebooks 01 to 06...")
    for path, reps in ALL_NOTEBOOKS_TO_STANDARDIZE.items():
        apply_replacements(path, reps)

if __name__ == "__main__":
    main()

