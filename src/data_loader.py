"""Module thu thập dữ liệu giá chứng khoán Việt Nam (VN100).

Hỗ trợ linh hoạt đa nguồn (Multi-backend):
1. Nguồn vnstock thế hệ mới (Gen 5: package `vnstock` từ vnstocks.com).
2. Nguồn vnstock3 (nếu có).
3. Nguồn Yahoo Finance (.VN) và API chứng khoán trực tiếp làm fallback đáng tin cậy.
"""

from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

# Danh sách 100 mã cổ phiếu tiêu biểu rổ VN100 (Niêm yết HOSE)
DEFAULT_VN100_SYMBOLS: list[str] = [
    # VN30
    "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG",
    "MBB", "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB",
    "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VJC", "VNM", "VPB", "VRE",
    # VNMidCap tiêu biểu trong VN100
    "AAA", "AGG", "ANV", "ASM", "BAF", "BFC", "BSI", "BWE", "CII", "CMG",
    "CTD", "CTR", "CTS", "DBC", "DCM", "DGC", "DGW", "DIG", "DPM", "DXG",
    "DXS", "EIB", "EVF", "FTS", "GEG", "GEX", "HAH", "HCM", "HDC", "HDG",
    "HHV", "HSG", "KBC", "KDC", "KDH", "LPB", "MSB", "NAB", "NKG", "NLG",
    "NT2", "NVL", "OCB", "PAN", "PC1", "PDR", "PET", "PHR", "PNJ", "PTB",
    "PVD", "PVT", "REE", "SBT", "SCR", "SCS", "SZC", "TCH", "TLG", "TMS",
    "VCI", "VGC", "VHC", "VIX", "VND", "VPI", "VOS", "VTP", "VSH", "KOS"
]
DEFAULT_VN100_SYMBOLS = sorted(list(dict.fromkeys(DEFAULT_VN100_SYMBOLS)))

# Bản đồ nhóm ngành cơ bản (ICB Sector) cho các mã VN100
SECTOR_MAP: dict[str, str] = {
    # Ngân hàng (Financials - Banking)
    "ACB": "Ngân hàng", "BID": "Ngân hàng", "CTG": "Ngân hàng", "HDB": "Ngân hàng",
    "MBB": "Ngân hàng", "SHB": "Ngân hàng", "SSB": "Ngân hàng", "STB": "Ngân hàng",
    "TCB": "Ngân hàng", "TPB": "Ngân hàng", "VCB": "Ngân hàng", "VIB": "Ngân hàng",
    "VPB": "Ngân hàng", "EIB": "Ngân hàng", "LPB": "Ngân hàng", "MSB": "Ngân hàng",
    "NAB": "Ngân hàng", "OCB": "Ngân hàng",
    # Chứng khoán (Financials - Securities)
    "SSI": "Dịch vụ tài chính", "VND": "Dịch vụ tài chính", "VCI": "Dịch vụ tài chính",
    "HCM": "Dịch vụ tài chính", "VIX": "Dịch vụ tài chính", "FTS": "Dịch vụ tài chính",
    "BSI": "Dịch vụ tài chính", "CTS": "Dịch vụ tài chính", "EVF": "Dịch vụ tài chính",
    # Bất động sản (Real Estate)
    "VIC": "Bất động sản", "VHM": "Bất động sản", "VRE": "Bất động sản",
    "NVL": "Bất động sản", "PDR": "Bất động sản", "DIG": "Bất động sản",
    "DXG": "Bất động sản", "KDH": "Bất động sản", "NLG": "Bất động sản",
    "KBC": "Bất động sản KCN", "SZC": "Bất động sản KCN", "BCM": "Bất động sản KCN",
    "TCH": "Bất động sản", "HDG": "Bất động sản", "HDC": "Bất động sản",
    "CII": "Hạ tầng - Bất động sản", "VPI": "Bất động sản", "AGG": "Bất động sản",
    # Thép & Vật liệu (Materials)
    "HPG": "Tài nguyên Cơ bản (Thép)", "HSG": "Tài nguyên Cơ bản (Thép)",
    "NKG": "Tài nguyên Cơ bản (Thép)", "DGC": "Hóa chất", "DCM": "Phân bón - Hóa chất",
    "DPM": "Phân bón - Hóa chất", "BFC": "Phân bón - Hóa chất", "GVR": "Cao su - Hóa chất",
    "PHR": "Cao su", "VGC": "Vật liệu xây dựng",
    # Bán lẻ & Tiêu dùng (Consumer Goods & Retail)
    "MWG": "Bán lẻ", "PNJ": "Bán lẻ", "FRT": "Bán lẻ", "DGW": "Bán lẻ công nghệ",
    "PET": "Bán lẻ", "MSN": "Thực phẩm - Tiêu dùng", "VNM": "Thực phẩm - Tiêu dùng",
    "SAB": "Đồ uống", "KDC": "Thực phẩm", "DBC": "Nông nghiệp - Thực phẩm",
    "BAF": "Nông nghiệp - Thực phẩm", "PAN": "Nông nghiệp",
    # Thủy sản & Dệt may (Export)
    "VHC": "Thủy sản", "ANV": "Thủy sản", "TLG": "Hàng tiêu dùng",
    # Công nghệ & Viễn thông (Technology)
    "FPT": "Công nghệ thông tin", "CMG": "Công nghệ thông tin",
    "CTR": "Công trình Viettel", "VTP": "Chuyển phát Viettel",
    # Dầu khí & Năng lượng (Energy & Utilities)
    "GAS": "Dầu khí", "PLX": "Dầu khí", "PVD": "Dịch vụ Dầu khí", "PVT": "Vận tải Dầu khí",
    "POW": "Điện lực", "REE": "Cơ điện - Năng lượng", "PC1": "Xây lắp điện - Năng lượng",
    "GEG": "Năng lượng tái tạo", "NT2": "Điện lực", "VSH": "Thủy điện",
    "BWE": "Nước - Môi trường",
    # Vận tải & Xây dựng (Industrials)
    "VJC": "Hàng không", "GEX": "Thiết bị điện", "HAH": "Cảng biển - Vận tải",
    "VOS": "Vận tải biển", "TMS": "Logistics", "SCS": "Dịch vụ hàng hóa",
    "CTD": "Xây dựng", "HHV": "Hạ tầng giao thông", "PTB": "Gỗ - Đá"
}


