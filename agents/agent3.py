import os
import pandas as pd

def check_environment(row):
    return "Violation" if row["E_Score"] < 60 else "Compliant"

def check_social(row):
    return "Violation" if row["S_Score"] < 60 else "Compliant"

def check_governance(row):
    if row["G_Score"] < 60 or row["Board_Independence"] < 0.5:
        return "Violation"
    return "Compliant"

def run_agent3(input_path, output_path):
    df = pd.read_csv(input_path)

    df["E_Compliance"] = df.apply(check_environment, axis=1)
    df["S_Compliance"] = df.apply(check_social, axis=1)
    df["G_Compliance"] = df.apply(check_governance, axis=1)

    df["Overall_Compliance"] = df.apply(
        lambda row: "Non-Compliant"
        if "Violation" in [
            row["E_Compliance"],
            row["S_Compliance"],
            row["G_Compliance"]
        ]
        else "Compliant",
        axis=1
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    return df.to_dict(orient="records")




# if __name__ == "__main__":
#     run_agent3(
#         input_path=r"C:\Users\HP\Desktop\ESG-Monitoring-System\outputs\agent2_financial_output.csv",
#         output_path=r"C:\Users\HP\Desktop\ESG-Monitoring-System\outputs\agent3_compliance_output.csv"
#     )

