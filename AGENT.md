# AGENT.md - Bộ nhớ dự án: Phân nhóm cổ phiếu phục vụ đa dạng hóa danh mục đầu tư

> **Phiên bản:** 1.0  
> **Cập nhật lần cuối:** 2026-10-27  
> **Môn học:** Học máy (Machine Learning) - Học kỳ 7  
> **Quy mô nhóm:** 2 thành viên  
> **Thời gian thực hiện:** 2 tháng (~8 tuần)  
> **Trạng thái:** Khởi tạo dự án (Phase 1: Setup & Data Pipeline)

---

## 1. Tổng quan đề tài (Project Overview)

- **Tên đề tài:** Phân nhóm cổ phiếu theo mức độ đồng biến động giá phục vụ đa dạng hóa danh mục đầu tư (Stock Clustering Based on Price Co-movement for Portfolio Diversification).
- **Thị trường mục tiêu:** Chứng khoán Việt Nam — Rổ chỉ số **VN100** (HOSE).
- **Khung thời gian thu thập dữ liệu thô:** **01/01/2022 đến 23/10/2026** (~5 năm, trải qua đầy đủ các pha thị trường: Downtrend 2022, Tích lũy 2023, Phục hồi 2024–2026).
- **Mục tiêu chính:**
  1. Nghiên cứu và hiện thực hóa kỹ thuật phân cụm phân cấp gộp (**Agglomerative Hierarchical Clustering**) với 4 tiêu chí liên kết: *Single*, *Complete*, *Average*, và *Ward*.
  2. Sử dụng độ đo khoảng cách dựa trên hệ số tương quan lợi suất logarit giữa các chuỗi cổ phiếu (**Mantegna Correlation Distance Metric**).
  3. Thu thập toàn bộ dữ liệu thô (OHLCV) của các mã thuộc VN100 vào `data/raw/` qua `vnstock3`, kèm metadata nhóm ngành ICB vào `data/metadata/`.
  4. Xác định số cụm tối ưu $k$ thông qua cắt Dendrogram và **Silhouette Score**, so sánh đối chứng với thuật toán **K-Means** trên không gian đặc trưng rút gọn bằng **PCA**.
  5. Đánh giá độ ổn định của các cụm qua các giai đoạn thời gian (Temporal Stability) bằng chỉ số **Adjusted Rand Index (ARI)**.
  6. Đối chiếu cụm học được với phân ngành thực tế của doanh nghiệp (ICB / GICS sector).
  7. Xây dựng bài toán ứng dụng: Xây dựng và đánh giá danh mục đầu tư đa dạng hóa (chọn đại diện mỗi cụm) so sánh với danh mục chọn ngẫu nhiên / trọng số đều (Equal-weighted) qua các chỉ số tài chính (Sharpe Ratio, Volatility, Maximum Drawdown).

---

## 2. Cơ sở lý thuyết & Công thức toán học (Mathematical Foundations)

### 2.1. Chuỗi lợi suất logarit (Log Returns)
Với $P_{i, t}$ là giá đóng cửa điều chỉnh (Adjusted Close) của cổ phiếu $i$ tại ngày giao dịch $t$:
$$r_{i, t} = \ln\left(\frac{P_{i, t}}{P_{i, t-1}}\right)$$

### 2.2. Ma trận tương quan & Độ đo khoảng cách tương quan (Correlation Distance)
Hệ số tương quan Pearson giữa hai chuỗi lợi suất của cổ phiếu $i$ và $j$:
$$\rho_{i, j} = \frac{\sum_{t=1}^T (r_{i,t} - \bar{r}_i)(r_{j,t} - \bar{r}_j)}{\sqrt{\sum_{t=1}^T (r_{i,t} - \bar{r}_i)^2 \sum_{t=1}^T (r_{j,t} - \bar{r}_j)^2}}$$

Để thỏa mãn các tiên đề của không gian metric (đặc biệt là bất đẳng thức tam giác theo chuẩn Mantegna 1999):
$$d(i, j) = \sqrt{2(1 - \rho_{i, j})}$$
*Ghi chú:* Giá trị $d(i, j) \in [0, 2]$. Khi $\rho = 1 \Rightarrow d = 0$; khi $\rho = 0 \Rightarrow d = \sqrt{2}$; khi $\rho = -1 \Rightarrow d = 2$.

### 2.3. Các tiêu chí liên kết (Linkage Criteria) trong Agglomerative Clustering
- **Single Linkage:** $D(A, B) = \min \{d(x, y) : x \in A, y \in B\}$
- **Complete Linkage:** $D(A, B) = \max \{d(x, y) : x \in A, y \in B\}$
- **Average Linkage (UPGMA):** $D(A, B) = \frac{1}{|A||B|} \sum_{x \in A} \sum_{y \in B} d(x, y)$
- **Ward's Linkage:** Tối thiểu hóa tổng phương sai nội cụm khi gộp 2 cụm:
  $$\Delta ESS_{AB} = \frac{|A| \cdot |B|}{|A| + |B|} \|\mu_A - \mu_B\|^2$$

### 2.4. Phương pháp đối chứng (Benchmark Algorithm)
- **PCA (Principal Component Analysis):** Giảm chiều không gian chuỗi lợi suất hoặc các đặc trưng thống kê (Volatility, Beta, Skewness, Kurtosis) xuống $p$ thành phần chính giải thích $\ge 80\%$ phương sai.
- **K-Means Clustering:** Tối ưu hóa hàm mục tiêu $J = \sum_{k=1}^K \sum_{x \in C_k} \|x - \mu_k\|^2$ trên không gian PCA.

