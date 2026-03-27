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
FALLBACK_MAPPING = {
    "Year": ["Year", "fiscal_year"],
    "Industry_Type": ["Industry_Type", "sector"],
    "E_Score": ["E_Score", "e_score_raw"],
    "S_Score": ["S_Score", "s_score_raw"],
    "G_Score": ["G_Score", "g_score_raw"],
    "ROA": ["ROA", "roa_pct"],
    "ROE": ["ROE", "roe_pct"],
    "Net Profit Margin": ["Net Profit Margin", "Net_Profit_Margin", "net_margin"],
    "Board_Independence": ["Board_Independence", "Board_Independence (%)", "board_indep_pct"],
}

def send_to_frontend(emit_callback, event_name, data):
    try:
        emit_callback(event_name, data)
        print(f"Websocket: Event '{event_name}' emitted for Firm: {data.get('Firm_ID')}")
    except Exception as e:
        print(f"Websocket Error: {e}")


def _load_mapping_file(db_name, firm_id_filter):
    candidate_names = []
    for name in [f"{db_name}_mapping.json", f"{firm_id_filter}_mapping.json" if firm_id_filter else None]:
        if name and name not in candidate_names:
            candidate_names.append(name)

    for file_name in candidate_names:
        mapping_file = CONFIG_DIR / file_name
        if mapping_file.exists():
            with open(mapping_file, "r", encoding="utf-8") as file_obj:
                return json.load(file_obj), mapping_file

    return None, None


def _standardize_document(raw_doc, client_mapping=None):
    standardized_data = {}

    if client_mapping:
        standardized_data.update({standard: raw_doc.get(source) for standard, source in client_mapping.items()})

    for column, aliases in FALLBACK_MAPPING.items():
        if standardized_data.get(column) is not None:
            continue
        for alias in aliases:
            if alias in raw_doc and raw_doc.get(alias) is not None:
                standardized_data[column] = raw_doc.get(alias)
                break

    for column in REQUIRED_COLUMNS + OPTIONAL_COLUMNS:
        standardized_data.setdefault(column, None)

    standardized_data["Firm_ID"] = raw_doc.get("Firm_ID") or raw_doc.get("firm_id")
    return standardized_data

def run_agent1_premium(emit_callback):
    # Fetching directly from your .env
    db_name = os.getenv("MONGO_DB_NAME", "company_database")
    firm_id_filter = os.getenv("MONGO_FIRM_ID") 
    uri = os.getenv("MONGO_URI")
    collection_name = os.getenv("MONGO_COLLECTION", "raw_firm_data")

    print(f"Agent 1 Premium: Real-time Listener started for DB: {db_name}")

    client_mapping, mapping_file = _load_mapping_file(db_name, firm_id_filter)
    if mapping_file:
        print(f"Agent 1 Premium: Using mapping file {mapping_file}")
    else:
        print(
            "Agent 1 Premium: No mapping file found. Using built-in fallback aliases for common raw_firm_data fields."
        )

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
                    
                    standardized_data = _standardize_document(raw_doc, client_mapping=client_mapping)
                    standardized_data["Firm_ID"] = standardized_data.get("Firm_ID") or firm_id_filter
                    standardized_data["Sync_Time"] = time.strftime('%H:%M:%S')

                    send_to_frontend(emit_callback, 'agent1_live_operational', standardized_data)

        except Exception as e:
            print(f"Connection lost: {e}. Retrying...")
            if client: client.close()
            time.sleep(5)
