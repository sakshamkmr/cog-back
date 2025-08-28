from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

from app.services.analyzer import analyze_orders
from app.services.optimizer import optimize_orders

router = APIRouter()

# -------------------- MODELS -------------------- #
class Order(BaseModel):
    id: int
    packingTime: int

class LoadBalancerRequest(BaseModel):
    orders: List[Order]
    stations: int


# -------------------- ROUTES -------------------- #

@router.post("/analyze-orders")
def analyze_load_balancer(req: LoadBalancerRequest):
    """Analyze orders before running optimizer"""
    return analyze_orders([order.dict() for order in req.orders], req.stations)


@router.post("/assign-orders")
def run_load_balancer(req: LoadBalancerRequest):
    """Run load balancing optimization"""
    return optimize_orders([order.dict() for order in req.orders], req.stations)