### 2.5. Chỉ số đánh giá (Evaluation Metrics)
1. **Silhouette Coefficient:** Đo lường độ gắn kết nội cụm so với độ tách biệt ngoại cụm ($s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$).
2. **Cophenetic Correlation Coefficient (CCC):** Đo mức độ bảo toàn khoảng cách gốc trên Dendrogram.
3. **Adjusted Rand Index (ARI):**
   - Đo lường mức độ đồng thuận giữa 2 phân cụm qua 2 khoảng thời gian (Cluster Stability: $T_1$ vs $T_2$).
   - Đo lường mức độ tương đồng giữa phân cụm học máy với phân loại ngành thực tế (Cluster vs Industry Sectors).
4. **Chỉ số đánh giá danh mục (Portfolio Metrics):**
   - Lợi suất kỳ vọng danh mục: $R_p = \mathbf{w}^T \boldsymbol{\mu}$
   - Độ biến động danh mục (Volatility): $\sigma_p = \sqrt{\mathbf{w}^T \boldsymbol{\Sigma} \mathbf{w}}$
   - Tỷ số Sharpe (Sharpe Ratio): $S_p = \frac{R_p - R_f}{\sigma_p}$
   - Mức sụt giảm tối đa (Maximum Drawdown - MDD).

---

## 3. Kiến trúc dự án & Cấu trúc thư mục (Project Structure)

```text
stock-clustering-portfolio-diversification/
│
├── AGENT.md                       # Bộ nhớ dự án & hướng dẫn AI/Developer
├── README.md                      # Giới thiệu dự án vắn tắt
├── requirements.txt               # Các thư viện Python phụ thuộc
├── .gitignore                     # Cấu hình bỏ qua file nhị phân, dữ liệu tạm
│
├── docs/                          # Tài liệu môn học, báo cáo, đề bài
│   ├── detai.txt                  # Yêu cầu gốc của đề tài
│   ├── theory_notes.md            # Ghi chú cơ sở toán học & tài liệu tham khảo
│   └── report_outline.md          # Đề cương báo cáo tiểu luận
│
├── data/                          # Dữ liệu phục vụ nghiên cứu
│   ├── raw/                       # Dữ liệu giá đóng cửa thô (CSV)
│   ├── processed/                 # Dữ liệu sạch toàn kỳ, train/ và test/
│   │   ├── train/                 # Dữ liệu In-Sample (2022 - 2024): giá, lợi suất, mantegna distance
│   │   └── test/                  # Dữ liệu Out-of-Sample (2025 - 2026): giá, lợi suất backtest
│   └── metadata/                  # Bảng tra cứu mã CP, tên cty, ngành ICB/GICS
│
├── notebooks/                     # Jupyter Notebooks nghiên cứu & trực quan hóa
│   ├── 01_data_collection_prep.ipynb    # Thu thập 100 mã VN100 & metadata ICB
│   ├── 02_data_preprocessing.ipynb      # Lọc VTP/NAB, khử ngày nghỉ, Forward-fill
│   ├── 03_feature_extraction_returns.ipynb # Lợi suất logarit & kiểm định đuôi béo
│   ├── 04_correlation_distance.ipynb    # Pearson & khoảng cách Mantegna toàn kỳ
│   ├── 05_train_test_split.ipynb        # Phân chia Train (2022-2024) / Test (2025-2026)
│   ├── 06_algorithm_selection_hierarchical_vs_kmeans.ipynb # Lựa chọn thuật toán: K-Means vs Phân cụm phân cấp (Quyết định 6)
│   ├── 07_hierarchical_clustering_linkages.ipynb # So sánh 4 Linkages, Dendrogram, CCC, Quét K* (Quyết định 7 & 8)
│   ├── 08_stability_and_sector.ipynb    # ARI theo thời gian & đối chiếu ngành ICB
│   └── 09_portfolio_backtest.ipynb      # Danh mục đa dạng hóa & Out-of-Sample Backtest
│
├── src/                           # Mã nguồn module tái sử dụng
│   ├── __init__.py
│   ├── data_loader.py             # Tải dữ liệu (yfinance / vnstock)
│   ├── metrics.py                 # Tính log return, ma trận tương quan, distance
│   ├── clustering.py              # Wrapper cho Agglomerative & K-Means
│   ├── evaluation.py              # Silhouette, Cophenetic, ARI calculation
│   └── portfolio.py               # Mô phỏng chọn danh mục & tính Sharpe/MDD
│
├── reports/                       # Báo cáo kết quả và hình ảnh xuất bản
│   ├── figures/                   # Dendrogram, Clustermap, PCA plot, Backtest chart
│   └── final_report.pdf           # Báo cáo tiểu luận hoàn chỉnh
│
└── tests/                         # Unit tests kiểm tra tính chính xác của hàm
    ├── test_metrics.py
    └── test_clustering.py
```

---

## 4. Kế hoạch thực hiện 8 tuần & Phân công nhiệm vụ (Roadmap & WBS)

