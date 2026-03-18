import asyncio
from typing import Dict, Optional
from datetime import datetime

_jobs: Dict[str, dict] = {}

def create_job(job_id: str) -> dict:
    job = {
        "job_id"      : job_id,
        "status"      : "queued",
        "progress"    : 0,
        "current_step": "Queued...",
        "error"       : None,
        "created_at"  : datetime.utcnow().isoformat()
    }
    _jobs[job_id] = job
    return job

async def update_job(job_id: str, progress: int,
                     current_step: str, status: str = "processing",
                     error: str = None):
    if job_id in _jobs:
        _jobs[job_id]["status"]       = status
        _jobs[job_id]["progress"]     = progress
        _jobs[job_id]["current_step"] = current_step
        _jobs[job_id]["error"]        = error
    await asyncio.sleep(0)

def get_job(job_id: str) -> Optional[dict]:
    return _jobs.get(job_id)

def get_all_jobs() -> list:
    return list(_jobs.values())
