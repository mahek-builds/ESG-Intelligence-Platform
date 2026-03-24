import os
import pandas as pd

def run_agent4(input_path, output_path):
    df = pd.read_csv(input_path)

    df["final_esg_risk_score"] = (
        (df["E_Compliance"] == "Violation").astype(int) +
        (df["S_Compliance"] == "Violation").astype(int) +
        (df["G_Compliance"] == "Violation").astype(int)
    ) * 33

    def assign_alert(score):
        if score >= 66:
            return "Critical"
        elif score >= 33:
            return "Warning"
        else:
            return "Low"

    df["alert_level"] = df["final_esg_risk_score"].apply(assign_alert)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    AGENT4_output = df[[
        "Firm_ID",
        "Year",
        "Overall_Compliance",
        "final_esg_risk_score",
        "alert_level"
    ]]

    AGENT4_output.to_csv(output_path, index=False)



return AGENT4_output.to_dict(orient="records")
