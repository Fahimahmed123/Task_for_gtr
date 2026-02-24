from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from rag_system import retrieve
import traceback
import re

app = FastAPI(title="Samsung Phone Advisor")

# Setup templates
templates = Jinja2Templates(directory="templates")

class Query(BaseModel):
    question: str


# ---------- HELPER FUNCTION TO CLEAN TEXT ----------

def clean_text(text):
    """Clean and format text to remove extra content"""
    if not text or text == "":
        return "N/A"
    
    # Convert to string if not already
    text = str(text)
    
    # Remove common unwanted patterns
    unwanted_patterns = [
        r'Prices.*?\n',
        r'These are the best offers.*?partners\.',
        r'We may get a commission.*?sales\.',
        r'Show all prices',
        r'₹.*?\d+',
        r'128GB.*?RAM',
        r'GB.*?RAM',
        r'\$.*?\d+',
        r'€.*?\d+',
    ]
    
    for pattern in unwanted_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove extra whitespace and newlines
    text = ' '.join(text.split())
    
    # Limit length and add ellipsis if too long
    if len(text) > 100:
        text = text[:100] + "..."
    
    return text.strip() or "N/A"

def extract_price(price_text):
    """Extract just the price value"""
    if not price_text:
        return "N/A"
    
    price_text = str(price_text)
    # Look for dollar amount
    dollar_match = re.search(r'\$\s*(\d+(?:\.\d{2})?)', price_text)
    if dollar_match:
        return f"${dollar_match.group(1)}"
    
    # Look for rupee amount
    rupee_match = re.search(r'₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)', price_text)
    if rupee_match:
        return f"₹{rupee_match.group(1)}"
    
    return clean_text(price_text)


# ---------- AGENT 1: INTENT EXTRACTOR ----------

def extract_intent(query):
    query = query.lower()
    
    if "compare" in query or "vs" in query or "versus" in query:
        return "comparison"
    elif "best" in query or "recommend" in query or "top" in query or "suggest" in query:
        return "recommendation"
    elif "under" in query or "budget" in query or "price" in query or "$" in query or "₹" in query:
        return "budget"
    else:
        return "specs"


# ---------- AGENT 2: RESPONSE GENERATOR ----------

def safe_get(phone, key, default="N/A"):
    """Safely get value from dictionary or string"""
    if isinstance(phone, dict):
        value = phone.get(key, default)
        if key == "price":
            return extract_price(value)
        else:
            return clean_text(value)
    else:
        return default

