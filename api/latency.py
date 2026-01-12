from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="eShopCo Latency Metrics")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)


class MetricsRequest(BaseModel):
    regions: List[str] = Field(..., min_length=1)
    threshold_ms: float


def _load_telemetry() -> List[Dict[str, Any]]:
    telemetry_path = Path(__file__).resolve().parents[1] / "q-vercel-latency.json"
    if not telemetry_path.exists():
        raise RuntimeError(f"Telemetry file not found: {telemetry_path}")
    return json.loads(telemetry_path.read_text(encoding="utf-8"))


_TELEMETRY: List[Dict[str, Any]]
try:
    _TELEMETRY = _load_telemetry()
except Exception:
    _TELEMETRY = []


def _percentile_linear(sorted_values: List[float], q: float) -> float:
    """Numpy-like percentile with linear interpolation.

    q in [0, 1]. For n==1 returns the single value.
    """

    n = len(sorted_values)
    if n == 0:
        raise ValueError("percentile of empty list")
    if n == 1:
        return float(sorted_values[0])

    q = max(0.0, min(1.0, float(q)))
    pos = (n - 1) * q
    lower_index = int(math.floor(pos))
    upper_index = int(math.ceil(pos))

    lower_value = float(sorted_values[lower_index])
    upper_value = float(sorted_values[upper_index])
    if lower_index == upper_index:
        return lower_value

    weight = pos - lower_index
    return lower_value + (upper_value - lower_value) * weight


def _region_metrics(region: str, threshold_ms: float) -> Dict[str, Any]:
    rows = [r for r in _TELEMETRY if r.get("region") == region]
    if not rows:
        return {
            "avg_latency": None,
            "p95_latency": None,
            "avg_uptime": None,
            "breaches": 0,
            "count": 0,
        }

    latencies = [float(r["latency_ms"]) for r in rows]
    uptimes = [float(r["uptime_pct"]) for r in rows]

    latencies_sorted = sorted(latencies)

    avg_latency = mean(latencies)
    p95_latency = _percentile_linear(latencies_sorted, 0.95)
    avg_uptime = mean(uptimes)
    breaches = sum(1 for v in latencies if v > threshold_ms)

    return {
        "avg_latency": round(avg_latency, 2),
        "p95_latency": round(p95_latency, 2),
        "avg_uptime": round(avg_uptime, 3),
        "breaches": int(breaches),
        "count": int(len(rows)),
    }


@app.post("/")
@app.post("/api/latency")
async def latency_metrics(body: MetricsRequest) -> Dict[str, Any]:
    if not _TELEMETRY:
        raise HTTPException(status_code=500, detail="Telemetry data not loaded")

    regions = [r.strip() for r in body.regions if r and r.strip()]
    if not regions:
        raise HTTPException(status_code=422, detail="regions must be a non-empty list")

    threshold_ms = float(body.threshold_ms)

    metrics = {region: _region_metrics(region, threshold_ms) for region in regions}
    return {
        "threshold_ms": threshold_ms,
        "metrics": metrics,
    }
