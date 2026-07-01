from pydantic import BaseModel, ConfigDict
from typing import List, Dict

class TopProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product_name: str
    mention_count: int

class ChannelActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    channel_name: str
    total_posts: int
    avg_posts_per_day: float

class MessageSearchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    message_id: int
    channel: str
    text: str
    date: str

class VisualContentStatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    channel_name: str
    total_images_processed: int
    detected_objects_summary: Dict[str, int]