with open("docs/report/Bao_cao_KT1_Nhom_StockClustering.log", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "[56]" in line or "[57]" in line or "[58]" in line:
        print(f"--- Line {i+1} ---")
        start = max(0, i-15)
        end = min(len(lines), i+15)
        for j in range(start, end):
            print(f"{j+1}: {lines[j].strip()}")

