import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("❌ DATABASE_URL not found. Check your .env file.")

engine = create_engine(DATABASE_URL)

def init_db():
    with engine.connect() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS samsung_phones (
            id SERIAL PRIMARY KEY,
            model_name TEXT UNIQUE,
            release_date TEXT,
            display TEXT,
            battery TEXT,
            camera_main TEXT,
            camera_selfie TEXT,
            ram TEXT,
            storage TEXT,
            price FLOAT,
            processor TEXT,
            os TEXT,
            weight TEXT,
            features TEXT
        )
        """))
        conn.commit()