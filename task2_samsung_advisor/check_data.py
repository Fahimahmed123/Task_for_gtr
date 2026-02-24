# view_scraped_data.py
import pandas as pd
from database import engine

def view_scraped_data():
    """View the scraped data in a readable format"""
    
    df = pd.read_sql("SELECT * FROM samsung_phones", engine)
    
    print("="*100)
    print("📱 SCRAPED SAMSUNG PHONE DATA")
    print("="*100)
    
    print(f"\n📊 Total phones scraped: {len(df)}")
    
    # Show all phones with basic info
    print("\n📋 ALL PHONES:")
    print("-"*100)
    
    for idx, row in df.iterrows():
        print(f"\n{idx+1}. {row['model_name']}")
        
        # Show available data
        if pd.notna(row['price']) and row['price'] != "":
            print(f"   💰 Price: {str(row['price'])[:80]}")
        
        if pd.notna(row['battery']) and row['battery'] != "":
            print(f"   🔋 Battery: {str(row['battery'])[:80]}")
        
        if pd.notna(row['camera_main']) and row['camera_main'] != "":
            print(f"   📸 Camera: {str(row['camera_main'])[:80]}")
        
        if pd.notna(row['display']) and row['display'] != "":
            print(f"   🖥️ Display: {str(row['display'])[:80]}")
    
    # Show data quality
    print("\n📊 DATA QUALITY:")
    print("-"*50)
    
    for col in df.columns:
        if col != 'model_name':
            non_empty = df[col].notna().sum() + (df[col] != "").sum()
            print(f"{col}: {non_empty}/{len(df)} have data")

if __name__ == "__main__":
    view_scraped_data()