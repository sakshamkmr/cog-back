from fastapi import FastAPI
from app.routers import load_balancer, inventory_optimizer
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Smart Supply Chain Optimizer")

# CORS (for frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in prod: put frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(load_balancer.router, prefix="/api")
app.include_router(inventory_optimizer.router, prefix="/api")
