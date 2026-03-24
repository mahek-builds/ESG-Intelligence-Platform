import os
import pandas as pd
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv()

def run_agent1(user_mapping, output_path):

    # 1. Database Connection
    # Ensure COMPANY_DB_URL is set in your .env
    DB_URL = os.getenv("COMPANY_DB_URL") 
    engine = create_engine(DB_URL)
    
    try:
        # 2. VALIDATION: Check if the user's typed column names actually exist
        inspector = inspect(engine)
        db_columns = [col['name'] for col in inspector.get_columns(user_mapping['table'])]
        
        # Check all mapped columns against the real database schema
        required_keys = [ 'year_col', 'ind_col', 'env_col', 'soc_col', 'gov_col', 'board_col']
        missing_columns = []
        
        for key in required_keys:
            col_name = user_mapping[key]
            if col_name not in db_columns:
                missing_columns.append(col_name)

        if missing_columns:
            return {
                "status": "error",
                "message": f"Mapping failed. The following columns do not exist in the database: {', '.join(missing_columns)}",
                "available_columns": db_columns
            }

        # 3. SQL ALIASING: Translating the database names into your project names
        # This ensures the CSV always has 'E_Score', 'S_Score', etc.
        query = f"""
        SELECT 
            {user_mapping['year_col']} AS Year,
            {user_mapping['ind_col']} AS Industry_Type,
            {user_mapping['env_col']} AS E_Score,
            {user_mapping['soc_col']} AS S_Score,
            {user_mapping['gov_col']} AS G_Score,
            {user_mapping['board_col']} AS Board_Independence
        FROM {user_mapping['table']}
        """

        print(f"Fetching and mapping data from {user_mapping['table']}...")
        df = pd.read_sql(query, engine)

        # 4. DATA CLEANING (Your Original Logic)
        df = df.dropna().reset_index(drop=True)

        # 5. SAVE TO CSV
        os.makedirs(output_path, exist_ok=True)
        output_file = os.path.join(output_path, "agent1_operational_output.csv")
        df.to_csv(output_file, index=False)
        
        return {
            "status": "success", 
            "message": "Data successfully fetched and mapped",
            "file_path": output_file
        }

    except Exception as e:
        return {
            "status": "error", 
            "message": f"System Error: {str(e)}"
        }

if __name__ == "__main__":
    # Test case: User typed 'b' for environment, but database only has 'e'
    form_data = {
        "table": "firm_metrics",
        "id_col": "Firm_ID",
        "year_col": "Year",
        "ind_col": "Industry_Type",
        "env_col": "b",  
        "soc_col": "S_Score",
        "gov_col": "G_Score",
        "board_col": "Board_Independence"
    }
    
    result = run_agent1(form_data, "outputs")
    print(result)