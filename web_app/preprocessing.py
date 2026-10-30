"""Data preprocessing module for stock clustering and portfolio diversification.

This module handles:
1. Auditing raw historical stock data.
2. Exchange holiday detection (Yahoo Finance 0-volume artifacts).
3. Trading calendar alignment.
4. Historical coverage filtering (e.g. dropping newly listed / transferred stocks with short history).
5. Missing value imputation via forward-fill (ffill).
6. Return extraction (Logarithmic return r_t = ln(P_t / P_{t-1}) and Simple return).
7. Co-movement modeling: Pearson correlation matrix C and Mantegna distance matrix D.
"""

from __future__ import annotations

import glob
import json
import os
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


@dataclass
class PreprocessingConfig:
    """Configuration parameters for data preprocessing and feature extraction."""
    raw_dir: str = "data/raw"
    metadata_path: str = "data/metadata/vn100_symbols.csv"
    output_dir: str = "data/processed"
    min_coverage_ratio: float = 0.90
    filter_holidays: bool = True
    holiday_zero_vol_ratio: float = 0.50
    imputation_method: str = "ffill"  # "ffill" or "none"
    calc_returns: bool = True  # Step 3.1: Log return feature extraction (ENABLED)
    calc_relations: bool = True  # Step 3.2: Correlation and Mantegna distance (ENABLED)
    return_type: str = "log"  # "log" or "simple"
    risk_free_rate_annual: float = 0.05  # 5% for Sharpe baseline


