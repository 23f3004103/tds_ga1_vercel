# Latency Metrics API

A FastAPI endpoint deployed on Vercel that streams latency pings from storefronts and provides metrics for dashboard monitoring.

## Features

- ✅ POST endpoint accepting region list and threshold
- ✅ Per-region metrics: average latency, 95th percentile latency, average uptime, breach count
- ✅ CORS enabled for cross-origin requests
- ✅ Deployed on Vercel serverless platform

## Project Structure

```
├── api/
│   └── index.py          # FastAPI application
├── q-vercel-latency.json # Sample telemetry data
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel configuration
└── README.md            # This file
```

## Setup & Deployment

### Prerequisites
- Python 3.9+
- Git
- GitHub account
- Vercel account

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/latency-metrics-api.git
cd latency-metrics-api
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run locally:
```bash
uvicorn api.index:app --reload
```

The API will be available at `http://localhost:8000`

### Deploy to Vercel

1. **Install Vercel CLI:**
```bash
npm install -g vercel
```

2. **Initialize Vercel project (if needed):**
```bash
vercel
```

3. **Deploy:**
```bash
vercel --prod
```

The endpoint will be at: `https://your-project-name.vercel.app/api/metrics`

## API Usage

### Endpoint

**POST** `/api/metrics`

### Request Body

```json
{
  "regions": ["amer", "emea"],
  "threshold_ms": 184
}
```

### Response

```json
{
  "metrics": {
    "amer": {
      "avg_latency": 156.42,
      "p95_latency": 201.33,
      "avg_uptime": 98.15,
      "breaches": 12
    },
    "emea": {
      "avg_latency": 168.91,
      "p95_latency": 212.45,
      "avg_uptime": 97.82,
      "breaches": 18
    }
  }
}
```

### Field Descriptions

- **avg_latency**: Mean latency across all records for the region (ms)
- **p95_latency**: 95th percentile latency (ms)
- **avg_uptime**: Mean uptime percentage
- **breaches**: Count of records where latency exceeded `threshold_ms`

### Health Check

**GET** `/health`

Response: `{"status": "ok"}`

## Telemetry Data

The `q-vercel-latency.json` file contains sample data with the following structure:

```json
{
  "region": "amer",
  "service": "checkout",
  "latency_ms": 152.75,
  "uptime_pct": 97.135,
  "timestamp": 20250301
}
```

**Regions in sample data:** amer, apac, emea, usakc

## CORS Configuration

CORS is enabled for POST requests from any origin. This allows dashboard applications to call the endpoint directly from the browser.

## License

MIT
