with open("docs/report/Bao_cao_KT1_Nhom_StockClustering.log", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

idx = text.find("Phụ lục B")
while idx != -1:
    print(text[max(0, idx-100):min(len(text), idx+300)])
    print("="*50)
    idx = text.find("Phụ lục B", idx+1)

