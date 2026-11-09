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
│   ├── 06_hierarchical_clustering.ipynb # Dendrogram, Silhouette, 4 Linkages trên Train
│   ├── 07_kmeans_pca_comparison.ipynb   # Đối chứng PCA + K-Means
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
  7. Thống nhất phương thức triển khai: Xây dựng Notebook `06_hierarchical_clustering.ipynb` tự chứa (self-contained), đi từng bước có kiểm soát chặt chẽ của người dùng.