class StockPreprocessor:
    """Core preprocessing engine for VN100 stock data."""

    def __init__(self, config: Optional[PreprocessingConfig] = None):
        self.config = config or PreprocessingConfig()
        os.makedirs(self.config.output_dir, exist_ok=True)

    def audit_raw_data(self) -> Dict[str, Any]:
        """Audit raw CSV files to detect discrepancies, missing values, and exchange holidays."""
        files = glob.glob(os.path.join(self.config.raw_dir, "*.csv"))
        if not files:
            raise FileNotFoundError(f"No CSV files found in {self.config.raw_dir}")

        stock_summaries: List[Dict[str, Any]] = []
        date_volume_map: Dict[str, List[float]] = {}
        all_dates_set = set()

        for file_path in files:
            symbol = os.path.splitext(os.path.basename(file_path))[0]
            df = pd.read_csv(file_path)

            if "date" not in df.columns or "adj_close" not in df.columns:
                continue

            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
            dates = df["date"].tolist()
            all_dates_set.update(dates)

            vol = df["volume"] if "volume" in df.columns else pd.Series(0, index=df.index)
            zero_vol_count = int((vol == 0).sum())
            null_adj_close = int(df["adj_close"].isnull().sum())

            # Record volume per date across stocks for holiday detection
            for d, v in zip(dates, vol):
                date_volume_map.setdefault(d, []).append(float(v))

            stock_summaries.append({
                "symbol": symbol,
                "total_rows": len(df),
                "start_date": min(dates) if dates else None,
                "end_date": max(dates) if dates else None,
                "null_adj_close": null_adj_close,
                "zero_vol_days": zero_vol_count,
                "zero_vol_pct": round((zero_vol_count / len(df) * 100) if len(df) else 0.0, 2)
            })

        total_stocks = len(stock_summaries)
        max_sessions = max((s["total_rows"] for s in stock_summaries), default=0)

        # Detect market holidays: dates where proportion of zero-volume stocks >= threshold
        holiday_candidates = []
        for dt, vols in sorted(date_volume_map.items()):
            zero_count = sum(1 for v in vols if v == 0)
            zero_ratio = zero_count / total_stocks if total_stocks else 0
            if zero_ratio >= self.config.holiday_zero_vol_ratio:
                holiday_candidates.append({
                    "date": dt,
                    "zero_vol_stocks": zero_count,
                    "total_active_stocks": len(vols),
                    "zero_vol_ratio": round(zero_ratio, 4)
                })

        return {
            "total_stocks": total_stocks,
            "max_sessions": max_sessions,
            "all_unique_dates_count": len(all_dates_set),
            "detected_holidays_count": len(holiday_candidates),
            "detected_holidays": holiday_candidates,
            "stock_summaries": stock_summaries,
        }

    def run_pipeline(
        self,
        min_coverage_ratio: Optional[float] = None,
        filter_holidays: Optional[bool] = None,
        holiday_zero_vol_ratio: Optional[float] = None,
        imputation_method: Optional[str] = None,
        calc_returns: Optional[bool] = None,
        calc_relations: Optional[bool] = None,
        return_type: Optional[str] = None,
        save_to_disk: bool = True
    ) -> Dict[str, Any]:
        """Execute the pipeline: Data Cleaning + Log Return Feature Extraction.
        
        calc_returns: Enabled by default (calculates r_t = ln(P_t/P_{t-1}) and financial profiles).
        calc_relations: Disabled by default (keeps Pearson correlation & Mantegna distance for Step 3.2).
        """
        min_cov = min_coverage_ratio if min_coverage_ratio is not None else self.config.min_coverage_ratio
        do_filter_holidays = filter_holidays if filter_holidays is not None else self.config.filter_holidays
        hol_ratio = holiday_zero_vol_ratio if holiday_zero_vol_ratio is not None else self.config.holiday_zero_vol_ratio
        impute_meth = imputation_method if imputation_method is not None else self.config.imputation_method
        do_calc_returns = calc_returns if calc_returns is not None else self.config.calc_returns
        do_calc_relations = calc_relations if calc_relations is not None else self.config.calc_relations
        ret_type = return_type if return_type is not None else self.config.return_type

        # 1. Audit raw data
        audit_res = self.audit_raw_data()
        all_holidays_set = {h["date"] for h in audit_res["detected_holidays"]} if do_filter_holidays else set()

        # 2. Load all raw stocks into date-indexed series
        files = glob.glob(os.path.join(self.config.raw_dir, "*.csv"))
        raw_price_dict: Dict[str, pd.Series] = {}
        raw_vol_dict: Dict[str, pd.Series] = {}

        for file_path in files:
            symbol = os.path.splitext(os.path.basename(file_path))[0]
            df = pd.read_csv(file_path)
            if "date" not in df.columns or "adj_close" not in df.columns:
                continue
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date").drop_duplicates(subset=["date"])
            df = df.set_index("date")

            raw_price_dict[symbol] = df["adj_close"].astype(float)
            if "volume" in df.columns:
                raw_vol_dict[symbol] = df["volume"].astype(float)

        raw_price_df = pd.DataFrame(raw_price_dict)
        raw_vol_df = pd.DataFrame(raw_vol_dict)

        # 3. Apply exchange holiday filtering on the entire calendar
        if do_filter_holidays and all_holidays_set:
            holiday_dts = pd.to_datetime(list(all_holidays_set))
            active_price_df = raw_price_df.drop(index=holiday_dts, errors="ignore")
            active_vol_df = raw_vol_df.drop(index=holiday_dts, errors="ignore")
        else:
            active_price_df = raw_price_df.copy()
            active_vol_df = raw_vol_df.copy()

        # 4. Master trading calendar: all trading sessions where at least 1 stock traded
        master_calendar = active_price_df.index.sort_values()
        total_master_sessions = len(master_calendar)

        # 5. Evaluate historical coverage per stock
        stock_coverage: Dict[str, Dict[str, Any]] = {}
        kept_symbols = []
        excluded_symbols = []

        for symbol in raw_price_df.columns:
            series = active_price_df[symbol].dropna()
            valid_sessions = len(series)
            coverage_pct = (valid_sessions / total_master_sessions) * 100 if total_master_sessions else 0

            is_kept = (valid_sessions / total_master_sessions) >= min_cov if total_master_sessions else False
            cov_info = {
                "symbol": symbol,
                "valid_sessions": valid_sessions,
                "total_master_sessions": total_master_sessions,
                "coverage_pct": round(coverage_pct, 2),
                "is_kept": is_kept,
                "reason": "OK (Historical coverage >= threshold)" if is_kept else f"Excluded: Historical coverage {coverage_pct:.1f}% < {min_cov*100:.0f}%"
            }
            stock_coverage[symbol] = cov_info

            if is_kept:
                kept_symbols.append(symbol)
            else:
                excluded_symbols.append(cov_info)

        # Sort kept symbols alphabetically
        kept_symbols = sorted(kept_symbols)

        # 6. Build clean price matrix with aligned calendar and track imputation
        clean_price_df = active_price_df[kept_symbols].reindex(master_calendar)
        raw_null_per_stock = clean_price_df.isnull().sum()
        raw_null_count = int(raw_null_per_stock.sum())
        
        imputed_stocks_detail = [
            {"symbol": sym, "missing_sessions": int(cnt), "pct_missing": round(cnt / total_master_sessions * 100, 2)}
            for sym, cnt in raw_null_per_stock[raw_null_per_stock > 0].items()
        ]

        if impute_meth == "ffill":
            # Forward-fill first, then backward-fill only if very first session is null
            clean_price_df = clean_price_df.ffill().bfill()
        
        post_null_count = int(clean_price_df.isnull().sum().sum())

        # Price-level descriptive statistics
        price_stats_list = []
        for sym in kept_symbols:
            s = clean_price_df[sym]
            p_start = float(s.iloc[0])
            p_end = float(s.iloc[-1])
            p_min = float(s.min())
            p_max = float(s.max())
            p_change = ((p_end - p_start) / p_start) * 100 if p_start > 0 else 0.0

            price_stats_list.append({
                "symbol": sym,
                "start_price": round(p_start, 1),
                "end_price": round(p_end, 1),
                "min_price": round(p_min, 1),
                "max_price": round(p_max, 1),
                "total_change_pct": round(p_change, 2)
            })

        # Coverage histogram
        all_coverages = [c["coverage_pct"] for c in stock_coverage.values()]
        cov_hist_counts, cov_bin_edges = np.histogram(all_coverages, bins=[50, 60, 70, 80, 90, 95, 100.1])
        coverage_histogram = {
            "labels": ["50-60%", "60-70%", "70-80%", "80-90%", "90-95%", "95-100%"],
            "counts": [int(c) for c in cov_hist_counts]
        }

        saved_files = []
        clean_price_path = os.path.join(self.config.output_dir, "adj_close_clean.csv")
        summary_path = os.path.join(self.config.output_dir, "preprocessing_summary.json")

        def _safe_to_csv(df_to_save: pd.DataFrame, target_path: str, **kwargs):
            try:
                df_to_save.to_csv(target_path, **kwargs)
                saved_files.append(target_path)
            except PermissionError:
                pass  # Silently skip if locked by Excel/another program

        if save_to_disk:
            _safe_to_csv(clean_price_df, clean_price_path, date_format="%Y-%m-%d")

        # 7. Step 3.1: Log Return Feature Extraction (ENABLED)
        return_results = None
        returns_df = None
        if do_calc_returns:
            if ret_type == "log":
                returns_df = np.log(clean_price_df / clean_price_df.shift(1)).dropna(how="all")
            else:
                returns_df = ((clean_price_df - clean_price_df.shift(1)) / clean_price_df.shift(1)).dropna(how="all")

            return_stats_list = []
            for sym in kept_symbols:
                r = returns_df[sym].dropna()
                mean_daily = float(r.mean())
                std_daily = float(r.std())
                ann_return = mean_daily * 252.0
                ann_vol = std_daily * np.sqrt(252.0)
                sharpe = (ann_return - self.config.risk_free_rate_annual) / ann_vol if ann_vol > 0 else 0.0

                return_stats_list.append({
                    "symbol": sym,
                    "mean_daily_return": round(mean_daily * 100, 4),
                    "annualized_return": round(ann_return * 100, 2),
                    "annualized_volatility": round(ann_vol * 100, 2),
                    "sharpe_ratio": round(sharpe, 3),
                    "skewness": round(float(r.skew()), 3),
                    "kurtosis": round(float(r.kurtosis()), 3),
                    "min_return": round(float(r.min()) * 100, 2),
                    "max_return": round(float(r.max()) * 100, 2),
                })

            flat_returns = returns_df.values.flatten()
            flat_returns = flat_returns[~np.isnan(flat_returns)]
            hist_counts, bin_edges = np.histogram(flat_returns * 100, bins=40, range=(-7, 7))

            return_hist_data = {
                "bins": [round(float(b), 2) for b in bin_edges[:-1]],
                "counts": [int(c) for c in hist_counts]
            }

            if save_to_disk:
                returns_path = os.path.join(self.config.output_dir, f"{ret_type}_returns.csv")
                stats_csv_path = os.path.join(self.config.output_dir, "stock_financial_features.csv")
                _safe_to_csv(returns_df, returns_path, date_format="%Y-%m-%d")
                _safe_to_csv(pd.DataFrame(return_stats_list), stats_csv_path, index=False)

            return_results = {
                "return_type": ret_type,
                "total_return_sessions": len(returns_df),
                "return_statistics": return_stats_list,
                "return_histogram": return_hist_data,
                "mean_market_annual_return": round(float(np.mean([s["annualized_return"] for s in return_stats_list])), 2),
                "mean_market_annual_volatility": round(float(np.mean([s["annualized_volatility"] for s in return_stats_list])), 2),
                "mean_market_sharpe": round(float(np.mean([s["sharpe_ratio"] for s in return_stats_list])), 3),
                "sample_returns_head": {
                    "dates": returns_df.index[:5].strftime("%Y-%m-%d").tolist(),
                    "symbols": kept_symbols[:10],
                    "rows": (returns_df.iloc[:5, :10] * 100).round(2).values.tolist()
                }
            }

        # 8. Step 3.2: Relational Modeling (Correlation & Mantegna Distance) (DISABLED by default)
        relation_results = None
        if do_calc_relations and returns_df is not None:
            corr_matrix = returns_df.corr(method="pearson").clip(-1.0, 1.0)
            dist_values = np.sqrt(np.maximum(0.0, 2.0 * (1.0 - corr_matrix.to_numpy(copy=True))))
            np.fill_diagonal(dist_values, 0.0)
            dist_matrix = pd.DataFrame(dist_values, index=corr_matrix.index, columns=corr_matrix.columns)

            triu_indices = np.triu_indices_from(corr_matrix.values, k=1)
            pairwise_corrs = corr_matrix.values[triu_indices]
            pairwise_dists = dist_matrix.values[triu_indices]

            pairs = []
            for i in range(len(kept_symbols)):
                for j in range(i + 1, len(kept_symbols)):
                    pairs.append({
                        "stock1": kept_symbols[i],
                        "stock2": kept_symbols[j],
                        "correlation": round(float(corr_matrix.iloc[i, j]), 4),
                        "mantegna_distance": round(float(dist_matrix.iloc[i, j]), 4)
                    })
            pairs_sorted = sorted(pairs, key=lambda x: x["correlation"], reverse=True)
            dist_hist_counts, dist_bin_edges = np.histogram(pairwise_dists, bins=30, range=(0, 2))

            if save_to_disk:
                corr_path = os.path.join(self.config.output_dir, "correlation_matrix.csv")
                dist_path = os.path.join(self.config.output_dir, "mantegna_distance_matrix.csv")
                _safe_to_csv(corr_matrix, corr_path)
                _safe_to_csv(dist_matrix, dist_path)

            relation_results = {
                "top_correlated_pairs": pairs_sorted[:10],
                "bottom_correlated_pairs": pairs_sorted[-10:],
                "distance_histogram": {
                    "bins": [round(float(b), 2) for b in dist_bin_edges[:-1]],
                    "counts": [int(c) for c in dist_hist_counts]
                },
                "mean_pairwise_correlation": round(float(np.mean(pairwise_corrs)), 4),
                "mean_mantegna_distance": round(float(np.mean(pairwise_dists)), 4)
            }

        if save_to_disk:
            saved_files.append(summary_path)

        # 9. Build Before vs After Comparison Report
        comparison = {
            "before": {
                "total_stocks": audit_res["total_stocks"],
                "total_calendar_days": audit_res["all_unique_dates_count"],
                "max_sessions": audit_res["max_sessions"],
                "missing_values_count": raw_null_count,
                "holiday_sessions_with_zero_vol": len(all_holidays_set)
            },
            "after": {
                "kept_stocks_count": len(kept_symbols),
                "excluded_stocks_count": len(excluded_symbols),
                "total_price_sessions": len(clean_price_df),
                "total_return_sessions": len(returns_df) if returns_df is not None else 0,
                "missing_values_count": post_null_count,
                "imputed_cells_count": raw_null_count,
                "saved_files": saved_files
            }
        }

        result = {
            "config": {
                "min_coverage_ratio": min_cov,
                "filter_holidays": do_filter_holidays,
                "holiday_zero_vol_ratio": hol_ratio,
                "imputation_method": impute_meth,
                "calc_returns": do_calc_returns,
                "calc_relations": do_calc_relations,
                "return_type": ret_type
            },
            "comparison": comparison,
            "excluded_stocks": excluded_symbols,
            "stock_coverage_summary": list(stock_coverage.values()),
            "detected_holidays": audit_res["detected_holidays"],
            "imputed_stocks_detail": imputed_stocks_detail,
            "price_statistics": price_stats_list,
            "coverage_histogram": coverage_histogram,
            "returns_data": return_results,
            "relations_data": relation_results
        }

        if save_to_disk:
            try:
                with open(summary_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
            except PermissionError:
                pass

        return result


if __name__ == "__main__":
    preprocessor = StockPreprocessor()
    res = preprocessor.run_pipeline(calc_returns=True, calc_relations=False)
    print("Pipeline executed successfully (Log Return Feature Extraction Enabled)!")
    print(f"Stocks kept: {res['comparison']['after']['kept_stocks_count']} / {res['comparison']['before']['total_stocks']}")
    print(f"Price sessions: {res['comparison']['after']['total_price_sessions']}")
    print(f"Return sessions: {res['comparison']['after']['total_return_sessions']}")
    print(f"Returns calculated: {res['returns_data'] is not None}")
    print(f"Relations calculated: {res['relations_data'] is not None}")
