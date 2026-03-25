from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import socketio
import threading
import joblib
import os

# Import individual agent routers
from API.agent1_routes import router as agent1
from API.agent2_routes import router as agent2
from API.agent3_routes import router as agent3
from API.agent4_routes import router as agent4
from API.agent5_routes import router as agent5

# Import Premium Logic
from agents.agent1_premium import run_agent1_premium

app = FastAPI(title="ESG Multi-Agent Monitoring System")

# 1. Setup Socket.IO Server (No separate manager file)
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio, app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Model Loading
MODEL_PATH = "models/risk_model.pkl"
app.state.model = joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None

# Register Agent Routers
app.include_router(agent1)
app.include_router(agent2)
app.include_router(agent3)
app.include_router(agent4)
app.include_router(agent5)

# --- 💎 PREMIUM ROUTE ---
@app.post("/api/premium/agent1/start")
async def activate_premium_agent1(company_id: str = "company3"):
    """
    Starts the Agent 1 Premium background thread.
    Passes the sio.emit function directly as a callback.
    """
    try:
        # Define the wrapper to bridge Async SIO with the Python Thread
        def socket_callback(event, data):
            # Use sio.emit inside a synchronous wrapper if needed
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(sio.emit(event, data))

        # Start the watcher in a background thread
        thread = threading.Thread(
            target=run_agent1_premium, 
            args=(socket_callback, company_id)
        )
        thread.daemon = True
        thread.start()

        return {
            "status": "Success", 
            "message": f"💎 Agent 1 Premium streaming started for {company_id}"
        }
    except Exception as e:
        return {"status": "Error", "message": str(e)}

@app.get("/")
def home():
    return {"message": "ESG Multi-Agent API Running Successfully"}

# --- IMPORTANT: SOCKET.IO ENTRY POINT ---
# Run this file using: uvicorn main:socket_app --host 0.0.0.0 --port 5000[]