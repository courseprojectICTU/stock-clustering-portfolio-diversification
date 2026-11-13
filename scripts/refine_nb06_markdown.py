"""
Script chuẩn hóa các ô Markdown trong Notebook 06:
Chuyển đổi sang phong cách con người viết, ngắn gọn, súc tích, đúng trọng tâm.
Giữ nguyên toàn bộ mã nguồn và outputs đã thực thi của các ô code.
"""

import nbformat

NB_PATH = "notebooks/06_algorithm_selection_hierarchical_vs_kmeans.ipynb"

with open(NB_PATH, "r", encoding="utf-8") as f:
    nb = nbformat.read(f, as_version=4)

# 1. Cell 0: Header
nb.cells[0].source = """# Bước 6: Lựa Chọn Thuật Toán - So Sánh K-Means & Phân Cụm Phân Cấp (Hierarchical)

- **Môn học:** Học máy (Machine Learning) - HK7
- **Đề tài:** Phân nhóm cổ phiếu VN100 phục vụ đa dạng hóa danh mục đầu tư
- **Dữ liệu vào:** Dữ liệu tập Train (`train_log_returns.csv`, `train_correlation_matrix.csv`, `train_mantegna_distance_matrix.csv`) từ **Notebook 05**
- **Mục đích:** Quyết định số 6 — Đưa K-Means và Phân cụm phân cấp lên bàn cân thực nghiệm để chọn mô hình chính (Proposed Model) và mô hình cơ sở (Baseline).

---

### Mục tiêu:
1. **So sánh lý thuyết:** Phân tích sự khác biệt về hàm mục tiêu, không gian đầu vào và cấu trúc cụm giữa K-Means và Phân cụm phân cấp (theo Bài 8 bài giảng).
2. **Khảo sát tính tương thích với dữ liệu tài chính:** Kiểm tra K-Means (Euclidean, PCA) vs Phân cụm phân cấp (nhận trực tiếp ma trận khoảng cách siêu mêtric Mantegna).
3. **Thực nghiệm đối chứng khách quan:**
   - Đo độ ổn định tái lập qua 30 random seeds (Adjusted Rand Index - ARI).
   - Đo khả năng bóc tách tương quan nội cụm vs liên cụm ($\\Delta = \\bar{\\rho}_{\\text{intra}} - \\bar{\\rho}_{\\text{inter}}$).
   - Đánh giá khả năng bảo toàn các cặp đồng ngành kinh điển (`HSG - NKG`, `DCM - DPM`, `SSI - VCI`).
4. **Kết luận:** Chọn mô hình đề xuất chính và mô hình cơ sở đối chứng cho Bài kiểm tra 2."""

# 2. Cell 2: Nạp dữ liệu
nb.cells[2].source = """---
## 1. Nạp Dữ Liệu Huấn Luyện (In-Sample Train Data)

Tuân thủ nguyên tắc không rò rỉ dữ liệu (López de Prado, 2018), toàn bộ quá trình so sánh và lựa chọn mô hình chỉ dùng dữ liệu tập **Train (2022–2024)**. Tập Test được giữ nguyên cho khâu Backtest sau này.

Nạp 3 tệp dữ liệu từ `data/processed/train/`:
- `train_log_returns.csv`: Chuỗi lợi suất logarit ($739 \\text{ phiên} \\times 98 \\text{ mã}$).
- `train_correlation_matrix.csv`: Ma trận tương quan Pearson $\\rho \\in [-1, 1]$ ($98 \\times 98$).
- `train_mantegna_distance_matrix.csv`: Ma trận khoảng cách siêu mêtric Mantegna $d = \\sqrt{2(1-\\rho)} \\in [0, 2]$ ($98 \\times 98$)."""

