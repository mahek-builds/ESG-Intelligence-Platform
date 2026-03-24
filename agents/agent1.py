import os
import sys
from pathlib import Path

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient
from agents.output_paths import ENV_FILE, get_agent_output_path, get_company_name


def _build_result(status, message, **extra):
    payload = {
        "status": status,
        "message": message,
    }
    payload.update(extra)
    return payload


def run_agent1(output_path=None):
    load_dotenv(ENV_FILE, override=True)
    db_name = get_company_name()
    target = Path(output_path) if output_path else get_agent_output_path(
        "agent1_operational_output",
        company_name=db_name,
    )
    target.parent.mkdir(parents=True, exist_ok=True)

    print("Agent 1: Fetching verified data from MongoDB...")

    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    collection_name = os.getenv("MONGO_COLLECTION", "raw_firm_data")

    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")

        collection = client[db_name][collection_name]
        raw_data = list(collection.find({}, {"_id": 0}))

        if not raw_data:
            return _build_result(
                "error",
                f"No data found in {db_name} -> {collection_name}. Please check your database.",
            )

        df = pd.DataFrame(raw_data).dropna().reset_index(drop=True)
        df.to_csv(target, index=False)

        print(f"Success: {len(df)} records saved to {target}")

        return _build_result(
            "success",
            "Data successfully fetched from MongoDB.",
            file_path=str(target),
            rows_processed=len(df),
            source_database=db_name,
            source_collection=collection_name,
        )
    except Exception as exc:
        return _build_result("error", f"Agent 1 failed: {exc}")


def sync_and_clean_pipeline(output_path=None):
    return run_agent1(output_path=output_path)


if __name__ == "__main__":
    print(run_agent1())
