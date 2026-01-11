import json
import statistics
from typing import List, Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Enable CORS for POST requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

# Load telemetry data
with open("q-vercel-latency.json", "r") as f:
    TELEMETRY_DATA = json.load(f)


class LatencyRequest(BaseModel):
    regions: List[str]
    threshold_ms: float


class RegionMetrics(BaseModel):
    avg_latency: float
    p95_latency: float
    avg_uptime: float
    breaches: int


class LatencyResponse(BaseModel):
    metrics: Dict[str, RegionMetrics]


def calculate_percentile(data: List[float], percentile: float) -> float:
    """Calculate percentile value from a list of numbers."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    index = (percentile / 100) * (len(sorted_data) - 1)
    lower = int(index)
    upper = lower + 1
    
    if upper >= len(sorted_data):
        return float(sorted_data[lower])
    
    weight = index - lower
    return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight


@app.post("/api/metrics", response_model=LatencyResponse)
async def get_metrics(request: LatencyRequest) -> LatencyResponse:
    """
    Calculate latency and uptime metrics for specified regions.
    
    Args:
        request: JSON body with regions list and threshold_ms
        
    Returns:
        Per-region metrics including avg_latency, p95_latency, avg_uptime, and breaches count
    """
    metrics = {}
    
    for region in request.regions:
        # Filter data for this region
        region_data = [record for record in TELEMETRY_DATA if record["region"] == region]
        
        if not region_data:
            metrics[region] = RegionMetrics(
                avg_latency=0.0,
                p95_latency=0.0,
                avg_uptime=0.0,
                breaches=0
            )
            continue
        
        # Extract latency and uptime values
        latencies = [record["latency_ms"] for record in region_data]
        uptimes = [record["uptime_pct"] for record in region_data]
        
        # Calculate metrics
        avg_latency = statistics.mean(latencies)
        p95_latency = calculate_percentile(latencies, 95)
        avg_uptime = statistics.mean(uptimes)
        breaches = sum(1 for latency in latencies if latency > request.threshold_ms)
        
        metrics[region] = RegionMetrics(
            avg_latency=round(avg_latency, 2),
            p95_latency=round(p95_latency, 2),
            avg_uptime=round(avg_uptime, 2),
            breaches=breaches
        )
    
    return LatencyResponse(metrics=metrics)


@app.get("/health")
async def health_check():
    """Health check endpoint for Vercel."""
    return {"status": "ok"}
