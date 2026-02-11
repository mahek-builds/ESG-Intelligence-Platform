import streamlit as st
import plotly.express as px
import pandas as pd


st.set_page_config(page_title="ESG Monitoring System", layout="wide")

st.title("📊 Real-Time ESG Risk Dashboard")


df = pd.read_csv(r"C:\Users\HP\Desktop\ESG-Monitoring-System\ML\ESG4_output.csv")

if df.empty:
    st.warning("Dataset is empty!")
    st.stop()


col1, col2, col3 = st.columns(3)

critical_count = df[df["alert_level"] == "🔴 Critical"].shape[0]
warning_count = df[df["alert_level"] == "🟠 Warning"].shape[0]
lowrisk_count = df[df["alert_level"] == "🟢 Low Risk"].shape[0]

col1.metric("🚨 Critical Firms", critical_count)
col2.metric("⚠️ Warning Firms", warning_count)
col3.metric("✅ Low Risk Firms", lowrisk_count)

st.divider()


fig_bar = px.bar(
    df,
    x="Firm_ID",
    y="final_esg_risk_score",
    color="alert_level",
    title="ESG Risk Score by Firm",
    height=400
)

st.plotly_chart(fig_bar, use_container_width=True)


fig_line = px.line(
    df,
    x="Year",
    y="ESG_Score",
    color="Firm_ID",
    title="ESG Score Trend Over Time",
    markers=True
)

st.plotly_chart(fig_line, use_container_width=True)


st.subheader("🔎 Filter by Firm")

selected_firm = st.selectbox("Select Firm", df["Firm_ID"].unique())

filtered_df = df[df["Firm_ID"] == selected_firm]

st.dataframe(filtered_df)


st.subheader("🧠 ESG Risk Explanation")

latest_row = filtered_df.sort_values("Year").iloc[-1]

explanation = f"""
Firm {latest_row['Firm_ID']} has a final ESG risk score of 
{round(latest_row['final_esg_risk_score'],2)}.

Overall Compliance Status: {latest_row['Overall_Compliance']}.

Alert Level: {latest_row['alert_level']}.

Lower ESG scores increase performance risk, and compliance violations 
increase compliance risk, resulting in higher final risk score.
"""

st.info(explanation)

st.success("Agent 5 Dashboard Running Successfully 🚀")
