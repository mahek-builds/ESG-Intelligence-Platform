from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import joblib
import os

# Import the individual agent routers
from API.agent1_routes import router as agent1
from API.agent2_routes import router as agent2
from API.agent3_routes import router as agent3
from API.agent4_routes import router as agent4
from API.agent5_routes import router as agent5

app = FastAPI(title="ESG Multi-Agent Monitoring System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Model Loading (Accessible across agents if needed)
MODEL_PATH = "models/risk_model.pkl"
app.state.model = joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None

# Registering all Agent Routes
app.include_router(agent1) # Data Sync
app.include_router(agent2) # Financial Risk
app.include_router(agent3) # Compliance Audit
app.include_router(agent4) # Final Alert Summary
app.include_router(agent5) # SHAP Explainability

@app.get("/")
def home():
    return {"message": "ESG Multi-Agent API Running Successfully"}