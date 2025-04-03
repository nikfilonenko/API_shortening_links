from pydantic import BaseModel, HttpUrl, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict

class UrlBase(BaseModel):
    full_url: HttpUrl
    expiry_time: Optional[datetime] = None
    category: Optional[str] = None

class UrlCreate(UrlBase):
    custom_key: Optional[str] = Field(None, min_length=3, max_length=50)
    auto_extend: Optional[bool] = False

class UrlUpdate(BaseModel):
    full_url: Optional[HttpUrl] = None
    expiry_time: Optional[datetime] = None
    category: Optional[str] = None
    auto_extend: Optional[bool] = None

class UrlInfo(UrlBase):
    url_id: int
    short_key: str
    custom_key: Optional[str]
    creation_time: datetime
    hit_count: int
    last_hit_time: Optional[datetime]
    auto_extend: bool
    creator_id: Optional[int]

    class Config:
        from_attributes = True

class UrlStats(UrlInfo):
    daily_stats: Optional[List[Dict[str, int]]] = None
    hourly_stats: Optional[List[Dict[str, int]]] = None
    agent_stats: Optional[List[Dict[str, int]]] = None

class UrlSearchResult(BaseModel):
    short_key: str
    full_url: HttpUrl

class StatusResponse(BaseModel):
    status: str = Field(title='Status')

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "status": "App healthy"
                }
            ]
        }
    )