"""
app.py — FastAPI server wrapper for HF Spaces deployment
=========================================================
The automated checker pings:
  GET  /          → health check, returns 200
  POST /reset     → calls env.reset()
  POST /step      → calls env.step(action)
  GET  /state     → calls env.state()

Run locally:  uvicorn app:app --host 0.0.0.0 --port 7860
HF Spaces:    auto-detected, port 7860
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Optional
import uvicorn

from env import ProcurementEnv

app = FastAPI(title="Procurement Negotiation Environment")

# Global env instance (one per server — fine for evaluation)
_env: Optional[ProcurementEnv] = None


class ResetRequest(BaseModel):
    task_level: str = "medium"
    seed: int = 42


class StepRequest(BaseModel):
    action: dict


@app.get("/")
def health():
    """Health check — automated checker pings this first."""
    return {"status": "ok", "env": "procurement-negotiation-env", "version": "1.0.0"}


@app.post("/reset")
def reset(req: ResetRequest):
    global _env
    try:
        _env = ProcurementEnv(task_level=req.task_level, seed=req.seed)
        obs = _env.reset()
        return JSONResponse(content={"observation": obs})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/step")
def step(req: StepRequest):
    global _env
    if _env is None:
        raise HTTPException(status_code=400, detail="Call /reset first.")
    try:
        result = _env.step(req.action)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/state")
def state():
    global _env
    if _env is None:
        raise HTTPException(status_code=400, detail="Call /reset first.")
    return JSONResponse(content=_env.state())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)