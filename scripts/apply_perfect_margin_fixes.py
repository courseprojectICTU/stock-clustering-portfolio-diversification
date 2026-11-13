# scripts/apply_perfect_margin_fixes.py
import re

def main():
    tex_path = "docs/report/Bao_cao_KT1_Nhom_StockClustering.tex"
    with open(tex_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Normalize line endings to LF
    text = text.replace("\r\n", "\n")

    # 1. Front matter student contribution table (fix 2.1pt overfull in student ID)
    s_from_front = r"\begin{tabularx}{\textwidth}{|>{\centering\arraybackslash}p{1cm}|p{3.2cm}|X|>{\centering\arraybackslash}p{2.3cm}|}"
    s_to_front = r"\begin{tabularx}{\textwidth}{|>{\centering\arraybackslash}p{0.8cm}|p{3.6cm}|X|>{\centering\arraybackslash}p{2.2cm}|}"
    if s_from_front in text:
        text = text.replace(s_from_front, s_to_front)
        print("Fixed front matter student contribution table width.")

    # 2. Table 4.2 (tab:k_sweep_ward): Silhouette column p{2.1cm}
    s_from_tab42_pattern = re.compile(
        r"(\\begin\{table\}\[H\]\s*\\centering\s*\\caption\{Kết quả quét thực nghiệm \$K \\in \[5, 15\]\$ cho Ward Linkage trên tập Train\}\s*\\label\{tab:k_sweep_ward\}.*?\\end\{table\})",
        re.DOTALL
    )

    s_to_tab42 = r"""\begin{table}[H]
  \centering
  \caption{Kết quả quét thực nghiệm $K \in [5, 15]$ cho Ward Linkage trên tập Train}
  \label{tab:k_sweep_ward}
  \begin{tabularx}{\textwidth}{|>{\centering\arraybackslash}p{0.5cm}|>{\centering\arraybackslash}p{1.7cm}|>{\centering\arraybackslash}p{2.1cm}|>{\centering\arraybackslash}p{1.7cm}|>{\centering\arraybackslash}p{1.7cm}|X|>{\centering\arraybackslash}p{2.1cm}|}
    \hline
    \rowcolor{black!8}$K$ & \textbf{Độ tách biệt} $\mathbf{\Delta}$ & \textbf{Silhouette} & \textbf{Entropy chuẩn} & \textbf{Tỷ lệ cụm max} & \textbf{Kích thước các cụm ($n_k$)} & \textbf{Composite Score} \\ \hline
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
\end{table}"""

    if s_from_tab42_pattern.search(text):
        text = s_from_tab42_pattern.sub(lambda m: s_to_tab42, text, count=1)
        print("Fixed Table 4.2 Silhouette width to 2.1cm.")

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("Updates applied.")

if __name__ == "__main__":
    main()
