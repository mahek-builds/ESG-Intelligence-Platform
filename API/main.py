from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import joblib
import os
import io
import numpy as np
from pydantic import BaseModel
from typing import Optional



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = "outputs/agent4_final_output.csv"
MODEL_PATH = "models/risk_model.pkl"


model = None
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)



@app.get("/")
def home():
    return {"message": "ESG Multi-Agent Monitoring API Running Successfully"}



@app.get("/esg-data")
def get_all_data():
    df = pd.read_csv(DATA_PATH)
    return df.to_dict(orient="records")



@app.get("/firm/{firm_id}")
def get_firm_data(firm_id: str):
    df = pd.read_csv(DATA_PATH)
    data = df[df["Firm_ID"] == firm_id]

    if data.empty:
        return {"error": "Firm not found"}

    return data.to_dict(orient="records")


@app.get("/risk-summary")
def risk_summary():
    df = pd.read_csv(DATA_PATH)

    return {
        "critical": int(df[df["alert_level"] == "Critical"].shape[0]),
        "warning": int(df[df["alert_level"] == "Warning"].shape[0]),
        "low": int(df[df["alert_level"] == "Low"].shape[0]),
    }



@app.get("/compliance-distribution")
def compliance_distribution():
    df = pd.read_csv(DATA_PATH)
    return df["Overall_Compliance"].value_counts().to_dict()


@app.get("/predict/{risk_score}")
def predict_risk(risk_score: float):

    if model is None:
        return {"error": "Model not found. Train model first."}

    prediction = model.predict([[risk_score]])

    return {
        "input_risk_score": risk_score,
        "predicted_risk_label": int(prediction[0])
    }


# ======================== BASIC PLAN ENDPOINTS ========================

def calculate_environmental_score(row):
    """
    Calculate environmental composite score using available metrics.
    Supports both detailed environmental data and E_Score fallback.
    """
    if all(col in row.index for col in ['carbon_emissions', 'energy_consumption', 
                                          'renewable_energy_percent', 'water_usage', 'waste_generated']):
        carbon_norm = min(100, max(0, 100 - (row['carbon_emissions'] / 1000 * 100)))
        energy_norm = min(100, max(0, 100 - (row['energy_consumption'] / 1000 * 100)))
        renewable_norm = min(100, max(0, row['renewable_energy_percent']))
        water_norm = min(100, max(0, 100 - (row['water_usage'] / 1000 * 100)))
        waste_norm = min(100, max(0, 100 - (row['waste_generated'] / 1000 * 100)))
        
        env_score = (carbon_norm + energy_norm + renewable_norm + water_norm + waste_norm) / 5
    elif 'E_Score' in row.index:
        env_score = row['E_Score']
    else:
        env_score = 70.0  
    
    return round(env_score, 2)


def calculate_emission_trend(df, firm_id):
    """
    Calculate Year-over-Year emission trend.
    """
    if 'Firm_ID' in df.columns and 'Year' in df.columns:
        firm_data = df[df['Firm_ID'] == firm_id].sort_values('Year')
        if len(firm_data) >= 2 and 'carbon_emissions' in df.columns:
            recent = firm_data.iloc[-1]['carbon_emissions']
            previous = firm_data.iloc[-2]['carbon_emissions']
            trend = ((recent - previous) / previous * 100) if previous != 0 else 0
            if trend < -5:
                return "Reducing"
            elif trend > 5:
                return "Increasing"
            else:
                return "Stable"
    if 'E_Score' in df.columns:
        avg_score = df['E_Score'].mean()
        firm_score = df[df['Firm_ID'] == firm_id]['E_Score'].mean() if 'Firm_ID' in df.columns else 70
        if firm_score > avg_score:
            return "Reducing"
        else:
            return "Increasing"
    return "Stable"


def calculate_renewable_status(row):
    """
    Determine renewable energy usage status.
    """
    if 'renewable_energy_percent' in row.index:
        renewable = row['renewable_energy_percent']
        if renewable >= 50:
            return "High"
        elif renewable >= 25:
            return "Moderate"
        else:
            return "Low"
    return "Moderate"  #


def calculate_csr_growth(row, df=None):
    """
    Calculate CSR growth (YoY).
    """
    if 'csr_spending' in row.index and df is not None and 'Firm_ID' in df.columns:
        firm_data = df[df['Firm_ID'] == row['Firm_ID']].sort_values('Year')
        if len(firm_data) >= 2:
            recent = firm_data.iloc[-1]['csr_spending']
            previous = firm_data.iloc[-2]['csr_spending']
            growth = ((recent - previous) / previous * 100) if previous != 0 else 0
            return f"{growth:+.0f}%"
    
    if 'Innovation_Spending' in row.index:
        innovation = row['Innovation_Spending']
        if innovation > 4.5:
            return "+15%"
        elif innovation > 3.5:
            return "+8%"
        else:
            return "+3%"
    
    return "+5%" 


def calculate_financial_alignment(row):
    """
    Determine financial ESG alignment based on financial indicators.
    """
    scores = []
    
    if 'ROA' in row.index:
        scores.append(min(row['ROA'], 15) / 15 * 100)
    if 'ROE' in row.index:
        scores.append(min(row['ROE'], 20) / 20 * 100)
    if 'Net_Profit_Margin' in row.index:
        scores.append(min(row['Net_Profit_Margin'], 12) / 12 * 100)
    
    if scores:
        avg_score = np.mean(scores)
        if avg_score >= 75:
            return "Excellent"
        elif avg_score >= 60:
            return "Good"
        elif avg_score >= 45:
            return "Fair"
        else:
            return "Poor"
    
    return "Good"  # Default


