import os, json
import numpy as np
import joblib
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict

router = APIRouter()

_HERE       = os.path.dirname(os.path.abspath(__file__))
_ROOT       = os.path.abspath(os.path.join(_HERE, "../../.."))
MODELS_DIR  = os.path.join(_ROOT, "models")
OUTPUTS_DIR = os.path.join(_ROOT, "outputs")

# Load models once at startup
_xgb_model    = None
_meta_model   = None
_meta_scaler  = None
_registry     = None

def _load():
    global _xgb_model, _meta_model, _meta_scaler, _registry
    if _xgb_model is None:
        _xgb_model   = joblib.load(os.path.join(MODELS_DIR, "xgb_final_model.pkl"))
        _meta_model  = joblib.load(os.path.join(MODELS_DIR, "hybrid_meta_model.pkl"))
        _meta_scaler = joblib.load(os.path.join(MODELS_DIR, "hybrid_meta_scaler.pkl"))
        with open(os.path.join(OUTPUTS_DIR, "feature_registry.json")) as f:
            _registry = json.load(f)


class SingleForecastRequest(BaseModel):
    sku_id       : str
    warehouse_id : str
    features     : Dict[str, float]
    blend_strategy: Optional[str] = "meta"


@router.post("/predict/single")
def predict_single(req: SingleForecastRequest):
    _load()
    registry     = _registry
    XGB_FEATURES = registry["xgboost_features"]

    # Build feature vector in registry order
    feat_vec = np.array(
        [req.features.get(f.lower(), req.features.get(f, 0.0)) for f in XGB_FEATURES],
        dtype=np.float32
    ).reshape(1, -1)

    xgb_pred = float(np.clip(_xgb_model.predict(feat_vec)[0], 0, None))

    # LSTM not available for single inference — use XGB as LSTM proxy
    lstm_pred = xgb_pred

    # Blend
    if req.blend_strategy == "simple":
        hybrid = (xgb_pred + lstm_pred) / 2
    elif req.blend_strategy == "weighted":
        hybrid = 0.3 * lstm_pred + 0.7 * xgb_pred
    else:  # meta (default)
        meta_in = _meta_scaler.transform([[lstm_pred, xgb_pred]])
        hybrid  = float(np.clip(_meta_model.predict(meta_in)[0], 0, None))

    return {
        "sku_id"            : req.sku_id,
        "warehouse_id"      : req.warehouse_id,
        "xgb_prediction"    : round(xgb_pred, 4),
        "lstm_prediction"   : round(lstm_pred, 4),
        "hybrid_prediction" : round(hybrid, 4),
        "blend_strategy"    : req.blend_strategy,
    }


@router.get("/predict/features")
def get_features():
    _load()
    return {
        "xgboost_features" : _registry["xgboost_features"],
        "lstm_features"    : _registry["lstm_features"],
        "target"           : _registry.get("target", "Units_Sold"),
    }
