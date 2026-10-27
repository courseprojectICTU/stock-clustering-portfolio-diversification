"""Script dòng lệnh (CLI) thu thập dữ liệu giá VN100 giai đoạn 2022 - 2026.

Cách sử dụng:
    python scripts/crawl_vn100.py
Hoặc tùy chỉnh tham số:
    python scripts/crawl_vn100.py --start 2022-01-01 --end 2026-10-23 --delay 0.5
"""

import argparse
import sys
import time
from pathlib import Path

# Thêm thư mục gốc vào PYTHONPATH để import module từ src
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import (
    DEFAULT_VN100_SYMBOLS,
    fetch_stock_history,
    get_vn100_symbols,
    save_symbol_data,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Thu thập dữ liệu giá lịch sử VN100 cho đề tài phân cụm cổ phiếu."
    )
    parser.add_argument(
        "--start",
        type=str,
        default="2022-01-01",
        help="Ngày bắt đầu (định dạng YYYY-MM-DD, mặc định: 2022-01-01)",
    )
    parser.add_argument(
        "--end",
        type=str,
        default="2026-10-23",
        help="Ngày kết thúc (định dạng YYYY-MM-DD, mặc định: 2026-10-23)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.6,
        help="Thời gian nghỉ giữa các lượt cào mã (giây, mặc định 0.6s để tránh rate limit)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Cào lại toàn bộ ngay cả khi file đã tồn tại trong data/raw/",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    start_date = args.start
    end_date = args.end
    delay = args.delay
    force = args.force

    raw_dir = PROJECT_ROOT / "data" / "raw"
    metadata_dir = PROJECT_ROOT / "data" / "metadata"
    raw_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print(" BẮT ĐẦU THU THẬP DỮ LIỆU GIÁ LỊCH SỬ VN100")
    print(f" Khoảng thời gian: {start_date} -> {end_date}")
    print(f" Thư mục lưu trữ: {raw_dir}")
    print("=" * 70)

    # 1. Lấy danh sách mã và lưu metadata
    print("\n[Bước 1/2] Lấy danh sách mã cổ phiếu rổ VN100...")
    symbols, df_meta = get_vn100_symbols(source="VCI")
    meta_file = metadata_dir / "vn100_symbols.csv"
    if df_meta is not None and not df_meta.empty:
        df_meta.to_csv(meta_file, index=False, encoding="utf-8-sig")
        print(f"-> Đã lưu metadata ({len(df_meta)} bản ghi) tại: {meta_file}")
    else:
        print(f"-> Sử dụng danh sách {len(symbols)} mã mặc định.")

    # 2. Thu thập dữ liệu từng mã
    print(f"\n[Bước 2/2] Thu thập dữ liệu OHLCV cho {len(symbols)} mã cổ phiếu...")

    successful_count = 0
    skipped_count = 0
    failed_symbols = []

    try:
        from tqdm import tqdm
        progress_bar = tqdm(symbols, desc="Tiến độ cào", unit="mã")
    except ImportError:
        progress_bar = symbols

    for symbol in progress_bar:
        target_file = raw_dir / f"{symbol}.csv"

        # Kiểm tra nếu file đã tồn tại và không bật --force
        if target_file.exists() and not force:
            skipped_count += 1
            successful_count += 1
            continue

        df = fetch_stock_history(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            source="AUTO",
            max_retries=3,
        )

        if df is not None and not df.empty:
            save_symbol_data(df, symbol, raw_dir)
            successful_count += 1
        else:
            failed_symbols.append(symbol)

        time.sleep(delay)

    # 3. Tổng kết
    print("\n" + "=" * 70)
    print(" KẾT QUẢ THU THẬP DỮ LIỆU:")
    print(f" + Tổng số mã đã xử lý: {len(symbols)}")
    print(f" + Thành công: {successful_count}/{len(symbols)}")
    if skipped_count > 0:
        print(f"   (Trong đó {skipped_count} mã đã có sẵn file từ trước, được bỏ qua)")
    if failed_symbols:
        print(f" + Thất bại ({len(failed_symbols)} mã): {', '.join(failed_symbols)}")
        print("   -> Bạn có thể chạy lại lệnh để tự động thử cào tiếp các mã lỗi.")
    else:
        print(" + Tuyệt vời! 100% mã cổ phiếu đã được thu thập đầy đủ vào data/raw/")
    print("=" * 70)


if __name__ == "__main__":
    main()
