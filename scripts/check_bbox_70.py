import subprocess

res = subprocess.run(["pdftotext", "-f", "70", "-l", "70", "-bbox", "docs/report/Bao_cao_KT1_Nhom_StockClustering.pdf", "-"], capture_output=True, text=True)
print("Page 70 bbox:")
print(res.stdout)

