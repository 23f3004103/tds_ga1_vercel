# Vercel latency endpoint

This repository contains a serverless FastAPI endpoint to compute per-region latency metrics from the provided `q-vercel-latency.json` telemetry bundle.

Endpoint path (after deploying to Vercel):

- POST `https://<your-vercel-project>.vercel.app/api/latency`

Example request body:

```
{"regions": ["apac", "amer"], "threshold_ms": 166}
```

Example curl test:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"regions":["apac","amer"],"threshold_ms":166}' \
  https://<your-vercel-project>.vercel.app/api/latency
```

Deploy steps (GitHub integration):

1. Create a new GitHub repository and push this project.
2. Go to https://vercel.com, sign in, and choose "New Project".
3. Import your GitHub repository and follow the defaults.
4. After deploy, call the POST endpoint shown above (replace `<your-vercel-project>` with the assigned domain).