def get_vn100_symbols(source: str = "VCI") -> tuple[list[str], pd.DataFrame]:
    """Lấy danh sách mã rổ VN100 kèm bảng phân ngành ICB metadata.

    Returns:
        tuple[list[str], pd.DataFrame]: (danh_sách_mã, dataframe_metadata)
    """
    rows = []
    for sym in DEFAULT_VN100_SYMBOLS:
        sector = SECTOR_MAP.get(sym, "Khác")
        is_vn30 = sym in [
            "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG",
            "MBB", "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB",
            "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VJC", "VNM", "VPB", "VRE"
        ]
        rows.append({
            "symbol": sym,
            "exchange": "HOSE",
            "group": "VN30" if is_vn30 else "VNMidCap",
            "sector": sector
        })

    df_meta = pd.DataFrame(rows)
    print(f"[INFO] Khởi tạo danh sách {len(DEFAULT_VN100_SYMBOLS)} mã VN100 kèm metadata phân ngành.")
    return DEFAULT_VN100_SYMBOLS, df_meta


def _fetch_from_vnstock_v5(symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
    """Tải lịch sử giá qua vnstock thế hệ mới (v5.x)."""
    try:
        import importlib
        vnstock_mod = importlib.import_module("vnstock")
        Market = getattr(vnstock_mod, "Market")
        mkt = Market()
        df = mkt.equity(symbol).ohlcv(start=start_date, end=end_date)
        if df is not None and not df.empty:
            df = df.reset_index()
            # Chuẩn hóa tên cột
            col_map = {"time": "date", "trading_date": "date", "Date": "date"}
            df = df.rename(columns=col_map)
            df["symbol"] = symbol
            return df
    except Exception:
        pass
    return None


def _fetch_from_vnstock3(symbol: str, start_date: str, end_date: str, source: str = "VCI") -> Optional[pd.DataFrame]:
    """Tải lịch sử giá qua vnstock3 (nếu có)."""
    try:
        import importlib
        vnstock3_module = importlib.import_module("vnstock3")
        Vnstock = getattr(vnstock3_module, "Vnstock")
        stock = Vnstock().stock(symbol=symbol, source=source)
        df = stock.quote.history(start=start_date, end=end_date, interval="1D")
        if df is not None and not df.empty:
            if "time" in df.columns:
                df["time"] = pd.to_datetime(df["time"])
                df = df.rename(columns={"time": "date"})
            df["symbol"] = symbol
            return df
    except Exception:
        pass
    return None


def _fetch_from_yahoo_finance(symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
    """Tải lịch sử giá miễn phí từ Yahoo Finance API cho mã HOSE (hậu tố .VN).

    Cực kỳ ổn định, không yêu cầu cài đặt thêm package độc quyền, trả về đầy đủ
    Adjusted Close, Open, High, Low, Volume.
    """
    try:
        start_ts = int(pd.Timestamp(start_date).timestamp())
        end_ts = int(pd.Timestamp(end_date).timestamp()) + 86400

        ticker = f"{symbol}.VN"
        url = (
            f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?"
            f"period1={start_ts}&period2={end_ts}&interval=1d&events=history"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        result = data.get("chart", {}).get("result")
        if not result:
            return None

        chart_data = result[0]
        timestamps = chart_data.get("timestamp", [])
        indicators = chart_data.get("indicators", {})
        quote = indicators.get("quote", [{}])[0]
        adjclose = indicators.get("adjclose", [{}])[0].get("adjclose", [])

        if not timestamps:
            return None

        dates = pd.to_datetime(timestamps, unit="s").strftime("%Y-%m-%d")
        df = pd.DataFrame({
            "date": dates,
            "open": quote.get("open", []),
            "high": quote.get("high", []),
            "low": quote.get("low", []),
            "close": quote.get("close", []),
            "adj_close": adjclose if adjclose else quote.get("close", []),
            "volume": quote.get("volume", []),
            "symbol": symbol
        })

        # Loại bỏ các phiên rỗng/lễ
        df = df.dropna(subset=["close"]).reset_index(drop=True)
        return df
    except Exception as e:
        # Im lặng trả về None để vòng ngoài thử tiếp
        return None


def fetch_stock_history(
    symbol: str,
    start_date: str = "2022-01-01",
    end_date: str = "2026-10-23",
    source: str = "AUTO",
    max_retries: int = 3,
    retry_delay: float = 1.0,
) -> Optional[pd.DataFrame]:
    """Tải lịch sử giá OHLCV của mã cổ phiếu với cơ chế tự động chuyển đổi nguồn.

    Thứ tự ưu tiên:
    1. vnstock Gen 5 (nếu đã cài đặt)
    2. vnstock3 (nếu có)
    3. Yahoo Finance .VN (sẵn có, tốc độ cao, đầy đủ Adjusted Close)

    Args:
        symbol: Mã cổ phiếu (ví dụ: 'HPG', 'VCB').
        start_date: Ngày bắt đầu (YYYY-MM-DD).
        end_date: Ngày kết thúc (YYYY-MM-DD).
        source: Nguồn ('AUTO', 'VNSTOCK', 'YAHOO').
        max_retries: Số lần thử lại tối đa.
        retry_delay: Thời gian nghỉ giữa các lần thử (giây).

    Returns:
        Optional[pd.DataFrame]: DataFrame lịch sử giá hoặc None nếu thất bại.
    """
    for attempt in range(1, max_retries + 1):
        df = None

        # 1. Thử vnstock v5 / vnstock3 nếu được yêu cầu hoặc AUTO
        if source in ("AUTO", "VNSTOCK"):
            df = _fetch_from_vnstock_v5(symbol, start_date, end_date)
            if df is None:
                df = _fetch_from_vnstock3(symbol, start_date, end_date)

        # 2. Fallback sang Yahoo Finance (cực kỳ ổn định và đầy đủ cho VN100)
        if df is None:
            df = _fetch_from_yahoo_finance(symbol, start_date, end_date)

        if df is not None and not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date").reset_index(drop=True)
            return df

        time.sleep(retry_delay * attempt)

    print(f"[WARN] Không tải được dữ liệu mã {symbol} sau {max_retries} lần thử.")
    return None


def save_symbol_data(df: pd.DataFrame, symbol: str, output_dir: str | Path) -> Path:
    """Lưu DataFrame giá của một mã vào thư mục data/raw/{symbol}.csv."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    file_path = out_path / f"{symbol}.csv"
    df.to_csv(file_path, index=False, encoding="utf-8-sig")
    return file_path
