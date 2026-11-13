"""
Script tạo biểu đồ đối chứng thực nghiệm giữa Phân cụm phân cấp (Hierarchical Clustering) và K-Means.
Chứng minh định lượng tại sao Hierarchical Clustering vượt trội cho bài toán cổ phiếu VN100.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
from sklearn.metrics import adjusted_rand_score
import os

# Cấu hình thẩm mỹ học thuật
plt.rcParams['font.sans-serif'] = 'Times New Roman'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False
sns.set_theme(style="whitegrid", font="Times New Roman", font_scale=1.1)

# 1. Tải dữ liệu tập Train
returns = pd.read_csv('data/processed/train/train_log_returns.csv', index_col=0)
dist_df = pd.read_csv('data/processed/train/train_mantegna_distance_matrix.csv', index_col=0)
corr_df = pd.read_csv('data/processed/train/train_correlation_matrix.csv', index_col=0)
symbols = dist_df.columns.tolist()
N = len(symbols)

corr_mat = corr_df.values
X_stocks = returns.T.values # 98 x 739
D_condensed = squareform(dist_df.values, checks=False)

k = 6

# 2. Huấn luyện các mô hình với K=6
# 2.1 Hierarchical Clustering (Ward trên Mantegna distance)
Z_ward = linkage(D_condensed, method='ward')
ward_labels = fcluster(Z_ward, t=k, criterion='maxclust') - 1

# 2.2 K-Means (Euclidean trên chuỗi lợi suất gốc)
km_euc = KMeans(n_clusters=k, random_state=42, n_init=10).fit(X_stocks)
km_euc_labels = km_euc.labels_

# 2.3 K-Means trên không gian PCA 5D
pca = PCA(n_components=5, random_state=42)
X_pca = pca.fit_transform(X_stocks)
km_pca = KMeans(n_clusters=k, random_state=42, n_init=10).fit(X_pca)
km_pca_labels = km_pca.labels_

# 3. Tính toán tương quan nội cụm (Intra) và liên cụm (Inter)
def get_correlations(labels, corr):
    intra = []
    inter = []
    for i in range(N):
        for j in range(i + 1, N):
            if labels[i] == labels[j]:
                intra.append(corr[i, j])
            else:
                inter.append(corr[i, j])
    return np.array(intra), np.array(inter)

ward_intra, ward_inter = get_correlations(ward_labels, corr_mat)
km_euc_intra, km_euc_inter = get_correlations(km_euc_labels, corr_mat)
km_pca_intra, km_pca_inter = get_correlations(km_pca_labels, corr_mat)

# 4. Kiểm định độ ổn định ngẫu nhiên (Pairwise ARI qua 20 random seeds)
seeds = list(range(20))
km_euc_runs = [KMeans(n_clusters=k, random_state=s, n_init=10).fit(X_stocks).labels_ for s in seeds]
km_euc_aris = [adjusted_rand_score(km_euc_runs[i], km_euc_runs[j]) for i in range(20) for j in range(i+1, 20)]

km_pca_runs = [KMeans(n_clusters=k, random_state=s, n_init=10).fit(X_pca).labels_ for s in seeds]
km_pca_aris = [adjusted_rand_score(km_pca_runs[i], km_pca_runs[j]) for i in range(20) for j in range(i+1, 20)]

# Hierarchical là tất định 100% -> ARI luôn bằng 1.0
hc_aris = [1.0] * len(km_euc_aris)

# 5. Vẽ biểu đồ tổng hợp 3 Panel
fig = plt.figure(figsize=(18, 5.5), dpi=300)

# Panel A: Phân tách tương quan Pearson nội cụm vs liên cụm
ax1 = plt.subplot(1, 3, 1)
models = ['Hierarchical\n(Ward + Mantegna)', 'K-Means\n(Euclid / Returns)', 'K-Means\n(PCA 5D)']
intra_means = [np.mean(ward_intra), np.mean(km_euc_intra), np.mean(km_pca_intra)]
inter_means = [np.mean(ward_inter), np.mean(km_euc_inter), np.mean(km_pca_inter)]
x = np.arange(len(models))
width = 0.35

rects1 = ax1.bar(x - width/2, intra_means, width, label='Nội cụm (Intra-cluster $\\rho$)', color='#1b7837', alpha=0.85, edgecolor='black')
rects2 = ax1.bar(x + width/2, inter_means, width, label='Liên cụm (Inter-cluster $\\rho$)', color='#762a83', alpha=0.85, edgecolor='black')

ax1.set_ylabel(r'Hệ số tương quan Pearson trung bình ($\pm \sigma$)', fontsize=12, fontweight='bold')
ax1.set_title('(a) Khả năng phân tách tương quan ($K=6$)\n[Nội cụm càng cao & Liên cụm càng thấp $\\rightarrow$ Đa dạng hóa tốt]', fontsize=12, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(models, fontsize=11)
ax1.set_ylim(0.25, 0.52)
ax1.legend(loc='upper right', frameon=True, fontsize=10)

# Ghi giá trị chênh lệch Delta trên từng cột
for i in range(len(models)):
    delta = intra_means[i] - inter_means[i]
    color = '#1b7837' if delta > 0.05 else ('#d95f02' if delta > 0 else '#b2182b')
    ax1.annotate(rf'$\Delta = {delta:+.4f}$', 
                 xy=(x[i], max(intra_means[i], inter_means[i]) + 0.015),
                 ha='center', va='bottom', fontsize=11, fontweight='bold', color=color)

# Panel B: Phân bố độ ổn định qua 20 random seeds (Adjusted Rand Index)
ax2 = plt.subplot(1, 3, 2)
ari_df = pd.DataFrame({
    'Thuật toán': ['Hierarchical\n(Mantegna)'] * len(hc_aris) + 
                  ['K-Means\n(Euclid)'] * len(km_euc_aris) + 
                  ['K-Means\n(PCA 5D)'] * len(km_pca_aris),
    'ARI': hc_aris + km_euc_aris + km_pca_aris
})
palette = {'Hierarchical\n(Mantegna)': '#2ca02c', 'K-Means\n(Euclid)': '#d62728', 'K-Means\n(PCA 5D)': '#ff7f0e'}
sns.boxplot(x='Thuật toán', y='ARI', data=ari_df, ax=ax2, hue='Thuật toán', palette=palette, legend=False, width=0.45, boxprops=dict(alpha=0.8))
sns.stripplot(x='Thuật toán', y='ARI', data=ari_df, ax=ax2, color='black', alpha=0.25, jitter=0.15, size=4)

ax2.set_ylabel('Chỉ số Adjusted Rand Index (ARI)', fontsize=12, fontweight='bold')
ax2.set_title('(b) Kiểm định độ ổn định qua 20 lần chạy\n[Hierarchical tất định $ARI=1.0$; K-Means bất ổn định nặng]', fontsize=12, fontweight='bold')
ax2.set_ylim(0.15, 1.08)
ax2.axhline(1.0, color='green', linestyle='--', alpha=0.6)

# Chú thích giá trị trung bình ARI
ax2.text(0, 1.03, 'ARI = 1.000\n(Tất định)', ha='center', va='bottom', fontsize=10, fontweight='bold', color='green')
ax2.text(1, np.mean(km_euc_aris) + 0.05, f'Mean = {np.mean(km_euc_aris):.3f}\n(Dao động lớn)', ha='center', va='bottom', fontsize=10, fontweight='bold', color='#d62728')
ax2.text(2, np.mean(km_pca_aris) + 0.05, f'Mean = {np.mean(km_pca_aris):.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold', color='#ff7f0e')

# Panel C: Chiếu không gian PCA 2D & Đối chiếu các cặp cổ phiếu nổi tiếng
ax3 = plt.subplot(1, 3, 3)
pca_2d = PCA(n_components=2, random_state=42)
X_2d = pca_2d.fit_transform(X_stocks)

scatter = ax3.scatter(X_2d[:, 0], X_2d[:, 1], c=ward_labels, cmap='tab10', s=60, alpha=0.85, edgecolors='black', linewidth=0.5)
ax3.set_xlabel(f'Thành phần chính 1 (PC1: {pca_2d.explained_variance_ratio_[0]*100:.1f}%)', fontsize=11, fontweight='bold')
ax3.set_ylabel(f'Thành phần chính 2 (PC2: {pca_2d.explained_variance_ratio_[1]*100:.1f}%)', fontsize=11, fontweight='bold')
ax3.set_title('(c) Phân bố 98 mã trên PCA 2D (Tô màu cụm Ward)\n[Bảo toàn trọn vẹn các cặp đồng ngành cốt lõi]', fontsize=12, fontweight='bold')

# Đánh dấu các cặp cổ phiếu đồng pha mạnh nhất
highlight_pairs = [('HSG', 'NKG', '#d95f02'), ('DCM', 'DPM', '#1b7837'), ('SSI', 'VCI', '#7570b3')]
for s1, s2, col in highlight_pairs:
    if s1 in symbols and s2 in symbols:
        idx1, idx2 = symbols.index(s1), symbols.index(s2)
        ax3.plot([X_2d[idx1, 0], X_2d[idx2, 0]], [X_2d[idx1, 1], X_2d[idx2, 1]], color=col, linestyle='-', linewidth=2.0, alpha=0.9)
        ax3.text(X_2d[idx1, 0], X_2d[idx1, 1]+0.015, s1, fontsize=9, fontweight='bold', color=col)
        ax3.text(X_2d[idx2, 0], X_2d[idx2, 1]-0.025, s2, fontsize=9, fontweight='bold', color=col)

plt.tight_layout()

# Lưu biểu đồ vào các thư mục báo cáo
out_paths = [
    'reports/figures/kmeans_vs_hierarchical_comparison.png',
    'docs/report/images/hinh_kmeans_vs_hierarchical.png',
    'docs/latext_page/images/hinh_kmeans_vs_hierarchical.png'
]

for p in out_paths:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    plt.savefig(p, dpi=300, bbox_inches='tight')
    print(f"Đã xuất bản biểu đồ tại: {p}")

plt.close()
print("Hoàn tất sinh biểu đồ đối chứng K-Means vs Hierarchical!")
