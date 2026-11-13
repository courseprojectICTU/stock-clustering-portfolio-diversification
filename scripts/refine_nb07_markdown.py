import json
import os

NOTEBOOK_PATH = "notebooks/07_hierarchical_clustering_linkages.ipynb"

# Define concise, human-styled markdown text for each markdown cell index
MD_REPLACEMENTS = {
    0: """# Notebook 07: So sánh Tiêu chí Liên kết và Chọn Số Cụm Tối ưu K*

- **Mục tiêu:**
  - Quyết định 7: Chọn tiêu chí liên kết (Single, Complete, Average, Ward).
  - Quyết định 8: Xác định số cụm tối ưu $K^*$ trong bài toán gom nhóm cổ phiếu VN100.
- **Dữ liệu:** Tập Train 2022–2024 (98 mã $\\times$ 739 phiên). Khoảng cách Mantegna $d(i,j) = \\sqrt{2(1 - \\rho_{ij})}$.
- **Mô hình:** Hierarchical Bottom-Up (đã chọn ở Notebook 06); đối chứng với Baseline K-Means.

### Các bước thực nghiệm:
1. **Vòng 1 (Hình thái cây & CCC):** Vẽ Dendrogram 4 linkage, đo hệ số tương quan Cophenetic (CCC).
2. **Vòng 2 (Quét $K \\in [3, 15]$):** Đo Silhouette, entropy kích thước cụm, kiểm tra cụm đơn lẻ (singleton) và độ phân tách tương quan $\\Delta = \\bar{\\rho}_{\\text{intra}} - \\bar{\\rho}_{\\text{inter}}$.
3. **Vòng 3 (Baseline & Đánh giá cụm):**
   - So sánh với K-Means (PCA 5D và PCA 45D giữ 80% phương sai).
   - Kiểm định độ ổn định qua Block Sub-sampling ($B=30$, lấy mẫu 80% số phiên).
   - Phân tích 10 cụm ngành và rà soát các mã cổ phiếu ở vùng ranh giới.""",

    2: """### Kiểm tra dữ liệu và cơ sở dùng Ward Linkage
- Dữ liệu Train gồm 98 cổ phiếu trong 739 phiên, không có giá trị thiếu. Tỷ số $T/N = 7.54 > 1$ đủ lớn để ma trận tương quan ổn định.
- **Tính hợp lệ của Ward Linkage trên khoảng cách Mantegna:**
  - Về mặt lý thuyết, Ward yêu cầu khoảng cách Euclid.
  - Khi vector lợi suất được chuẩn hóa (z-score chia $\\sqrt{T}$), khoảng cách Euclid giữa hai chuỗi chính bằng khoảng cách Mantegna: $d(i,j) = \\sqrt{2(1 - \\rho_{ij})}$.
  - Sai số số học tối đa đo được trên dữ liệu thực tế là $3.77 \\times 10^{-15}$ (bằng 0 trên độ chính xác dấu phẩy động). Do đó, áp dụng Ward trực tiếp lên ma trận Mantegna là hoàn toàn chuẩn xác.""",

    4: """### Vòng 1: Đánh giá hình thái cây và Hệ số Cophenetic (CCC)
- **Average ($CCC = 0.9046$) và Single ($CCC = 0.8664$):** Có CCC cao nhất do bảo toàn khoảng cách trung bình và tối thiểu khi gộp cụm. Tuy nhiên, dendrogram cho thấy cả hai đều bị hiệu ứng xâu chuỗi (chaining effect): phần lớn cổ phiếu dồn vào một nhánh lớn, chỉ có vài mã ngoại lai tách riêng.
- **Complete ($CCC = 0.6760$):** Cây cân đối hơn Single nhưng vẫn còn một số nhánh dồn mã.
- **Ward ($CCC = 0.3615$):** CCC thấp hơn vì Ward tối thiểu hóa phương sai nội cụm ($\\Delta WSS$) thay vì bảo toàn khoảng cách tuyến tính ban đầu. Bù lại, dendrogram của Ward chia nhánh đồng đều, tạo thành các cụm có quy mô cân bằng và dễ phân tách thành các nhóm ngành.""",

    6: """### Vòng 2: Đánh giá Silhouette và hiện tượng cụm đơn lẻ (Singleton)
- **Single và Average:** Ở $K=3$, hai phương pháp này đạt Silhouette cao ($0.1486$), nhưng cụm lớn nhất chiếm tới **98%** (96 mã), còn 2 cụm còn lại mỗi cụm chỉ có 1 mã (`[96, 1, 1]`). Cấu trúc này không thể dùng để đa dạng hóa danh mục vì 96 mã chỉ được chọn 1 đại diện.
- **Complete:** Đạt Silhouette cao nhất ở $K=14$ ($0.0526$), nhưng sinh ra tới 8 cụm 1 mã (singleton) và một cụm lớn chiếm 58.2% (57 mã).
- **Ward:** Là phương pháp duy nhất không có cụm đơn lẻ nào từ $K=3$ đến $K=14$. Tỷ lệ cụm lớn nhất giảm đều từ 34.7% xuống 21.4%, kích thước các cụm đồng đều và độ phân tách tương quan $\\Delta$ tăng đều theo $K$.""",

    8: """### Quyết định 7 và Quyết định 8: Chọn Linkage và Số cụm K*
- **Quyết định 7 (Tiêu chí liên kết):**
  - Trong 52 cấu hình thử nghiệm (4 linkage $\\times$ 13 giá trị $K$), chỉ có **11 cấu hình** thỏa mãn điều kiện khả thi (0 singleton và cụm lớn nhất $\\le 50\\%$).
  - Tất cả 11 cấu hình này đều thuộc **Ward Linkage**. Single, Complete và Average đều bị loại do dồn cụm hoặc tạo nhiều cụm 1 mã.
- **Quyết định 8 (Số cụm tối ưu $K^*$):**
  - Trong phạm vi danh mục từ 5 đến 10 cổ phiếu, cấu hình **Ward tại $K^* = 10$** có điểm tổng hợp cao nhất (Composite Score = 0.5889).
  - Tại $K^* = 10$, các chỉ số đạt: Silhouette = 0.0296, $\\Delta = +0.1389$, Normalized Entropy = 0.9203, kích thước cụm: `[21, 19, 13, 10, 10, 8, 7, 4, 3, 3]`.
  - So với $K = 6$ ($\\Delta = +0.0932$), mức $K^* = 10$ bóc tách rõ các nhóm ngành riêng biệt (ngân hàng, phân bón, họ Vingroup) và nâng độ phân tách tương quan lên thêm 49%.""",

    10: """### Vòng 3A: So sánh mô hình đề xuất với Baseline K-Means
- **PCA 5D vs PCA 45D:** 5 thành phần chính chỉ giữ được 30.50% phương sai; để đạt trên 80% phương sai (80.34%) cần dùng tới 45 chiều.
- **Ảnh hưởng số chiều lên K-Means:** Khi tăng lên 45 chiều (`KMeans_PCA_45D_80pct`), dữ liệu bị nhiễu làm $\\Delta$ giảm mạnh còn +0.0224 (Silhouette = 0.0111). Ngược lại, `KMeans_PCA_5D` cho kết quả tốt hơn ($\\Delta = +0.0771$, Silhouette = 0.0228) nhưng vẫn có 1 cụm đơn lẻ.
- **So sánh với Bottom-Up Ward ($K^*=10$):**
  - Mô hình đề xuất đạt $\\Delta = +0.1389$, cao gấp 1.8 lần PCA 5D và gấp 6.2 lần PCA 45D.
  - Silhouette đạt 0.0296 (cao hơn cả hai Baseline) và không có cụm đơn lẻ.""",

    12: """### Vòng 3B: Kiểm định độ ổn định bằng Block Sub-sampling
- Thực nghiệm lấy mẫu lại 30 lần (mỗi lần giữ 80% số khối phiên giao dịch trên tập Train):
  - **Chỉ số tách tương quan ($\\Delta$) và Silhouette:** Bottom-Up Ward ($K^*=10$) đạt $\\Delta = +0.1398 \\pm 0.0114$ và Silhouette = $0.0317 \\pm 0.0037$, cao gần gấp đôi Baseline K-Means 5D ($\\Delta = +0.0736 \\pm 0.0093$, Silhouette = $0.0188 \\pm 0.0029$). Độ lệch chuẩn nhỏ cho thấy kết quả phân cụm không bị phụ thuộc vào một vài phiên đột biến.
  - **Chỉ số tương đồng ARI:** Baseline đạt ARI = $0.8485 \\pm 0.0823$, cao hơn Ward ($0.6914 \\pm 0.1215$). Lý do là 5 trục PCA gom biến động vĩ mô diện rộng nên gán nhãn ít đổi khi bớt ngày, còn Ward ở mức 10 cụm chi tiết hơn nên một số mã ở vùng ranh giới có thể nhảy giữa hai nhánh lân cận. Tuy nhiên, về tiêu chí phân tách tương quan phục vụ danh mục, Ward vẫn tốt hơn nhiều.""",

    14: """### Phân tích 10 cụm ngành và các cổ phiếu ranh giới
- **Đặc điểm kinh tế của 10 cụm (Ward Linkage, $K^*=10$):**
  - **Cụm thuần ngành có tương quan nội bộ cao:**
    - Cụm 2 (Chứng khoán & Thép, $\\bar{\\rho} = 0.696$): `SSI, VCI, HCM, VND, FTS, HPG, HSG, NKG`.
    - Cụm 3 (Phân bón - Hóa chất, $\\bar{\\rho} = 0.670$): `DCM, DPM, DGC, BFC`.
    - Cụm 6 (13 mã Ngân hàng thương mại, $\\bar{\\rho} = 0.600$): `ACB, BID, CTG, MBB, STB, VPB...`
    - Cụm 8 (Nhóm Vingroup, $\\bar{\\rho} = 0.534$): `VIC, VHM, VRE`.
  - **Cụm tương quan thấp (tiềm năng phòng vệ cho danh mục):**
    - Cụm 9 (`KDC, KOS, TMS`, $\\bar{\\rho} = 0.085$) và Cụm 10 (`VCB, TCB, SSB, VNM, SAB, VJC, SCS, VPI`, $\\bar{\\rho} = 0.192$) gồm các mã có diễn biến riêng biệt, ít chạy theo chỉ số chung.
- **Cổ phiếu vùng ranh giới (Silhouette âm):**
  - Một số mã có Silhouette âm: `TCB` (-0.1421), `VCB` (-0.1123), `SSB` (-0.0920), `SBT` (-0.1233), `CTD` (-0.1132).
  - VCB, TCB, SSB nằm ở Cụm 10 thay vì Cụm 6 vì trong giai đoạn 2022–2024 các mã này biến động tương đối độc lập so với nhóm ngân hàng thương mại còn lại. SBT và CTD nằm ở vùng giao thoa giữa nhóm sản xuất và xây dựng.""",

    15: """## Tổng kết thực nghiệm Notebook 07

### Câu hỏi & Trả lời
- **Tiêu chí liên kết nào phù hợp nhất cho bài toán phân cụm cổ phiếu?**
  - **Ward Linkage** là lựa chọn duy nhất phù hợp. Toàn bộ 11/11 cấu hình thỏa mãn điều kiện thực tế (0 cụm đơn lẻ và cụm lớn nhất $\\le 50\\%$) đều thuộc Ward.
  - Average ($CCC = 0.9046$) và Single ($CCC = 0.8664$) có hệ số CCC cao nhưng bị dồn 88%–98% mã vào một cụm, không dùng được cho bài toán đầu tư.
- **Số cụm tối ưu $K^*$ là bao nhiêu và có tốt hơn Baseline không?**
  - Trong vùng 5–10 cụm phù hợp với quy mô danh mục, **Ward tại $K^* = 10$** đạt điểm tổng hợp cao nhất (Composite Score = 0.5889; Silhouette = 0.0296; $\\Delta = +0.1389$; không có singleton).
  - So với Baseline, Ward ($K^*=10$) vượt trội cả `KMeans_PCA_5D` (Silhouette = 0.0228, $\\Delta = +0.0771$, có 1 singleton) và `KMeans_PCA_45D_80pct` (Silhouette = 0.0111, $\\Delta = +0.0224$).

### Kết quả phân tích dữ liệu chính
- **Cơ sở toán học của Ward:** Khoảng cách Mantegna tương đương khoảng cách Euclid trên mặt cầu chuẩn hóa (sai số số học $3.77 \\times 10^{-15}$), do đó áp dụng Ward là chính xác.
- **Số chiều PCA:** Để giữ 80% phương sai lợi suất cần tới 45 chiều PCA, nhưng số chiều cao khiến K-Means bị nhiễu và giảm mạnh khả năng phân tách ($\\Delta$ chỉ còn +0.0224). PCA 5D là Baseline phù hợp hơn nhưng $\\Delta$ vẫn chỉ bằng một nửa so với Ward.
- **Kiểm định ổn định (Block Sub-sampling, $B=30$):** Ward đạt $\\Delta = +0.1398 \\pm 0.0114$ và Silhouette = $0.0317 \\pm 0.0037$, cao gấp đôi Baseline ($\\Delta = +0.0736 \\pm 0.0093$). Chỉ số ARI của Ward ($0.6914 \\pm 0.1215$) thấp hơn Baseline do các mã ranh giới (`TCB, VCB, SBT, CTD`) nhạy cảm khi rút bớt dữ liệu ngày.
- **Dữ liệu đầu ra:** Đã lưu nhãn cụm tối ưu vào `train_clusters_optimal.csv`, bảng số liệu quét $K$ vào `linkage_k_sweep_metrics.csv` và tóm tắt kết quả tại `nb07_summary.json`.

### Nhận định & Hướng đi tiếp theo
- **Notebook 08:** Đánh giá độ ổn định của 10 cụm qua 3 chu kỳ thị trường (2022 Giảm, 2023 Tích lũy, 2024 Phục hồi) bằng ARI và đối chiếu nhãn cụm với phân ngành ICB.
- **Notebook 09:** Chọn cổ phiếu đại diện từ 10 cụm (theo Sharpe cao nhất) để xây dựng danh mục đa dạng hóa và backtest trên tập Test độc lập 2025–2026."""
}

