# clean_existing_data.py
import pandas as pd
import re
from database import engine

def clean_database_data():
    """Clean the messy data in your database"""
    
    # Read current data
    df = pd.read_sql("SELECT * FROM samsung_phones", engine)
    
    print("="*80)
    print("🧹 CLEANING DATABASE DATA")
    print("="*80)
    print(f"📊 Found {len(df)} phones to clean")
    
    def clean_text_field(text):
        """Clean messy text fields"""
        if pd.isna(text) or text == "":
            return ""
        
        text = str(text)
        
        # Remove all the HTML/affiliate garbage
        garbage_patterns = [
            r'Prices\s*',
            r'Samsung\s+\w+\s*',
            r'These are the best offers.*?sales\.',
            r'We may get a commission.*?sales\.',
            r'Show all prices',
            r'128GB\s+\d+GB\s+RAM',
            r'64GB\s+\d+GB\s+RAM',
            r'256GB\s+\d+GB\s+RAM',
            r'512GB\s+\d+GB\s+RAM',
            r'£\s*\d+\.?\d*',
            r'€\s*\d+\.?\d*',
            r'₹\s*\d+\.?\d*',
            r'\$\s*\d+\.?\d*',
            r'From our affiliate partners',
            r'affiliate partners',
            r'commission',
            r'qualifying sales',
            r'\+',  # Remove plus signs used for multiline
            r'\|',  # Remove pipes
            r'_+',  # Remove underscores
        ]
        
        for pattern in garbage_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Clean up extra whitespace and newlines
        text = ' '.join(text.split())
        
        return text.strip()
    
    def extract_price(text):
        """Extract just the price number"""
        if pd.isna(text) or text == "":
            return ""
        
        text = str(text)
        
        # Look for dollar amounts
        dollar = re.search(r'\$\s*(\d+\.?\d*)', text)
        if dollar:
            return f"${dollar.group(1)}"
        
        # Look for euro
        euro = re.search(r'€\s*(\d+\.?\d*)', text)
        if euro:
            return f"€{euro.group(1)}"
        
        # Look for pound
        pound = re.search(r'£\s*(\d+\.?\d*)', text)
        if pound:
            return f"£{pound.group(1)}"
        
        # Look for rupee
        rupee = re.search(r'₹\s*(\d+\.?\d*)', text)
        if rupee:
            return f"₹{rupee.group(1)}"
        
        # Look for any number
        number = re.search(r'(\d+\.?\d*)', text)
        if number:
            return f"${number.group(1)}"
        
        return ""
    
    def extract_camera(text):
        """Clean camera field"""
        if pd.isna(text) or text == "":
            return ""
        
        text = str(text)
        if "Triple" in text or "Dual" in text or "Single" in text:
            # Keep just the camera type
            if "Triple" in text:
                return "Triple Camera"
            elif "Dual" in text:
                return "Dual Camera"
            elif "Single" in text:
                return "Single Camera"
        
        return clean_text_field(text)
    
    def extract_battery(text):
        """Clean battery field"""
        if pd.isna(text) or text == "":
            return ""
        
        text = str(text)
        if "Type - Charging" in text:
            return "Information not available"
        
        return clean_text_field(text)
    
    # Clean each column
    print("\n🔍 Cleaning data...")
    
    # Clean price
    if 'price' in df.columns:
        df['price'] = df['price'].apply(extract_price)
    
    # Clean camera
    if 'camera_main' in df.columns:
        df['camera_main'] = df['camera_main'].apply(extract_camera)
    
    # Clean battery
    if 'battery' in df.columns:
        df['battery'] = df['battery'].apply(extract_battery)
    
    # Clean other text fields
    text_fields = ['display', 'camera_selfie', 'ram', 'storage', 'processor', 'os', 'features']
    for field in text_fields:
        if field in df.columns:
            df[field] = df[field].apply(clean_text_field)
    
    # Show before and after
    print("\n📊 BEFORE CLEANING (First 3 phones):")
    for idx, row in df.head(3).iterrows():
        print(f"\n{row['model_name']}:")
        print(f"  Price: {row['price']}")
        print(f"  Battery: {row['battery']}")
        print(f"  Camera: {row['camera_main']}")
    
    # Save cleaned data
    print("\n💾 Saving cleaned data...")
    df.to_sql("samsung_phones", engine, if_exists="replace", index=False)
    
    print("\n✅ DATA CLEANED SUCCESSFULLY!")
    
    # Show cleaned data
    print("\n📊 AFTER CLEANING (First 3 phones):")
    for idx, row in df.head(3).iterrows():
        print(f"\n{row['model_name']}:")
        print(f"  Price: {row['price']}")
        print(f"  Battery: {row['battery']}")
        print(f"  Camera: {row['camera_main']}")
    
    return df

if __name__ == "__main__":
    clean_database_data()