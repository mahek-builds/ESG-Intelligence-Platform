from fastapi import APIRouter
import threading
from agents.agent1_premium import run_agent1_premium

router = APIRouter(prefix="/agent1-premium", tags=["Premium Data Streaming"])

@router.post("/start")
async def start_premium_sync():
    """
    Starts premium monitoring using .env credentials. 
    No manual input required in Swagger.
    """
    try:
        # Import sio from your main app entry point
        from API.main import sio 

        def emit_callback(event, data):
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Thread-safe async emission
            loop.run_until_complete(sio.emit(event, data))

        # Start the background thread
        thread = threading.Thread(target=run_agent1_premium, args=(emit_callback,))
        thread.daemon = True
        thread.start()

        return {"status": "success", "message": "Premium listener is live."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