def generate_response(query, phones):
    try:
        intent = extract_intent(query)
        
        # Ensure phones is a list
        if not phones:
            return "No phones found matching your query. Please try a different question."
        
        # Handle budget queries
        if intent == "budget":
            response = "💰 **PHONES WITHIN YOUR BUDGET:**\n\n"
            
            # Try to extract budget from query
            budget_match = re.search(r'under\s*\$?(\d+)', query.lower())
            budget_match2 = re.search(r'(\d+)\s*\$', query.lower())
            budget_match3 = re.search(r'under\s*₹?(\d+)', query.lower())
            budget = None
            
            if budget_match:
                budget = int(budget_match.group(1))
            elif budget_match2:
                budget = int(budget_match2.group(1))
            elif budget_match3:
                budget = int(budget_match3.group(1))
            
            filtered_phones = []
            for p in phones:
                price = safe_get(p, 'price')
                # Try to convert price to number
                if price and price != "N/A":
                    try:
                        # Remove currency symbols and commas
                        price_clean = re.sub(r'[₹$,]', '', price)
                        price_num = float(price_clean)
                        
                        if budget and price_num <= budget:
                            filtered_phones.append((p, price_num))
                        elif not budget:
                            filtered_phones.append((p, price_num))
                    except:
                        pass
            
            # Sort by price
            filtered_phones.sort(key=lambda x: x[1])
            
            if filtered_phones:
                for i, (p, price_num) in enumerate(filtered_phones[:5], 1):
                    response += f"{i}. 📱 **{safe_get(p, 'model_name')}**\n"
                    response += f"   💰 Price: ${price_num:.2f}\n"
                    response += f"   🔋 Battery: {safe_get(p, 'battery')}\n"
                    response += f"   📸 Camera: {safe_get(p, 'camera_main')}\n"
                    response += f"   🖥️ Display: {safe_get(p, 'display')}\n\n"
            else:
                response += "No phones found within your budget. Here are some options:\n\n"
                for i, p in enumerate(phones[:3], 1):
                    response += f"{i}. 📱 **{safe_get(p, 'model_name')}**\n"
                    response += f"   💰 Price: {safe_get(p, 'price')}\n"
                    response += f"   🔋 Battery: {safe_get(p, 'battery')}\n\n"
            
            return response
        
        # Handle comparison
        elif intent == "comparison" and len(phones) >= 2:
            p1, p2 = phones[0], phones[1]
            return f"""
📊 **COMPARISON**

📱 **{safe_get(p1, 'model_name')}**:
• 📸 Camera: {safe_get(p1, 'camera_main')}
• 🔋 Battery: {safe_get(p1, 'battery')}
• 🖥️ Display: {safe_get(p1, 'display')}
• 💾 RAM: {safe_get(p1, 'ram')}
• 📦 Storage: {safe_get(p1, 'storage')}
• 💰 Price: {safe_get(p1, 'price')}
• ⚡ Processor: {safe_get(p1, 'processor')}

VS

📱 **{safe_get(p2, 'model_name')}**:
• 📸 Camera: {safe_get(p2, 'camera_main')}
• 🔋 Battery: {safe_get(p2, 'battery')}
• 🖥️ Display: {safe_get(p2, 'display')}
• 💾 RAM: {safe_get(p2, 'ram')}
• 📦 Storage: {safe_get(p2, 'storage')}
• 💰 Price: {safe_get(p2, 'price')}
• ⚡ Processor: {safe_get(p2, 'processor')}

💡 **Recommendation**:
The {safe_get(p1, 'model_name') if 'better' in query.lower() else safe_get(p2, 'model_name')} might be better for your needs. Consider your priorities for camera vs battery life.
"""
        
        # Handle recommendations
        elif intent == "recommendation":
            response = "🎯 **TOP RECOMMENDATIONS:**\n\n"
            for i, p in enumerate(phones[:5], 1):
                response += f"{i}. 📱 **{safe_get(p, 'model_name')}**\n"
                response += f"   • 🔋 Battery: {safe_get(p, 'battery')}\n"
                response += f"   • 📸 Camera: {safe_get(p, 'camera_main')}\n"
                response += f"   • 🖥️ Display: {safe_get(p, 'display')}\n"
                response += f"   • 💰 Price: {safe_get(p, 'price')}\n"
                response += f"   • ⚡ Processor: {safe_get(p, 'processor')}\n\n"
            return response
        
        # Handle specs
        else:
            p = phones[0]
            return f"""
📱 **{safe_get(p, 'model_name')} - DETAILED SPECIFICATIONS**

🖥️ **Display**: {safe_get(p, 'display')}
🔋 **Battery**: {safe_get(p, 'battery')}
📸 **Main Camera**: {safe_get(p, 'camera_main')}
🤳 **Selfie Camera**: {safe_get(p, 'camera_selfie')}
⚡ **Processor**: {safe_get(p, 'processor')}
💾 **RAM**: {safe_get(p, 'ram')}
📦 **Storage**: {safe_get(p, 'storage')}
💰 **Price**: {safe_get(p, 'price')}
📅 **Release Date**: {safe_get(p, 'release_date')}
⚖️ **Weight**: {safe_get(p, 'weight')}
📱 **OS**: {safe_get(p, 'os')}
✨ **Features**: {safe_get(p, 'features')}
"""
    except Exception as e:
        print(f"Error in generate_response: {e}")
        traceback.print_exc()
        return f"I encountered an error while processing your request. Please try a different question."


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ask")
async def ask(query: Query):
    try:
        print(f"\n📝 Received question: {query.question}")
        phones = retrieve(query.question)
        
        if not phones:
            return {"answer": "No phones found matching your query. Please try a different question."}
        
        answer = generate_response(query.question, phones)
        return {"answer": answer}
    except Exception as e:
        print(f"❌ Error in ask endpoint: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Samsung Phone Advisor API is running"}

@app.get("/debug/db")
async def debug_db():
    """Debug endpoint to check database content"""
    try:
        from rag_system import df
        if df.empty:
            return {"status": "no data", "message": "Database is empty"}
        
        # Clean the sample for display
        sample = df.head(3).to_dict('records')
        for record in sample:
            for key in record:
                if isinstance(record[key], str):
                    # Truncate long strings
                    if len(record[key]) > 100:
                        record[key] = record[key][:100] + "..."
        
        return {
            "status": "ok",
            "total_phones": len(df),
            "sample": sample,
            "columns": list(df.columns)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}