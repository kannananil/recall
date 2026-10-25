"""
FastAPI main application for Recall.
"""
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from database import get_db, init_db, engine
from models import Bookmark, Tag, ProcessingJob
from schemas import (
    BookmarkCreate, 
    BookmarkResponse, 
    BookmarkListResponse,
    SearchResponse,
    StatsResponse
)
from utils import normalize_url, extract_domain, clean_text

# Create FastAPI app
app = FastAPI(
    title="Recall API",
    description="Local-first AI reading assistant",
    version="1.0.0"
)

# Configure CORS to allow requests from browser extension and dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "chrome-extension://*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Initialize database on startup."""
    init_db()
    print("✅ Database initialized")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Recall API",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/api/bookmarks", response_model=BookmarkResponse, status_code=201)
def create_bookmark(
    bookmark_data: BookmarkCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new bookmark.
    
    - Normalizes URL for deduplication
    - Returns existing bookmark if already saved
    - Creates processing job for new bookmarks
    """
    # Normalize URL for deduplication
    normalized_url = normalize_url(bookmark_data.url)
    
    # Check if bookmark already exists
    existing_bookmark = db.query(Bookmark).filter(
        Bookmark.normalized_url == normalized_url
    ).first()
    
    if existing_bookmark:
        return existing_bookmark
    
    # Extract domain
    domain = extract_domain(bookmark_data.url)
    
    # Clean content text
    content_text = clean_text(bookmark_data.content_text)
    
    # Create new bookmark
    new_bookmark = Bookmark(
        url=bookmark_data.url,
        normalized_url=normalized_url,
        title=bookmark_data.title,
        domain=domain,
        content_text=content_text,
        processing_status='pending',
        saved_at=datetime.utcnow()
    )
    
    db.add(new_bookmark)
    db.commit()
    db.refresh(new_bookmark)
    
    # Create processing job
    job = ProcessingJob(
        bookmark_id=new_bookmark.id,
        status='pending',
        created_at=datetime.utcnow()
    )
    
    db.add(job)
    db.commit()
    
    return new_bookmark


@app.get("/api/bookmarks", response_model=BookmarkListResponse)
def list_bookmarks(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by processing status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    db: Session = Depends(get_db)
):
    """
    List bookmarks with pagination and filters.
    """
    # Build query
    query = db.query(Bookmark)
    
    # Apply filters
    if status:
        query = query.filter(Bookmark.processing_status == status)
    
    if category:
        query = query.filter(Bookmark.category == category)
    
    if tag:
        query = query.join(Bookmark.tags).filter(Tag.name == tag)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering (newest first)
    bookmarks = query.order_by(Bookmark.saved_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return {
        "bookmarks": bookmarks,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@app.get("/api/bookmarks/{bookmark_id}", response_model=BookmarkResponse)
def get_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific bookmark by ID.
    """
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    return bookmark


@app.get("/api/search", response_model=SearchResponse)
def search_bookmarks(
    q: str = Query(..., min_length=1, description="Search query"),
    db: Session = Depends(get_db)
):
    """
    Search bookmarks by title, content, summary, or tags.
    Uses SQL LIKE for basic full-text search.
    """
    search_pattern = f"%{q}%"
    
    # Search in title, content_text, summary, and tags
    query = db.query(Bookmark).filter(
        (Bookmark.title.ilike(search_pattern)) |
        (Bookmark.content_text.ilike(search_pattern)) |
        (Bookmark.summary.ilike(search_pattern)) |
        (Bookmark.category.ilike(search_pattern))
    ).order_by(Bookmark.saved_at.desc())
    
    # Also search in tags
    tag_results = db.query(Bookmark).join(Bookmark.tags).filter(
        Tag.name.ilike(search_pattern)
    ).order_by(Bookmark.saved_at.desc()).all()
    
    # Combine results (deduplicate)
    all_results = query.all()
    result_ids = {b.id for b in all_results}
    
    for bookmark in tag_results:
        if bookmark.id not in result_ids:
            all_results.append(bookmark)
            result_ids.add(bookmark.id)
    
    return {
        "bookmarks": all_results,
        "total": len(all_results),
        "query": q
    }


@app.get("/api/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """
    Get application statistics.
    """
    total_bookmarks = db.query(Bookmark).count()
    pending = db.query(Bookmark).filter(Bookmark.processing_status == 'pending').count()
    processing = db.query(Bookmark).filter(Bookmark.processing_status == 'processing').count()
    completed = db.query(Bookmark).filter(Bookmark.processing_status == 'completed').count()
    failed = db.query(Bookmark).filter(Bookmark.processing_status == 'failed').count()
    
    return {
        "total_bookmarks": total_bookmarks,
        "pending": pending,
        "processing": processing,
        "completed": completed,
        "failed": failed
    }


@app.delete("/api/bookmarks/{bookmark_id}", status_code=204)
def delete_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a bookmark.
    """
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    db.delete(bookmark)
    db.commit()
    
    return None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
