from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import ValidationError
import os

from api.models import ActionRequest, ResetRequest, StepResponse, StateResponse, Observation
from env.cyber_env import env_instance

app = FastAPI(title="Cybersecurity Defense API", version="1.0.0")

# Setup UI later
os.makedirs("ui", exist_ok=True)

# Endpoint: POST /reset
@app.post("/reset", response_model=Observation)
def reset_env(req: ResetRequest):
    if req.task_id not in ["easy", "medium", "hard"]:
        raise HTTPException(status_code=400, detail="Invalid task_id")
    obs = env_instance.reset(task_id=req.task_id, seed=req.seed)
    return obs

# Endpoint: POST /step
@app.post("/step", response_model=StepResponse)
def step_env(req: ActionRequest):
    if env_instance.step_count >= env_instance.max_steps:
        raise HTTPException(status_code=400, detail="Episode already finished. Please reset.")
    if req.action not in ["block_ip", "scan_system", "deploy_patch", "ignore"]:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    obs, reward, done, info = env_instance.step(req.action)
    return StepResponse(
        observation=obs,
        reward=reward,
        done=done,
        info=info
    )

# Endpoint: GET /state
@app.get("/state")
def get_state():
    return env_instance.get_state()

# Serve UI
@app.get("/")
def serve_ui():
    index_path = os.path.join("ui", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "UI not found"}

app.mount("/static", StaticFiles(directory="ui"), name="static")
