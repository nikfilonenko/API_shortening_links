from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.db.base import BaseModel

class ShortenedUrl(BaseModel):
    __tablename__ = "short_urls"

    url_id = Column(Integer, primary_key=True, index=True)
    short_key = Column(String(50), unique=True, index=True, nullable=False)
    full_url = Column(String, nullable=False)
    custom_key = Column(String(50), unique=True, index=True, nullable=True)
    category = Column(String(50), nullable=True)
    creation_time = Column(DateTime, server_default=func.now())
    expiry_time = Column(DateTime, nullable=True)
    hit_count = Column(Integer, default=0)
    last_hit_time = Column(DateTime, nullable=True)
    auto_extend = Column(Boolean, default=False)
    creator_id = Column(Integer, ForeignKey("accounts.account_id"), nullable=True)

class UrlVisit(BaseModel):
    __tablename__ = "url_visits"

    visit_id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, ForeignKey("short_urls.url_id"), nullable=False)
    visit_date = Column(DateTime, server_default=func.now())
    visitor_ip = Column(String(50), nullable=True)
    visitor_agent = Column(String, nullable=True)

class UrlArchive(BaseModel):
    __tablename__ = "url_archive"

    archive_id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer)
    short_key = Column(String(50))
    full_url = Column(String)
    archive_time = Column(DateTime, server_default=func.now())
    archive_reason = Column(String(50), nullable=False)