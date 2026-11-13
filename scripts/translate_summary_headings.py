import json
import glob
import os
import re

HEADINGS_MAP = [
    (r"###\s*Q&A", "### Câu hỏi & Trả lời"),
    (r"###\s*Data Analysis Key Findings", "### Kết quả phân tích dữ liệu chính"),
    (r"###\s*DATA Analysis key findings", "### Kết quả phân tích dữ liệu chính"),
    (r"###\s*Insights or Next Steps", "### Nhận định & Hướng đi tiếp theo"),
    (r"###\s*insights or next steps", "### Nhận định & Hướng đi tiếp theo"),
]

def update_text(text):
    for pattern, replacement in HEADINGS_MAP:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def process_notebook(nb_path):
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    modified = False
    for cell in nb["cells"]:
        if cell["cell_type"] == "markdown":
            source_text = "".join(cell["source"])
            updated_text = update_text(source_text)
            if source_text != updated_text:
                lines = [line + "\n" for line in updated_text.split("\n")]
                if lines:
                    lines[-1] = lines[-1].rstrip("\n")
                cell["source"] = lines
                modified = True

    if modified:
        with open(nb_path, "w", encoding="utf-8") as f:
            json.dump(nb, f, ensure_ascii=False, indent=1)
        print(f"[UPDATED] {nb_path}")
    else:
        print(f"[UNCHANGED] {nb_path}")

def process_file(file_path):
    if not os.path.exists(file_path):
        return
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    updated = update_text(content)
    if content != updated:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated)
        print(f"[UPDATED] {file_path}")
    else:
        print(f"[UNCHANGED] {file_path}")

def main():
    print("=== Translating Summary Headings in Notebooks ===")
    for path in sorted(glob.glob("notebooks/*.ipynb")):
        process_notebook(path)

    print("\n=== Translating Summary Headings in Supporting Scripts ===")
    scripts_to_update = [
        "scripts/standardize_all_notebooks_markdown.py",
        "scripts/create_nb06.py",
        "scripts/create_nb07.py",
        "scripts/refine_nb07_markdown.py"
    ]
    for s in scripts_to_update:
        process_file(s)

if __name__ == "__main__":
    main()

