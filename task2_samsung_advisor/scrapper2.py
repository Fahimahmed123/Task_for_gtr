# samsung_bd_full_scraper.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from database import engine, init_db
from urllib.parse import urljoin
import random

BASE_URL = "https://www.gsmarena.com.bd"

def get_all_phone_links():
    """Get all Samsung phone links from the main listing page and pagination"""
    
    print("="*80)
    print("🇧🇩 SAMSUNG BANGLADESH FULL SPECS SCRAPER")
    print("="*80)
    print("📱 Step 1: Collecting all phone links...")
    
    all_links = []
    page_num = 1
    
    while True:
        url = f"{BASE_URL}/samsung/" if page_num == 1 else f"{BASE_URL}/samsung/{page_num}"
        print(f"\n📄 Scraping page {page_num}: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find all product thumbnails (each contains a phone)
            product_thumbs = soup.find_all("div", class_="product-thumb")
            
            if not product_thumbs:
                print("No more products found")
                break
            
            page_links = []
            for product in product_thumbs:
                try:
                    # Get the details link
                    link = product.find("a", href=True)
                    if not link:
                        continue
                    
                    href = link['href']
                    full_url = urljoin(BASE_URL, href)
                    
                    # Get phone name
                    name_div = product.find("div", class_="mobile_name")
                    phone_name = name_div.text.strip() if name_div else link.get('title', '')
                    
                    # Get price
                    price_div = product.find("div", class_="mobile_price")
                    price_text = price_div.text.strip() if price_div else ""
                    
                    # Get status
                    status_span = product.find("span", class_="dstatus")
                    status = status_span.text.strip() if status_span else ""
                    
                    if phone_name and "Samsung" in phone_name:
                        phone_info = {
                            'name': phone_name,
                            'url': full_url,
                            'price': price_text,
                            'status': status
                        }
                        page_links.append(phone_info)
                        print(f"  ✅ Found: {phone_name[:40]}...")
                        
                except Exception as e:
                    print(f"  ⚠️ Error parsing product: {e}")
                    continue
            
            all_links.extend(page_links)
            print(f"  📊 Found {len(page_links)} phones on page {page_num}")
            
            # Check if there's a next page
            pagination = soup.find("ul", class_="pagination")
            if pagination:
                next_link = pagination.find("a", text=re.compile(r"Next|»|›"))
                if not next_link:
                    break
            else:
                break
            
            page_num += 1
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            print(f"❌ Error on page {page_num}: {e}")
            break
    
    print(f"\n📊 Total unique phones found: {len(all_links)}")
    return all_links

def extract_specs_from_table(soup):
    """Extract specifications from the table_specs tables"""
    
    specs = {
        'battery': '',
        'battery_capacity': '',
        'battery_type': '',
        'charging': '',
        'camera_main': '',
        'camera_main_mp': '',
        'camera_selfie': '',
        'camera_selfie_mp': '',
        'display': '',
        'display_size': '',
        'display_type': '',
        'display_resolution': '',
        'ram': '',
        'storage': '',
        'processor': '',
        'chipset': '',
        'cpu': '',
        'gpu': '',
        'os': '',
        'os_version': '',
        'release_date': '',
        'launch_date': '',
        'weight': '',
        'dimensions': '',
        'sim': '',
        'water_resistant': '',
        'sensors': '',
        'colors': ''
    }
    
    # Find all specification tables
    spec_tables = soup.find_all("table", class_="table_specs")
    
    for table in spec_tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 2:
                key = cells[0].text.strip().lower()
                value = cells[1].text.strip()
                
                # Battery
                if "battery capacity" in key:
                    specs['battery_capacity'] = value
                    specs['battery'] = value
                    # Extract mAh number
                    mah_match = re.search(r'(\d+)\s*mAh', value)
                    if mah_match:
                        specs['battery'] = f"{mah_match.group(1)} mAh"
                elif "battery type" in key:
                    specs['battery_type'] = value
                elif "charging" in key:
                    specs['charging'] = value
                
                # Camera
                elif "primary camera" in key:
                    specs['camera_main'] = value
                    mp_match = re.search(r'(\d+)\s*MP', value)
                    if mp_match:
                        specs['camera_main_mp'] = mp_match.group(1)
                elif "secondary camera" in key:
                    specs['camera_selfie'] = value
                    mp_match = re.search(r'(\d+)\s*MP', value)
                    if mp_match:
                        specs['camera_selfie_mp'] = mp_match.group(1)
                
                # Display
                elif "display type" in key:
                    specs['display_type'] = value
                    specs['display'] = value
                elif "display size" in key:
                    specs['display_size'] = value
                    if not specs['display']:
                        specs['display'] = value
                elif "display resolution" in key:
                    specs['display_resolution'] = value
                
                # Memory
                elif "ram" in key:
                    specs['ram'] = value
                elif "memory internal" in key:
                    specs['storage'] = value
                
                # Processor
                elif "chipset" in key:
                    specs['chipset'] = value
                    specs['processor'] = value
                elif "cpu" in key:
                    specs['cpu'] = value
                elif "gpu" in key:
                    specs['gpu'] = value
                
                # OS
                elif "operating system" in key or "os" in key:
                    specs['os'] = value
                    version_match = re.search(r'(\d+(?:\.\d+)?)', value)
                    if version_match:
                        specs['os_version'] = version_match.group(0)
                
                # Launch
                elif "launch announcement" in key:
                    specs['launch_date'] = value
                elif "launch date" in key:
                    specs['release_date'] = value
                
                # Body
                elif "body weight" in key:
                    specs['weight'] = value
                elif "body dimensions" in key:
                    specs['dimensions'] = value
                elif "network sim" in key:
                    specs['sim'] = value
                elif "water resistant" in key:
                    specs['water_resistant'] = value
                
                # Features
                elif "sensors" in key:
                    specs['sensors'] = value
                elif "body color" in key:
                    specs['colors'] = value
    
    return specs

def scrape_phone_details(phone_info):
    """Scrape detailed specifications from individual phone page"""
    
    print(f"\n  🔍 Scraping: {phone_info['name'][:50]}...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(phone_info['url'], headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract specifications from tables
        specs = extract_specs_from_table(soup)
        
        # Combine with basic info
        phone_data = {
            'model_name': phone_info['name'],
            'price': phone_info['price'],
            'status': phone_info['status'],
            **specs  # Add all the extracted specs
        }
        
        # Try to extract price from the description if not in table
        if not phone_data['price']:
            price_p = soup.find("p", string=re.compile(r"price starts from BDT"))
            if price_p:
                price_match = re.search(r'BDT\.?\s*([\d,]+\.?\d*)', price_p.text)
                if price_match:
                    phone_data['price'] = f"৳ {price_match.group(1)}"
        
        print(f"    ✅ Got: Battery={phone_data['battery'][:20]}, Camera={phone_data['camera_main_mp']}MP, RAM={phone_data['ram']}")
        return phone_data
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return {
            'model_name': phone_info['name'],
            'price': phone_info['price'],
            'status': phone_info['status'],
            'battery': '', 'battery_capacity': '', 'battery_type': '', 'charging': '',
            'camera_main': '', 'camera_main_mp': '', 'camera_selfie': '', 'camera_selfie_mp': '',
            'display': '', 'display_size': '', 'display_type': '', 'display_resolution': '',
            'ram': '', 'storage': '', 'processor': '', 'chipset': '', 'cpu': '', 'gpu': '',
            'os': '', 'os_version': '', 'release_date': '', 'launch_date': '',
            'weight': '', 'dimensions': '', 'sim': '', 'water_resistant': '',
            'sensors': '', 'colors': ''
        }

def scrape_all_phones(limit=30):
    """Main function to scrape all phones with detailed specs"""
    
    # Initialize database
    init_db()
    
    # Step 1: Get all phone links
    all_links = get_all_phone_links()
    
    if not all_links:
        print("❌ No phone links found")
        return
    
    # Limit to specified number (default 30)
    if limit and limit < len(all_links):
        all_links = all_links[:limit]
        print(f"\n📊 Limiting to first {limit} phones")
    
    print(f"\n{'='*80}")
    print(f"📱 Step 2: Scraping detailed specs for {len(all_links)} phones")
    print(f"{'='*80}")
    
    # Step 2: Scrape details for each phone
    all_phones = []
    
    for idx, phone_info in enumerate(all_links, 1):
        print(f"\n[{idx}/{len(all_links)}] ", end="")
        
        phone_data = scrape_phone_details(phone_info)
        all_phones.append(phone_data)
        
        # Save progress periodically
        if idx % 10 == 0:
            temp_df = pd.DataFrame(all_phones)
            temp_df.to_sql("samsung_bd_temp", engine, if_exists="replace", index=False)
            print(f"\n💾 Saved progress ({idx} phones)")
        
        # Random delay to be respectful
        time.sleep(random.uniform(2, 4))
    
    # Create final DataFrame
    df = pd.DataFrame(all_phones)
    df = df.fillna('')
    
    # Save to database
    df.to_sql("samsung_phones_bd", engine, if_exists="replace", index=False)
    
    print(f"\n{'='*80}")
    print(f"✅ SCRAPING COMPLETE!")
    print(f"📊 Total phones: {len(df)}")
    print(f"{'='*80}")
    
    # Show statistics
    print("\n📊 DATA COLLECTED:")
    print("-"*50)
    for col in ['battery', 'ram', 'storage', 'camera_main_mp', 'processor']:
        filled = df[col].astype(bool).sum()
        print(f"{col}: {filled}/{len(df)} phones have data")
    
    # Show sample
    print("\n📋 SAMPLE PHONES WITH DETAILS:")
    print("-"*100)
    for idx, row in df.head(10).iterrows():
        print(f"\n📱 {idx+1}. {row['model_name']}")
        print(f"   💰 Price: {row['price']}")
        print(f"   🔋 Battery: {row['battery']}")
        print(f"   📸 Camera: {row['camera_main']} ({row['camera_main_mp']}MP)")
        print(f"   🖥️ Display: {row['display']}")
        print(f"   ⚡ Processor: {row['processor']}")
        print(f"   💾 RAM: {row['ram']}")
        print(f"   📦 Storage: {row['storage']}")
        print(f"   📊 Status: {row['status']}")
    
    return df

def update_main_database():
    """Update the main samsung_phones table with all the detailed data"""
    try:
        # Read detailed data
        bd_df = pd.read_sql("SELECT * FROM samsung_phones_bd", engine)
        
        # Map to main table columns
        main_df = pd.DataFrame()
        main_df['model_name'] = bd_df['model_name']
        main_df['price'] = bd_df['price']
        main_df['battery'] = bd_df['battery']
        main_df['camera_main'] = bd_df['camera_main']
        main_df['camera_selfie'] = bd_df['camera_selfie']
        main_df['display'] = bd_df['display']
        main_df['ram'] = bd_df['ram']
        main_df['storage'] = bd_df['storage']
        main_df['processor'] = bd_df['processor']
        main_df['os'] = bd_df['os']
        main_df['release_date'] = bd_df['release_date']
        main_df['weight'] = bd_df['weight']
        main_df['features'] = f"Status: {bd_df['status']} | Sensors: {bd_df['sensors']} | Colors: {bd_df['colors']}"
        
        # Save to main table
        main_df.to_sql("samsung_phones", engine, if_exists="replace", index=False)
        
        print(f"\n✅ Main database updated with {len(main_df)} phones")
        print("\n📱 SAMPLE FROM MAIN DATABASE:")
        print(main_df[['model_name', 'price', 'battery', 'camera_main', 'ram']].head(10).to_string())
        
    except Exception as e:
        print(f"❌ Error updating main database: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--update":
            update_main_database()
        elif sys.argv[1] == "--view":
            df = pd.read_sql("SELECT * FROM samsung_phones_bd", engine)
            print(df[['model_name', 'price', 'battery', 'camera_main', 'ram', 'storage']].head(30).to_string())
        elif sys.argv[1] == "--limit":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            df = scrape_all_phones(limit=limit)
            
            if df is not None and len(df) > 0:
                print("\n" + "="*80)
                response = input("\n💾 Save to main database? (yes/no): ")
                if response.lower() == 'yes':
                    update_main_database()
    else:
        # Run with default limit of 30
        df = scrape_all_phones(limit=30)
        
        if df is not None and len(df) > 0:
            print("\n" + "="*80)
            response = input("\n💾 Save to main database? (yes/no): ")
            if response.lower() == 'yes':
                update_main_database()