# 3. Cell 4: So sánh lý thuyết
nb.cells[4].source = """---
## 2. So Sánh Lý Thuyết Giữa K-Means & Phân Cụm Phân Cấp

*(Theo Bài giảng Bài 8 — Thầy Nguyễn Tuấn Anh)*

| Tiêu chí | K-Means (Lloyd / k-means++) | Phân cụm phân cấp (Agglomerative) |
| :--- | :--- | :--- |
| **Cơ chế tối ưu** | Cực tiểu hóa tổng bình phương sai số nội cụm: $\\mathcal{L} = \\sum \\|\\mathbf{x}_i - \\boldsymbol{\\mu}_{c_i}\\|^2$ | Gộp dần từng cặp cụm gần nhất từ dưới lên (Bottom-up) |
| **Không gian đầu vào** | Vector Euclid $\\mathbb{R}^d$ (tính tâm $\\boldsymbol{\\mu}_k$). Không nhận ma trận khoảng cách | Nhận trực tiếp ma trận khoảng cách $D \\in \\mathbb{R}^{N \\times N}$ bất kỳ |
| **Cấu trúc cụm** | Phân hoạch phẳng thành đúng $K$ cụm rời rạc | Cây phân cấp lồng nhau (Dendrogram) đa cấp độ |
| **Tính tất định** | Phụ thuộc seed khởi tạo, dễ rơi vào cực tiểu địa phương | Tất định 100% (cùng dữ liệu và linkage luôn cho cùng 1 kết quả) |
| **Giả định hình dạng** | Cụm tròn lồi, kích thước tương đương | Linh hoạt tùy theo tiêu chí liên kết (linkage) |
| **Độ phức tạp** | $O(NKd)$ mỗi vòng lặp — tối ưu cho Big Data | Bộ nhớ $O(N^2)$, thời gian $O(N^2) \\to O(N^3)$ |

**Nhận xét:**
- Nhược điểm $O(N^2)$ của Phân cụm phân cấp không ảnh hưởng do số lượng cổ phiếu nhỏ ($N = 98$ mã chạy dưới 0.05 giây).
- K-Means bắt buộc dùng khoảng cách hình học Euclid nên dễ mắc bẫy biên độ và bẫy ngược pha khi chạy trên chuỗi lợi suất."""

# 4. Cell 5: Thiết kế thực nghiệm
nb.cells[5].source = """---
## 3. Thiết Kế Thực Nghiệm Đối Chứng

Để đảm bảo khách quan, ta chưa chọn trước tiêu chí liên kết nào cho Phân cụm phân cấp mà khảo sát đồng thời:
1. **K-Means:** Chạy trên chuỗi lợi suất gốc (Euclidean) và trên không gian PCA 5D.
2. **Phân cụm phân cấp:** Khảo sát cả 4 tiêu chí liên kết (*Single, Complete, Average, Ward*) trên ma trận khoảng cách Mantegna.
3. **Số cụm thử nghiệm:** Cố định $K = 6$ (mức phân cụm phổ biến phản ánh các nhóm ngành chính trên thị trường)."""

# 5. Cell 7: Nhận xét thực nghiệm 1
nb.cells[7].source = """### Nhận xét Thực nghiệm 1: Độ Ổn Định Tái Lập (Stability)

- **K-Means bất ổn định:** ARI trung bình của K-Means trên chuỗi lợi suất chỉ đạt **$0.4722$** (thấp nhất $0.2675$); trên PCA 5D đạt **$0.7081$**. Khi đổi `random_state`, hơn 50% số cổ phiếu bị gán sang cụm khác do thuật toán rơi vào các cực tiểu địa phương khác nhau.
- **Ý nghĩa tài chính:** Cụm thay đổi thất thường khiến danh mục phải đảo hàng liên tục, tốn chi phí giao dịch và thuế.
- **Phân cụm phân cấp tất định:** Ở mọi tiêu chí liên kết, $ARI = 1.0000$ tuyệt đối (phương sai bằng 0). Kết quả hoàn toàn tái lập, không phụ thuộc seed khởi tạo."""