| Tuần | Giai đoạn | Nhiệm vụ chính | Người phụ trách | Sản phẩm đầu ra |
| :--- | :--- | :--- | :--- | :--- |
| **T1 - T2** | **Phase 1: Khởi động & Thu thập dữ liệu** | - Xây dựng pipeline tải giá (50–100 mã VN100/S&P 100, 2–3 năm).<br>- Tiền xử lý, kiểm tra dữ liệu thiếu, tính log-returns.<br>- Lập bảng metadata ánh xạ mã cổ phiếu - nhóm ngành. | **Thành viên 1 & 2** | `data/raw/`, `data/processed/`, Notebook `01` |
| **T3 - T4** | **Phase 2: Xây dựng khoảng cách & Phân cụm phân cấp** | - Xây dựng ma trận tương quan & khoảng cách Mantegna.<br>- Thực nghiệm Agglomerative với 4 linkage: Single, Complete, Average, Ward.<br>- Trực quan hóa Dendrogram & Clustermap.<br>- Xác định số cụm tối ưu $k$ qua Silhouette Score. | **Thành viên 1** | Notebook `02`, `03`, module `clustering.py` |
| **T5** | **Phase 3: Đối chứng PCA + K-Means** | - Thực hiện PCA trích xuất đặc trưng từ chuỗi lợi suất/chỉ số thống kê.<br>- Huấn luyện K-Means, vẽ biểu đồ cụm trên không gian 2D/3D PCA.<br>- So sánh Silhouette và cấu trúc cụm với Hierarchical Clustering. | **Thành viên 2** | Notebook `04` |
| **T6** | **Phase 4: Đánh giá độ ổn định & Phân tích ngành** | - Chia dữ liệu thành các khung thời gian (rolling / sub-periods), đo ARI.<br>- Đối chiếu phân cụm với phân ngành ICB/GICS (Confusion Matrix, ARI/NMI). | **Thành viên 1** | Notebook `05`, module `evaluation.py` |
| **T7** | **Phase 5: Ứng dụng Đa dạng hóa danh mục** | - Chọn danh mục đại diện: 1 mã/cụm (chọn mã min volatility hoặc max Sharpe).<br>- So sánh với Benchmark (Random Portfolios 1000 mẫu & Equal-Weighted).<br>- Backtest hiệu suất: Cumulative Returns, Sharpe Ratio, Max Drawdown. | **Thành viên 2** | Notebook `06`, module `portfolio.py` |
| **T8** | **Phase 6: Hoàn thiện báo cáo & Slide bảo vệ** | - Tổng hợp toàn bộ kết quả, biểu đồ chất lượng cao vào báo cáo.<br>- Viết báo cáo tiểu luận hoàn chỉnh và slide thuyết trình.<br>- Rà soát mã nguồn, kiểm thử tái lập (reproducibility). | **Cả nhóm** | `reports/final_report.pdf`, slide bảo vệ |

---

## 5. Quy tắc phát triển & Tiêu chuẩn học máy (ML Best Practices)

Tuân thủ nghiêm ngặt kỹ năng `ml-best-practices`:
1. **Storytelling qua Notebooks:** Mọi cell mã nguồn phân tích phải đi kèm ít nhất một cell Markdown giải thích ý nghĩa kinh tế/tài chính và kết luận thống kê.
2. **Xử lý chuỗi thời gian chặt chẽ (Temporal Discipline):**
   - Không được xáo trộn ngẫu nhiên dữ liệu chuỗi thời gian (No random shuffle).
   - Khi chia tập thời gian để kiểm định độ ổn định (Stability Test), luôn chia theo thứ tự thời gian (Chronological Split: ví dụ Năm 1 vs Năm 2, hoặc Bull Market vs Bear Market).
3. **Tính toán ma trận tương quan:** Luôn kiểm tra tính xác định dương (Positive Semi-Definite) của ma trận tương quan/hiệp phương sai.
4. **Reproducibility:** Mọi thuật toán ngẫu nhiên (K-Means, PCA solver, Monte Carlo Random Portfolios) phải gán `random_state=42`.
5. **Tiêu chuẩn Code:**
   - Đặt type hint đầy đủ trong các hàm thuộc `src/`.
   - Viết docstring giải thích tham số đầu vào, đầu ra, công thức toán sử dụng.
   - Thư viện trực quan hóa: ưu tiên `seaborn` và `matplotlib` cho ấn bản in ấn/báo cáo; có thể dùng `plotly` cho dashboard/tương tác.

---

## 6. Lời khuyên và Chỉ dẫn dành cho AI Pair-Programming

- Khi làm việc với người dùng, luôn giao tiếp bằng **Tiếng Việt có dấu**, phong cách mạch lạc, học thuật nhưng thực tế.
- Tạo đường dẫn nhấp được (clickable links) theo định dạng markdown `file:///path/to/file` cho mọi file và ký hiệu hàm/class.
- Luôn kiểm tra tính khả thi của dữ liệu tài chính (Yahoo Finance API `yfinance` hoặc `vnstock` cho chứng khoán Việt Nam).
- Ưu tiên tính tái lập và giải thích rõ ràng từng quyết định lựa chọn siêu tham số (như ngưỡng cắt dendrogram $k$, linkage criterion).

---

## 7. Nhật ký các phiên làm việc (Session Logs & Handover)

### Phiên 1 (2026-10-27) - Khởi động dự án, Pipeline thu thập & Thu thập hoàn tất 100 mã VN100
- **Trạng thái:** Hoàn tất Mốc 1 - Bước 1 & Bước 2 theo [docs/lo_trinh_machine_learning.md](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/docs/lo_trinh_machine_learning.md).
- **Những việc đã làm:**
  1. Phân tích chi tiết yêu cầu đề tài từ [docs/detai.txt](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/docs/detai.txt), xác định bài toán theo Tom Mitchell $[T, E, P]$.
  2. Thống nhất phạm vi nghiên cứu: Rổ chỉ số **VN100 (HOSE)** trong khung thời gian 5 năm (**01/01/2022 – 23/10/2026**).
  3. Xây dựng module thu thập [src/data_loader.py](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/src/data_loader.py) với kiến trúc Multi-backend (dynamic importlib, hỗ trợ vnstock v5 và fallback tự động Yahoo Finance `.VN`).
  4. Xây dựng script dòng lệnh [scripts/crawl_vn100.py](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/scripts/crawl_vn100.py) kèm thanh tiến trình `tqdm` và tính năng Resume bỏ qua mã đã cào xong.
  5. Người dùng đã tự thực thi cào dữ liệu thành công **100/100 mã cổ phiếu** thô lưu trữ độc lập tại `data/raw/{symbol}.csv`.
  6. Xây dựng bảng metadata đối chứng nhóm ngành ICB cấp 1-2 tại [data/metadata/vn100_symbols.csv](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/data/metadata/vn100_symbols.csv).
  7. Khởi tạo notebook [notebooks/01_data_collection_prep.ipynb](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/notebooks/01_data_collection_prep.ipynb) và ghi chép đề cương báo cáo tại [docs/note_dua_vao_bao_cao.md](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/docs/note_dua_vao_bao_cao.md).
