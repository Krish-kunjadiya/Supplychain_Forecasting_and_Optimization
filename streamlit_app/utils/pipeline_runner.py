import asyncio
import sys
import os

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, _ROOT)

from backend.app.services.pipeline_service import run_pipeline
from backend.app.services.job_service import create_job, get_job

def run_pipeline_sync(csv_path: str, job_id: str):
	"""
	Run the ML pipeline synchronously.
	Streamlit runs in a single thread — no event loop needed.
	"""
	create_job(job_id)
	asyncio.run(run_pipeline(csv_path, job_id))
	return get_job(job_id)
