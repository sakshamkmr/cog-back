# from fastapi import APIRouter
# from pydantic import BaseModel
# from typing import List

# router = APIRouter()

# class SKUItem(BaseModel):
#     sku: str
#     forecastDemand: int
#     actualDemand: int
#     stock: int

# class InventoryRequest(BaseModel):
#     skuData: List[SKUItem]
#     capacity: int

# @router.post("/optimize-inventory")
# def optimize_inventory(request: InventoryRequest):
#     skuData = request.skuData
#     capacity = request.capacity

#     allocationPlan = []
#     shortages = []
#     excess = []

#     # Step 1: Effective demand = min(forecast, actual)
#     effective_demand = {sku.sku: min(sku.forecastDemand, sku.actualDemand) for sku in skuData}

#     # Step 2: Totals
#     total_demand = sum(effective_demand.values())
#     total_stock = sum([sku.stock for sku in skuData])
#     distributable_stock = min(total_stock, capacity)  # enforce capacity limit

#     # Step 3: Proportional allocation
#     provisional_allocations = {}
#     for sku in skuData:
#         demand = effective_demand[sku.sku]
#         weight = demand / total_demand if total_demand > 0 else 0
#         provisional_allocations[sku.sku] = weight * distributable_stock

#     # Step 4: Final allocation (respect stock & demand limits)
#     for sku in skuData:
#         demand = effective_demand[sku.sku]
#         alloc = int(round(min(sku.stock, demand, provisional_allocations[sku.sku])))
#         allocationPlan.append({"sku": sku.sku, "allocated": alloc})

#         # shortages if allocation < demand
#         if alloc < demand:
#             shortages.append({"sku": sku.sku, "shortage": demand - alloc})

#         # excess if stock not used
#         if alloc < sku.stock:
#             excess.append({"sku": sku.sku, "excess": sku.stock - alloc})

#     return {
#         "allocationPlan": allocationPlan,
#         "shortages": shortages,
#         "excess": excess
#     }
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
