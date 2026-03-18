from pydantic import BaseModel
from typing import Optional, Literal

class JobStatus(BaseModel):
    job_id: str
    status: Literal["queued", "processing", "done", "failed"]
    progress: int          # 0-100
    current_step: str
    error: Optional[str] = None

class PipelineResult(BaseModel):
    job_id: str
    created_at: str
    row_count: int
    sku_count: int
    hybrid_mape: Optional[float] = None