- **Phát hiện quan trọng:** Một số cổ phiếu niêm yết muộn/chuyển sàn (như `VTP` chuyển sàn 03/2024 chỉ có ~686 phiên thay vì ~1200 phiên). Bắt buộc phải dùng `adj_close` để loại bỏ nhiễu chia cổ tức.

### Phiên 2 (2026-10-29) - Tiền xử lý Dữ liệu Thực nghiệm & Trích chọn Đặc trưng Lợi suất Logarit (Bước 3.1)
- **Trạng thái:** Hoàn tất Mốc 1 - Bước 2 (Làm sạch & Căn chỉnh lịch) & Bước 3.1 (Trích chọn Đặc trưng Lợi suất Logarit).
- **Những việc đã làm:**
  1. Commit và push toàn bộ 100 tệp CSV dữ liệu giá thô VN100 (2022–2026) lên GitHub repository sau khi mở chặn `.gitignore` (commit `6419b21`).
  2. Xây dựng module tiền xử lý cốt lõi [src/preprocessing.py](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/src/preprocessing.py):
     - Phát hiện và lọc bỏ 68 ngày nghỉ lễ sàn HOSE ($Volume = 0$) bị Yahoo Finance điền lặp giá, bảo toàn lịch giao dịch thực 1.187 phiên.
     - Lọc độ bao phủ lịch sử $\ge 90\%$: Giữ lại 98 mã cổ phiếu, loại bỏ 2 mã chuyển sàn muộn `VTP` và `NAB`.
     - Căn chỉnh lịch giao dịch chuẩn và điền khuyết 48 ô cho 3 mã `CTR`, `HHV`, `EVF` bằng phương pháp Forward-Fill (`ffill`). Dữ liệu đạt độ sạch 100% (0 NaN).
  3. Xây dựng ứng dụng web tương tác [scripts/preprocessing_app.py](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/scripts/preprocessing_app.py) (chạy tại `http://127.0.0.1:8000`) trực quan hóa so sánh Trước vs Sau xử lý, biểu đồ phân phối chuỗi lợi suất, biểu đồ Top 10 rủi ro vs lợi nhuận và bảng hồ sơ tài chính 98 mã.
  4. Thực hiện Trích chọn Đặc trưng Lợi suất Logarit $r_t = \ln(P_t / P_{t-1})$:
     - Tạo ma trận đặc trưng $1.186 \text{ phiên} \times 98 \text{ mã}$ tại [data/processed/log_returns.csv](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/data/processed/log_returns.csv).
     - Tạo bảng 8 chỉ số tài chính 98 mã tại [data/processed/stock_financial_features.csv](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/data/processed/stock_financial_features.csv).
  5. Thống nhất kiến trúc: Phân định ranh giới rõ ràng giữa Trích chọn Đặc trưng (Mục 3.1 - Lợi suất logarit đơn lẻ) và Biểu diễn Tri thức Liên kết (Mục 3.2 - Ma trận tương quan Pearson và Ma trận khoảng cách siêu mêtric Mantegna, hiện tạm khóa để người dùng kiểm chứng).
  6. Cập nhật tài liệu: [docs/note_dua_vao_bao_cao.md](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/docs/note_dua_vao_bao_cao.md), [docs/ghi_chu_data.xlsx](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/docs/ghi_chu_data.xlsx) và script cập nhật [scripts/update_ghi_chu_excel.py](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/scripts/update_ghi_chu_excel.py).
### Phiên 3 (2026-10-30) - Bước 3.2: Biểu diễn Tri thức Quan hệ & Thiết lập Không gian Khoảng cách Siêu Mêtric Mantegna
- **Trạng thái:** Hoàn tất Mốc 1 - Bước 3.2 (Ma trận tương quan Pearson, Không gian Khoảng cách Siêu Mêtric Mantegna, Kiểm định 4 Tiên đề Metric, Phản chứng Nghịch lý Euclid, và Web App Studio v1.2.0).
- **Những việc đã làm:**
  1. Chứng minh toán học và thực nghiệm **Nghịch lý Khoảng cách Euclid (The Euclidean Paradox)**:
     - Phản chứng *Bẫy biên độ dao động (Scale Bias)* và *Bẫy ngược pha (Antiphase Trap)*.
     - Xuất bản biểu đồ minh họa khoa học [`reports/figures/euclidean_vs_pearson_paradox.png`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/reports/figures/euclidean_vs_pearson_paradox.png).
  2. Xây dựng cơ sở lý thuyết **Khoảng cách Siêu Mêtric Mantegna** $d(i, j) = \sqrt{2(1 - \rho_{i, j})}$:
     - Chứng minh hình học mặt cầu đơn vị $\mathbb{S}^{T-1}$ và 4 tiên đề mêtric (đặc biệt là bất đẳng thức tam giác loại bỏ lỗi đảo ngược phân cấp - Inversion trên Dendrogram).
     - Xuất bản biểu đồ hình học [`reports/figures/mantegna_transformation_metric.png`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/reports/figures/mantegna_transformation_metric.png).
  3. Hoàn thành và chạy live Notebook khoa học [`notebooks/02_correlation_distance.ipynb`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/notebooks/02_correlation_distance.ipynb):
     - Kiểm định bất đẳng thức tam giác trên 20.000 bộ ba: $0$ vi phạm ($100\%$ hợp lệ).
     - Phát hiện các cặp đồng biến động mạnh phản ánh hoàn hảo phân ngành thực tế: `HSG - NKG` ($\rho=0.8873, d=0.4747$), `DCM - DPM` ($\rho=0.8625, d=0.5244$), `SSI - VCI` ($\rho=0.8197, d=0.6004$).
  4. Xuất bản 2 ma trận cốt lõi:
     - [`data/processed/correlation_matrix.csv`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/data/processed/correlation_matrix.csv) ($98 \times 98$).
     - [`data/processed/mantegna_distance_matrix.csv`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/data/processed/mantegna_distance_matrix.csv) ($98 \times 98$).
  5. Tách biệt hoàn toàn và kích hoạt ứng dụng Web Dashboard Studio v1.2.0 tại thư mục độc lập [`web_app/`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/web_app):
     - Chạy nền trực tiếp tại `http://127.0.0.1:8000`.
     - Kích hoạt tính năng tính ma trận tương quan và khoảng cách Mantegna.
     - Thêm bảng Top 10 cặp đồng pha nhất vs Top 10 cặp phân kỳ/trực giao nhất.
     - Thêm biểu đồ phân phối khoảng cách Mantegna và Bản đồ nhiệt tương tác (Heatmap Canvas) chuyển đổi mượt mà giữa $\rho$ và $d$.
   6. Tái cơ cấu và hoàn thiện hệ thống 4 Notebooks tuần tự:
      - 01_data_collection_prep.ipynb: Thu thập giá thô 100 mã.
      - 02_data_preprocessing.ipynb: Tiền xử lý, lọc VTP/NAB, khử 68 ngày lễ, điền khuyết ffill.
      - 03_feature_extraction_returns.ipynb: Trích chọn đặc trưng lợi suất logarit, kiểm định Jarque-Bera.
      - 04_correlation_distance.ipynb: Biểu diễn quan hệ tương quan Pearson và Mantegna metric.
  7. Đồng bộ tài liệu báo cáo: [`docs/note_dua_vao_bao_cao.md`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/docs/note_dua_vao_bao_cao.md).
