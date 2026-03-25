import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_DIR = BASE_DIR / "config"

def run_agent1_premium(emit_callback, company_id="company3"):
    """
     PREMIUM AGENT 1: 
    Listens to MongoDB, applies Client-Specific Mapping, 
    and streams Standardized data via WebSockets.
    """
    print(f" Agent 1 Premium: Real-time Listener active for {company_id}...")

    # 1. Load the Client Mapping (The "Translation" dictionary)
    mapping_file = CONFIG_DIR / f"{company_id}_mapping.json"
    if not mapping_file.exists():
        print(f" Error: Mapping file missing for {company_id}")
        return

    with open(mapping_file, "r") as f:
        client_mapping = json.load(f)

    # 2. Setup MongoDB Connection
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", company_id)
    collection_name = os.getenv("MONGO_COLLECTION", "raw_firm_data")

    try:
        client = MongoClient(uri)
        collection = client[db_name][collection_name]

        # 3. Watch for Live Insertions
        with collection.watch([{"$match": {"operationType": "insert"}}]) as stream:
            for change in stream:
                raw_doc = change['fullDocument']
                
                # 4. Standardize the Data (Mapping Task)
                # We translate "environme" -> "E_Score", etc., based on the UI mapping
                standardized_data = {}
                for standard_col, client_col in client_mapping.items():
                    standardized_data[standard_col] = raw_doc.get(client_col)

                # Add Metadata
                standardized_data["Firm_ID"] = raw_doc.get("Firm_ID", "Unknown")
                standardized_data["Sync_Time"] = time.strftime('%H:%M:%S')
                standardized_data["Type"] = "PREMIUM_REALTIME_MAPPED"

                # 5. Emit via WebSocket Callback
                # Injected from main.py
                emit_callback('agent1_live_operational', standardized_data)
                
                print(f" [Agent 1 Premium] Streamed mapped data for: {standardized_data['Firm_ID']}")

    except Exception as e:
        print(f" Agent 1 Premium failed: {e}")
        time.sleep(5) 
        run_agent1_premium(emit_callback, company_id)