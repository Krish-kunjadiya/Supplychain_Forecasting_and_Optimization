import os, uuid, asyncio, json
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import shutil

from backend.app.services.job_service import create_job, get_job, get_all_jobs
from backend.app.services.pipeline_service import run_pipeline

router = APIRouter()
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "../../.."))
UPLOADS_DIR = os.path.join(_ROOT, "uploads")


def _job_path(job_id: str, filename: str) -> str:
    return os.path.join(UPLOADS_DIR, job_id, filename)


def _require_file(job_id: str, filename: str) -> str:
    path = _job_path(job_id, filename)
    if not os.path.exists(path):
        raise HTTPException(404, f"{filename} not found for job {job_id}. "
                                  "Job may still be processing.")
    return path


def _run_sync(csv_path: str, job_id: str):
    """Wrapper so BackgroundTasks (sync thread) can call async pipeline."""
    asyncio.run(run_pipeline(csv_path, job_id))


@router.post("/pipeline/upload")
async def upload_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Only CSV files are accepted.")

    job_id = str(uuid.uuid4())
    job_dir = os.path.join(UPLOADS_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    csv_path = os.path.join(job_dir, "input.csv")
    with open(csv_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    create_job(job_id)
    background_tasks.add_task(_run_sync, csv_path, job_id)

    return {"job_id": job_id, "status": "queued"}


@router.get("/pipeline/job/{job_id}")
def job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, f"Job {job_id} not found.")
    return job


@router.get("/pipeline/jobs")
def all_jobs():
    return get_all_jobs()


@router.get("/pipeline/results/{job_id}/kpi")
def result_kpi(job_id: str):
    path = _require_file(job_id, "business_value.json")
    with open(path) as f:
        return json.load(f)


@router.get("/pipeline/results/{job_id}/forecasts")
def result_forecasts(job_id: str, sku_id: str = None, limit: int = 500):
    path = _require_file(job_id, "hybrid_predictions.csv")
    df = pd.read_csv(path, parse_dates=["Date"])
    if sku_id:
        df = df[df["SKU_ID"] == sku_id]
    df = df.head(limit)
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
    return df.to_dict(orient="records")


@router.get("/pipeline/results/{job_id}/inventory")
def result_inventory(job_id: str):
    path = _require_file(job_id, "inventory_policy.csv")
    df = pd.read_csv(path)
    return df.to_dict(orient="records")


@router.get("/pipeline/results/{job_id}/sku-list")
def result_sku_list(job_id: str):
    path = _require_file(job_id, "hybrid_predictions.csv")
    df = pd.read_csv(path)
    skus = df["SKU_ID"].unique().tolist()
    return {"sku_ids": sorted(skus)}


@router.get("/pipeline/results/{job_id}/sku/{sku_id}")
def result_sku(job_id: str, sku_id: str):
    path = _require_file(job_id, "hybrid_predictions.csv")
    df = pd.read_csv(path, parse_dates=["Date"])
    grp = df[df["SKU_ID"] == sku_id]
    if grp.empty:
        raise HTTPException(404, f"SKU {sku_id} not found in job {job_id}.")
    y_true = grp["Units_Sold"].values
    y_hybrid = grp["Hybrid_Pred"].values
    mask = y_true > 0
    mape = float((abs(y_true[mask] - y_hybrid[mask]) / y_true[mask]).mean() * 100) if mask.sum() > 0 else 0.0
    mae = float(abs(y_true - y_hybrid).mean())
    grp = grp.copy()
    grp["Date"] = grp["Date"].dt.strftime("%Y-%m-%d")
    return {
        "sku_id": sku_id,
        "mape": round(mape, 4),
        "mae": round(mae, 4),
        "row_count": len(grp),
        "forecasts": grp.to_dict(orient="records")
    }
