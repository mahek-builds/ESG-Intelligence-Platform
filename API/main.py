import os
import asyncio
import threading
import joblib
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import socketio

# Import individual agent routers
from API.agent1_routes import router as agent1
from API.agent2_routes import router as agent2
from API.agent3_routes import router as agent3
from API.agent4_routes import router as agent4
from API.agent5_routes import router as agent5

# Import Premium Logic
from agents.agent1_premium import run_agent1_premium

app = FastAPI(title="ESG Multi-Agent Monitoring System")

# 1. Setup Socket.IO Server
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

# --- 💎 PREMIUM ROUTE (Fixed) ---
@app.post("/api/premium/agent1/start")
async def activate_premium_agent1(company_id: str = "company3"):
    """
    Starts the Agent 1 Premium background thread safely.
    """
    try:
        # 1. Main loop ka reference lenge
        main_loop = asyncio.get_running_loop()

        # 2. Corrected Callback: Thread-safe tareeke se emit karega
        def socket_callback(event, data):
            # Bina naya loop banaye, main loop par task schedule karega
            asyncio.run_coroutine_threadsafe(sio.emit(event, data), main_loop)

        # 3. Start the watcher thread
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

# Start using: uvicorn main:socket_app --host 0.0.0.0 --port 5000

# --- IMPORTANT: SOCKET.IO ENTRY POINT ---
# Run this file using: uvicorn main:socket_app --host 0.0.0.0 --port 5000[]
# # --- IMPORTANT: SOCKET.IO ENTRY POINT ---
# # Run this file using: uvicorn main:socket_app --host 0.0.0.0 --port 5000[]