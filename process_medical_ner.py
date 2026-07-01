import pathlib
import json
import re
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

def extract_medical_entities(text):
    """
    An optimized medical entity parser designed to catch products, 
    categories, and prices directly from regional Telegram post patterns.
    """
    # Regex Patterns tailored for clinical data formats
    price_pattern = r'\b\d+(?:\.\d+)?\s?(?:ETB|Birr|usd|\$)\b'
    
    # Common medical/product keywords found in the pipeline channels
    known_products = [
        "Amoxicillin", "Paracetamol", "CeraVe", "Cleanser", "Syrup", 
        "Capsules", "Insulin", "Metformin", "Ibuprofen", "Augmentin"
    ]
    known_categories = [
        "Antibiotics", "Analgesics", "Skincare", "Cosmetics", "Pharma", "Medical"
    ]
    
    # Find matching elements
    prices = re.findall(price_pattern, text, re.IGNORECASE)
    products = [prod for prod in known_products if prod.lower() in text.lower()]
    categories = [cat for cat in known_categories if cat.lower() in text.lower()]
    
    return {
        "products": products if products else ["Unknown Product"],
        "categories": categories if categories else ["General"],
        "prices": prices if prices else ["Contact for Price"]
    }

def run_ner_and_vector_store():
    print("🚀 Initializing Task 3: Network-Independent NER & Vector Storage Pipeline...")
    
    # 1. Load Embedding Model (Lightweight, ~90MB - handles local fallback cleanly)
    print("📦 Loading Local Semantic Embedding Engine...")
    embed_model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

    # 2. Sample Unstructured Raw Message Entries from Telegram Stream
    raw_messages = [
        {"id": 1, "channel": "CheMed123", "text": "Available now: Amoxicillin 500mg capsules. Category: Antibiotics. Price: 450 ETB per pack."},
        {"id": 2, "channel": "tikvahpharma", "text": "New stock warning! Paracetamol Syrup for kids. Category: Analgesics. Only 120 ETB."},
        {"id": 3, "channel": "lobelia4cosmetics", "text": "CeraVe Hydrating Cleanser back in stock. Category: Skincare. Price: 1800 ETB."}
    ]

    processed_records = []
    corpus_texts = []

    print("\n🔍 Extracting Named Entities (Products, Categories, Prices)...")
    for msg in raw_messages:
        text = msg["text"]
        print(f"📄 Processing Text ID [{msg['id']}]: '{text}'")
        
        # Run local extraction logic
        entities = extract_medical_entities(text)
        
        # Structure record layout
        record = {
            "id": msg["id"],
            "channel": msg["channel"],
            "raw_text": text,
            "extracted_entities": {
                "products": entities["products"],
                "categories": entities["categories"],
                "prices": entities["prices"]
            }
        }
        processed_records.append(record)
        
        # String representing document context inside the vector index matrix
        corpus_texts.append(f"Channel: {msg['channel']} | Content: {text} | Entities: {entities['products']}")

    # 3. Generating Dense Text Embeddings
    print("\n🧬 Generating Dense Text Embeddings...")
    embeddings = embed_model.encode(corpus_texts, show_progress_bar=False)
    embeddings_matrix = np.array(embeddings).astype("float32")
    
    # 4. Initialize and Populate FAISS Vector Index
    dimension = embeddings_matrix.shape[1]
    print(f"⚡ Creating FAISS Index (FlatL2 Indexing, Dimension Size: {dimension})...")
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_matrix)
    
    # 5. Persist Everything Locally to Disk
    project_root = pathlib.Path(__file__).parent.resolve()
    storage_dir = project_root / "data" / "processed"
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    # Write files
    faiss.write_index(index, str(storage_dir / "medical_warehouse.index"))
    with open(storage_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(processed_records, f, indent=4)

    print(f"\n✅ Task 3 Successfully Completed! Stored vector index and metadata records in: {storage_dir}")

if __name__ == "__main__":
    run_ner_and_vector_store()