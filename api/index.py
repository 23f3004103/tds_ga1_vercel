from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.latency import router as latency_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(latency_router, prefix="/api/latency")


@app.get("/", include_in_schema=False)
async def health():
    return {"status": "ok"}


