import os
import json
import pandas as pd
import math

# Absolute paths — works regardless of where uvicorn is launched from
_HERE       = os.path.dirname(os.path.abspath(__file__))          # .../backend/app/services/
_ROOT       = os.path.abspath(os.path.join(_HERE, "../../..")) # project root
OUTPUTS_DIR = os.path.join(_ROOT, "outputs")
MODELS_DIR  = os.path.join(_ROOT, "models")
UPLOADS_DIR = os.path.join(_ROOT, "uploads")

def _clean_nans(obj):
    if isinstance(obj, float) and math.isnan(obj):
        return None
    elif isinstance(obj, dict):
        return {k: _clean_nans(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_clean_nans(v) for v in obj]
    return obj

def _safe_read_csv(filename: str):
    filepath = os.path.join(OUTPUTS_DIR, filename)
    if not os.path.exists(filepath):
        return []
    try:
        df = pd.read_csv(filepath)
        records = df.where(pd.notnull(df), None).to_dict(orient="records")
        return _clean_nans(records)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return []

def _safe_read_json(filename: str):
    filepath = os.path.join(OUTPUTS_DIR, filename)
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return {}

class DataService:
    @staticmethod
    def get_kpi():
        return {
            "business_value": _safe_read_json("business_value.json"),
            "hybrid_metrics": _safe_read_json("hybrid_metrics.json")
        }

    @staticmethod
    def get_forecasts(sku_id: str = None, page: int = 1, page_size: int = 50):
        filepath = os.path.join(OUTPUTS_DIR, "hybrid_predictions.csv")
        if not os.path.exists(filepath):
            return {"data": [], "total": 0, "page": page, "page_size": page_size, "total_pages": 0}
        
        df = pd.read_csv(filepath)
        if sku_id:
            df = df[df["SKU_ID"] == sku_id]
            
        total = len(df)
        start = (page - 1) * page_size
        end = start + page_size
        
        paginated = df.iloc[start:end]
        records = paginated.where(pd.notnull(paginated), None).to_dict(orient="records")
        return {
            "data": _clean_nans(records),
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if page_size else 0
        }

    @staticmethod
    def get_models():
        return _safe_read_csv("all_model_comparison.csv")

    @staticmethod
    def get_inventory():
        return {
            "policy_comparison": _safe_read_csv("policy_comparison.csv"),
            "simulation_results": _safe_read_csv("simulation_results.csv"),
            "inventory_policy": _safe_read_csv("inventory_policy.csv")
        }

    @staticmethod
    def get_sku_list():
        filepath = os.path.join(OUTPUTS_DIR, "hybrid_predictions.csv")
        if not os.path.exists(filepath):
            return []
        df = pd.read_csv(filepath, usecols=["SKU_ID", "Warehouse_ID"])
        records = df.drop_duplicates().to_dict(orient="records")
        return _clean_nans(records)

    @staticmethod
    def get_sku_details(sku_id: str):
        lstm_perf = _safe_read_csv("lstm_sku_performance.csv")
        xgb_perf = _safe_read_csv("xgb_sku_performance.csv")
        dyn_weights = _safe_read_csv("sku_dynamic_weights.csv")
        
        lstm_sku = next((item for item in lstm_perf if str(item.get("SKU_ID")) == str(sku_id)), None)
        xgb_sku = next((item for item in xgb_perf if str(item.get("SKU_ID")) == str(sku_id)), None)
        weights = next((item for item in dyn_weights if str(item.get("SKU_ID")) == str(sku_id)), None)
        
        return {
            "sku_id": sku_id,
            "lstm_performance": lstm_sku,
            "xgb_performance": xgb_sku,
            "dynamic_weights": weights
        }

    @staticmethod
    def get_waterfall():
        return _safe_read_json("business_value.json")

    @staticmethod
    def get_raw_csv(filename: str):
        return _safe_read_csv(filename)
