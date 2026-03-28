import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from env_emailassist.env import EmailAssistEnv
from env_emailassist.models import Action


# -----------------------------
# FastAPI App
# -----------------------------

app = FastAPI(title="EmailAssist OpenEnv Environment")

# single environment instance
ENV = EmailAssistEnv()


# -----------------------------
# API Models for endpoints
# -----------------------------

class StepRequest(BaseModel):
    action: Action


# -----------------------------
# Endpoints
# -----------------------------

@app.post("/reset")
def reset():
    """Resets the environment and returns the initial observation."""
    result = ENV.reset()
    return {
        "observation": result.observation.model_dump(),
        "reward": result.reward,
        "done": result.done,
        "info": result.info,
    }


@app.post("/step")
def step(req: StepRequest):
    """Takes an action and returns the environment transition."""
    result = ENV.step(req.action)
    return {
        "observation": result.observation.model_dump(),
        "reward": result.reward,
        "done": result.done,
        "info": result.info,
    }


@app.get("/state")
def state():
    """Returns internal environment state."""
    return ENV.state().model_dump()


@app.post("/close")
def close():
    """Stops the environment."""
    ENV.close()
    return {"status": "closed"}


# -----------------------------
# Dev mode entry point
# -----------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
