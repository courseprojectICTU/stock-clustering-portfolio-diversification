# scripts/apply_wording_fixes.py
import re

def main():
    tex_path = "docs/report/Bao_cao_KT1_Nhom_StockClustering.tex"
    with open(tex_path, "r", encoding="utf-8") as f:
        text = f.read()

    # 1. Chapter 4 and Chapter 5 titles (lowercase 'so sánh' and 'đối chiếu')
    text = text.replace(
        r"\chapter{Thực nghiệm phân cụm và So sánh đối chứng mô hình}",
        r"\chapter{Thực nghiệm phân cụm và so sánh đối chứng mô hình}"
    )
    text = text.replace(
        r"\chapter{Đánh giá độ ổn định liên pha và Đối chiếu phân ngành ICB}",
        r"\chapter{Đánh giá độ ổn định liên pha và đối chiếu phân ngành ICB}"
    )

    # In overview list (Section 5. Bố cục báo cáo)
    text = text.replace(
        r"\item \textbf{Chương 4. Thực nghiệm phân cụm và So sánh đối chứng mô hình:} Đối chứng 3 trường phái thuật toán,",
        r"\item \textbf{Chương 4. Thực nghiệm phân cụm và so sánh đối chứng mô hình:} Đối chứng các thuật toán phân cụm,"
    )
    text = text.replace(
        r"\item \textbf{Chương 5. Đánh giá độ ổn định liên pha và Đối chiếu phân ngành ICB:}",
        r"\item \textbf{Chương 5. Đánh giá độ ổn định liên pha và đối chiếu phân ngành ICB:}"
    )

    # 2. Front matter student task table (line 320)
    text = text.replace(
        r"-- Thực nghiệm đối chứng 3 trường phái thuật toán ($K$-Means, Bisecting, DIANA, Agglomerative)",
        r"-- Thực nghiệm đối chứng các thuật toán phân cụm ($K$-Means, Bisecting, DIANA, Agglomerative)"
    )

    # 3. Chapter 1 Markowitz school of thought -> theory
    text = text.replace(
        r"theo trường phái hiện đại của Harry Markowitz",
        r"theo lý thuyết hiện đại của Harry Markowitz"
    )

    # 4. Chapter 4 Section 4.1 title and introductory paragraphs
    text = text.replace(
        r"\section{Lựa chọn thuật toán: Đối chứng khách quan ba trường phái phân cụm}",
        r"\section{Lựa chọn thuật toán: Đối chứng khách quan các thuật toán phân cụm}"
    )
    text = text.replace(
        r"tiến hành đưa cả ba trường phái phân cụm kinh điển lên bàn cân",
        r"tiến hành đưa các thuật toán phân cụm kinh điển lên bàn cân"
    )

    # 3 bullet points in Section 4.1
    text = text.replace(
        r"\item \textbf{Trường phái Phân hoạch phẳng (Flat Partitioning):}",
        r"\item \textbf{Thuật toán Phân hoạch phẳng (Flat Partitioning):}"
    )
    text = text.replace(
        r"\item \textbf{Trường phái Phân cấp Chia dần từ trên xuống (Top-Down Hierarchical):}",
        r"\item \textbf{Thuật toán Phân cấp chia dần từ trên xuống (Top-Down Hierarchical):}"
    )
    text = text.replace(
        r"\item \textbf{Trường phái Phân cấp Gộp dần từ dưới lên (Bottom-Up Agglomerative):}",
        r"\item \textbf{Thuật toán Phân cấp gộp dần từ dưới lên (Bottom-Up Agglomerative):}"
    )

    # Subsection 4.1.1
    text = text.replace(
        r"\subsection{Bằng chứng định lượng so sánh đối chứng ba trường phái}",
        r"\subsection{Bằng chứng định lượng so sánh đối chứng các thuật toán phân cụm}"
    )
    text = text.replace(
        r"Ba trường phái thuật toán được huấn luyện trên cùng tập Train",
        r"Các thuật toán phân cụm được huấn luyện trên cùng tập Train"
    )

    # Caption Table 4.1
    text = text.replace(
        r"\caption{So sánh đối chứng định lượng giữa ba trường phái thuật toán phân cụm trên tập Train}",
        r"\caption{So sánh đối chứng định lượng giữa các thuật toán phân cụm trên tập Train}"
    )

    # Conclusion checklist & highlights
    text = text.replace(
        r"Thực nghiệm đối chứng khách quan 3 trường phái thuật toán ($K$-Means phẳng vs Bisecting/DIANA vs Agglomerative Bottom-Up)",
        r"Thực nghiệm đối chứng khách quan các thuật toán phân cụm ($K$-Means phẳng vs Bisecting/DIANA vs Agglomerative Bottom-Up)"
    )
    text = text.replace(
        r"Thực nghiệm đối chứng khách quan 3 trường phái thuật toán; biện luận bản chất vi mô",
        r"Thực nghiệm đối chứng khách quan các thuật toán phân cụm; biện luận bản chất vi mô"
    )

    # Appendix A
    text = text.replace(
        r"Thực nghiệm đối chứng 3 trường phái thuật toán ($K$-Means phẳng vs Phân cấp chia dần DIANA/Bisecting vs Phân cấp gộp Bottom-Up)",
        r"Thực nghiệm đối chứng các thuật toán phân cụm ($K$-Means phẳng vs Phân cấp chia dần DIANA/Bisecting vs Phân cấp gộp Bottom-Up)"
    )

    # Appendix B
    text = text.replace(
        r"Cài đặt và so sánh đối chứng 3 trường phái thuật toán ($K$-Means, Bisecting, Agglomerative)",
        r"Cài đặt và so sánh đối chứng các thuật toán phân cụm ($K$-Means, Bisecting, Agglomerative)"
    )

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("All wording fixes applied to Bao_cao_KT1_Nhom_StockClustering.tex successfully!")

    # Also apply to update_master_report_latex.py if present
    py_path = "scripts/update_master_report_latex.py"
    try:
        with open(py_path, "r", encoding="utf-8") as f:
            py_text = f.read()
        py_text = py_text.replace(
            r"\chapter{Thực nghiệm phân cụm và So sánh đối chứng mô hình}",
            r"\chapter{Thực nghiệm phân cụm và so sánh đối chứng mô hình}"
        )
        py_text = py_text.replace(
            r"\chapter{Đánh giá độ ổn định liên pha và Đối chiếu phân ngành ICB}",
            r"\chapter{Đánh giá độ ổn định liên pha và đối chiếu phân ngành ICB}"
        )
        py_text = py_text.replace(
            r"\section{Lựa chọn thuật toán: Đối chứng khách quan ba trường phái phân cụm}",
            r"\section{Lựa chọn thuật toán: Đối chứng khách quan các thuật toán phân cụm}"
        )
        py_text = py_text.replace(
            r"tiến hành đưa cả ba trường phái phân cụm kinh điển lên bàn cân",
            r"tiến hành đưa các thuật toán phân cụm kinh điển lên bàn cân"
        )
        py_text = py_text.replace(
            r"\subsection{Bằng chứng định lượng so sánh đối chứng ba trường phái}",
            r"\subsection{Bằng chứng định lượng so sánh đối chứng các thuật toán phân cụm}"
        )
        py_text = py_text.replace(
            r"Ba trường phái thuật toán được huấn luyện trên cùng tập Train",
            r"Các thuật toán phân cụm được huấn luyện trên cùng tập Train"
        )
        py_text = py_text.replace(
            r"\caption{So sánh đối chứng định lượng giữa ba trường phái thuật toán phân cụm trên tập Train}",
            r"\caption{So sánh đối chứng định lượng giữa các thuật toán phân cụm trên tập Train}"
        )
        with open(py_path, "w", encoding="utf-8") as f:
            f.write(py_text)
        print("Updated scripts/update_master_report_latex.py successfully!")
    except Exception as e:
        print("Error updating python script:", e)

if __name__ == "__main__":
    main()

