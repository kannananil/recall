"""
SQLAlchemy ORM models for Recall application.
"""
from datetime import datetime
from typing import List
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship
from database import Base


# Association table for many-to-many relationship between bookmarks and tags
bookmark_tags = Table(
    'bookmark_tags',
    Base.metadata,
    Column('bookmark_id', Integer, ForeignKey('bookmarks.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)


class Bookmark(Base):
    """
    Represents a saved article/bookmark.
    """
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048), nullable=False)
    normalized_url = Column(String(2048), index=True, nullable=False)
    title = Column(String(512), nullable=True)
    domain = Column(String(256), index=True, nullable=True)
    content_text = Column(Text, nullable=True)
    
    # AI-generated metadata
    summary = Column(Text, nullable=True)
    key_points = Column(JSON, nullable=True)  # Stored as JSON array
    category = Column(String(128), index=True, nullable=True)
    estimated_read_minutes = Column(Integer, nullable=True)
    
    # Status tracking
    processing_status = Column(
        String(32), 
        nullable=False, 
        default='pending',
        index=True
    )  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    saved_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    tags = relationship("Tag", secondary=bookmark_tags, back_populates="bookmarks")
    jobs = relationship("ProcessingJob", back_populates="bookmark", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Bookmark(id={self.id}, title='{self.title}', status='{self.processing_status}')>"


class Tag(Base):
    """
    Represents a tag that can be associated with bookmarks.
    """
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, nullable=False, index=True)
    
    # Relationships
    bookmarks = relationship("Bookmark", secondary=bookmark_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"


class ProcessingJob(Base):
    """
    Represents a background processing job for a bookmark.
    """
    __tablename__ = "processing_jobs"

    id = Column(Integer, primary_key=True, index=True)
    bookmark_id = Column(Integer, ForeignKey('bookmarks.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Job status
    status = Column(
        String(32), 
        nullable=False, 
        default='pending',
        index=True
    )  # pending, processing, completed, failed
    attempts = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    bookmark = relationship("Bookmark", back_populates="jobs")

    def __repr__(self):
        return f"<ProcessingJob(id={self.id}, bookmark_id={self.bookmark_id}, status='{self.status}')>"
