import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.job_service import JobService

def test_job_service():
    job_id = JobService.create_job()
    print("Created job:", job_id)
    
    job = JobService.get_job(job_id)
    assert job["status"] == "queued"
    
    JobService.update_job(job_id, status="processing", progress=10, current_step="Validating data...")
    job = JobService.get_job(job_id)
    assert job["status"] == "processing"
    assert job["progress"] == 10
    
    JobService.update_job(job_id, status="done", progress=100, current_step="Finished.")
    job = JobService.get_job(job_id)
    assert job["status"] == "done"
    assert job["progress"] == 100
    
    print("Job service working perfectly!")

if __name__ == "__main__":
    test_job_service()