def main():
    with open(NOTEBOOK_PATH, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    print(f"Total cells before: {len(nb['cells'])}")
    modified_count = 0

    for idx, new_text in MD_REPLACEMENTS.items():
        if idx < len(nb['cells']):
            cell = nb['cells'][idx]
            if cell['cell_type'] == 'markdown':
                # Preserve lines format
                lines = [line + '\n' for line in new_text.split('\n')]
                # Remove trailing newline from last line if needed
                if lines:
                    lines[-1] = lines[-1].rstrip('\n')
                cell['source'] = lines
                modified_count += 1
                print(f"Updated Cell {idx} (markdown)")
            else:
                print(f"Warning: Cell {idx} is not markdown! It is {cell['cell_type']}")
        else:
            print(f"Warning: Cell index {idx} out of range!")

    with open(NOTEBOOK_PATH, 'w', encoding='utf-8') as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)

    print(f"Successfully refined {modified_count} markdown cells in {NOTEBOOK_PATH}")

    # Verification
    code_cells = [c for c in nb['cells'] if c['cell_type'] == 'code']
    md_cells = [c for c in nb['cells'] if c['cell_type'] == 'markdown']
    errs = [o for c in code_cells for o in c.get('outputs', []) if o.get('output_type') == 'error']
    print(f"Verification: {len(nb['cells'])} total cells ({len(code_cells)} code, {len(md_cells)} markdown).")
    print(f"Total error outputs in code cells: {len(errs)}")
    for i, c in enumerate(code_cells):
        out_types = [o.get('output_type') for o in c.get('outputs', [])]
        print(f"  Code cell {i}: {len(out_types)} outputs {out_types}")

    # Also update scripts/create_nb07.py so generator script is in sync
    create_script_path = "scripts/create_nb07.py"
    if os.path.exists(create_script_path):
        import re
        with open(create_script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()

        keys = [0, 2, 4, 6, 8, 10, 12, 14, 15]
        pattern = re.compile(r'cells\.append\(nbf\.v4\.new_markdown_cell\(r\"\"\"(.*?)\"\"\"\)\)', re.DOTALL)
        matches = list(pattern.finditer(script_content))
        print(f"Found {len(matches)} markdown calls in {create_script_path}")
        if len(matches) == 9:
            new_script = ""
            last_idx = 0
            for i, m in enumerate(matches):
                new_script += script_content[last_idx:m.start()]
                k = keys[i]
                new_script += f'cells.append(nbf.v4.new_markdown_cell(r"""{MD_REPLACEMENTS[k]}"""))'
                last_idx = m.end()
            new_script += script_content[last_idx:]
            with open(create_script_path, 'w', encoding='utf-8') as f:
                f.write(new_script)
            print(f"Successfully updated {create_script_path}")
        else:
            print("Warning: Count mismatch in create_nb07.py")

if __name__ == '__main__':
    main()
