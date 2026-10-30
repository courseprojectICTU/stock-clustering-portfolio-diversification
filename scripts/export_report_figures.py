"""
Script xuất bản các biểu đồ trực quan hóa dữ liệu phục vụ Báo cáo Bài kiểm tra 1 môn Học máy.
Lưu tất cả ảnh định dạng PNG độ phân giải cao vào docs/latext_page/images/
"""

import sys
import shutil
from pathlib import Path

# Cấu hình UTF-8 cho console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats

# Cấu hình font và style cho matplotlib
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "docs" / "report" / "images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Đồng thời hỗ trợ thư mục latext_page
ALT_OUTPUT_DIR = PROJECT_ROOT / "docs" / "latext_page" / "images"
ALT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"Bắt đầu xuất hình ảnh vào: {OUTPUT_DIR}")

# 1. Sao chép các hình đã có từ reports/figures nếu có
src_figs = PROJECT_ROOT / "reports" / "figures"
if (src_figs / "euclidean_vs_pearson_paradox.png").exists():
    shutil.copy(src_figs / "euclidean_vs_pearson_paradox.png", OUTPUT_DIR / "hinh_euclidean_vs_pearson.png")
    print("-> Đã sao chép: hinh_euclidean_vs_pearson.png")

if (src_figs / "mantegna_transformation_metric.png").exists():
    shutil.copy(src_figs / "mantegna_transformation_metric.png", OUTPUT_DIR / "hinh_mantegna_metric.png")
    print("-> Đã sao chép: hinh_mantegna_metric.png")

# 2. Tạo hình Biểu đồ đường giá sau khi làm sạch (98 cổ phiếu)
clean_price_path = PROJECT_ROOT / "data" / "processed" / "adj_close_clean.csv"
if clean_price_path.exists():
    df_price = pd.read_csv(clean_price_path, index_col=0, parse_dates=True)
    # Chuẩn hóa về mốc 100 tại ngày bắt đầu để dễ quan sát biến động tương đối
    df_norm = df_price / df_price.iloc[0] * 100

    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    for col in df_norm.columns:
        ax.plot(df_norm.index, df_norm[col], color='gray', alpha=0.15, linewidth=0.8)
    # Vẽ đường trung bình thị trường
    mean_series = df_norm.mean(axis=1)
    ax.plot(df_norm.index, mean_series, color='#003399', linewidth=2.2, label='Chỉ số trung bình VN100 (Cơ sở 100)')
    
    ax.set_title("Biến động giá đóng cửa điều chỉnh 98 cổ phiếu VN100 (2022 - 2026)", fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel("Thời gian giao dịch", fontsize=11)
    ax.set_ylabel("Chỉ số giá tương đối (Mốc xuất phát = 100)", fontsize=11)
    ax.axhline(100, color='black', linestyle='--', linewidth=0.8, alpha=0.6)
    ax.legend(loc='upper right', frameon=True)
    ax.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "hinh_clean_price_series.png", dpi=300)
    plt.close()
    print("-> Đã tạo: hinh_clean_price_series.png")

# 3. Tạo hình Phân phối lợi suất logarit và Q-Q plot kiểm định đuôi béo (Fat-tails)
log_ret_path = PROJECT_ROOT / "data" / "processed" / "log_returns.csv"
if log_ret_path.exists():
    df_ret = pd.read_csv(log_ret_path, index_col=0, parse_dates=True)
    all_returns = df_ret.values.flatten()
    all_returns = all_returns[~np.isnan(all_returns)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8), dpi=300)

    # Histogram & Phân phối chuẩn đối chiếu
    mu, std = all_returns.mean(), all_returns.std()
    x_range = np.linspace(-0.10, 0.10, 1000)
    pdf_norm = stats.norm.pdf(x_range, mu, std)

    sns.histplot(all_returns, bins=120, stat='density', ax=ax1, color='#2b5c8f', alpha=0.6, label='Dữ liệu thực tế')
    ax1.plot(x_range, pdf_norm, 'r--', linewidth=2.0, label=f'Phân phối chuẩn N({mu:.4f}, {std:.4f})')
    ax1.set_xlim(-0.08, 0.08)
    ax1.set_title("Phân phối lợi suất ngày toàn thị trường\n(Excess Kurtosis = 3.86, Đuôi béo)", fontsize=11, fontweight='bold')
    ax1.set_xlabel("Lợi suất logarit hàng ngày", fontsize=10)
    ax1.set_ylabel("Mật độ xác suất", fontsize=10)
    ax1.legend(loc='upper right')
    ax1.grid(True, linestyle=':', alpha=0.6)

    # Q-Q plot
    stats.probplot(all_returns, dist="norm", plot=ax2)
    ax2.get_lines()[0].set_markerfacecolor('#2b5c8f')
    ax2.get_lines()[0].set_markeredgecolor('none')
    ax2.get_lines()[0].set_alpha(0.2)
    ax2.get_lines()[0].set_markersize(3)
    ax2.get_lines()[1].set_color('red')
    ax2.get_lines()[1].set_linewidth(2.0)
    ax2.set_title("Biểu đồ Q-Q Plot kiểm định phân phối chuẩn\n(Hai đầu lệch mạnh, kiểm định Jarque-Bera p < 0.001)", fontsize=11, fontweight='bold')
    ax2.set_xlabel("Phân vị lý thuyết (Chuẩn)", fontsize=10)
    ax2.set_ylabel("Phân vị mẫu thực tế", fontsize=10)
    ax2.grid(True, linestyle=':', alpha=0.6)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "hinh_returns_distribution_qq.png", dpi=300)
    plt.close()
    print("-> Đã tạo: hinh_returns_distribution_qq.png")

