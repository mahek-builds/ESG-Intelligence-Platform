import time

import pandas as pd

from agents.agent1 import sync_and_clean_pipeline


def _clean_record(record):
    cleaned = {}
    for key, value in record.items():
        cleaned[key] = None if pd.isna(value) else value
    return cleaned


def run_agent1_premium(emit_callback, company_id="company3", output_dir=None):
    """
    Agent 1 Premium:
    Runs the same pipeline as Agent 1 and emits the resulting rows over WebSocket.
    """
    print(f"Agent 1 Premium: Running websocket sync for {company_id}...")

    result = sync_and_clean_pipeline(company_id=company_id, output_dir=output_dir)
    if result.get("status") != "success":
        emit_callback(
            "agent1_live_error",
            {
                "company_id": company_id,
                "message": result.get("message", "Agent 1 Premium failed."),
            },
        )
        return result

    df = pd.read_csv(result["file_path"])
    sync_time = time.strftime("%H:%M:%S")

    for record in df.to_dict(orient="records"):
        payload = _clean_record(record)
        payload["Sync_Time"] = sync_time
        payload["Type"] = "PREMIUM_WEBSOCKET"
        emit_callback("agent1_live_operational", payload)

    return result