# 6. Cell 9: Nhận xét thực nghiệm 2
nb.cells[9].source = """### Nhận xét Thực nghiệm 2: Khả Năng Tách Biệt Tương Quan

Để đa dạng hóa danh mục (Markowitz 1952), cụm tốt cần:
- Tương quan nội cụm $\\bar{\\rho}_{\\text{intra}}$ cao (gom mã cùng biến động).
- Tương quan liên cụm $\\bar{\\rho}_{\\text{inter}}$ thấp (các cụm độc lập nhau).
$\\implies$ Độ chênh lệch $\\Delta = \\bar{\\rho}_{\\text{intra}} - \\bar{\\rho}_{\\text{inter}}$ càng dương càng tốt.

**Kết quả:**
- **Phân cụm phân cấp:** Mọi linkage đều cho $\\Delta > 0$ rõ rệt ($+0.0932 \\to +0.2210$). Khoảng cách Mantegna bảo toàn đúng mức độ đồng pha, gom chặt mã đồng ngành và tách xa các nhóm độc lập.
- **K-Means (Euclidean):** $\\Delta \\approx +0.0136$ (gần như bằng 0, cổ phiếu cùng cụm tương quan không khác gì khác cụm).
- **K-Means (PCA 5D):** Bị nghịch lý $\\Delta = -0.0222$ (ngoài cụm tương quan cao hơn trong cụm) do PCA gom theo biên độ phương sai thay vì chiều biến động giá."""

# 7. Cell 12: Tổng kết
nb.cells[12].source = """---
## 4. Tổng Kết & Quyết Định Thuật Toán

### Bảng đối chứng tổng hợp:

| Tiêu chí đánh giá | K-Means (Euclidean) | K-Means (PCA 5D) | Phân cụm phân cấp (Mantegna) | Đánh giá |
| :--- | :---: | :---: | :---: | :--- |
| **Độ ổn định (ARI)** | $0.4722$ (Kém) | $0.7081$ (Khá) | **$1.0000$ (Tất định)** | **Hierarchical thắng:** Tái lập 100%, không đổi cụm khi đổi seed |
| **Tách biệt tương quan ($\\Delta$)** | $+0.0136$ (Kém) | $-0.0222$ (Nghịch lý) | **$+0.0932 \\to +0.2210$ (Tốt)** | **Hierarchical thắng:** Bóc tách rõ ranh giới đồng biến động |
| **Không gian khoảng cách** | Ép buộc Euclid | Chiếu phương sai PCA | **Ma trận Mantegna $d = \\sqrt{2(1-\\rho)}$** | **Hierarchical thắng:** Tránh bẫy biên độ & ngược pha |
| **Cấu trúc biểu diễn** | Phân hoạch phẳng | Phân hoạch phẳng | **Cây phân cấp (Dendrogram)** | **Hierarchical thắng:** Thấy quan hệ đa tầng từ cặp mã tới ngành |
| **Độ phức tạp dữ liệu** | Phù hợp Big Data | Phù hợp Big Data | **Lý tưởng cho $N = 98$ cổ phiếu** | Điểm yếu $O(N^2)$ của Hierarchical không ảnh hưởng |

---

### Quyết định kỹ thuật số 6:
1. **Mô hình chính (Proposed Model):** **Phân cụm phân cấp (Agglomerative Hierarchical)** trên không gian khoảng cách Mantegna.
2. **Mô hình cơ sở (Baseline Model):** **K-Means trên không gian PCA 5D** (phục vụ đối chứng theo Tiêu chí 2 của Bài kiểm tra 2).

---

### Bước tiếp theo (Notebook 07):
Sau khi chọn Phân cụm phân cấp làm thuật toán chính, bước tiếp theo là:
> **So sánh 4 tiêu chí liên kết (*Single, Complete, Average, Ward*)** để tìm tiêu chí tối ưu về hệ số bảo toàn khoảng cách gốc (Cophenetic CCC) và số cụm tối ưu $K^*$ tại **Notebook `07_hierarchical_clustering_linkages.ipynb`**."""

with open(NB_PATH, "w", encoding="utf-8") as f:
    nbformat.write(nb, f)

print("Đã chuẩn hóa thành công toàn bộ văn bản trong Notebook 06!")

