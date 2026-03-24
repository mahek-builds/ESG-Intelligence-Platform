from pymongo import MongoClient
from pprint import pprint

def fetch_and_print_data():
    print("🔌 Connecting to MongoDB...")
    
    # 1. Connect to your local MongoDB server
    client = MongoClient("mongodb://localhost:27017/")
    
    # 2. Target the exact database and collection from your screenshot
    db = client["company1"]
    collection = db["raw_firm_data"]
    
    # 3. Fetch all documents (dropping the internal MongoDB '_id' for a cleaner look)
    data = list(collection.find({}, {"_id": 0}))
    
    # 4. Display the results
    if not data:
        print("⚠️ No data found! Double-check your database name in Compass.")
        return

    print(f"✅ Successfully fetched {len(data)} records for Firm: {data[0].get('Firm_ID')}\n")
    
    # Print each record neatly
    for i, record in enumerate(data, 1):
        print(f"--- Record {i} (Year: {record.get('Year')}) ---")
        pprint(record)
        print("\n")

if __name__ == "__main__":
    fetch_and_print_data()