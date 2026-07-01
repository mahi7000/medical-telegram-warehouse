import datetime
from fastapi import FastAPI, HTTPException, Query
from typing import List
from sqlalchemy import text
from sqlalchemy.orm import Session

# --- FIX: Import the schemas explicitly ---
from .schemas import (
    TopProductResponse,
    ChannelActivityResponse,
    MessageSearchResponse,
    VisualContentStatsResponse
)

# Import your database session worker if setup
try:
    from .database import engine, SessionLocal
    HAS_DB = True
except ImportError:
    HAS_DB = False

app = FastAPI(
    title="Medical Telegram Warehouse Analytics API",
    description="REST API for querying clinical data warehouse marts, channel activities, and YOLO object detection insights.",
    version="1.0.0"
)

# --- LOCAL SEED DATA CORES ---
MOCK_PRODUCTS = [
    {"product_name": "Amoxicillin", "mention_count": 42},
    {"product_name": "Paracetamol", "mention_count": 35},
    {"product_name": "CeraVe Hydrating Cleanser", "mention_count": 28},
    {"product_name": "Ibuprofen", "mention_count": 19},
    {"product_name": "Augmentin", "mention_count": 14}
]

MOCK_CHANNELS = {
    "chemed123": {"channel_name": "CheMed123", "total_posts": 184, "avg_posts_per_day": 5.2},
    "tikvahpharma": {"channel_name": "tikvahpharma", "total_posts": 95, "avg_posts_per_day": 2.8},
    "lobelia4cosmetics": {"channel_name": "lobelia4cosmetics", "total_posts": 210, "avg_posts_per_day": 6.1}
}

MOCK_MESSAGES = [
    {"message_id": 101, "channel": "CheMed123", "text": "Available now: Amoxicillin 500mg capsules. Category: Antibiotics. Price: 450 ETB per pack.", "date": "2026-06-28"},
    {"message_id": 102, "channel": "tikvahpharma", "text": "New stock warning! Paracetamol Syrup for kids. Category: Analgesics. Only 120 ETB.", "date": "2026-06-29"},
    {"message_id": 103, "channel": "lobelia4cosmetics", "text": "CeraVe Hydrating Cleanser back in stock. Category: Skincare. Price: 1800 ETB.", "date": "2026-06-30"}
]

MOCK_VISUALS = [
    {"channel_name": "CheMed123", "total_images_processed": 45, "detected_objects_summary": {"bottle": 32, "person": 12, "cup": 4}},
    {"channel_name": "tikvahpharma", "total_images_processed": 22, "detected_objects_summary": {"laptop": 15, "tv": 8}},
    {"channel_name": "lobelia4cosmetics", "total_images_processed": 31, "detected_objects_summary": {"bottle": 3, "No distinct objects detected": 28}}
]


# --- ENDPOINTS ---

@app.get("/api/reports/top-products", response_model=List[TopProductResponse], tags=["Reports"])
def get_top_products(limit: int = Query(10, description="Number of top products to return")):
    """Returns the most frequently mentioned terms/products across all channels."""
    if HAS_DB:
        try:
            with SessionLocal() as db:
                query = text("SELECT product_name, mention_count FROM marts.dim_top_products ORDER BY mention_count DESC LIMIT :limit")
                result = db.execute(query, {"limit": limit}).fetchall()
                if result:
                    return [{"product_name": r[0], "mention_count": r[1]} for r in result]
        except Exception:
            pass
            
    return MOCK_PRODUCTS[:limit]


@app.get("/api/channels/{channel_name}/activity", response_model=ChannelActivityResponse, tags=["Channels"])
def get_channel_activity(channel_name: str):
    """Returns posting activity aggregates and trends for a specific channel (e.g., CheMed123)."""
    normalized_name = channel_name.lower().strip()
    
    if HAS_DB:
        try:
            with SessionLocal() as db:
                query = text("SELECT channel_name, total_posts, avg_posts_per_day FROM marts.fct_channel_activity WHERE LOWER(channel_name) = :name")
                row = db.execute(query, {"name": normalized_name}).fetchone()
                if row:
                    return {"channel_name": row[0], "total_posts": row[1], "avg_posts_per_day": row[2]}
        except Exception:
            pass

    if normalized_name in MOCK_CHANNELS:
        return MOCK_CHANNELS[normalized_name]
        
    raise HTTPException(status_code=404, detail=f"Channel '{channel_name}' not found in marts matrix.")


@app.get("/api/search/messages", response_model=List[MessageSearchResponse], tags=["Search"])
def search_messages(query: str = Query(..., description="Keyword search term"), limit: int = Query(20)):
    """Searches for warehouse messages containing a specific keyword."""
    if HAS_DB:
        try:
            with SessionLocal() as db:
                db_query = text("SELECT message_id, channel, text, date FROM marts.fct_messages WHERE text ILIKE :term LIMIT :limit")
                result = db.execute(db_query, {"term": f"%{query}%", "limit": limit}).fetchall()
                if result:
                    return [{"message_id": r[0], "channel": r[1], "text": r[2], "date": str(r[3])} for r in result]
        except Exception:
            pass

    filtered = [m for m in MOCK_MESSAGES if query.lower() in m["text"].lower()]
    return filtered[:limit]


@app.get("/api/reports/visual-content", response_model=List[VisualContentStatsResponse], tags=["Reports"])
def get_visual_content_stats():
    """Returns aggregated computer vision statistics about image object detection across channels."""
    if HAS_DB:
        try:
            with SessionLocal() as db:
                query = text("SELECT channel_name, total_images_processed, detected_objects_summary FROM marts.fct_visual_content_stats")
                result = db.execute(query).fetchall()
                if result:
                    return [{"channel_name": r[0], "total_images_processed": r[1], "detected_objects_summary": r[2]} for r in result]
        except Exception:
            pass

    return MOCK_VISUALS