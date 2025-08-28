# app/services/optimizer.py
import numpy as np

# ----------- LOAD BALANCER OPTIMIZER ----------- #
def optimize_orders(orders, stations: int):
    """
    Simple greedy load balancing algorithm.
    Assign orders to stations to balance total load.
    """
    station_loads = [0] * stations
    assignments = []

    for order in orders:
        # Find the station with minimum load
        min_station = int(np.argmin(station_loads))
        station_loads[min_station] += order["packingTime"]
        assignments.append({
            "orderId": order["id"],
            "station": min_station + 1
        })

    station_summary = [{"station": i+1, "totalTime": station_loads[i]} for i in range(stations)]

    return {
        "assignments": assignments,
        "stationLoadSummary": station_summary,
        "imbalancePercent": round((max(station_loads) - min(station_loads)) / (sum(station_loads)/stations) * 100, 2),
        "insight": f"Load imbalance reduced to {round((max(station_loads) - min(station_loads)) / (sum(station_loads)/stations) * 100, 2)}%."
    }


# ----------- INVENTORY OPTIMIZER ----------- #
def optimize_inventory(skuData, capacity: int):
    """
    Proportional allocation optimizer for inventory.
    """
    effective_demand = {sku.sku: min(sku.forecastDemand, sku.actualDemand) for sku in skuData}
    total_demand = sum(effective_demand.values())
    total_stock = sum([sku.stock for sku in skuData])
    distributable_stock = min(total_stock, capacity)

    allocationPlan, shortages, excess = [], [], []
    provisional_allocations = {}

    for sku in skuData:
        demand = effective_demand[sku.sku]
        weight = demand / total_demand if total_demand > 0 else 0
        provisional_allocations[sku.sku] = weight * distributable_stock

    for sku in skuData:
        demand = effective_demand[sku.sku]
        alloc = int(round(min(sku.stock, demand, provisional_allocations[sku.sku])))
        allocationPlan.append({"sku": sku.sku, "allocated": alloc})

        if alloc < demand:
            shortages.append({"sku": sku.sku, "shortage": demand - alloc})

        if alloc < sku.stock:
            excess.append({"sku": sku.sku, "excess": sku.stock - alloc})

    return {
        "allocationPlan": allocationPlan,
        "shortages": shortages,
        "excess": excess,
        "insight": f"Distributed {distributable_stock} units fairly across SKUs using proportional allocation."
    }
