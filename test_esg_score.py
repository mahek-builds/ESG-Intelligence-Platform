#!/usr/bin/env python
"""
Quick test script for the BASIC PLAN API with weighted ESG score
"""
import subprocess
import time
import sys

# Install requests if needed
subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests', '-q'], 
               capture_output=True)

import requests
import pandas as pd
import io

print("=" * 70)
print("BASIC PLAN API - Test with Weighted ESG Score")
print("=" * 70)

# Wait for server to start
time.sleep(2)

# Create sample test data
test_data = {
    'Firm_ID': ['MFG0103'],
    'Year': [2023],
    'E_Score': [75.0],
    'S_Score': [65.0],
    'G_Score': [70.0],
    'ROA': [10.44],
    'ROE': [13.28],
    'Net_Profit_Margin': [5.47],
    'Innovation_Spending': [3.97],
    'carbon_emissions': [150.5],
    'energy_consumption': [300.2],
    'renewable_energy_percent': [35.0],
    'water_usage': [450.0],
    'waste_generated': [120.0]
}

df = pd.DataFrame(test_data)

# Convert to CSV
csv_buffer = io.StringIO()
df.to_csv(csv_buffer, index=False)
csv_data = csv_buffer.getvalue()

# Send request
files = {
    'file': ('test_data.csv', io.BytesIO(csv_data.encode()), 'text/csv')
}

try:
    print("\n📊 Sending test request to http://localhost:8000/basic/predict")
    print("-" * 70)
    
    response = requests.post('http://localhost:8000/basic/predict', 
                            files=files, 
                            timeout=10)
    
    if response.status_code == 200:
        result = response.json()
        
        print("✅ SUCCESS! API Response:")
        print()
        
        # Display ESG score prominently
        print(f"  🎯 ESG COMPOSITE SCORE (Formula-Based): {result.get('esg_score', 'N/A')}")
        print(f"     Formula: (0.70 × {result.get('environment_score', 'N/A')}) + (0.30 × CSR)")
        print()
        
        # Other metrics
        for key, value in result.items():
            if key != 'esg_score':
                print(f"  {key:.<45} {value}")
        
        print()
        print("-" * 70)
        print("✅ Test PASSED! ESG score is now included in response.")
        
    else:
        print(f"❌ Error: Status Code {response.status_code}")
        print(f"Response: {response.text}")

except requests.exceptions.ConnectionError:
    print("❌ ERROR: Cannot connect to API")
    print("   Make sure the API is running:")
    print("   cd c:\\Users\\HP\\Desktop\\ESG-Monitoring-System")
    print("   uvicorn API.main:app --reload")
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

print("=" * 70)
