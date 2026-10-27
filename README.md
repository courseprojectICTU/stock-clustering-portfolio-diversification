# Phân Nhóm Cổ Phiếu Theo Mức Độ Đồng Biến Động Giá Phục Vụ Đa Dạng Hóa Danh Mục Đầu Tư

> **Đề tài tiểu luận môn:** Học máy (Machine Learning) - HK7  
> **Bộ nhớ & Hướng dẫn kỹ thuật:** Chi tiết tại [AGENT.md](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/AGENT.md)  
> **Yêu cầu gốc:** Xem tại [docs/detai.txt](file:///d:/HocTap/HK7/H%E1%BB%8Dc%20m%C3%A1y/project/stock-clustering-portfolio-diversification/docs/detai.txt)

---

## 📌 1. Giới thiệu đề tài
Dự án nghiên cứu và ứng dụng các kỹ thuật Học máy không giám sát (**Unsupervised Learning**) nhằm phân nhóm các mã cổ phiếu có mức độ đồng biến động giá tương đồng, từ đó xây dựng chiến lược đa dạng hóa danh mục đầu tư nhằm giảm thiểu rủi ro phi hệ thống (unsystematic risk).

### Các trụ cột phương pháp:
1. **Phân cụm phân cấp gộp (Agglomerative Hierarchical Clustering):** Khảo sát 4 tiêu chí liên kết (*Single, Complete, Average, Ward*) trên ma trận khoảng cách tương quan Mantegna $d(i, j) = \sqrt{2(1 - \rho_{i,j})}$.
2. **Đối chứng K-Means & PCA:** Giảm chiều không gian đặc trưng bằng PCA và phân cụm K-Means làm baseline.
3. **Đánh giá đa chiều:** Cắt Dendrogram kết hợp Silhouette Score để tối ưu số cụm $k$; đo độ ổn định cụm qua thời gian bằng **Adjusted Rand Index (ARI)**.
4. **Ứng dụng thực tiễn:** Xây dựng danh mục phân bổ đại diện mỗi cụm và backtest so với danh mục ngẫu nhiên / chỉ số thị trường (Sharpe Ratio, Volatility, Max Drawdown).

---

## 📂 2. Cấu trúc thư mục dự án
- `data/`: Dữ liệu thô và dữ liệu đã làm sạch (`raw`, `processed`, `metadata`).
- `notebooks/`: Chuỗi 6 notebook nghiên cứu theo chu trình phân tích và thực nghiệm.
- `src/`: Codebase module hóa các hàm tính toán lợi suất, phân cụm, đánh giá và mô phỏng danh mục.
- `reports/`: Đồ thị (`figures/`) và báo cáo tiểu luận.
- `docs/`: Yêu cầu đề tài, ghi chú lý thuyết toán học.
