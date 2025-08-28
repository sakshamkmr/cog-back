from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

from app.services.analyzer import analyze_inventory
from app.services.optimizer import optimize_inventory

router = APIRouter()

# -------------------- MODELS -------------------- #
class SKU(BaseModel):
    sku: str
    forecastDemand: int
    actualDemand: int
    stock: int

class InventoryRequest(BaseModel):
    skuData: List[SKU]
    capacity: int


# -------------------- ROUTES -------------------- #

@router.post("/analyze-inventory")
def analyze_inventory_route(req: InventoryRequest):
    """Analyze inventory before running optimizer"""
    return analyze_inventory(req.skuData)


@router.post("/optimize-inventory")
def run_inventory_optimizer(req: InventoryRequest):
    """Run inventory optimization"""
    return optimize_inventory(req.skuData, req.capacity)
