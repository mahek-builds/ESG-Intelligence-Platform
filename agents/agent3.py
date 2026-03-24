from pathlib import Path

import pandas as pd
from agents.output_paths import get_agent_output_path, get_company_name


def check_environment(row):
    return "Violation" if row["E_Score"] < 60 else "Compliant"


def check_social(row):
    return "Violation" if row["S_Score"] < 60 else "Compliant"


def check_governance(row):
    if row["G_Score"] < 60 or row["Board_Independence"] < 0.5:
        return "Violation"
    return "Compliant"


def run_agent3(input_path=None, output_path=None):
    company_name = get_company_name()
    source = Path(input_path) if input_path else get_agent_output_path(
        "agent2_financial_output",
        company_name=company_name,
    )
    target = Path(output_path) if output_path else get_agent_output_path(
        "agent3_compliance_output",
        company_name=company_name,
        input_path=source,
    )

    if not source.exists():
        return {
            "error": f"Input file not found: {source}. Run Agent 2 first.",
        }

    try:
        df = pd.read_csv(source)
        df["E_Compliance"] = df.apply(check_environment, axis=1)
        df["S_Compliance"] = df.apply(check_social, axis=1)
        df["G_Compliance"] = df.apply(check_governance, axis=1)

        df["Overall_Compliance"] = df.apply(
            lambda row: "Non-Compliant"
            if "Violation" in [row["E_Compliance"], row["S_Compliance"], row["G_Compliance"]]
            else "Compliant",
            axis=1,
        )

        target.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(target, index=False)
        return df.to_dict(orient="records")
    except Exception as exc:
        return {"error": f"Agent 3 failed: {exc}"}
