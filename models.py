from pydantic import BaseModel
from typing import Dict, Any, Optional

class Observation(BaseModel):
    incoming_requests: int
    system_load: float
    suspicious_activity: int
    network_health: float

class ActionRequest(BaseModel):
    action: str

class StepResponse(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: Dict[str, Any]

class StateResponse(StepResponse):
    pass

class ResetRequest(BaseModel):
    task_id: str
    seed: Optional[int] = None
