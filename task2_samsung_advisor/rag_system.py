import pandas as pd
import numpy as np
import faiss
import re
from sentence_transformers import SentenceTransformer
from database import engine

model = SentenceTransformer("all-MiniLM-L6-v2")

def clean_data(df):
    """Clean the dataframe before creating documents"""
    # Replace NaN with empty string
    df = df.fillna("")
    
    # Clean text fields
    text_columns = ['display', 'battery', 'camera_main', 'camera_selfie', 
                    'ram', 'storage', 'price', 'processor', 'os', 'features']
    
    for col in text_columns:
        if col in df.columns:
            # Convert to string and clean
            df[col] = df[col].astype(str)
            # Remove common unwanted patterns
            df[col] = df[col].apply(lambda x: re.sub(r'Prices.*?(\n|$)', '', x))
            df[col] = df[col].apply(lambda x: re.sub(r'These are the best offers.*?partners\.', '', x))
            df[col] = df[col].apply(lambda x: re.sub(r'Show all prices', '', x))
            # Trim whitespace
            df[col] = df[col].str.strip()
    
    return df

def load_documents():
    try:
        df = pd.read_sql("SELECT * FROM samsung_phones", engine)
        print(f"✅ Loaded {len(df)} phones from database")
        
        # Clean the data
        df = clean_data(df)
        
        # Create documents for embedding
        documents = df.apply(lambda x: f"{x['model_name']} {x['display']} {x['battery']} {x['camera_main']} {x['ram']} {x['storage']} {x['price']} {x['processor']}", axis=1).tolist()
        
        return df, documents
    except Exception as e:
        print(f"❌ Error loading documents: {e}")
        return pd.DataFrame(), []

# Load data
df, documents = load_documents()

# Create embeddings if we have data
if len(documents) > 0:
    embeddings = model.encode(documents)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    print(f"✅ Created FAISS index with {len(documents)} documents")
else:
    print("⚠️ No documents loaded, FAISS index not created")
    index = None

def retrieve(query, top_k=3):
    """Retrieve relevant phones based on query"""
    try:
        if index is None or len(documents) == 0:
            print("⚠️ No index or documents available")
            return df.to_dict('records')[:top_k]
        
        query_embedding = model.encode([query])
        distances, indices = index.search(np.array(query_embedding), min(top_k, len(documents)))
        
        # Convert to list of dictionaries
        results = df.iloc[indices[0]].to_dict('records')
        
        print(f"🔍 Query: '{query}'")
        print(f"📊 Found {len(results)} results")
            
        return results
    except Exception as e:
        print(f"❌ Error in retrieve: {e}")
        return df.to_dict('records')[:top_k]