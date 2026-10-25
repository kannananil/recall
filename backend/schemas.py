"""
Pydantic models for request/response validation.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field, ConfigDict


class BookmarkCreate(BaseModel):
    """Schema for creating a new bookmark."""
    url: str = Field(..., max_length=2048, description="URL of the article")
    title: Optional[str] = Field(None, max_length=512, description="Title of the article")
    content_text: Optional[str] = Field(None, description="Extracted article text")


class TagResponse(BaseModel):
    """Schema for tag response."""
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class BookmarkResponse(BaseModel):
    """Schema for bookmark response."""
    id: int
    url: str
    title: Optional[str]
    domain: Optional[str]
    summary: Optional[str]
    key_points: Optional[List[str]]
    category: Optional[str]
    estimated_read_minutes: Optional[int]
    processing_status: str
    error_message: Optional[str]
    saved_at: datetime
    processed_at: Optional[datetime]
    tags: List[TagResponse] = []

    model_config = ConfigDict(from_attributes=True)


class BookmarkListResponse(BaseModel):
    """Schema for paginated bookmark list response."""
    bookmarks: List[BookmarkResponse]
    total: int
    page: int
    page_size: int


class SearchResponse(BaseModel):
    """Schema for search results."""
    bookmarks: List[BookmarkResponse]
    total: int
    query: str


class StatsResponse(BaseModel):
    """Schema for application statistics."""
    total_bookmarks: int
    pending: int
    processing: int
    completed: int
    failed: int


class LLMMetadata(BaseModel):
    """Schema for LLM-generated metadata."""
    summary: str = Field(..., description="2-3 sentence summary of the article")
    key_points: List[str] = Field(..., description="3-5 main takeaways")
    category: str = Field(..., description="Single category (e.g., Technology, Science)")
    tags: List[str] = Field(..., max_length=5, description="3-5 relevant tags")
    estimated_read_minutes: int = Field(..., ge=1, le=120, description="Estimated reading time")
