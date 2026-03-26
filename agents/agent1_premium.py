import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_DIR = BASE_DIR / "config"

REQUIRED_COLUMNS = ["Year", "Industry_Type", "E_Score", "S_Score", "G_Score", "ROA", "ROE", "Net Profit Margin"]
OPTIONAL_COLUMNS = ["Board_Independence"]

def send_to_frontend(emit_callback, event_name, data):
    try:
        emit_callback(event_name, data)
        print(f"Websocket: Event '{event_name}' emitted for Firm: {data.get('Firm_ID')}")
    except Exception as e:
        print(f"Websocket Error: {e}")

def run_agent1_premium(emit_callback):
    # Fetching directly from your .env
    db_name = os.getenv("MONGO_DB_NAME", "company_database")
    firm_id_filter = os.getenv("MONGO_FIRM_ID") 
    uri = os.getenv("MONGO_URI")
    collection_name = os.getenv("MONGO_COLLECTION", "raw_firm_data")

    print(f"Agent 1 Premium: Real-time Listener started for DB: {db_name}")

    # Load mapping based on your MONGO_DB_NAME
    mapping_file = CONFIG_DIR / f"{db_name}_mapping.json"
    
    if not mapping_file.exists():
        print(f"Error: Mapping file {mapping_file} not found. Please create it.")
        return

    with open(mapping_file, "r", encoding="utf-8") as f:
        client_mapping = json.load(f)

    while True:
        client = None
        try:
            client = MongoClient(uri)
            db = client[db_name]
            collection = db[collection_name]

            # Watch filter: Only for the specific Firm_ID in your .env if provided
            match_logic = {"operationType": "insert"}
            if firm_id_filter:
                match_logic["fullDocument.Firm_ID"] = firm_id_filter

            pipeline = [{"$match": match_logic}]
            
            with collection.watch(pipeline, full_document="updateLookup") as stream:
                print(f"Connected to Atlas. Watching {collection_name}...")
                
                for change in stream:
                    raw_doc = change['fullDocument']
                    
                    # Standardize using mapping
                    standardized_data = {std: raw_doc.get(cli) for std, cli in client_mapping.items()}

                    # Fill missing columns
                    for col in REQUIRED_COLUMNS + OPTIONAL_COLUMNS:
                        if col not in standardized_data:
                            standardized_data[col] = None

                    standardized_data["Firm_ID"] = raw_doc.get("Firm_ID", firm_id_filter)
                    standardized_data["Sync_Time"] = time.strftime('%H:%M:%S')

                    send_to_frontend(emit_callback, 'agent1_live_operational', standardized_data)

        except Exception as e:
            print(f"Connection lost: {e}. Retrying...")
            if client: client.close()
            time.sleep(5)