with open("scripts/pages_app_final.txt", "r", encoding="utf-8", errors="ignore") as f:
    pages = f.read().split("\x0c")

print("=== PAGE 69 (page 56) ===")
print(repr(pages[3]))

print("=== PAGE 70 (page 57) ===")
print(repr(pages[4]))

print("=== PAGE 71 (page 58) ===")
print(repr(pages[5]))