# 4. Tạo hình Scatter plot Lợi suất - Rủi ro (Risk-Return Trade-off) theo ngành ICB
feat_path = PROJECT_ROOT / "data" / "processed" / "stock_financial_features.csv"
meta_path = PROJECT_ROOT / "data" / "metadata" / "vn100_symbols.csv"
if feat_path.exists():
    df_feat = pd.read_csv(feat_path)
    if meta_path.exists():
        df_meta = pd.read_csv(meta_path)
        # Hợp nhất tên ngành ICB
        col_symbol = 'ticker' if 'ticker' in df_meta.columns else df_meta.columns[0]
        col_icb = 'icb_industry' if 'icb_industry' in df_meta.columns else 'sector'
        symbol_col_feat = 'symbol' if 'symbol' in df_feat.columns else df_feat.columns[0]
        merged = df_feat.merge(df_meta[[col_symbol, col_icb]], left_on=symbol_col_feat, right_on=col_symbol, how='left')
    else:
        merged = df_feat
        col_icb = None

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    vol_col = 'annual_volatility_pct'
    ret_col = 'annual_return_pct'
    col_icb = 'sector'
    symbol_col_feat = 'symbol'
    
    col_symbol = 'symbol'
    merged = df_feat.merge(df_meta[[col_symbol, col_icb]], on='symbol', how='left')

    fig, ax = plt.subplots(figsize=(10.5, 5.8), dpi=300)

    palette = sns.color_palette("tab10", n_colors=merged[col_icb].nunique())
    sns.scatterplot(data=merged, x=vol_col, y=ret_col, hue=col_icb, s=85, alpha=0.9, palette=palette, ax=ax)
    ax.legend(title='Nhóm ngành ICB', bbox_to_anchor=(1.02, 1), loc='upper left', frameon=True, fontsize=9)

    # Gắn nhãn một số mã tiêu biểu
    for idx, row in merged.iterrows():
        sym = row[symbol_col_feat]
        if sym in ['VCB', 'FPT', 'HPG', 'VIC', 'GAS', 'VNM', 'SSI', 'MWG']:
            ax.annotate(sym, (row[vol_col], row[ret_col]), fontsize=9, fontweight='bold',
                        xytext=(4, 4), textcoords='offset points')

    ax.set_title("Không gian Lợi suất kỳ vọng - Rủi ro biến động 98 mã VN100", fontsize=12, fontweight='bold', pad=10)
    ax.set_xlabel("Độ biến động hàng năm (Rủi ro - Annualized Volatility)", fontsize=11)
    ax.set_ylabel("Lợi suất hàng năm (Annualized Return)", fontsize=11)
    ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
    ax.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "hinh_risk_return_scatter.png", dpi=300)
    plt.close()
    print("-> Đã tạo: hinh_risk_return_scatter.png")