- **Kế hoạch cho phiên tiếp theo (Phiên 5 - Mốc 2: Mô hình hóa Phân cụm):**
  - Chuyển sang **Notebook `06_hierarchical_clustering.ipynb`**:
    1. Huấn luyện Phân cụm Phân cấp (Agglomerative Hierarchical Clustering) với 4 tiêu chí liên kết: *Single*, *Complete*, *Average (UPGMA)*, và *Ward*.
    2. Vẽ Dendrogram và Clustermap sắp xếp lại theo thứ tự cụm.
    3. Đo hệ số bảo toàn khoảng cách gốc Cophenetic Correlation Coefficient (CCC).
    4. Quét số cụm tối ưu $k \in [3, 15]$ bằng Silhouette Score Analysis.

### Phiên 4 (2026-10-30) - Bước 3.3: Phân chia Train/Test Chuỗi Thời Gian & Hoàn tất Báo cáo KT1 (XeLaTeX)
- **Trạng thái:** Hoàn tất toàn diện 100% yêu cầu Bài kiểm tra 1 (Mốc 1: Bước 1, Bước 2, Bước 3.1, 3.2, 3.3).
- **Những việc đã làm:**
  1. Xây dựng và thực thi [notebooks/05_train_test_split.ipynb](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/notebooks/05_train_test_split.ipynb):
     - Phân chia tập dữ liệu In-Sample Train (2022--2024: 740 phiên giá, 739 phiên lợi suất) và Out-of-Sample Test (2025--2026: 447 phiên giá).
     - Độc lập tính ma trận tương quan và khoảng cách Mantegna cách ly hoàn toàn trên tập Train ($Q = 7.54 \gg 1$), lưu trữ tại `data/processed/train/`.
  2. Soạn thảo và hoàn thiện Báo cáo kỹ thuật chuẩn mực [docs/report/Bao_cao_KT1_Nhom_StockClustering.tex](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/docs/report/Bao_cao_KT1_Nhom_StockClustering.tex):
     - Chuẩn hóa toàn bộ phông chữ Times New Roman bằng XeLaTeX (`fontspec`).
     - Tích hợp logo chính thức ICTU và bảng tự đánh giá 10 tiêu chí (xltabular).
     - Rà soát và tinh gọn 5 tài liệu tham khảo cốt lõi học thuật (Markowitz 1952, Mitchell 1997, Mantegna 1999, Laloux 1999, Lopez de Prado 2018) đi kèm trích dẫn `\cite` chính xác trong văn bản.
     - Hoàn thiện Phụ lục B với bảng nhật ký đóng góp của các thành viên nhóm.
  3. Xuất bản tệp PDF hoàn chỉnh: [docs/report/Bao_cao_KT1_Nhom_StockClustering.pdf](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/docs/report/Bao_cao_KT1_Nhom_StockClustering.pdf).

