with open("docs/report/Bao_cao_KT1_Nhom_StockClustering.log", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

count = 0
for i, line in enumerate(lines):
    if "Overfull \\hbox" in line:
        count += 1
        print(f"Log Line {i+1}: {line.strip()}")
        for j in range(i+1, min(i+4, len(lines))):
            print(f"   {lines[j].strip()}")

print(f"\n===> TOTAL OVERFULL \\HBOX COUNT: {count}")
