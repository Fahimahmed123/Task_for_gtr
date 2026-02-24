# Algorithmic Trading Adventure & Samsung Phone Advisor

Two Python projects demonstrating algorithmic trading strategies and a smart phone advisor system with RAG and multi-agent capabilities.

## 📁 Repository Structure

.
├── task1_algorithmic_trading/
│ ├── task1.ipynb
│ 
│ 
├── task2_samsung_advisor/
│ ├── main.py
│ ├── database.py
│ ├── rag_system.py
│ ├── scrapper2.py
│ ├── templates/
│ │ └── index.html
│ ├── requirements.txt
│ └── README.md
├── run_all.sh
└── README.md (this file)



---

## Task 1: Algorithmic Trading Adventure

A class-based trading strategy tool that analyzes stock data and identifies golden cross opportunities.

### Features
- Fetches historical stock data using yfinance
- Calculates 50-day and 200-day moving averages
- Identifies golden cross (bullish) and death cross (bearish) signals
- Manages trades with a $5000 budget
- Calculates profit/loss automatically

### How to Run

```bash
cd task1_algorithmic_trading

# Install dependencies
pip install -r requirements.txt

# Run the trading strategy
python trading_strategy.py

Example Output


📈 Analyzing AAPL from 2018-01-01 to 2023-12-31
💰 Initial Budget: $5000.00

🔍 Golden Cross detected on 2020-04-15!
✅ Bought 45 shares at $110.23 each

🔍 Position closed on 2020-09-02
✅ Sold 45 shares at $134.18 each
📊 Profit: $1077.75

🏁 Final Balance: $6077.75

Task 2: Samsung Phone Advisor

A natural language query system for Samsung phones using RAG (Retrieval-Augmented Generation) and multi-agent architecture.
Features

    Web scraping from GSMarena Bangladesh

    PostgreSQL database storage

    RAG-based semantic search

    Multi-agent system for intent recognition

    FastAPI web interface

    Natural language queries

Prerequisites

    PostgreSQL installed and running

    Python 3.8+

Setup Instructions
1. Database Setup


# Login to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE samsung_db;
CREATE USER samsung_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE samsung_db TO samsung_user;
\q

2. Configure Environment

Create .env file in task2_samsung_advisor/:

DATABASE_URL=postgresql://samsung_user:password@localhost:5432/samsung_db

3. Install Dependencies

cd task2_samsung_advisor
pip install -r requirements.txt

4. Run the Application

# Option 1: Run the complete setup script
python run.py

# Option 2: Run steps manually

# Step 1: Scrape phone data
python scraper.py

# Step 2: Start the web server
uvicorn main:app --reload

5. Access the Application

Open your browser and navigate to:

    Web Interface: http://localhost:8000

    API Documentation: http://localhost:8000/docs

Example Queries

Try these questions in the web interface:

    "What are the specs of Samsung Galaxy S23 Ultra?"

    "Compare Galaxy S23 Ultra and S22 Ultra"

    "Which Samsung phone has the best battery under 50000 taka?"

    "Recommend a phone with good camera under 30000"

    "Show me all phones with 6000mAh battery"

API Usage

# Query the API directly
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Compare Galaxy S23 Ultra and S22 Ultra"}'

🚀 Running Everything with One Script

Use the provided run_all.sh script to run both tasks:
bash

# Make the script executable
chmod +x run_all.sh

# Run everything
./run_all.sh

📹 Video Demonstration

Watch the video demonstration here:  [GoogleDriveLink](https://drive.google.com/drive/folders/12yO3XIQNFhOEFGfNo6Hvkt-XY0LPz0Od?usp=sharing)

The video shows:

    Task 1: Algorithmic trading strategy execution

    Task 2: Samsung Phone Advisor web interface and queries

    Both tasks running successfully

🛠️ Requirements
Task 1

    Python 3.8+

    yfinance

    pandas

    numpy

Task 2

    Python 3.8+

    PostgreSQL

    fastapi

    uvicorn

    sqlalchemy

    pandas

    requests

    beautifulsoup4

    sentence-transformers

    faiss-cpu

    jinja2

📊 Dataset

The Samsung phone dataset is scraped from GSMarena Bangladesh. It includes:

    100+ Samsung phone models

    Full specifications (display, battery, camera, etc.)

    Prices in Bangladesh Taka

    Release dates and status

