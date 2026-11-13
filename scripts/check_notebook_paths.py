import json
import glob

for path in sorted(glob.glob("notebooks/*.ipynb")):
    with open(path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    print(f"\n=== {path} ===")
    for i, c in enumerate(nb["cells"]):
        if c["cell_type"] == "code":
            text = "".join(c["source"])
            if "PROJECT_ROOT" in text or "Path(" in text:
                print(f"  Cell {i:02d}: uses PROJECT_ROOT / Path")
            elif "read_csv" in text:
                # check if raw string relative path
                first_read = [l.strip() for l in text.split("\n") if "read_csv" in l][:2]
                print(f"  Cell {i:02d}: read_csv -> {first_read}")