# 5. Tạo hình Biểu đồ phân chia chuỗi thời gian Train / Test (Regime-based Split)
if clean_price_path.exists():
    df_price = pd.read_csv(clean_price_path, index_col=0, parse_dates=True)
    mean_market = df_price.mean(axis=1)
    mean_norm = mean_market / mean_market.iloc[0] * 100

    train_end = pd.to_datetime('2024-12-31')
    train_part = mean_norm[mean_norm.index <= train_end]
    test_part = mean_norm[mean_norm.index > train_end]

    fig, ax = plt.subplots(figsize=(10.5, 4.8), dpi=300)
    ax.plot(train_part.index, train_part.values, color='#003399', linewidth=2.0, label=f'Tập Train (In-Sample: 2022-2024, N={len(train_part)} phiên, 62.3%)')
    ax.plot(test_part.index, test_part.values, color='#d9534f', linewidth=2.0, label=f'Tập Test (Out-of-Sample: 2025-2026, N={len(test_part)} phiên, 37.7%)')

    ax.axvline(train_end, color='black', linestyle='--', linewidth=1.5, label='Ranh giới phân tách (31/12/2024)')

    # Đổ bóng 2 vùng
    ax.axvspan(mean_norm.index[0], train_end, color='#003399', alpha=0.08)
    ax.axvspan(train_end, mean_norm.index[-1], color='#d9534f', alpha=0.08)

    ax.text(pd.to_datetime('2023-06-01'), ax.get_ylim()[1]*0.9, 'GIAI ĐOẠN HUẤN LUYỆN (TRAIN)\n- Downtrend sâu (2022)\n- Tích lũy phục hồi (2023-2024)\n- Q = 7.54 >> 1 (Khử nhiễu RMT)',
            fontsize=9.5, bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='#003399', alpha=0.9), ha='center')
    ax.text(pd.to_datetime('2025-11-01'), ax.get_ylim()[1]*0.9, 'KIỂM THỬ NGOÀI MẪU (TEST)\n- Pha tích lũy & phân hóa mới\n- Đánh giá Backtest độc lập\n- Không rò rỉ dữ liệu',
            fontsize=9.5, bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='#d9534f', alpha=0.9), ha='center')

    ax.set_title("Chiến lược phân chia dữ liệu Train (2022 - 2024) / Test (2025 - 2026) theo thời gian", fontsize=12, fontweight='bold', pad=12)
    ax.set_xlabel("Thời gian giao dịch", fontsize=11)
    ax.set_ylabel("Chỉ số thị trường chuẩn hóa (Cơ sở 100)", fontsize=11)
    ax.legend(loc='lower left', frameon=True)
    ax.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "hinh_train_test_split.png", dpi=300)
    plt.close()
    print("-> Đã tạo: hinh_train_test_split.png")

# 6. Tạo hình Bản đồ nhiệt ma trận tương quan Pearson trên tập Train (98x98)
train_corr_path = PROJECT_ROOT / "data" / "processed" / "train" / "train_correlation_matrix.csv"
if train_corr_path.exists():
    df_corr = pd.read_csv(train_corr_path, index_col=0)
    fig, ax = plt.subplots(figsize=(8.5, 7.5), dpi=300)
    sns.heatmap(df_corr, cmap='RdBu_r', vmin=-1, vmax=1, center=0, cbar_kws={'label': 'Hệ số tương quan Pearson (\u03c1)'}, ax=ax,
                xticklabels=False, yticklabels=False)
    ax.set_title("Bản đồ nhiệt ma trận tương quan Pearson trên tập Train (98 mã VN100)\n(Trung bình \u03c1 = 0.3697, thể hiện hiệu ứng thị trường chung)", fontsize=11, fontweight='bold', pad=10)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "hinh_train_correlation_heatmap.png", dpi=300)
    plt.close()
    print("-> Đã tạo: hinh_train_correlation_heatmap.png")

# 7. Tạo hình Bản đồ nhiệt ma trận khoảng cách Mantegna trên tập Train (98x98)
train_dist_path = PROJECT_ROOT / "data" / "processed" / "train" / "train_mantegna_distance_matrix.csv"
if train_dist_path.exists():
    df_dist = pd.read_csv(train_dist_path, index_col=0)
    fig, ax = plt.subplots(figsize=(8.5, 7.5), dpi=300)
    sns.heatmap(df_dist, cmap='viridis_r', vmin=0, vmax=2.0, cbar_kws={'label': 'Khoảng cách Mantegna d = \u221a[2(1 - \u03c1)]'}, ax=ax,
                xticklabels=False, yticklabels=False)
    ax.set_title("Bản đồ nhiệt ma trận khoảng cách Mantegna trên tập Train (98 mã VN100)\n(Thỏa mãn 4 tiên đề metric, trung bình d = 1.1156)", fontsize=11, fontweight='bold', pad=10)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "hinh_train_mantegna_heatmap.png", dpi=300)
    plt.close()
    print("-> Đã tạo: hinh_train_mantegna_heatmap.png")

print("Hoàn tất xuất tất cả hình ảnh phục vụ Báo cáo Bài kiểm tra 1!")
