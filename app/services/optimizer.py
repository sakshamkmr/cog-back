import numpy as np

# ----------- LOAD BALANCER OPTIMIZER ----------- #
import numpy as np

def optimize_orders(orders, stations: int):
    """
    LPT (Longest Processing Time first) load balancing algorithm.
    Assign orders to stations by sorting jobs descending and
    always giving next largest job to least loaded station.
    """
    # Sort orders by packingTime (largest first)
    sorted_orders = sorted(orders, key=lambda x: x["packingTime"], reverse=True)

    station_loads = [0] * stations
    assignments = []

    for order in sorted_orders:
        # Find the station with minimum load
        min_station = int(np.argmin(station_loads))
        station_loads[min_station] += order["packingTime"]
        assignments.append({
            "orderId": order["id"],
            "station": min_station + 1
        })

    station_summary = [
        {"station": i+1, "totalTime": station_loads[i]} 
        for i in range(stations)
    ]

    imbalance = round(
        (max(station_loads) - min(station_loads)) / (sum(station_loads)/stations) * 100,
        2
    )

    return {
        "assignments": assignments,
        "stationLoadSummary": station_summary,
        "imbalancePercent": imbalance,
        "insight": f"LPT scheduling reduced load imbalance to {imbalance}%."
    }



# ----------- INVENTORY OPTIMIZER ----------- #
import pulp

def optimize_inventory(skuData, capacity: int):
    """
    Optimizes inventory allocation using a weighted linear programming model.
    Each SKU has a priority weight (default = 1 if not provided).
    Higher weight => more important to meet demand.
    """
    # 1. Create the model
    model = pulp.LpProblem("Inventory_Optimization", pulp.LpMinimize)

    # 2. Define Decision Variables
    alloc_vars = {
        sku.sku: pulp.LpVariable(f"alloc_{sku.sku}", lowBound=0, cat='Integer')
        for sku in skuData
    }

    # 3. Define Effective Demand and Weights
    effective_demand = {sku.sku: min(sku.forecastDemand, sku.actualDemand) for sku in skuData}
    weights = {sku.sku: getattr(sku, "priority", 1) for sku in skuData}  
    # if sku has no priority field, defaults to 1

    # 4. Define Weighted Objective Function
    model += pulp.lpSum(
        [weights[sku.sku] * (effective_demand[sku.sku] - alloc_vars[sku.sku]) for sku in skuData]
    ), "Weighted_Shortage"

    # 5. Constraints
    model += pulp.lpSum([alloc_vars[sku.sku] for sku in skuData]) <= capacity
    for sku in skuData:
        model += alloc_vars[sku.sku] <= sku.stock
        model += alloc_vars[sku.sku] <= effective_demand[sku.sku]

    # 6. Solve the model
    model.solve()

    if model.status != pulp.LpStatusOptimal:
        return {
            "allocationPlan": [],
            "shortages": [],
            "excess": [],
            "status": pulp.LpStatus[model.status]
        }

    # 7. Extract Results
    allocationPlan = []
    shortages = []
    excess = []

    for sku in skuData:
        allocated_val = int(alloc_vars[sku.sku].varValue)
        allocationPlan.append({
            "sku": sku.sku,
            "allocated": allocated_val,
            "priority": weights[sku.sku]
        })

        demand = effective_demand[sku.sku]
        if allocated_val < demand:
            shortages.append({
                "sku": sku.sku,
                "shortage": demand - allocated_val,
                "priority": weights[sku.sku]
            })

        if allocated_val < sku.stock:
            excess.append({
                "sku": sku.sku,
                "excess": sku.stock - allocated_val
            })

    return {
        "allocationPlan": allocationPlan,
        "shortages": shortages,
        "excess": excess,
        "status": pulp.LpStatus[model.status]
    }