def calculate_csr_score(row):
    """
    Calculate CSR (Social) score from available data.
    Returns numeric score 0-100.
    Uses S_Score if available, otherwise estimates from financial indicators.
    """
    if 'S_Score' in row.index:
        return round(float(row['S_Score']), 2)
    
    if 'Innovation_Spending' in row.index:
        innovation = row['Innovation_Spending']
        csr_proxy = min(100, max(0, (innovation / 6.0) * 100))
        return round(csr_proxy, 2)
    
    return 65.0


def calculate_weighted_esg_score(environmental_score, csr_score):
    """
    Calculate weighted ESG composite score using formula-based approach.
    Formula: ESG_Score = (0.70 * Environmental_Score) + (0.30 * CSR_Score)
    
    Args:
        environmental_score: Environmental score (0-100)
        csr_score: CSR/Social score (0-100)
    
    Returns:
        Weighted ESG composite score (0-100)
    """
    esg_score = (0.70 * environmental_score) + (0.30 * csr_score)
    return round(esg_score, 2)


def predict_risk_category(final_esg_score):
    """
    Predict risk category and probability using loaded model.
    """
    global model
    
    if model is None:
        if final_esg_score >= 70:
            return "Low", 0.15
        elif final_esg_score >= 55:
            return "Medium", 0.55
        else:
            return "High", 0.85
    
    try:
        risk_prob = model.predict_proba([[final_esg_score]])[0]
        prediction = model.predict([[final_esg_score]])[0]
        
        risk_map = {0: "Low", 1: "Medium", 2: "High"}
        risk_category = risk_map.get(prediction, "Medium")
        
        risk_probability = round(float(risk_prob[prediction]), 2)
        
        return risk_category, risk_probability
    except Exception as e:
        # Fallback
        if final_esg_score >= 70:
            return "Low", 0.15
        elif final_esg_score >= 55:
            return "Medium", 0.55
        else:
            return "High", 0.85


def generate_summary(env_score, emission_trend, renewable_status, csr_growth, financial_alignment):
    """
    Generate human-readable ESG performance summary.
    """
    summary_parts = []
    
    # Environmental assessment
    if env_score >= 75:
        summary_parts.append("Company environmental practices are strong")
    elif env_score >= 55:
        summary_parts.append("Company environmental practices are moderate")
    else:
        summary_parts.append("Company environmental practices need improvement")
    
    # Trend assessment
    if emission_trend == "Reducing":
        summary_parts.append("and emissions are trending downward")
    elif emission_trend == "Increasing":
        summary_parts.append("but emissions are increasing")
    else:
        summary_parts.append("with stable emission levels")
    
    # Renewable energy assessment
    if renewable_status == "High":
        summary_parts.append(". Renewable energy adoption is commendable")
    elif renewable_status == "Low":
        summary_parts.append(". Renewable energy usage can improve significantly")
    else:
        summary_parts.append(". Renewable energy usage is at moderate levels")
    
    # Financial alignment
    if financial_alignment == "Excellent":
        summary_parts.append(", with excellent financial ESG alignment")
    elif financial_alignment == "Good":
        summary_parts.append(", with good financial ESG alignment")
    else:
        summary_parts.append(", but financial ESG alignment needs work")
    
    return ". ".join(summary_parts) + "."


@app.post("/basic/predict")
async def basic_plan_predict(file: UploadFile = File(...)):
    """
    BASIC PLAN API Endpoint for Foundational ESG Intelligence
    
    - Lightweight, fast, low-compute processing
    - Operational Agent: Environmental metrics
    - Financial Agent: CSR and financial alignment
    - Risk Prediction: RandomForest model inference
    - Returns structured ESG assessment
    
    Upload a CSV with columns like:
    - Firm_ID, Year, E_Score, S_Score, G_Score (minimal)
    - Or detailed: carbon_emissions, energy_consumption, renewable_energy_percent, water_usage, waste_generated
    - Revenue, ROA, ROE, Net_Profit_Margin for financial assessment
    """
    try:
        # Read uploaded CSV file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        if df.empty:
            return {"error": "Uploaded CSV is empty"}
        
        if len(df) > 1:
            data_row = df.iloc[0] 
        else:
            data_row = df.iloc[0]
        
        environment_score = calculate_environmental_score(data_row)
        emission_trend = calculate_emission_trend(df, data_row.get('Firm_ID', 'Unknown'))
        renewable_status = calculate_renewable_status(data_row)
        
        csr_growth = calculate_csr_growth(data_row, df)
        financial_alignment = calculate_financial_alignment(data_row)
        
        csr_score = calculate_csr_score(data_row)
        
  
        esg_score = calculate_weighted_esg_score(environment_score, csr_score)

        e_score = data_row.get('E_Score', environment_score)
        s_score = data_row.get('S_Score', 65.0)
        g_score = data_row.get('G_Score', 65.0)
        final_esg_score = (e_score + s_score + g_score) / 3
        
        risk_category, risk_probability = predict_risk_category(final_esg_score)

        
        response = {
            "esg_score": esg_score,
            "risk_category": risk_category,
            "risk_probability": risk_probability,
            "environment_score": round(environment_score, 2),
            "emission_trend": emission_trend,
            "renewable_usage_status": renewable_status,
            "csr_growth": csr_growth,
            "financial_esg_alignment": financial_alignment
        }
        
        return response
    
    except Exception as e:
        return {"error": f"Failed to process file: {str(e)}"}