### Phiên 5 (2026-11-09) - Thấu triệt Triết lý Giảng viên & Thiết lập Kế hoạch Evidence-Based Mốc 2 (Bài kiểm tra 2)
- **Trạng thái:** Chuẩn bị sẵn sàng 100% nền tảng lý thuyết và kế hoạch hành động thực nghiệm cho Mốc 2 (Tuần 6).
- **Những việc đã làm:**
  1. Phân tích toàn diện bộ bài giảng 9 tuần của thầy Nguyễn Tuấn Anh tại `machine-learning/` (đặc biệt là Bài 8: Học không giám sát và Phân cụm; Bài 2: Quy trình dự án ML; và Giáo trình 2026 Chương 11 & 12).
  2. Đối chiếu sâu sắc giữa bài giảng của thầy với các công trình nghiên cứu quốc tế trên Google Scholar (Mantegna 1999, Markowitz 1952, Marcos López de Prado 2016/2018, Laloux et al. 1999, Rousseeuw 1987, Sokal & Rohlf 1962), lưu trữ tại [`docs/phan_tich_bai_giang_va_tai_lieu_scholar.md`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/docs/phan_tich_bai_giang_va_tai_lieu_scholar.md).
  3. Thấu triệt chỉ đạo trực tiếp từ giảng viên: *"Mọi quyết định, thuật toán, con số đều phải trải qua so sánh thực nghiệm và lựa chọn thứ tốt nhất có chỉ số chứng minh"*.
  4. Hệ thống hóa **Chuỗi 7 Quyết định Kỹ thuật có Bằng chứng Thực nghiệm** từ Mốc 1 đến Mốc 2 vào [`docs/note_dua_vao_bao_cao.md`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/docs/note_dua_vao_bao_cao.md).
  5. Xây dựng Kế hoạch 3 Vòng thực nghiệm lặp cho Mốc 2:
     - *Vòng 1:* Thử nghiệm 4 Linkages (Single, Complete, Average, Ward), đo hệ số Cophenetic CCC và phân bố kích thước cụm để bộc lộ nhược điểm Chaining effect.
     - *Vòng 2:* Quét siêu tham số $K \in [3, 15]$ theo Silhouette Score, nhận diện "điểm số ảo" và chứng minh $K^* = 6$ (Ward) là tối ưu.
     - *Vòng 3:* Xây dựng Baseline (PCA + K-Means) và kiểm định ổn định thời gian qua Adjusted Rand Index (ARI).
  6. Xây dựng "Công thức vàng 4 bước" trả lời vấn đáp cá nhân đạt điểm 10 trước giảng viên.
  7. Thống nhất phương thức triển khai: Xây dựng Notebook `06_algorithm_selection_hierarchical_vs_kmeans.ipynb` để đối chứng thuật toán không thiên vị trước khi bước sang so sánh 4 linkage.

### Phiên 6 (2026-11-10) - Bước 6: So Sánh Đối Chứng Toàn Diện 3 Trường Phái & Hoàn Thành Notebook 06
- **Trạng thái:** Hoàn tất toàn diện Quyết định Kỹ thuật số 6: Lựa chọn Thuật toán cốt lõi cho đề tài (Đáp ứng trọn vẹn Tiêu chí 1: Lựa chọn thuật toán & Tiêu chí 2: Mô hình cơ sở Baseline của Bài kiểm tra 2 - Tuần 6).
- **Những việc đã làm:**
  1. Thấu triệt chỉ đạo mở rộng đối chứng không chỉ giữa K-Means và Hierarchical Bottom-Up, mà mở rộng so sánh toàn diện **3 trường phái thuật toán phân cụm**:
     - *Phân hoạch phẳng (Flat Partitioning):* K-Means (Euclid) và K-Means (PCA 5D).
     - *Phân cấp Chia dần (Top-Down / Divisive):* Bisecting K-Means (chia nhị phân từ gốc) và DIANA (Divisive Analysis trên khoảng cách Mantegna).
     - *Phân cấp Gộp dần (Bottom-Up / Agglomerative):* Khảo sát 4 tiêu chí liên kết (*Single, Complete, Average, Ward*) trên ma trận khoảng cách Mantegna.
  2. Xây dựng và thực thi thành công 100% mã nguồn Notebook khoa học tự chứa [`notebooks/06_algorithm_selection_hierarchical_vs_kmeans.ipynb`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/notebooks/06_algorithm_selection_hierarchical_vs_kmeans.ipynb) trên tập dữ liệu Train ($739 \text{ phiên} \times 98 \text{ mã}$).
  3. Thu thập các bằng chứng định lượng thực nghiệm đanh thép:
     - *Tính ổn định tái lập (Pairwise ARI qua 30 random seeds):* Flat K-Means bị bất ổn định nặng ($\overline{ARI} = 0.4722 \pm 0.1272$); Top-Down Bisecting K-Means đạt $0.5517 \pm 0.0883$ (do mỗi nhánh chia nhị phân vẫn dùng 2-Means stochastic); Bottom-Up Hierarchical đạt $ARI = 1.0000 \pm 0.0000$ tuyệt đối (tất định 100%, 0 phương sai ở mọi linkage).
     - *Khả năng bóc tách tương quan ($\Delta = \bar{\rho}_{\text{intra}} - \bar{\rho}_{\text{inter}}$):*
       - Flat K-Means (Euclid) rơi vào bẫy nghịch lý: $\Delta = -0.0018$ (ngoài cụm tương quan cao hơn trong cụm).
       - Top-Down Bisecting K-Means: $\Delta = +0.0428$.
       - Top-Down DIANA: $\Delta = +0.2122$ nhưng rơi vào **Bẫy lột vỏ ngoại lai (Outlier Peeling Trap)**, bóc 4 mã cá biệt để lại siêu cụm 90 mã $[90, 4, 1, 1, 1, 1]$ (không thể dùng phân bổ vốn).
       - Bottom-Up Ward: $\bar{\rho}_{\text{intra}} = 0.4438$ (cao nhất), $\Delta = +0.0932$ và kích thước cụm phân bổ cân bằng lý tưởng $[33, 21, 14, 13, 10, 7]$.
     - *Bảo toàn liên kết ngành vi mô:* Cặp cổ phiếu cùng ngành (`HSG-NKG`, `DCM-DPM`) tạo các hạt nhân vi mô ($d \approx 0.47 - 0.52$), Bottom-Up khóa chặt các cặp này từ đáy cây, trong khi các phương pháp top-down và flat dễ bị chia cắt sai ranh giới.
  4. Xuất bản biểu đồ khoa học 3 Panel đối chứng tại [`reports/figures/06_kmeans_vs_hierarchical_comparison.png`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/reports/figures/06_kmeans_vs_hierarchical_comparison.png) và đồng bộ vào [`docs/report/images/hinh_kmeans_vs_hierarchical.png`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/docs/report/images/hinh_kmeans_vs_hierarchical.png).
  5. Đồng bộ hóa toàn bộ tài liệu dự án: Cập nhật đầy đủ Mục 1, Mục 8, Mục 9, Mục 11–14 trong [`docs/note_dua_vao_bao_cao.md`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/docs/note_dua_vao_bao_cao.md) (bao gồm sửa trùng lặp số mục 10, đồng bộ toàn bộ số liệu thực nghiệm 3 trường phái từ Notebook 06 và tách bạch trạng thái bước tiếp theo tại Notebook 07). Chuẩn hóa toàn bộ văn bản Markdown trong Notebook 06 theo phong cách con người súc tích, học thuật, đúng trọng tâm.
