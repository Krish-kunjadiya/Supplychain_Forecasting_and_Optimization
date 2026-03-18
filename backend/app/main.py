import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routers import dashboard, pipeline, predict, inventory

app = FastAPI(title="Supply Chain Optimization API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(pipeline.router)
app.include_router(predict.router)
app.include_router(inventory.router)

@app.on_event("startup")
async def startup():
    # Auto-create uploads dir if missing
    _HERE = os.path.dirname(os.path.abspath(__file__))
    _ROOT = os.path.abspath(os.path.join(_HERE, "../../.."))
    os.makedirs(os.path.join(_ROOT, "uploads"), exist_ok=True)

@app.get("/health")
async def health():
    return {"status": "ok", "uploads_dir": "ready"}
