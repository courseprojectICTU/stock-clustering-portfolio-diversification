"""
Script sửa tất cả các dấu gạch dưới chưa được escape trong văn bản thường của tệp LaTeX.
"""
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

tex_path = Path("docs/latext_page/Mau bao cao mon Hoc may.tex")
content = tex_path.read_text(encoding="utf-8")

# Sửa các chuỗi cụ thể đã biết
replacements = [
    ("01_data_collection_prep.ipynb", "01\\_data\\_collection\\_prep.ipynb"),
    ("02_data_preprocessing.ipynb", "02\\_data\\_preprocessing.ipynb"),
    ("03_feature_extraction_returns.ipynb", "03\\_feature\\_extraction\\_returns.ipynb"),
    ("04_correlation_distance.ipynb", "04\\_correlation\\_distance.ipynb"),
    ("05_train_test_split.ipynb", "05\\_train\\_test\\_split.ipynb"),
    ("01\\_data_collection_prep.ipynb", "01\\_data\\_collection\\_prep.ipynb"),
    ("02\\_data_preprocessing.ipynb", "02\\_data\\_preprocessing.ipynb"),
    ("03\\_feature_extraction_returns.ipynb", "03\\_feature\\_extraction\\_returns.ipynb"),
    ("04\\_correlation_distance.ipynb", "04\\_correlation\\_distance.ipynb"),
    ("05\\_train_test_split.ipynb", "05\\_train\\_test\\_split.ipynb"),
    ("Path(__file__)", "Path(\\_\\_file\\_\\_)"),
    ("stock_financial_features.csv", "stock\\_financial\\_features.csv"),
    ("vn100_symbols.csv", "vn100\\_symbols.csv"),
    ("adj_close_clean.csv", "adj\\_close\\_clean.csv"),
    ("train_adj_close.csv", "train\\_adj\\_close.csv"),
    ("train_log_returns.csv", "train\\_log\\_returns.csv"),
    ("train_correlation_matrix.csv", "train\\_correlation\\_matrix.csv"),
    ("train_mantegna_distance_matrix.csv", "train\\_mantegna\\_distance\\_matrix.csv"),
    ("test_adj_close.csv", "test\\_adj\\_close.csv"),
    ("test_log_returns.csv", "test\\_log\\_returns.csv"),
    ("mean_daily_pct", "mean\\_daily\\_pct"),
    ("annual_return_pct", "annual\\_return\\_pct"),
    ("annual_volatility_pct", "annual\\_volatility\\_pct"),
    ("sharpe_ratio", "sharpe\\_ratio"),
    ("excess_kurtosis", "excess\\_kurtosis"),
    ("jb_pvalue", "jb\\_pvalue"),
    ("is_normal", "is\\_normal"),
]

for old, new in replacements:
    content = content.replace(old, new)

tex_path.write_text(content, encoding="utf-8")
print("Đã thay thế thành công các dấu gạch dưới trong LaTeX.")
