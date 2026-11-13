import subprocess

cmd = ["pdftotext", "-f", "66", "-l", "71", "docs/report/Bao_cao_KT1_Nhom_StockClustering.pdf", "scripts/pages_app_final.txt"]
subprocess.run(cmd)

with open("scripts/pages_app_final.txt", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

pages = content.split("\x0c")
for i, page_text in enumerate(pages):
    print(f"=== PDF Page {66 + i} ===")
    lines = [l.strip() for l in page_text.splitlines() if l.strip()]
    print("Line count:", len(lines))
    for l in lines[:10]:
        print("  ", l)
    if len(lines) > 10:
        print("   ...")
        for l in lines[-3:]:
            print("  ", l)

