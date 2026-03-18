import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_dashboard():
    print("Testing /dashboard/kpi...")
    response = client.get("/dashboard/kpi")
    assert response.status_code == 200, response.text
    print("KPI keys:", response.json().keys())

    print("Testing /dashboard/forecasts...")
    response = client.get("/dashboard/forecasts?page=1&page_size=3")
    assert response.status_code == 200, response.text
    print("Forecasts returned total:", response.json()["total"])

    print("Testing /dashboard/models...")
    response = client.get("/dashboard/models")
    assert response.status_code == 200, response.text
    print("Models count:", len(response.json()))

    print("Testing /dashboard/inventory...")
    response = client.get("/dashboard/inventory")
    assert response.status_code == 200, response.text
    print("Inventory keys:", response.json().keys())

    print("Testing /dashboard/sku-list...")
    response = client.get("/dashboard/sku-list")
    assert response.status_code == 200, response.text
    print("SKU list count:", len(response.json()))
    skus = response.json()
    if skus:
        sku_id = str(skus[0].get("SKU_ID"))
        print(f"Testing /dashboard/sku/{sku_id}...")
        response = client.get(f"/dashboard/sku/{sku_id}")
        assert response.status_code == 200, response.text
        print("SKU details keys:", response.json().keys())

    print("Testing /dashboard/waterfall...")
    response = client.get("/dashboard/waterfall")
    assert response.status_code == 200, response.text

    print("ALL API ENDPOINTS PASSED!")

if __name__ == "__main__":
    test_dashboard()
