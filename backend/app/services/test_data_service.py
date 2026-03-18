import sys
from pathlib import Path

# Add project root to sys.path so imports work
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from backend.app.services.data_service import DataService

def test_data_service():
    print("Testing get_kpi...")
    kpi = DataService.get_kpi()
    assert "business_value" in kpi
    print("KPI keys:", kpi.keys())

    print("Testing get_forecasts...")
    forecasts = DataService.get_forecasts(page=1, page_size=5)
    print("Forecasts returned total:", forecasts["total"], "len(data):", len(forecasts["data"]))

    print("Testing get_models...")
    models = DataService.get_models()
    print("Models count:", len(models))

    print("Testing get_inventory...")
    inventory = DataService.get_inventory()
    print("Inventory keys:", inventory.keys())

    print("Testing get_sku_list...")
    skus = DataService.get_sku_list()
    print("SKUs count:", len(skus))
    if skus:
        first_sku = str(skus[0].get("SKU_ID"))
        print(f"Testing get_sku_details for {first_sku}...")
        details = DataService.get_sku_details(first_sku)
        print("Details keys:", details.keys())

    print("Testing get_waterfall...")
    waterfall = DataService.get_waterfall()
    print("Waterfall data read.")

    print("ALL TESTS PASSED!")

if __name__ == "__main__":
    test_data_service()
