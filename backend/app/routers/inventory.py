import numpy as np
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class InventoryRequest(BaseModel):
    sku_id              : str
    warehouse_id        : str
    avg_daily_demand    : float
    std_daily_demand    : float
    avg_lead_time       : float
    std_lead_time       : Optional[float] = 1.5
    avg_unit_cost       : float
    service_level       : Optional[float] = 0.95
    ordering_cost       : Optional[float] = 50.0
    holding_rate        : Optional[float] = 0.25


@router.post("/inventory/policy")
def inventory_policy(req: InventoryRequest):
    Z      = 1.645 if req.service_level >= 0.95 else 1.28
    ss     = Z * np.sqrt(
        req.avg_lead_time * req.std_daily_demand**2 +
        req.avg_daily_demand**2 * req.std_lead_time**2
    )
    rop    = req.avg_daily_demand * req.avg_lead_time + ss
    annual = req.avg_daily_demand * 365
    eoq    = np.sqrt(
        2 * annual * req.ordering_cost /
        max(req.avg_unit_cost * req.holding_rate, 0.01)
    )
    return {
        "sku_id"          : req.sku_id,
        "warehouse_id"    : req.warehouse_id,
        "safety_stock"    : round(float(max(0, ss)),  2),
        "rop"             : round(float(max(0, rop)), 2),
        "eoq"             : round(float(max(1, eoq)), 0),
        "annual_demand"   : round(annual, 1),
        "service_level"   : req.service_level,
    }
