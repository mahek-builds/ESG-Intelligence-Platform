from fastapi import APIRouter, Request, HTTPException
import threading
import asyncio

router = APIRouter(prefix="/premium/agent1", tags=["Agent 1 Premium"])

@router.post("/start-prime")
async def start_prime_stream(request: Request, company_id: str = "company3"):
    """
     PRIME ACTIVATION:
    Starts the real-time MongoDB listener and WebSockets.
    """
    from agents.agent1_premium import run_agent1_premium
    
    # 1. Main loop ka reference lena (Socket.IO ke liye zaroori hai)
    try:
        loop = asyncio.get_running_loop()
        sio = request.app.state.sio # Main app se SIO object uthana
    except Exception:
        raise HTTPException(status_code=500, detail="Socket.IO server not found in App State")

    # 2. Bridge function jo Thread se Async SIO ko call karega
    def socket_callback(event, data):
        asyncio.run_coroutine_threadsafe(sio.emit(event, data), loop)

    # 3. Thread mein Premium Agent start karna
    thread = threading.Thread(
        target=run_agent1_premium, 
        args=(socket_callback, company_id),
        daemon=True
    )
    thread.start()

    return {
        "status": "Success",
        "mode": "PRIME_ACTIVE",
        "message": f"Real-time MongoDB handler started for {company_id}"
    }

@router.get("/status")
def premium_status():
    return {
        "tier": "Premium/Prime",
        "features": ["Real-time Mapping", "MongoDB Change Streams", "WebSocket Delivery"]
    }