import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from database import engine, init_db

BASE_URL = "https://www.gsmarena.com"

def get_samsung_models():
    """Get list of Samsung phone models"""
    url = "https://www.gsmarena.com/samsung-phones-9.php"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        phones = []
        # Find all phone links in the makers section
        for link in soup.select(".makers ul li a")[:25]:  # Get first 25 phones
            phone_url = link.get("href")
            if phone_url:
                full_url = BASE_URL + "/" + phone_url
                phone_name = link.find("span").text.strip() if link.find("span") else link.text.strip()
                
                print(f"Found phone: {phone_name}")
                phones.append({
                    "name": phone_name,
                    "url": full_url
                })
        
        print(f"✅ Found {len(phones)} Samsung phones")
        return phones
    except Exception as e:
        print(f"❌ Error fetching phone list: {e}")
        return []

def extract_specs(phone):
    """Extract specifications from individual phone page"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"📱 Scraping: {phone['name']}")
        response = requests.get(phone["url"], headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        specs = {
            "model_name": phone["name"],
            "release_date": "",
            "display": "",
            "battery": "",
            "camera_main": "",
            "camera_selfie": "",
            "ram": "",
            "storage": "",
            "price": "",
            "processor": "",
            "os": "",
            "weight": "",
            "features": ""
        }
        
        # Find the specs list
        specs_list = soup.find("div", {"id": "specs-list"})
        if not specs_list:
            print(f"⚠️ No specs list found for {phone['name']}")
            return specs
        
        # Extract all specifications
        tables = specs_list.find_all("table")
        
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                th = row.find("th")
                td = row.find("td")
                
                if not th or not td:
                    continue
                
                key = th.text.strip().lower()
                value = td.text.strip()
                
                # Network -> Technology
                if "technology" in key:
                    specs["features"] += f"Network: {value} | "
                
                # Launch -> Announced
                elif "announced" in key:
                    specs["release_date"] = value
                
                # Body -> Weight
                elif "weight" in key:
                    specs["weight"] = value
                
                # Display -> Type
                elif "display" in key and "type" in key:
                    specs["display"] = value
                
                # Platform -> OS
                elif "os" in key:
                    specs["os"] = value
                
                # Platform -> Chipset
                elif "chipset" in key:
                    specs["processor"] = value
                
                # Memory -> Internal
                elif "internal" in key and ("ram" in key.lower() or "storage" in key.lower()):
                    # Parse RAM and storage from internal memory
                    parts = value.split(',')
                    if len(parts) >= 1:
                        specs["storage"] = parts[0].strip()
                    if len(parts) >= 2 and "ram" in parts[1].lower():
                        specs["ram"] = parts[1].strip()
                
                # Memory -> Card slot (features)
                elif "card slot" in key:
                    specs["features"] += f"Card slot: {value} | "
                
                # Main Camera
                elif "main camera" in key:
                    # Try to get camera details
                    camera_row = row.find_next_sibling("tr")
                    if camera_row and camera_row.find("td"):
                        camera_details = camera_row.find("td").text.strip()
                        specs["camera_main"] = f"{value} - {camera_details}"
                    else:
                        specs["camera_main"] = value
                
                # Selfie Camera
                elif "selfie camera" in key:
                    camera_row = row.find_next_sibling("tr")
                    if camera_row and camera_row.find("td"):
                        camera_details = camera_row.find("td").text.strip()
                        specs["camera_selfie"] = f"{value} - {camera_details}"
                    else:
                        specs["camera_selfie"] = value
                
                # Battery
                elif "battery" in key:
                    battery_row = row.find_next_sibling("tr")
                    if battery_row and battery_row.find("td"):
                        battery_details = battery_row.find("td").text.strip()
                        specs["battery"] = f"{value} - {battery_details}"
                    else:
                        specs["battery"] = value
        
        # Try to find price from various places
        price_elem = soup.find("div", {"class": "price"})
        if price_elem:
            specs["price"] = price_elem.text.strip()
        
        # Also check for "Estimated" or "Expected" price
        for elem in soup.find_all(string=re.compile(r'\$\d+')):
            if elem and '$' in elem:
                specs["price"] = elem.strip()
                break
        
        print(f"✅ Successfully scraped {phone['name']}")
        time.sleep(1)  # Be respectful to the server
        
        return specs
        
    except Exception as e:
        print(f"❌ Error scraping {phone['name']}: {e}")
        return specs

def scrape_and_store():
    """Main function to scrape all phones and store in database"""
    print("🚀 Starting Samsung phone scraper...")
    
    # Initialize database
    init_db()
    
    # Get list of phones
    phones = get_samsung_models()
    if not phones:
        print("❌ No phones found to scrape")
        return
    
    data = []
    successful = 0
    
    for i, phone in enumerate(phones, 1):
        try:
            print(f"\n[{i}/{len(phones)}] ", end="")
            specs = extract_specs(phone)
            
            # Only add if we got at least some data
            if any(specs[key] for key in specs if key != "model_name"):
                data.append(specs)
                successful += 1
            else:
                print(f"⚠️ No data extracted for {phone['name']}")
                
        except Exception as e:
            print(f"❌ Failed to scrape {phone['name']}: {e}")
            continue
    
    if data:
        # Convert to DataFrame and save
        df = pd.DataFrame(data)
        
        # Clean up empty strings
        df = df.replace('', pd.NA)
        
        # Save to database
        df.to_sql("samsung_phones", engine, if_exists="replace", index=False)
        
        print(f"\n✅ Scraping complete!")
        print(f"📊 Successfully scraped {successful} out of {len(phones)} phones")
        print(f"💾 Data saved to database")
        
        # Show sample
        print("\n📋 Sample of scraped data:")
        print(df[['model_name', 'display', 'battery', 'camera_main', 'price']].head())
    else:
        print("❌ No data was successfully scraped")

if __name__ == "__main__":
    scrape_and_store()