- **Kế hoạch cho bước tiếp theo (Notebook 07):**
  - Chuyển sang **Notebook `07_hierarchical_clustering_linkages.ipynb`**:
    1. Huấn luyện và so sánh chi tiết 4 tiêu chí liên kết: *Single*, *Complete*, *Average (UPGMA)*, và *Ward* trên ma trận khoảng cách Mantegna tập Train.
    2. Vẽ 4 cây phả hệ Dendrogram, đo hệ số tương quan Cophenetic (CCC).
    3. Nhận diện hiện tượng xâu chuỗi (Chaining effect) của Single Linkage.
    4. Quét siêu tham số số cụm $K \in [3, 15]$ bằng Silhouette Score Analysis để chốt số cụm tối ưu $K^* = 6$.

### Phiên 7 (2026-11-12) - Bước 7: So Sánh 4 Tiêu Chí Liên Kết, Chốt Ward & $K^* = 10$ (Hoàn Thành Notebook 07)
- **Trạng thái:** Hoàn tất toàn diện Quyết định Kỹ thuật số 7 (*Chọn tiêu chí liên kết*) và Quyết định Kỹ thuật số 8 (*Chọn số cụm tối ưu $K^*$*), đáp ứng đầy đủ Tiêu chí 1–7 của Bài kiểm tra 2 (Tuần 6).
- **Những việc đã làm:**
  1. Xây dựng và thực thi tự chứa 100% [`notebooks/07_hierarchical_clustering_linkages.ipynb`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/notebooks/07_hierarchical_clustering_linkages.ipynb) (qua script [`scripts/create_nb07.py`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/scripts/create_nb07.py)) trên dữ liệu tập Train ($739 \text{ phiên} \times 98 \text{ mã}$).
  2. Kiểm chứng tính hợp lệ toán học của **Ward Linkage** trên khoảng cách Mantegna thông qua đẳng thức Euclid trên mặt cầu đơn vị $\mathbb{S}^{T-1}$ với sai số cực đại chỉ $3.77 \times 10^{-15}$.
  3. **Vòng 1 (CCC & Dendrogram):** `Average` ($CCC = 0.9046$), `Single` ($0.8664$), `Complete` ($0.6760$), `Ward` ($0.3615$). Xuất biểu đồ `07_dendrograms_4_linkages.png`.
  4. **Vòng 2 (Quét $K \in [3, 15]$ & Ma trận Đa tiêu chí):**
     - Lật tẩy điểm số Silhouette ảo ở $K=3$ của `Single` và `Average` (`0.1486`, nhưng dồn `98.0%` mã vào 1 cụm `[96, 1, 1]`).
     - Trong $52$ cấu hình khảo sát, chỉ có **$11$ cấu hình** vượt qua bộ lọc khả thi (`0 Singleton` & `MaxShare <= 50%`) và 100% thuộc về **Ward Linkage**.
     - Trong dải danh mục $K \in [5, 10]$, ma trận đa tiêu chí chốt **Ward Linkage tại $K^* = 10$** (`Composite Score = 0.5889`, `Silhouette = 0.0296`, $\Delta = +0.1389$, `Norm Entropy = 0.9203`, `0 Singleton`, kích thước `[21, 19, 13, 10, 10, 8, 7, 4, 3, 3]`).
  5. **Vòng 3A & 3B (Đối chứng 2 biến thể Baseline & Block Sub-sampling):**
     - Đối chứng tại $K^*=10$: Bottom-Up Ward ($\Delta = +0.1389$) vượt trội cả `KMeans_PCA_5D` ($\Delta = +0.0771$, $30.50\%$ phương sai, $1$ Singleton) lẫn `KMeans_PCA_45D_80pct` ($\Delta = +0.0224$, $80.34\%$ phương sai, bị lời nguyền số chiều).
     - Kiểm định Block Sub-sampling ($B=30$, $80\%$ khối phiên): Ward đạt $\Delta = +0.1398 \pm 0.0114$ và `Silhouette = 0.0317 ± 0.0037` (cao gần gấp đôi Baseline `+0.0736 ± 0.0093` và `0.0188 ± 0.0029`), trong khi `ARI` đạt `0.6914 ± 0.1215` (so với `0.8485 ± 0.0823` của `PCA 5D` do Ward nhạy hơn ở các nhánh hợp nhất mức cao cho mã ranh giới).
  6. **Phân tích hồ sơ 10 cụm & Error Analysis:** Tách rõ các khối thuần ngành (*Ngân hàng* 13 mã $\bar{\rho}=0.600$, *Vingroup* 3 mã $\bar{\rho}=0.534$, *Phân bón* 4 mã $\bar{\rho}=0.670$, *Chứng khoán-Thép* 10 mã $\bar{\rho}=0.696$); chỉ ra các mã ranh giới có Silhouette âm (`TCB -0.1421`, `SBT -0.1233`, `CTD -0.1132`, `VCB -0.1123`).
  7. **Xuất bản Artifact & Đồng bộ tài liệu:** Lưu 5 bộ biểu đồ vào `reports/figures/` & `docs/report/images/`, xuất [`data/processed/train/train_clusters_optimal.csv`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/data/processed/train/train_clusters_optimal.csv), `linkage_k_sweep_metrics.csv`, `nb07_summary.json` và cập nhật [`docs/note_dua_vao_bao_cao.md`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/docs/note_dua_vao_bao_cao.md).
  8. **Chuẩn hóa văn phong Markdown toàn diện (Notebooks 01–07):** Chuẩn hóa đồng bộ cách diễn đạt của toàn bộ 7 notebook theo phong cách kỹ thuật con người (ngắn gọn, súc tích, dựa trên số liệu thực tế, không có từ ngữ trừu tượng hoa mỹ). Thống nhất định dạng cấu trúc chung: Header chuẩn hóa (`Mục tiêu, Dữ liệu, Phương pháp, Các bước thực hiện`), tiêu đề mục rõ ràng, và ô Tổng kết thống nhất 3 phần tiếng Việt (`Câu hỏi & Trả lời`, `Kết quả phân tích dữ liệu chính`, `Nhận định & Hướng đi tiếp theo`). Toàn bộ 100% code cells và kết quả thực thi được bảo lưu nguyên vẹn (0 lỗi). Đồng bộ cả 2 generator scripts `create_nb06.py` và `create_nb07.py`.
