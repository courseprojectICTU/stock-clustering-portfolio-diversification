"""
Script thay thế và loại bỏ tất cả các cụm từ liên quan tới (BÀI KIỂM TRA 1 -- TUẦN 4)
trong file docs/report/Bao_cao_KT1_Nhom_StockClustering.tex
"""
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

tex_path = Path("docs/report/Bao_cao_KT1_Nhom_StockClustering.tex")
content = tex_path.read_text(encoding="utf-8")

replacements = [
    # Dòng tiêu đề chú thích
    ("%  BÁO CÁO TIỂU LUẬN HỌC PHẦN HỌC MÁY - BÀI KIỂM TRA 1 (TUẦN 4)",
     "%  BÁO CÁO TIỂU LUẬN HỌC PHẦN HỌC MÁY"),
    
    # Loại báo cáo
    ("\\newcommand{\\loaibaocao}{BÁO CÁO TIỂU LUẬN (BÀI KIỂM TRA 1 -- TUẦN 4)}",
     "\\newcommand{\\loaibaocao}{BÁO CÁO TIỂU LUẬN}"),
    
    # Đầu trang fancyhead
    ("\\fancyhead[L]{\\small\\itshape Báo cáo học phần \\hocphan\\ -- Bài kiểm tra 1}",
     "\\fancyhead[L]{\\small\\itshape Báo cáo tiểu luận học phần \\hocphan}"),
    
    # Trang nhận xét
    ("\\noindent\\textbf{2. Về nội dung và kết quả thực hiện (Bài kiểm tra 1 -- Tuần 4):}",
     "\\noindent\\textbf{2. Về nội dung và kết quả thực hiện:}"),
    
    ("\\noindent\\textbf{4. Điểm đánh giá Bài kiểm tra 1:}",
     "\\noindent\\textbf{4. Điểm đánh giá:}"),
    
    # Lời cam đoan
    ("Chúng em xin cam đoan báo cáo tiểu luận ``\\textit{\\tendetai}'' (nội dung Bài kiểm tra 1 -- Tuần 4: Xác định bài toán, khảo sát và tiền xử lý dữ liệu) là kết quả làm việc nghiêm túc của nhóm dưới sự định hướng chuyên môn của \\giangvien.",
     "Chúng em xin cam đoan báo cáo tiểu luận ``\\textit{\\tendetai}'' là kết quả làm việc nghiêm túc của nhóm dưới sự định hướng chuyên môn của \\giangvien."),
    
    # Bảng phân công nhiệm vụ
    ("\\rowcolor{black!8}\\textbf{STT} & \\textbf{Họ và tên} & \\textbf{Nhiệm vụ phụ trách (Bài kiểm tra 1 -- Tuần 4)} & \\textbf{Mức độ hoàn thành} \\\\ \\hline",
     "\\rowcolor{black!8}\\textbf{STT} & \\textbf{Họ và tên} & \\textbf{Nhiệm vụ phụ trách} & \\textbf{Mức độ hoàn thành} \\\\ \\hline"),
    
    # Mở đầu mục 2
    ("\\section*{2. Mục tiêu và nhiệm vụ của Bài kiểm tra 1}",
     "\\section*{2. Mục tiêu và nhiệm vụ nghiên cứu}"),
    
    ("Báo cáo này đại diện cho kết quả thực hiện của \\textbf{Bài kiểm tra 1 (Mốc Tuần 4)}, tập trung giải quyết toàn diện các yêu cầu về khảo sát bài toán, thu thập, tiền xử lý dữ liệu và thiết lập không gian mêtric cho mô hình học máy:",
     "Báo cáo tập trung giải quyết toàn diện các yêu cầu về khảo sát bài toán, thu thập, tiền xử lý dữ liệu và thiết lập không gian mêtric cho mô hình học máy phục vụ phân nhóm cổ phiếu và đa dạng hóa danh mục:"),
    
    # Mở đầu mục 5
    ("Nội dung báo cáo Bài kiểm tra 1 được trình bày trong 3 chương trọng tâm:",
     "Nội dung báo cáo được trình bày trong 3 chương trọng tâm:"),
    
    # Caption hình quy trình
    ("\\caption{Quy trình tổng thể dự án (các khối tô sáng đại diện cho Bài kiểm tra 1 đã hoàn thành)}",
     "\\caption{Quy trình tổng thể dự án học máy (các khối tô màu xanh đại diện cho các bước đã hoàn thành)}"),
    
    # Kết luận mục 1
    ("\\section*{1. Kết quả đạt được của Bài kiểm tra 1 (Tuần 4)}",
     "\\section*{1. Kết quả đạt được}"),
    
    ("Trong khuôn khổ Bài kiểm tra 1, nhóm đã hoàn thành toàn diện 100\\% các mục tiêu đặt ra theo đúng Bộ tiêu chí đánh giá dự án học máy của bộ môn:",
     "Nhóm đã hoàn thành toàn diện 100\\% các mục tiêu đặt ra theo đúng Bộ tiêu chí đánh giá dự án học máy của bộ môn:"),
    
    # Bảng tự đánh giá
    ("%  BẢNG TỰ ĐÁNH GIÁ TIÊU CHÍ CHẤM BÀI KIỂM TRA 1",
     "%  BẢNG TỰ ĐÁNH GIÁ TIÊU CHÍ CHẤM"),
    
    ("\\unnumberedchapter{BẢNG TỰ ĐÁNH GIÁ BÀI KIỂM TRA 1 (TUẦN 4)}",
     "\\unnumberedchapter{BẢNG TỰ ĐÁNH GIÁ THEO TIÊU CHÍ CHẤM}"),
    
    ("\\caption{Bảng tự đánh giá kết quả thực hiện theo 10 tiêu chí chấm điểm Bài kiểm tra 1 (Tuần 4)}",
     "\\caption{Bảng tự đánh giá kết quả thực hiện theo 10 tiêu chí đánh giá dự án học máy}"),
    
    ("\\multicolumn{3}{|c|}{\\textbf{TỔNG ĐIỂM TỰ ĐÁNH GIÁ BÀI KIỂM TRA 1}} & \\textbf{10,0} & \\textbf{10,0} \\\\ \\hline",
     "\\multicolumn{3}{|c|}{\\textbf{TỔNG ĐIỂM TỰ ĐÁNH GIÁ}} & \\textbf{10,0} & \\textbf{10,0} \\\\ \\hline"),
    
    # Nhật ký
    ("\\caption{Nhật ký tiến độ công việc thực hiện Bài kiểm tra 1 (Tuần 1 -- Tuần 4)}",
     "\\caption{Nhật ký tiến độ công việc của nhóm}"),
    
    ("Tuần 4 & 28/10/2026 & Cả hai thành viên & Tổng hợp số liệu, xuất bản hình ảnh độ phân giải cao và hoàn thiện Báo cáo LaTeX Bài kiểm tra 1. \\\\ \\hline",
     "Tuần 4 & 28/10/2026 & Cả hai thành viên & Tổng hợp số liệu, xuất bản hình ảnh độ phân giải cao và hoàn thiện Báo cáo LaTeX tiểu luận. \\\\ \\hline")
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f"Đã thay thế: {old[:50]}...")
    else:
        print(f"Không tìm thấy: {old[:50]}...")

tex_path.write_text(content, encoding="utf-8")
print("Hoàn tất việc loại bỏ các cụm từ (BÀI KIỂM TRA 1 -- TUẦN 4)!")
