"""Interactive Feature Extraction & Relational Modeling Studio (Web Application).

Auxiliary interactive system external to the core Machine Learning pipeline.
Provides a web dashboard for:
1. Auditing raw VN100 data quality.
2. Executing the data cleaning and feature extraction pipeline on demand.
3. Exploring pairwise correlation and Mantegna metric distance distributions.
4. Inspecting sector leaders via interactive Canvas Heatmap.

To run:
    py -3.12 web_app/main.py

Dashboard will be accessible at:
    http://127.0.0.1:8000
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

try:
    from web_app.preprocessing import PreprocessingConfig, StockPreprocessor
except ImportError:
    from preprocessing import PreprocessingConfig, StockPreprocessor

app = FastAPI(
    title="VN100 Stock Feature Extraction & Mantegna Studio",
    version="1.2.0",
    description="Interactive Web Studio for Exploratory Analysis and Relational Modeling"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

preprocessor = StockPreprocessor(PreprocessingConfig(
    raw_dir=str(PROJECT_ROOT / "data" / "raw"),
    metadata_path=str(PROJECT_ROOT / "data" / "metadata" / "vn100_symbols.csv"),
    output_dir=str(PROJECT_ROOT / "data" / "processed"),
    calc_returns=True,
    calc_relations=True
))

INDEX_HTML_PATH = Path(__file__).resolve().parent / "templates" / "index.html"


class PipelineParams(BaseModel):
    min_coverage_pct: float = 90.0
    filter_holidays: bool = True
    holiday_zero_vol_ratio: float = 0.50
    imputation_method: str = "ffill"
    calc_returns: bool = True
    calc_relations: bool = True
    return_type: str = "log"
    save_to_disk: bool = True


@app.get("/", response_class=FileResponse)
async def serve_index(request: Request):
    """Serve the interactive HTML dashboard."""
    if not INDEX_HTML_PATH.exists():
        return JSONResponse(status_code=404, content={"status": "error", "message": "index.html not found"})
    return FileResponse(INDEX_HTML_PATH)


@app.get("/api/audit")
async def get_audit():
    """Get raw data audit statistics before preprocessing."""
    try:
        audit_data = preprocessor.audit_raw_data()
        return JSONResponse(content={"status": "success", "data": audit_data})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.post("/api/process")
async def run_processing(params: PipelineParams):
    """Execute preprocessing and relational modeling pipeline."""
    try:
        result = preprocessor.run_pipeline(
            min_coverage_ratio=params.min_coverage_pct / 100.0,
            filter_holidays=params.filter_holidays,
            holiday_zero_vol_ratio=params.holiday_zero_vol_ratio,
            imputation_method=params.imputation_method,
            calc_returns=params.calc_returns,
            calc_relations=params.calc_relations,
            return_type=params.return_type,
            save_to_disk=params.save_to_disk
        )
        return JSONResponse(content={"status": "success", "data": result})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.get("/api/heatmap_sample")
async def get_heatmap_sample():
    """Return correlation and Mantegna distance submatrices for 15 prominent stocks."""
    try:
        corr_path = PROJECT_ROOT / "data" / "processed" / "correlation_matrix.csv"
        dist_path = PROJECT_ROOT / "data" / "processed" / "mantegna_distance_matrix.csv"
        if not corr_path.exists() or not dist_path.exists():
            return JSONResponse(status_code=404, content={"status": "error", "message": "Matrices not computed yet"})

        sample_symbols = ["VCB", "BID", "CTG", "MBB", "HPG", "HSG", "VHM", "VIC", "NVL", "MWG", "FRT", "FPT", "GAS", "PLX", "MSN"]

        df_corr = pd.read_csv(corr_path, index_col=0)
        df_dist = pd.read_csv(dist_path, index_col=0)

        avail = [s for s in sample_symbols if s in df_corr.columns and s in df_dist.columns]
        sub_corr = df_corr.loc[avail, avail]
        sub_dist = df_dist.loc[avail, avail]

        return JSONResponse(content={
            "status": "success",
            "symbols": avail,
            "correlation": sub_corr.round(3).values.tolist(),
            "mantegna_distance": sub_dist.round(3).values.tolist()
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    port = 8000
    host = "127.0.0.1"
    url = f"http://{host}:{port}"
    print("=" * 70)
    print(" VN100 STOCK FEATURE EXTRACTION & MANTEGNA RELATIONAL STUDIO")
    print(" [Web Application - Auxiliary Interactive System]")
    print("=" * 70)
    print(f" Dashboard running at: {url}")
    print(" Press Ctrl+C to stop.")
    print("=" * 70)
    uvicorn.run(app, host=host, port=port, log_level="warning")


if __name__ == "__main__":
    main()
