# API/agent1_routes.py
from fastapi import APIRouter, HTTPException
from agents.agent1_premium import run_agent1_premium    
router = APIRouter(prefix="/agent1", tags=["Data Synchronization"])

@router.post("/sync")
def trigger_data_sync():
    """
    Triggers Agent 1 to fetch raw data from SQL, 
    clean it, cache it in MongoDB, and generate the Operational CSV.
    """
    result = run_agent1_premium()
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
        
    return result
# API/agent1_routes.py
from fastapi import APIRouter, HTTPException
from agents.agent1 import sync_and_clean_pipeline

router = APIRouter(prefix="/agent1", tags=["Data Synchronization"])

@router.post("/sync")
def trigger_data_sync():
    """
    Triggers Agent 1 to fetch raw data from SQL, 
    clean it, cache it in MongoDB, and generate the Operational CSV.
    """
    result = sync_and_clean_pipeline()
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
        
    return result