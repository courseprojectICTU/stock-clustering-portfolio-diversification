with open("docs/report/Bao_cao_KT1_Nhom_StockClustering.log", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

import re
# Find occurrences of [56], [57], [58]
pos56 = text.find("[56]")
pos57 = text.find("[57]")
pos58 = text.find("[58]")

print("Log around [56], [57], [58]:")
print(text[max(0, pos56-200):min(len(text), pos58+300)])

