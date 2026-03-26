import random
from pymongo import MongoClient

def generate_full_test_database():
    print("Connecting to MongoDB...")
    client = MongoClient("mongodb://localhost:27017/")
    db = client["company_database"]

    # Clear old data
    db.company_info.drop()
    db.sustainability_logs.drop()
    db.finance_data.drop()

    companies = [
        {"firm_id": "TECH001", "sector": "Technology"},
        {"firm_id": "MFG002", "sector": "Manufacturing"},
        {"firm_id": "ENG003", "sector": "Energy"},
        {"firm_id": "HLT004", "sector": "Healthcare"},
        {"firm_id": "FIN005", "sector": "Finance"}
    ]

    company_info_data = []
    sustainability_data = []
    finance_data_list = []

    print("Generating 10 years of FULL data for 5 companies...")
    
    for comp in companies:
        # 1. Company Profile (Adding Firm Size)
        firm_size = random.randint(500, 5000)
        company_info_data.append({
            "firm_id": comp["firm_id"], 
            "sector": comp["sector"],
            "firm_size_employees": firm_size
        })
        
        for year in range(2014, 2024):
            # 2. Sustainability Data (Adding Total ESG & Board Independence)
            e_score = round(random.uniform(40.0, 95.0), 1)
            s_score = round(random.uniform(50.0, 95.0), 1)
            g_score = round(random.uniform(60.0, 98.0), 1)
            
            sustainability_data.append({
                "firm_id": comp["firm_id"],
                "fiscal_year": year,
                "e_score_raw": e_score,
                "s_score_raw": s_score,
                "g_score_raw": g_score,
                "board_indep_pct": round(random.uniform(50.0, 95.0), 1)
            })
            
            # 3. Finance Data (Adding Revenue, Cost, Innovation)
            revenue = round(random.uniform(100.0, 1000.0), 1)
            op_cost = round(revenue * random.uniform(0.6, 0.85), 1) # Cost is 60-85% of revenue
            
            finance_data_list.append({
                "firm_id": comp["firm_id"],
                "fiscal_year": year,
                "roa_pct": round(random.uniform(2.0, 18.0), 1),
                "roe_pct": round(random.uniform(5.0, 25.0), 1),
                "net_margin": round(random.uniform(4.0, 22.0), 1),
                "revenue_mil": revenue,
                "operating_cost_mil": op_cost,
                "innovation_spend_mil": round(revenue * random.uniform(0.01, 0.05), 1) # 1-5% of revenue
            })

    db.company_info.insert_many(company_info_data)
    db.sustainability_logs.insert_many(sustainability_data)
    db.finance_data.insert_many(finance_data_list)

    print("Success! Database is fully loaded with all expanded columns.")

if __name__ == "__main__":
    generate_full_test_database()