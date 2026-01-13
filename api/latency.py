from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import pathlib
import math


class Query(BaseModel):
    regions: List[str]
    threshold_ms: float


router = APIRouter()

DATA_PATH = pathlib.Path(__file__).parent.parent / "q-vercel-latency.json"


def load_data() -> List[Dict[str, Any]]:
    try:
        with DATA_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def percentile(data: List[float], p: float) -> float:
    if not data:
        return 0.0
    s = sorted(data)
    k = (len(s) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return float(s[int(k)])
    d0 = s[f] * (c - k)
    d1 = s[c] * (k - f)
    return float(d0 + d1)


@router.post("", tags=["latency"])
async def check_latency(q: Query):
    data = load_data()
    result: Dict[str, Dict[str, float]] = {}

    for region in q.regions:
        records = [r for r in data if r.get("region") == region]
        latencies = [float(r.get("latency_ms", 0)) for r in records]
        uptimes = [float(r.get("uptime_pct", 0)) for r in records]

        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        p95_latency = percentile(latencies, 95) if latencies else 0.0
        avg_uptime = sum(uptimes) / len(uptimes) if uptimes else 0.0
        breaches = sum(1 for v in latencies if v > q.threshold_ms)

        result[region] = {
            "avg_latency": round(avg_latency, 3),
            "p95_latency": round(p95_latency, 3),
            "avg_uptime": round(avg_uptime, 3),
            "breaches": breaches,
        }

    return {"regions": result}
