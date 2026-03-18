from fastapi import APIRouter, Query
from typing import Optional
from backend.app.services.data_service import DataService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/kpi")
async def get_dashboard_kpi():
    return DataService.get_kpi()

@router.get("/forecasts")
async def get_dashboard_forecasts(
    sku_id: Optional[str] = Query(None, description="Filter by SKU ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=1000)
):
    return DataService.get_forecasts(sku_id, page, page_size)

@router.get("/models")
async def get_dashboard_models():
    return DataService.get_models()

@router.get("/inventory")
async def get_dashboard_inventory():
    return DataService.get_inventory()

@router.get("/sku-list")
async def get_dashboard_sku_list():
    return DataService.get_sku_list()

@router.get("/sku/{sku_id}")
async def get_dashboard_sku_details(sku_id: str):
    return DataService.get_sku_details(sku_id)

@router.get("/waterfall")
async def get_dashboard_waterfall():
    return DataService.get_waterfall()
