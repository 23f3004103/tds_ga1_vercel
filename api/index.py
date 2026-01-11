from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json, os, statistics
from typing import List, Dict

app = FastAPI()


@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# Load data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "q-vercel-latency.json")

with open(DATA_PATH) as f:
    DATA = json.load(f)

class LatencyRequest(BaseModel):
    regions: List[str]
    threshold_ms: float


def percentile(data: List[float], p: float) -> float:
    if not data:
        return 0.0
    if p <= 0:
        return float(min(data))
    if p >= 100:
        return float(max(data))

    sorted_data = sorted(float(x) for x in data)
    idx = (p / 100.0) * (len(sorted_data) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(sorted_data) - 1)
    frac = idx - lo
    return sorted_data[lo] * (1 - frac) + sorted_data[hi] * frac


@app.options("/api/latency")
def latency_preflight():
    return JSONResponse(content={})


@app.post("/api/latency")
def latency(req: LatencyRequest):
    result = {}

    for region in req.regions:
        rows = [r for r in DATA if r["region"] == region]

        if not rows:
            result[region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0
            }
            continue

        lat = [r["latency_ms"] for r in rows]
        up = [r["uptime_pct"] for r in rows]

        result[region] = {
            "avg_latency": round(statistics.mean(lat), 2),
            "p95_latency": round(percentile(lat, 95), 2),
            "avg_uptime": round(statistics.mean(up), 2),
            "breaches": sum(1 for x in lat if x > req.threshold_ms)
        }

    return {"metrics": result}