- **Kế hoạch cho bước tiếp theo (Notebook 08):**
  - Chuyển sang **Notebook `08_stability_and_sector.ipynb`**: Đánh giá tính ổn định liên pha theo chu kỳ năm (*2022 Downtrend* vs *2023 Tích lũy* vs *2024 Phục hồi*) bằng `ARI` và đối chiếu 10 cụm tối ưu với 11 nhóm ngành thực tế chuẩn ICB.

### Phiên 8 (2026-11-13) - Bước 9: Đánh Giá Độ Ổn Định Liên Pha & Đối Chiếu 11 Phân Ngành ICB (Hoàn Thành Notebook 08)
- **Trạng thái:** Hoàn thành 100% Notebook `08_stability_and_sector.ipynb` (9/10 bước toàn dự án), đáp ứng trọn vẹn toàn bộ 7 tiêu chí nhóm của Mốc 2 (Bài kiểm tra 2 - Tuần 6).
- **Những việc đã làm:**
  1. Xây dựng và thực thi tự chứa 100% [`notebooks/08_stability_and_sector.ipynb`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/notebooks/08_stability_and_sector.ipynb) qua [`scripts/create_nb08.py`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/scripts/create_nb08.py) (13 cells: 6 code cells, 7 markdown cells; 0 lỗi).
  2. **Thực nghiệm 1 (Độ ổn định liên pha - Temporal Stability):**
     - Huấn luyện độc lập mô hình Ward trên 3 chu kỳ: 2022 (Downtrend 245 phiên), 2023 (Tích lũy 247 phiên), 2024 (Phục hồi 247 phiên).
     - Đo ma trận đối xứng ARI: Tương đồng giữa các pha độc lập đạt trung bình $ARI = 0.3220 \pm 0.0142$ ($2022 \text{ vs } 2023: 0.3074$; $2023 \text{ vs } 2024: 0.3173$; $2022 \text{ vs } 2024: 0.3413$).
     - Tương đồng giữa từng pha với Toàn kỳ Train: 2022 đạt **$0.5686$**, 2023 đạt **$0.3623$**, 2024 đạt **$0.3427$** (trung bình $0.4245$). Khẳng định mô hình nắm bắt cấu trúc rủi ro cốt lõi của giai đoạn thị trường giảm mà vẫn thích ứng linh hoạt với các pha phục hồi.
  3. **Thực nghiệm 2 (Đối chiếu 10 cụm với 11 ngành ICB cấp 1):**
     - Ánh xạ 41 mô tả ngành ban đầu về 11 ngành ICB cấp 1 chuẩn quốc tế.
     - Lập ma trận chéo $10 \times 11$: $NMI = 0.5339$, $V\text{-Measure} = 0.5339$, $ARI_{ICB} = 0.2895$, độ thuần khiết bình quân $Purity = 60.20\%$.
     - **3 cụm đạt Purity 100%:** Cụm 6 (13/13 Ngân hàng thương mại), Cụm 3 (4/4 Phân bón - Hóa chất `DCM, DPM, DGC, BFC`), Cụm 8 (3/3 Họ Vingroup `VIC, VHM, VRE`).
     - **Cụm liên ngành High-Beta:** Cụm 2 gom 7 mã Chứng khoán và 3 mã Thép (`HPG, HSG, NKG`), chứng minh thuật toán phát hiện tính chất đồng chu kỳ thanh khoản thị trường sâu sắc hơn phân ngành danh nghĩa.
     - **Cụm phòng thủ:** Cụm 10 gom các mã vốn hóa lớn/điều tiết (`VCB, TCB, SSB` cùng `VNM, SAB, VJC, SCS, VPI`).
  4. **Xuất bản Artifacts & Đồ thị:**
     - Biểu đồ lưu vào `reports/figures/` và `docs/report/images/`: `08_temporal_stability_ari.png` và `08_crosstab_clusters_vs_icb.png`.
     - File dữ liệu: [`cluster_icb_mapping.csv`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/data/processed/train/cluster_icb_mapping.csv) và [`nb08_stability_summary.json`](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/data/processed/train/nb08_stability_summary.json).
- **Kế hoạch cho bước tiếp theo:**
  - Hoàn thiện Báo cáo Tiểu luận LaTeX cho Bài kiểm tra 2 (`Bao_cao_KT2_Nhom_StockClustering.tex`).
  - Chuẩn bị cẩm nang vấn đáp 3 câu hỏi cá nhân (Tiêu chí 8, 9, 10).
  - Triển khai **Notebook `09_portfolio_backtest.ipynb`** (Ứng dụng danh mục Markowitz & Backtest Out-of-Sample 2025–2026).



