import os
import pandas as pd

def run_agent2(input_path, output_path):
    df = pd.read_csv(input_path)

    df["financial_risk_score"] = (
        (df["E_Score"] < 60).astype(int) +
        (df["S_Score"] < 60).astype(int) +
        (df["G_Score"] < 60).astype(int)
    ) * 33

    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, "agent2_financial_output.csv")
    return df.to_dict(orient="records")



# if __name__ == "__main__":
#     run_agent2(
#         input_path=r"C:\Users\HP\Desktop\ESG-Monitoring-System\outputs\agent1_operational_output.csv",
#         output_path=r"C:\Users\HP\Desktop\ESG-Monitoring-System\outputs"
#     )
