import asyncio
import os
import threading

import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    import socketio
except ModuleNotFoundError:
    socketio = None

from API.agent1_routes import router as agent1
from API.agent1_premium_routes import router as agent1_premium
from API.agent2_routes import router as agent2
from API.agent3_routes import router as agent3
from API.agent4_routes import router as agent4
from API.agent5_routes import router as agent5
from agents.agent1_premium import run_agent1_premium

app = FastAPI(title="ESG Multi-Agent Monitoring System")

if socketio is not None:
    sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
    socket_app = socketio.ASGIApp(sio, app)
else:
    sio = None
    socket_app = app

app.state.sio = sio

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = "models/risk_model.pkl"
app.state.model = joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None

app.include_router(agent1)
app.include_router(agent1_premium)
app.include_router(agent2)
app.include_router(agent3)
app.include_router(agent4)
app.include_router(agent5)


@app.post("/api/premium/agent1/start")
async def activate_premium_agent1(company_id: str = "company3"):
    """
    Starts the Agent 1 Premium background thread safely.
    """
    try:
        if sio is None:
            return {
                "status": "Error",
                "message": "Premium streaming requires python-socketio to be installed.",
            }

        main_loop = asyncio.get_running_loop()

        def socket_callback(event, data):
            asyncio.run_coroutine_threadsafe(sio.emit(event, data), main_loop)

        thread = threading.Thread(
            target=run_agent1_premium,
            args=(socket_callback, company_id),
            daemon=True,
        )
        thread.start()

        return {
            "status": "Success",
            "message": f"Agent 1 Premium streaming started for {company_id}",
        }
    except Exception as exc:
        return {"status": "Error", "message": str(exc)}


@app.get("/")
def home():
    return {"message": "ESG Multi-Agent API Running Successfully"}
