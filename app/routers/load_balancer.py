
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import google.generativeai as genai
from typing import Any, Dict

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

class AIInsightRequest(BaseModel):
    question: str
    analysis_data: Dict[str, Any]
    optimization_data: Dict[str, Any]



# -------------------- ROUTES -------------------- #

@router.post("/analyze-orders")
def analyze_load_balancer(req: LoadBalancerRequest):
    """Analyze orders before running optimizer"""
    return analyze_orders([order.dict() for order in req.orders], req.stations)


@router.post("/assign-orders")
def run_load_balancer(req: LoadBalancerRequest):
    """Run load balancing optimization"""
    return optimize_orders([order.dict() for order in req.orders], req.stations)

@router.post("/load-balancer-insights")
def get_ai_insights(req: AIInsightRequest):
    """Get AI-powered insights for load balancing"""
    
    # It's best to set your API key as an environment variable
    # For local testing you can hardcode it, but change it later
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    
    model = genai.GenerativeModel('gemini-pro')

    prompt = f"""
    You are a supply chain analyst. Based on the following data, please answer the user's question.
    
    User Question: {req.question}
    
    Initial Analysis Data (before optimization):
    {req.analysis_data}
    
    Optimized Results Data:
    {req.optimization_data}
    
    Please provide a concise and helpful answer.
    """
    
    response = model.generate_content(prompt)
    
    return {"insight": response.text}