import subprocess

cmd = ["pdftotext", "docs/report/Bao_cao_KT1_Nhom_StockClustering.pdf", "scripts/all_pages.txt"]
subprocess.run(cmd)

with open("scripts/all_pages.txt", "r", encoding="utf-8", errors="ignore") as f:
    pages = f.read().split("\x0c")

print("Total pages in PDF:", len(pages))
for i, p in enumerate(pages[:-1]):
    lines = [l.strip() for l in p.splitlines() if l.strip()]
    last_line = lines[-1] if lines else "<empty>"
    first_line = lines[0] if lines else "<empty>"
    # Print pages from 65 to end
    if i >= 64:
        print(f"PDF Page {i+1}: first='{first_line}', last='{last_line}', num_lines={len(lines)}")

