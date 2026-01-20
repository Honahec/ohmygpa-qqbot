from pydantic import BaseModel
from typing import List, Optional


class Config(BaseModel):
    #  API Configuration
    api_key: str = "YOUR_API_KEY"
    base_url: str = "YOUR_API_BASE_URL"
    model: str = "YOUR_MODEL"

    # Forum API Configuration
    forum_api_url: str = "https://your-forum.com/api/v1/posts"
    forum_api_token: str = "YOUR_FORUM_TOKEN"

    # Plugin Behavior
    target_group_ids: List[int] = []  # Groups to listen to
    sync_keywords: List[str] = ["交易", "出", "收", "转让", "课", "换"]
