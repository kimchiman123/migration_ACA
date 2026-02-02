import pandas as pd
try:
    print("--- CHECKING COLUMNS ---")
    df_head = pd.read_csv('cleaned_merged_export_trends.csv', nrows=1)
    print("ALL COLUMNS:", df_head.columns.tolist())
    
    print("\n--- CHECKING PERIOD FORMATS ---")
    # Read period as string to check exact formatting
    df = pd.read_csv('cleaned_merged_export_trends.csv', dtype={'period': str})
    
    # Check 2022 data specifically
    periods = [str(p).strip() for p in df['period'].unique() if pd.notna(p)]
    periods_2022 = sorted([p for p in periods if '2022' in p])
    print("ALL 2022 PERIODS in CSV:", periods_2022)
    
    has_01 = '2022.01' in periods_2022
    has_1 = '2022.1' in periods_2022
    has_10 = '2022.10' in periods_2022
    
    print(f"Has 2022.01: {has_01}")
    print(f"Has 2022.1: {has_1}")
    print(f"Has 2022.10: {has_10}")
    
except Exception as e:
    print(f"Error: {e}")
