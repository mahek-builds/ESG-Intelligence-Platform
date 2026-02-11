import os
import pandas as pd

def run_agent1(input_path, output_path):
    df = pd.read_csv(input_path)

    operational_cols = [
        "Firm_ID",
        "Year",
        "Industry_Type",
        "E_Score",
        "S_Score",
        "G_Score",
        "Board_Independence"
    ]

    df = df[operational_cols]
    df = df.dropna()
    df = df.reset_index(drop=True)

    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, "agent1_operational_output.csv")

    df.to_csv(output_file, index=False)

if __name__ == "__main__":
    run_agent1(
        input_path=r"C:\Users\HP\Desktop\ESG-Monitoring-System\Dataset\Manufacturing_ESG_Financial_Data.csv",
        output_path=r"C:\Users\HP\Desktop\ESG-Monitoring-System\outputs"
    )
