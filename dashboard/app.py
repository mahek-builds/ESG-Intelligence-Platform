import streamlit as st
import pandas as pd
import plotly.express as px

df = pd.read_csv(r"C:\Users\HP\Desktop\ESG-Monitoring-System\ML\ESG4_output.csv")


st.title("Real-Time ESG Risk Dashboard")

st.dataframe(df)

fig = px.bar(
    df,
    x="Firm_ID",
    y="final_esg_risk_score",
    color="alert_level",
    title="ESG Risk Score by Firm"
)
st.plotly_chart(fig)

trend = px.line(
    df,
    x="Year",
    y="ESG_Score",
    color="Firm_ID",
    title="ESG Score Trend Over Time"
)
st.plotly_chart(trend)

critical_count = df[df["alert_level"] == "🔴 Critical"].shape[0]
st.metric("🚨 Critical Firms", critical_count)
