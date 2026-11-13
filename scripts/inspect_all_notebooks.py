import json
import glob

def main():
    notebooks = sorted(glob.glob("notebooks/*.ipynb"))
    all_ok = True
    for path in notebooks:
        with open(path, "r", encoding="utf-8") as f:
            nb = json.load(f)
        code_cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
        md_cells = [c for c in nb["cells"] if c["cell_type"] == "markdown"]
        errs = [o for c in code_cells for o in c.get("outputs", []) if o.get("output_type") == "error"]
        total_outputs = sum(len(c.get("outputs", [])) for c in code_cells)
        print(f"\n{'='*70}\n{path}: {len(nb['cells'])} cells ({len(code_cells)} code, {len(md_cells)} md) | {total_outputs} outputs, {len(errs)} errors")
        if len(errs) > 0 or total_outputs == 0:
            all_ok = False
        for i, c in enumerate(nb["cells"]):
            if c["cell_type"] == "markdown":
                lines = [line.strip() for line in "".join(c["source"]).split("\n") if line.strip()]
                preview = lines[0] if lines else "EMPTY"
                print(f"  [Cell {i:02d} MD]: {preview[:80]}")
    print(f"\n{'='*70}\nALL NOTEBOOKS VALIDATED PERFECTLY: {all_ok}")

if __name__ == "__main__":
    main()
