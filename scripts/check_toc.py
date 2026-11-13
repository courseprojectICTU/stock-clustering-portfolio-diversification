import subprocess

cmd = ["pdftotext", "-f", "5", "-l", "8", "docs/report/Bao_cao_KT1_Nhom_StockClustering.pdf", "scripts/toc_pages.txt"]
subprocess.run(cmd)

with open("scripts/toc_pages.txt", "r", encoding="utf-8", errors="ignore") as f:
    print(f.read())

