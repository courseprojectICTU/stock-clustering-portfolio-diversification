import subprocess

cmd = ["pdftotext", "-f", "55", "-l", "62", "docs/report/Bao_cao_KT1_Nhom_StockClustering.pdf", "scripts/pages_appendix.txt"]
subprocess.run(cmd)

with open("scripts/pages_appendix.txt", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

pages = content.split("\x0c")
for i, page_text in enumerate(pages):
    print(f"=== PDF Page {55 + i} ===")
    lines = [l.strip() for l in page_text.splitlines() if l.strip()]
    for l in lines[:15]:
        print("  ", l)
    if len(lines) > 15:
        print("   ... (total lines:", len(lines), ")")
        for l in lines[-4:]:
            print("  ", l)

