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
│   ├── processed/                 # Lợi suất logarit, ma trận tương quan, sạch
│   └── metadata/                  # Bảng tra cứu mã CP, tên cty, ngành ICB/GICS
│
├── notebooks/                     # Jupyter Notebooks nghiên cứu & trực quan hóa
│   ├── 01_data_collection_prep.ipynb    # Thu thập, làm sạch & EDA lợi suất
│   ├── 02_correlation_distance.ipynb    # Ma trận tương quan & khoảng cách Mantegna
│   ├── 03_hierarchical_clustering.ipynb # Dendrogram, Silhouette, 4 Linkages
│   ├── 04_kmeans_pca_comparison.ipynb   # Đối chứng PCA + K-Means
│   ├── 05_stability_and_sector.ipynb    # ARI theo thời gian & đối chiếu ngành
│   └── 06_portfolio_backtest.ipynb      # Xây dựng danh mục đa dạng hóa & Backtest
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
- **Kế hoạch cho phiên tiếp theo (Phiên 2):**
  - Thực hiện **Mốc 1 - Bước 3 & Bước 4 (EDA & Tiền xử lý)**:
    1. Căn chỉnh lịch giao dịch chung giữa 100 mã (Trading Calendar Alignment).
    2. Xử lý dữ liệu thiếu: Thống kê số phiên hợp lệ và đưa ra tiêu chí chọn lọc danh sách mã đạt chuẩn ($>90-95\%$ số phiên).
    3. Tính chuỗi lợi suất logarit $r_t = \ln(P_t/P_{t-1})$.
    4. Xây dựng ma trận tương quan $\mathbf{C} = [\rho_{i,j}]$ và ma trận khoảng cách Mantegna $d(i, j) = \sqrt{2(1 - \rho_{i,j})}$ lưu vào `data/processed/`.

