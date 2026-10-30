"""Script to generate illustrative figures comparing Euclidean Distance vs Pearson + Mantegna Metric.

These figures demonstrate:
1. The Euclidean Paradox in Stock Co-movement (Scale Bias & Antiphase Trap).
2. The Mantegna Metric Transformation from Pearson Correlation to Metric Space.
3. Real-world VN100 comparison: Raw Euclidean Distance Matrix vs Mantegna Distance Matrix.
"""

import sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Set visual style
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8

OUTPUT_DIR = Path("reports/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_figure1_euclidean_paradox():
    """Figure 1: Demonstration of the Euclidean Paradox in Stock Co-movement."""
    np.random.seed(42)
    t = np.linspace(0, 10, 200)

    # Base market shock signal
    base_signal = np.sin(t) + 0.5 * np.cos(2 * t)

    # Pair 1: Stock A (High Beta / Speculative) & Stock B (Low Beta / Defensive)
    # Perfectly in-phase (rho = 1.0)
    stock_a = 0.08 * base_signal  # ±8% daily returns
    stock_b = 0.01 * base_signal  # ±1% daily returns

    # Pair 2: Stock C & Stock D (Low amplitude, but 100% antiphase)
    # Opposite phase (rho = -1.0)
    stock_c = 0.005 * np.cos(t)
    stock_d = -0.005 * np.cos(t)

    # Calculate Euclidean distances
    d_euc_ab = np.linalg.norm(stock_a - stock_b)
    d_euc_cd = np.linalg.norm(stock_c - stock_d)

    # Calculate Pearson correlations
    rho_ab = np.corrcoef(stock_a, stock_b)[0, 1]
    rho_cd = np.corrcoef(stock_c, stock_d)[0, 1]

    # Calculate Mantegna distances
    d_mant_ab = np.sqrt(2 * (1 - rho_ab))
    d_mant_cd = np.sqrt(2 * (1 - rho_cd))

    fig = plt.figure(figsize=(14, 8), dpi=300)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.2, 1])

    # Subplot 1: Pair A & B (In-phase, different scales)
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(t, stock_a * 100, label="Cổ phiếu A (Biên độ lớn: ±8%)", color="#d9534f", linewidth=1.8)
    ax1.plot(t, stock_b * 100, label="Cổ phiếu B (Biên độ nhỏ: ±1%)", color="#0275d8", linewidth=2.0, linestyle="--")
    ax1.set_title("Cặp 1: Đồng pha tuyệt đối (Cùng tăng / Cùng giảm)\nNhưng lệch biên độ dao động (Scale Bias)", fontsize=11, fontweight="bold", pad=10)
    ax1.set_xlabel("Thời gian (Phiên)", fontsize=10)
    ax1.set_ylabel("Lợi suất hàng ngày (%)", fontsize=10)
    ax1.legend(loc="upper right", frameon=True)
    ax1.grid(True, linestyle="--", alpha=0.5)

    # Subplot 2: Pair C & D (Antiphase, tiny scales)
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(t, stock_c * 100, label="Cổ phiếu C (Biên độ nhỏ: +0.5%)", color="#5cb85c", linewidth=1.8)
    ax2.plot(t, stock_d * 100, label="Cổ phiếu D (Biên độ nhỏ: -0.5%)", color="#f0ad4e", linewidth=1.8, linestyle="--")
    ax2.set_title("Cặp 2: Ngược pha tuyệt đối (Mã tăng - Mã giảm)\nNhưng biên độ dao động rất nhỏ (Antiphase Trap)", fontsize=11, fontweight="bold", pad=10)
    ax2.set_xlabel("Thời gian (Phiên)", fontsize=10)
    ax2.set_ylabel("Lợi suất hàng ngày (%)", fontsize=10)
    ax2.legend(loc="upper right", frameon=True)
    ax2.grid(True, linestyle="--", alpha=0.5)

    # Subplot 3: Comparison of Metrics
    ax3 = fig.add_subplot(gs[1, :])
    categories = [
        "Cặp A & B\n(Đồng pha 100%, Lệch biên độ)",
        "Cặp C & D\n(Ngược pha 100%, Biên độ nhỏ)"
    ]
    x = np.arange(len(categories))
    width = 0.25

    val_euc = [d_euc_ab, d_euc_cd]
    val_rho = [rho_ab, rho_cd]
    val_mant = [d_mant_ab, d_mant_cd]

    rects1 = ax3.bar(x - width, val_euc, width, label=f"Khoảng cách Euclid (d_Euclid)", color="#d9534f", alpha=0.85)
    rects2 = ax3.bar(x, val_rho, width, label=f"Tương quan Pearson (rho)", color="#0275d8", alpha=0.85)
    rects3 = ax3.bar(x + width, val_mant, width, label=f"Khoảng cách Mantegna (d_Mantegna)", color="#5cb85c", alpha=0.85)

    ax3.set_ylabel("Giá trị độ đo", fontsize=11, fontweight="bold")
    ax3.set_title("So sánh Phản ứng của 3 Độ đo: Nghịch lý Euclid vs Chuẩn xác của Mantegna", fontsize=12, fontweight="bold", pad=12)
    ax3.set_xticks(x)
    ax3.set_xticklabels(categories, fontsize=10, fontweight="bold")
    ax3.legend(loc="upper center", bbox_to_anchor=(0.5, 1.25), ncol=3, frameon=True, fontsize=10)
    ax3.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax3.grid(True, linestyle=":", alpha=0.6)

    # Attach values on bars
    for i, rect in enumerate(rects1):
        h = rect.get_height()
        status = "(LỚN - Bị tách cụm)" if i == 0 else "(BÉ - Bị lừa gộp cụm)"
        ax3.annotate(f"{h:.3f}\n{status}", xy=(rect.get_x() + rect.get_width() / 2, h),
                     xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#d9534f")
    for rect in rects2:
        h = rect.get_height()
        if h >= 0:
            ax3.annotate(f"{h:.2f}", xy=(rect.get_x() + rect.get_width() / 2, h),
                         xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=9.5, fontweight="bold", color="#0275d8")
        else:
            ax3.annotate(f"{h:.2f}", xy=(rect.get_x() + rect.get_width() / 2, h / 2),
                         xytext=(0, 0), textcoords="offset points", ha="center", va="center", fontsize=9.5, fontweight="bold", color="white")
    for rect in rects3:
        h = rect.get_height()
        status = "(CÙNG CỤM: 0.0)" if h < 0.1 else "(XA NHẤT: 2.0)"
        ax3.annotate(f"{h:.3f}\n{status}", xy=(rect.get_x() + rect.get_width() / 2, h),
                     xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#5cb85c")

    ax3.set_ylim(-1.35, 2.35)
    plt.tight_layout()
    fig_path = OUTPUT_DIR / "euclidean_vs_pearson_paradox.png"
    plt.savefig(fig_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Đã lưu biểu đồ 1 tại: {fig_path}")


def generate_figure2_mantegna_transformation():
    """Figure 2: Geometric & Metric Properties of Mantegna Distance Metric."""
    rho = np.linspace(-1, 1, 500)
    d_mantegna = np.sqrt(2 * (1 - rho))
    d_naive = 1 - rho

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)

    # Panel 1: Transformation curves
    ax1.plot(rho, d_mantegna, label=r"Mantegna Distance: $d(i, j) = \sqrt{2(1 - \rho)}$", color="#2e6da4", linewidth=2.5)
    ax1.plot(rho, d_naive, label=r"Naive Linear: $d_{naive} = 1 - \rho$ (Vi phạm BĐT tam giác)", color="#d9534f", linewidth=1.8, linestyle="--")
    
    # Key anchor points
    anchors = [
        (-1.0, 2.0, r"$\rho = -1 \rightarrow d = 2.0$" + "\n(Ngược pha, Xa nhất)", (25, -25)),
        (0.0, np.sqrt(2), r"$\rho = 0 \rightarrow d = \sqrt{2} \approx 1.414$" + "\n(Trực giao / Độc lập)", (-15, 18)),
        (1.0, 0.0, r"$\rho = 1 \rightarrow d = 0.0$" + "\n(Đồng pha, Trùng khít)", (-35, 18))
    ]
    for r_val, d_val, label, offset in anchors:
        ax1.scatter(r_val, d_val, color="#d9534f" if r_val==1.0 else "#2e6da4", s=60, zorder=5)
        ax1.annotate(label, xy=(r_val, d_val), xytext=offset, textcoords="offset points",
                     fontsize=9, fontweight="bold", bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#cccccc", alpha=0.9))

    ax1.set_ylim(-0.2, 2.3)
    ax1.set_title("Hàm Chuyển đổi từ Tương quan Pearson sang Khoảng cách Mantegna", fontsize=11, fontweight="bold", pad=12)
    ax1.set_xlabel("Hệ số tương quan Pearson " + r"($\rho \in [-1, 1]$)", fontsize=10)
    ax1.set_ylabel("Khoảng cách " + r"($d \in [0, 2]$)", fontsize=10)
    ax1.legend(loc="lower left", frameon=True, fontsize=9)
    ax1.grid(True, linestyle=":", alpha=0.6)

    # Panel 2: Geometry on Unit Sphere
    theta = np.linspace(0, 2*np.pi, 200)
    ax2.plot(np.cos(theta), np.sin(theta), color="#bbbbbb", linestyle="--", label=r"Mặt cầu đơn vị $\mathbb{S}^1$")
    
    # Vector x_i at angle 0
    ax2.quiver(0, 0, 1, 0, angles='xy', scale_units='xy', scale=1, color="#0275d8", width=0.012, label=r"$\hat{x}_i$ (Cổ phiếu $i$)")
    
    # Vector x_j at angle 60 deg (rho = cos(60) = 0.5)
    angle_rad = np.pi / 3  # 60 degrees -> rho = 0.5 -> d = sqrt(2*(1-0.5)) = 1.0
    ax2.quiver(0, 0, np.cos(angle_rad), np.sin(angle_rad), angles='xy', scale_units='xy', scale=1, color="#5cb85c", width=0.012, label=r"$\hat{x}_j$ (Cổ phiếu $j$, $\theta=60^\circ$)")
    
    # Chord line connecting heads (Euclidean distance on sphere)
    ax2.plot([1, np.cos(angle_rad)], [0, np.sin(angle_rad)], color="#d9534f", linewidth=2.2, linestyle="-",
             label=r"Dây cung $\| \hat{x}_i - \hat{x}_j \| = \sqrt{2(1 - \cos\theta)} = d(i, j)$")
    
    ax2.set_xlim(-1.2, 1.4)
    ax2.set_ylim(-0.3, 1.3)
    ax2.set_aspect("equal")
    ax2.set_title("Bản chất Hình học: Khoảng cách Euclid giữa 2 Đầu mút Vector\ntrên Mặt cầu Đơn vị (Thỏa mãn 4 Tiên đề Mêtric)", fontsize=11, fontweight="bold")
    ax2.legend(loc="upper right", frameon=True, fontsize=8.5)
    ax2.grid(True, linestyle=":", alpha=0.5)

    plt.tight_layout()
    fig_path = OUTPUT_DIR / "mantegna_transformation_metric.png"
    plt.savefig(fig_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Đã lưu biểu đồ 2 tại: {fig_path}")


def generate_figure3_vn100_comparison():
    """Figure 3: Real VN100 Data - Raw Euclidean Distance vs Mantegna Distance."""
    df_returns = pd.read_csv("data/processed/log_returns.csv", index_col=0)
    
    # Take top 15 liquid/prominent stocks across sectors for clean visualization
    sample_symbols = ["VCB", "BID", "CTG", "MBB", "HPG", "HSG", "VHM", "VIC", "NVL", "MWG", "FRT", "FPT", "GAS", "PLX", "MSN"]
    available_symbols = [s for s in sample_symbols if s in df_returns.columns]
    
    sub_df = df_returns[available_symbols]
    
    # Raw Euclidean distance between return series
    raw_vectors = sub_df.values.T  # (15, 1186)
    n = len(available_symbols)
    euc_mat = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            euc_mat[i, j] = np.linalg.norm(raw_vectors[i] - raw_vectors[j])
            
    # Correlation & Mantegna distance
    corr_mat = sub_df.corr().values
    mantegna_mat = np.sqrt(2 * np.clip(1 - corr_mat, 0, 2))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

    im1 = ax1.imshow(euc_mat, cmap="viridis")
    ax1.set_title("Ma trận Khoảng cách Euclid Thô\n(Bị chi phối bởi độ biến động riêng lẻ, ranh giới mờ nhạt)", fontsize=11, fontweight="bold")
    ax1.set_xticks(range(n))
    ax1.set_yticks(range(n))
    ax1.set_xticklabels(available_symbols, rotation=45, fontsize=8.5)
    ax1.set_yticklabels(available_symbols, fontsize=8.5)
    fig.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04, label="Khoảng cách Euclid")

    im2 = ax2.imshow(mantegna_mat, cmap="Blues_r", vmin=0, vmax=2)
    ax2.set_title("Ma trận Khoảng cách Mantegna Siêu Mêtric\n(Phản ánh sắc nét cụm ngành: VCB-BID-CTG, HPG-HSG, MWG-FRT)", fontsize=11, fontweight="bold")
    ax2.set_xticks(range(n))
    ax2.set_yticks(range(n))
    ax2.set_xticklabels(available_symbols, rotation=45, fontsize=8.5)
    ax2.set_yticklabels(available_symbols, fontsize=8.5)
    fig.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04, label="Khoảng cách Mantegna (0: Gần, 2: Xa)")

    plt.tight_layout()
    fig_path = OUTPUT_DIR / "vn100_euclidean_vs_mantegna_heatmap.png"
    plt.savefig(fig_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Đã lưu biểu đồ 3 tại: {fig_path}")


if __name__ == "__main__":
    generate_figure1_euclidean_paradox()
    generate_figure2_mantegna_transformation()
    generate_figure3_vn100_comparison()
    print("Hoàn tất tạo toàn bộ biểu đồ so sánh chất lượng cao!")
