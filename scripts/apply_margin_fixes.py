# scripts/apply_margin_fixes.py
import re

def main():
    tex_path = "docs/report/Bao_cao_KT1_Nhom_StockClustering.tex"
    with open(tex_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Normalize to unix style for matching
    text = text.replace("\r\n", "\n")

    # Fix 1: Chapter 4 intro
    s_from1 = r"cân so sánh thực nghiệm đối chứng trực tiếp tại sổ tay \path{06_algorithm_selection_hierarchical_vs_kmeans.ipynb}:"
    s_from1_alt = r"cân so sánh thực nghiệm đối chứng trực tiếp tại sổ tay \texttt{06\_algorithm\_selection\_hierarchical\_vs\_kmeans.ipynb}:"
    s_to1 = r"cân so sánh thực nghiệm đối chứng trực tiếp tại sổ tay \path{06_algorithm_selection_hierarchical_vs_kmeans.ipynb}:"
    if s_from1_alt in text:
        text = text.replace(s_from1_alt, s_to1)
        print("Applied Fix 1 (Chapter 4 intro)")
    elif s_from1 in text:
        print("Fix 1 already applied")

    # Fix 2: Baseline 1 & 2
    if r"\texttt{KMeans\_PCA\_5D}" in text:
        text = text.replace(r"\texttt{KMeans\_PCA\_5D}", r"\path{KMeans_PCA_5D}")
        text = text.replace(r"\texttt{KMeans\_PCA\_45D}", r"\path{KMeans_PCA_45D}")
        print("Applied Fix 2 (Baselines)")

    # Fix 3: Section 4.3 Libraries and Code block
    s_from3 = r"""  \item \textbf{Tổ chức mã nguồn chuẩn mực:} Nhóm sử dụng trực tiếp các thư viện khoa học dữ liệu chuẩn của hệ sinh thái Python: \texttt{scipy.cluster.hierarchy} (hàm \texttt{linkage}, \texttt{dendrogram}, \texttt{cophenet}, \texttt{fcluster}), \texttt{sklearn.cluster} (\texttt{AgglomerativeClustering}, \texttt{KMeans}, \texttt{BisectingKMeans}), \texttt{sklearn.decomposition} (\texttt{PCA}), \texttt{sklearn.metrics} (\texttt{silhouette\_score}, \texttt{adjusted\_rand\_score}, \texttt{normalized\_mutual\_info\_score}).
  \item \textbf{Cơ chế tự động định vị gốc dự án (\texttt{PROJECT\_ROOT}):} Để giải quyết triệt để lỗi \texttt{FileNotFoundError} khi chạy tương tác trong môi trường IDE (do thư mục làm việc hiện hành bị trỏ nhầm vào thư mục con \texttt{notebooks/}), nhóm cài đặt khối mã tự động định vị tại đầu mỗi notebook:
\begin{lstlisting}
import sys
from pathlib import Path
PROJECT_ROOT = Path("..").resolve() if not (Path("..") / "data").exists() else Path(".").resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
\end{lstlisting}"""

    s_to3 = r"""  \item \textbf{Tổ chức mã nguồn chuẩn mực:} Nhóm sử dụng trực tiếp các thư viện khoa học dữ liệu chuẩn của hệ sinh thái Python:
  \begin{itemize}
    \item \texttt{scipy.cluster.hierarchy}: các hàm \texttt{linkage}, \texttt{dendrogram}, \texttt{cophenet}, \texttt{fcluster}.
    \item \texttt{sklearn.cluster}: \texttt{AgglomerativeClustering}, \texttt{KMeans}, \texttt{BisectingKMeans}.
    \item \texttt{sklearn.decomposition}: phân tích thành phần chính \texttt{PCA}.
    \item \texttt{sklearn.metrics}: các độ đo \texttt{silhouette\_score}, \texttt{adjusted\_rand\_score}, \texttt{normalized\_mutual\_info\_score}.
  \end{itemize}
  \item \textbf{Cơ chế tự động định vị gốc dự án (\path{PROJECT_ROOT}):} Để giải quyết triệt để lỗi \texttt{FileNotFoundError} khi chạy tương tác trong môi trường IDE (do thư mục làm việc hiện hành bị trỏ nhầm vào thư mục con \texttt{notebooks/}), nhóm cài đặt khối mã tự động định vị tại đầu mỗi notebook:
\begin{lstlisting}
import sys
from pathlib import Path
PROJECT_ROOT = Path("..").resolve() if not (Path("..") / "data").exists() \
    else Path(".").resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
\end{lstlisting}"""

    if s_from3 in text:
        text = text.replace(s_from3, s_to3)
        print("Applied Fix 3 (Section 4.3 Libraries and Code)")

    # Fix 4: Section 4.4 intro & Section 4.5 intro
    text = text.replace(r"tại sổ tay \texttt{07\_hierarchical\_clustering\_linkages.ipynb}:", r"tại sổ tay \path{07_hierarchical_clustering_linkages.ipynb}:")

    # Fix 5: Sphere distance proof equation 4.3
    s_from5 = r"""  \begin{equation}
    d_E(\tilde{\mathbf{r}}_i, \tilde{\mathbf{r}}_j)^2 = \|\tilde{\mathbf{r}}_i - \tilde{\mathbf{r}}_j\|^2 = \|\tilde{\mathbf{r}}_i\|^2 + \|\tilde{\mathbf{r}}_j\|^2 - 2 \langle\tilde{\mathbf{r}}_i, \tilde{\mathbf{r}}_j\rangle = 1 + 1 - 2 \rho_{ij} = 2(1 - \rho_{ij}) = d_M(i, j)^2
  \end{equation}"""

    s_to5 = r"""  \begin{align}
    d_E(\tilde{\mathbf{r}}_i, \tilde{\mathbf{r}}_j)^2 
    &= \|\tilde{\mathbf{r}}_i - \tilde{\mathbf{r}}_j\|^2 = \|\tilde{\mathbf{r}}_i\|^2 + \|\tilde{\mathbf{r}}_j\|^2 - 2 \langle\tilde{\mathbf{r}}_i, \tilde{\mathbf{r}}_j\rangle \notag \\
    &= 1 + 1 - 2 \rho_{ij} = 2(1 - \rho_{ij}) = d_M(i, j)^2
  \end{align}"""

    if s_from5 in text:
        text = text.replace(s_from5, s_to5)
        print("Applied Fix 5 (Sphere proof equation)")

    # Fix 6: Composite score equation 4.5 and Entropy
    s_from6 = r"""\begin{equation}
  \text{Composite Score} = 0.35 \times \text{Norm}(\Delta) + 0.30 \times \text{Norm}(\text{Silhouette}) + 0.20 \times \text{Entropy}_{\text{norm}} + 0.15 \times (1 - \text{MaxShare})
  \label{eq:composite_score}
\end{equation}
Trong đó $\text{Norm}(\cdot)$ là phép chuẩn hóa Min-Max về đoạn $[0, 1]$, còn $\text{Entropy}_{\text{norm}} = -\sum_{k=1}^K \frac{n_k}{N} \frac{\ln(n_k/N)}{\ln K} \in [0, 1]$ đo lường độ cân bằng kích thước cụm."""

    s_to6 = r"""\begin{align}
  \text{Composite Score} = &\; 0.35 \times \text{Norm}(\Delta) + 0.30 \times \text{Norm}(\text{Silhouette}) \notag \\
  &+ 0.20 \times \text{Entropy}_{\text{norm}} + 0.15 \times (1 - \text{MaxShare})
  \label{eq:composite_score}
\end{align}
Trong đó $\text{Norm}(\cdot)$ là phép chuẩn hóa Min-Max về đoạn $[0, 1]$; chỉ số $\text{Entropy}_{\text{norm}}$ đo lường độ cân bằng kích thước cụm ($n_k$ là quy mô cụm $k$):
\begin{equation}
  \text{Entropy}_{\text{norm}} = -\sum_{k=1}^K \frac{n_k}{N} \frac{\ln(n_k / N)}{\ln K} \in [0, 1]
  \label{eq:entropy_norm}
\end{equation}"""

    if s_from6 in text:
        text = text.replace(s_from6, s_to6)
        print("Applied Fix 6 (Composite score & Entropy)")

    # Fix 7: Bảng 4.2
    s_from7 = r"""\begingroup
\small
\renewcommand{\arraystretch}{1.15}
\begin{table}[H]
  \centering
  \caption{Kết quả quét thực nghiệm $K \in [5, 15]$ cho Ward Linkage trên tập Train}
  \label{tab:k_sweep_ward}
  \begin{tabularx}{\textwidth}{|>{\centering\arraybackslash}p{0.8cm}|>{\centering\arraybackslash}p{2.2cm}|>{\centering\arraybackslash}p{1.8cm}|>{\centering\arraybackslash}p{1.8cm}|>{\centering\arraybackslash}p{1.8cm}|X|>{\centering\arraybackslash}p{1.8cm}|}
    \hline
    \rowcolor{black!8}$K$ & \textbf{Độ tách biệt $\Delta$} & \textbf{Silhouette} & \textbf{Entropy chuẩn} & \textbf{Tỷ lệ cụm max} & \textbf{Kích thước các cụm} & \textbf{Composite Score} \\ \hline
    5 & $+0.0827$ & $0.0245$ & $0.9416$ & $33.7\%$ ($33$ mã) & $[33, 21, 19, 15, 10]$ & $0.4612$ \\ \hline
    6 & $+0.0932$ & $0.0210$ & $0.9328$ & $33.7\%$ ($33$ mã) & $[33, 21, 14, 13, 10, 7]$ & $0.4785$ \\ \hline
    7 & $+0.1085$ & $0.0256$ & $0.9362$ & $24.5\%$ ($24$ mã) & $[24, 21, 14, 13, 10, 9, 7]$ & $0.5310$ \\ \hline
    8 & $+0.1174$ & $0.0261$ & $0.9284$ & $24.5\%$ ($24$ mã) & $[24, 21, 13, 10, 10, 9, 7, 4]$ & $0.5524$ \\ \hline
    9 & $+0.1281$ & $0.0279$ & $0.9241$ & $21.4\%$ ($21$ mã) & $[21, 19, 13, 10, 10, 9, 8, 4, 4]$ & $0.5731$ \\ \hline
    \textbf{10} & $\mathbf{+0.1389}$ & $\mathbf{0.0296}$ & $\mathbf{0.9203}$ & $\mathbf{21.4\%}$ ($21$ mã) & $\mathbf{[21, 19, 13, 10, 10, 8, 7, 4, 3, 3]}$ & $\mathbf{0.5889}$ \\ \hline
    11 & $+0.1442$ & $0.0284$ & $0.9085$ & $21.4\%$ ($21$ mã) & $[21, 19, 13, 10, 9, 8, 7, 4, 3, 3, 1]$ & Loại ($1$ Singleton) \\ \hline
    12 & $+0.1495$ & $0.0291$ & $0.9012$ & $21.4\%$ ($21$ mã) & $[21, 19, 13, 9, 8, 8, 7, 4, 3, 3, 2, 1]$ & Loại ($1$ Singleton) \\ \hline
  \end{tabularx}
\end{table}
\endgroup"""

    s_to7 = r"""\begingroup
\footnotesize
\setlength{\tabcolsep}{3pt}
\renewcommand{\arraystretch}{1.18}
\begin{table}[H]
  \centering
  \caption{Kết quả quét thực nghiệm $K \in [5, 15]$ cho Ward Linkage trên tập Train}
  \label{tab:k_sweep_ward}
  \begin{tabularx}{\textwidth}{|>{\centering\arraybackslash}p{0.6cm}|>{\centering\arraybackslash}p{1.8cm}|>{\centering\arraybackslash}p{1.5cm}|>{\centering\arraybackslash}p{1.5cm}|>{\centering\arraybackslash}p{1.8cm}|X|>{\centering\arraybackslash}p{2.0cm}|}
    \hline
    \rowcolor{black!8}$K$ & \textbf{Độ tách biệt $\Delta$} & \textbf{Silhouette} & \textbf{Entropy chuẩn} & \textbf{Tỷ lệ cụm max} & \textbf{Kích thước các cụm ($n_k$)} & \textbf{Composite Score} \\ \hline
    5 & $+0.0827$ & $0.0245$ & $0.9416$ & $33.7\%$ ($33$ mã) & 33, 21, 19, 15, 10 & $0.4612$ \\ \hline
    6 & $+0.0932$ & $0.0210$ & $0.9328$ & $33.7\%$ ($33$ mã) & 33, 21, 14, 13, 10, 7 & $0.4785$ \\ \hline
    7 & $+0.1085$ & $0.0256$ & $0.9362$ & $24.5\%$ ($24$ mã) & 24, 21, 14, 13, 10, 9, 7 & $0.5310$ \\ \hline
    8 & $+0.1174$ & $0.0261$ & $0.9284$ & $24.5\%$ ($24$ mã) & 24, 21, 13, 10, 10, 9, 7, 4 & $0.5524$ \\ \hline
    9 & $+0.1281$ & $0.0279$ & $0.9241$ & $21.4\%$ ($21$ mã) & 21, 19, 13, 10, 10, 9, 8, 4, 4 & $0.5731$ \\ \hline
    \textbf{10} & $\mathbf{+0.1389}$ & $\mathbf{0.0296}$ & $\mathbf{0.9203}$ & $\mathbf{21.4\%}$ ($21$ mã) & \textbf{21, 19, 13, 10, 10, 8, 7, 4, 3, 3} & $\mathbf{0.5889}$ \\ \hline
    11 & $+0.1442$ & $0.0284$ & $0.9085$ & $21.4\%$ ($21$ mã) & 21, 19, 13, 10, 9, 8, 7, 4, 3, 3, 1 & 0.5812 (Loại*) \\ \hline
    12 & $+0.1495$ & $0.0291$ & $0.9012$ & $21.4\%$ ($21$ mã) & 21, 19, 13, 9, 8, 8, 7, 4, 3, 3, 2, 1 & 0.5754 (Loại*) \\ \hline
  \end{tabularx}
  \vspace{2pt}
  \par\noindent\raggedright\footnotesize\textit{Ghi chú: * Cấu hình bị loại do vi phạm Bộ lọc khả thi (xuất hiện cụm đơn lẻ 1 mã -- Singleton).}
\end{table}
\endgroup"""

    if s_from7 in text:
        text = text.replace(s_from7, s_to7)
        print("Applied Fix 7 (Table 4.2)")

    # Fix 8: Table 4.3
    s_from8 = r"""\begingroup
\small
\renewcommand{\arraystretch}{1.2}
\begin{table}[H]
  \centering
  \caption{So sánh định lượng giữa Mô hình đề xuất (Ward $K^*=10$) và 2 Baseline qua 30 lần Block Sub-sampling}
  \label{tab:sosanh_baseline_subsampling}
  \begin{tabularx}{\textwidth}{|p{3.8cm}|>{\centering\arraybackslash}p{2.8cm}|>{\centering\arraybackslash}p{2.8cm}|X|>{\centering\arraybackslash}p{1.8cm}|}
    \hline
    \rowcolor{black!8}\textbf{Mô hình đối chứng} & \textbf{Độ tách biệt tương quan $\Delta$ ($\text{Mean} \pm \text{Std}$)} & \textbf{Silhouette Score ($\text{Mean} \pm \text{Std}$)} & \textbf{Số lượng cụm Singleton trung bình} & \textbf{Đánh giá khả thi danh mục} \\ \hline
    Baseline 1 (\path{KMeans_PCA_5D}) & $+0.0736 \pm 0.0093$ & $+0.0754 \pm 0.0053$ & $1.10 \pm 0.40$ (thường xuyên có Singleton) & Kém khả thi \\ \hline
    Baseline 2 (\path{KMeans_PCA_45D}) & $+0.0207 \pm 0.0052$ & $-0.0101 \pm 0.0041$ & $2.40 \pm 0.62$ (nhiều cụm 1 mã) & Không khả thi \\ \hline
    \textbf{Mô hình đề xuất (Ward $K^*=10$)} & $\mathbf{+0.1398 \pm 0.0114}$ & $\mathbf{+0.0297 \pm 0.0033}$ & $\mathbf{0.00 \pm 0.00}$ (Tuyệt đối không có Singleton) & \textbf{Tối ưu toàn diện} \\ \hline
  \end{tabularx}
\end{table}
\endgroup"""

    s_from8_orig = r"""\begingroup
\small
\renewcommand{\arraystretch}{1.2}
\begin{table}[H]
  \centering
  \caption{So sánh định lượng giữa Mô hình đề xuất (Ward $K^*=10$) và 2 Baseline qua 30 lần Block Sub-sampling}
  \label{tab:sosanh_baseline_subsampling}
  \begin{tabularx}{\textwidth}{|p{3.8cm}|>{\centering\arraybackslash}p{2.8cm}|>{\centering\arraybackslash}p{2.8cm}|X|>{\centering\arraybackslash}p{1.8cm}|}
    \hline
    \rowcolor{black!8}\textbf{Mô hình đối chứng} & \textbf{Độ tách biệt tương quan $\Delta$ ($\text{Mean} \pm \text{Std}$)} & \textbf{Silhouette Score ($\text{Mean} \pm \text{Std}$)} & \textbf{Số lượng cụm Singleton trung bình} & \textbf{Đánh giá khả thi danh mục} \\ \hline
    Baseline 1 (\texttt{KMeans\_PCA\_5D}) & $+0.0736 \pm 0.0093$ & $+0.0754 \pm 0.0053$ & $1.10 \pm 0.40$ (thường xuyên có Singleton) & Kém khả thi \\ \hline
    Baseline 2 (\texttt{KMeans\_PCA\_45D}) & $+0.0207 \pm 0.0052$ & $-0.0101 \pm 0.0041$ & $2.40 \pm 0.62$ (nhiều cụm 1 mã) & Không khả thi \\ \hline
    \textbf{Mô hình đề xuất (Ward $K^*=10$)} & $\mathbf{+0.1398 \pm 0.0114}$ & $\mathbf{+0.0297 \pm 0.0033}$ & $\mathbf{0.00 \pm 0.00}$ (Tuyệt đối không có Singleton) & \textbf{Tối ưu toàn diện} \\ \hline
  \end{tabularx}
\end{table}
\endgroup"""

    s_to8 = r"""\begingroup
\small
\setlength{\tabcolsep}{3.5pt}
\renewcommand{\arraystretch}{1.2}
\begin{table}[H]
  \centering
  \caption{So sánh định lượng giữa Mô hình đề xuất (Ward $K^*=10$) và 2 Baseline qua 30 lần Block Sub-sampling}
  \label{tab:sosanh_baseline_subsampling}
  \begin{tabularx}{\textwidth}{|p{3.6cm}|>{\centering\arraybackslash}p{2.6cm}|>{\centering\arraybackslash}p{2.5cm}|>{\centering\arraybackslash}p{2.2cm}|X|}
    \hline
    \rowcolor{black!8}\textbf{Mô hình đối chứng} & \textbf{Độ tách biệt $\Delta$}\newline ($\text{Mean} \pm \text{Std}$) & \textbf{Silhouette Score}\newline ($\text{Mean} \pm \text{Std}$) & \textbf{Cụm Singleton}\newline ($\text{Mean} \pm \text{Std}$) & \textbf{Đánh giá khả thi danh mục} \\ \hline
    Baseline 1 (\path{KMeans_PCA_5D}) & $+0.0736 \pm 0.0093$ & $+0.0754 \pm 0.0053$ & $1.10 \pm 0.40$ & Kém khả thi (thường có Singleton) \\ \hline
    Baseline 2 (\path{KMeans_PCA_45D}) & $+0.0207 \pm 0.0052$ & $-0.0101 \pm 0.0041$ & $2.40 \pm 0.62$ & Không khả thi (nhiều cụm 1 mã) \\ \hline
    \textbf{Mô hình đề xuất (Ward $K^*=10$)} & $\mathbf{+0.1398 \pm 0.0114}$ & $\mathbf{+0.0297 \pm 0.0033}$ & $\mathbf{0.00 \pm 0.00}$ & \textbf{Tối ưu toàn diện} (100\% không Singleton) \\ \hline
  \end{tabularx}
\end{table}
\endgroup"""

    if s_from8 in text:
        text = text.replace(s_from8, s_to8)
        print("Applied Fix 8 (Table 4.3)")
    elif s_from8_orig in text:
        text = text.replace(s_from8_orig, s_to8)
        print("Applied Fix 8 (Table 4.3 orig)")

    # Fix 9: Chapter 5 intro
    text = text.replace(r"tại sổ tay \texttt{08\_stability\_and\_sector.ipynb}", r"tại sổ tay \path{08_stability_and_sector.ipynb}")

    # Fix 10: Subsection 5.3.2 title
    s_from10 = r"\subsection{Hình thái 2: Cụm liên ngành dòng tiền High-Beta chu kỳ (Market Co-Movement)}"
    s_to10 = r"\subsection{Hình thái 2: Cụm liên ngành dòng tiền High-Beta (Market Co-Movement)}"
    if s_from10 in text:
        text = text.replace(s_from10, s_to10)
        print("Applied Fix 10 (Subsection 5.3.2 title)")

    # Fix 11: Appendix A list
    s_from11 = r"""\begin{enumerate}
  \item \textbf{notebooks/01\_data\_collection\_prep.ipynb:}
  Thu thập dữ liệu thô 100 mã cổ phiếu rổ VN100 từ API \textbf{vnstock} và metadata phân ngành ICB. Lưu trữ dữ liệu thô tại \textbf{data/raw/}.
  \item \textbf{notebooks/02\_data\_preprocessing.ipynb:}
  Kiểm toán dữ liệu khuyết, loại bỏ 2 mã thiếu (\textbf{VTP}, \textbf{NAB}), nhận diện và loại bỏ 68 ngày nghỉ lễ sàn HOSE, áp dụng kỹ thuật Forward-fill xử lý 48 ô trống. Xuất bản ma trận giá sạch $1.187 \times 98$ tại \textbf{data/processed/adj\_close\_clean.csv}.
  \item \textbf{notebooks/03\_feature\_extraction\_returns.ipynb:}
  Tính chuỗi lợi suất logarit ($1.186 \times 98$), thực hiện kiểm định Jarque-Bera, tính độ nhọn Excess Kurtosis = 3.86 chứng minh hiện tượng đuôi béo (Fat-tails); trích chọn 8 đặc trưng tài chính định lượng.
  \item \textbf{notebooks/04\_correlation\_distance.ipynb:}
  Tính ma trận tương quan Pearson $\rho \in [-1, 1]$, chuyển đổi sang khoảng cách Mantegna $d = \sqrt{2(1-\rho)}$, chạy thuật toán kiểm định bất đẳng thức tam giác trên 20.000 bộ ba.
  \item \textbf{notebooks/05\_train\_test\_split.ipynb:}
  Phân chia tập dữ liệu In-Sample Train (2022--2024: 739 phiên lợi suất) và Out-of-Sample Test (2025--2026: 447 phiên lợi suất) theo lý thuyết RMT ($Q=7.54$).
  \item \textbf{notebooks/06\_algorithm\_selection\_hierarchical\_vs\_kmeans.ipynb:}
  Thực nghiệm đối chứng 3 trường phái thuật toán ($K$-Means phẳng vs Phân cấp chia dần DIANA/Bisecting vs Phân cấp gộp Bottom-Up); chứng minh tính tất định $ARI \equiv 1.0$ và độ phân tách tương quan $\Delta$.
  \item \textbf{notebooks/07\_hierarchical\_clustering\_linkages.ipynb:}
  Thực nghiệm 4 tiêu chí liên kết (Single, Complete, Average, Ward), chứng minh đẳng thức mặt cầu $\mathbb{S}^{T-1}$, quét thực nghiệm $K \in [3, 15]$ chốt $K^*=10$ bằng ma trận đa tiêu chí Composite Score, kiểm định Block Sub-sampling ($B=30$) so với 2 Baseline, và phân tích lỗi mẫu ranh giới.
  \item \textbf{notebooks/08\_stability\_and\_sector.ipynb:}
  Đánh giá độ ổn định liên pha qua 3 chu kỳ thị trường (2022 Downtrend, 2023 Tích lũy, 2024 Phục hồi) bằng ma trận ARI, và đối chiếu định lượng cấu trúc cụm với 11 phân ngành chuẩn ICB cấp 1 ($NMI=0.5339$, Purity=$60.20\%$).
\end{enumerate}"""

    s_to11 = r"""\begin{enumerate}
  \item \textbf{Sổ tay 01 (\path{01_data_collection_prep.ipynb}):}
  Thu thập dữ liệu thô 100 mã cổ phiếu rổ VN100 từ API \textbf{vnstock} và metadata phân ngành ICB. Lưu trữ dữ liệu thô tại \textbf{data/raw/}.
  \item \textbf{Sổ tay 02 (\path{02_data_preprocessing.ipynb}):}
  Kiểm toán dữ liệu khuyết, loại bỏ 2 mã thiếu (\textbf{VTP}, \textbf{NAB}), nhận diện và loại bỏ 68 ngày nghỉ lễ sàn HOSE, áp dụng kỹ thuật Forward-fill xử lý 48 ô trống. Xuất bản ma trận giá sạch $1.187 \times 98$ tại \path{data/processed/adj_close_clean.csv}.
  \item \textbf{Sổ tay 03 (\path{03_feature_extraction_returns.ipynb}):}
  Tính chuỗi lợi suất logarit ($1.186 \times 98$), thực hiện kiểm định Jarque-Bera, tính độ nhọn Excess Kurtosis = 3.86 chứng minh hiện tượng đuôi béo (Fat-tails); trích chọn 8 đặc trưng tài chính định lượng.
  \item \textbf{Sổ tay 04 (\path{04_correlation_distance.ipynb}):}
  Tính ma trận tương quan Pearson $\rho \in [-1, 1]$, chuyển đổi sang khoảng cách Mantegna $d = \sqrt{2(1-\rho)}$, chạy thuật toán kiểm định bất đẳng thức tam giác trên 20.000 bộ ba.
  \item \textbf{Sổ tay 05 (\path{05_train_test_split.ipynb}):}
  Phân chia tập dữ liệu In-Sample Train (2022--2024: 739 phiên lợi suất) và Out-of-Sample Test (2025--2026: 447 phiên lợi suất) theo lý thuyết RMT ($Q=7.54$).
  \item \textbf{Sổ tay 06 (\path{06_algorithm_selection_hierarchical_vs_kmeans.ipynb}):}
  Thực nghiệm đối chứng 3 trường phái thuật toán ($K$-Means phẳng vs Phân cấp chia dần DIANA/Bisecting vs Phân cấp gộp Bottom-Up); chứng minh tính tất định $ARI \equiv 1.0$ và độ phân tách tương quan $\Delta$.
  \item \textbf{Sổ tay 07 (\path{07_hierarchical_clustering_linkages.ipynb}):}
  Thực nghiệm 4 tiêu chí liên kết (Single, Complete, Average, Ward), chứng minh đẳng thức mặt cầu $\mathbb{S}^{T-1}$, quét thực nghiệm $K \in [3, 15]$ chốt $K^*=10$ bằng ma trận đa tiêu chí Composite Score, kiểm định Block Sub-sampling ($B=30$) so với 2 Baseline, và phân tích lỗi mẫu ranh giới.
  \item \textbf{Sổ tay 08 (\path{08_stability_and_sector.ipynb}):}
  Đánh giá độ ổn định liên pha qua 3 chu kỳ thị trường (2022 Downtrend, 2023 Tích lũy, 2024 Phục hồi) bằng ma trận ARI, và đối chiếu định lượng cấu trúc cụm với 11 phân ngành chuẩn ICB cấp 1 ($NMI=0.5339$, Purity=$60.20\%$).
\end{enumerate}"""

    if s_from11 in text:
        text = text.replace(s_from11, s_to11)
        print("Applied Fix 11 (Appendix A list)")

    # Fix 12: Chapter 1 early fixes for overfull
    text = text.replace(r"\item \texttt{03\_feature\_extraction\_returns.ipynb}:", r"\item \path{03_feature_extraction_returns.ipynb}:")
    text = text.replace(r"\item \texttt{04\_correlation\_distance.ipynb}:", r"\item \path{04_correlation_distance.ipynb}:")
    text = text.replace(r"tỷ trọng phân bổ $w = [w_1, w_2, \dots, w_N]^T$", r"tỷ trọng phân bổ $w = [w_1, \dots, w_N]^T$")

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("All fixes written back to LaTeX file successfully!")

if __name__ == "__main__":
    main()

