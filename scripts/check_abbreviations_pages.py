with open("scripts/pages_9_13.txt", "r", encoding="utf-8", errors="ignore") as f:
    pages = f.read().split("\x0c")

print("--- PAGE 12 (xi) FULL TEXT ---")
print(pages[3]) # 0-indexed: 9=0, 10=1, 11=2, 12=3

print("--- PAGE 13 (xii) FULL TEXT ---")
print(pages[4])

