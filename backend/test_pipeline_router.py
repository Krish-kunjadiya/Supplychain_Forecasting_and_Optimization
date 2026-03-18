import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_pipeline():
    print("Testing /pipeline/upload...")
    with open("dummy.csv", "w") as f:
        f.write("test_col\n1\n2\n")
    
    with open("dummy.csv", "rb") as f:
        response = client.post("/pipeline/upload", files={"file": ("dummy.csv", f, "text/csv")})
    
    assert response.status_code == 200, response.text
    data = response.json()
    job_id = data["job_id"]
    print("Upload returned job_id:", job_id)

    print("Polling /pipeline/job/{job_id}...")
    response = client.get(f"/pipeline/job/{job_id}")
    assert response.status_code == 200, response.text
    print("Job status:", response.json()["status"])

    print("Testing /pipeline/results/{job_id}/kpi...")
    response = client.get(f"/pipeline/results/{job_id}/kpi")
    assert response.status_code == 200, response.text
    print("ALL PIPELINE ENDPOINTS PASSED!")

if __name__ == "__main__":
    test_pipeline()
