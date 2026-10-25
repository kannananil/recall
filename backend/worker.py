"""
Background worker for processing bookmarks with Ollama.
"""
import time
import json
import httpx
from datetime import datetime
from sqlalchemy import and_
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Bookmark, Tag, ProcessingJob, bookmark_tags
from schemas import LLMMetadata
from utils import truncate_content

# Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma:2b"
MAX_RETRIES = 2
POLL_INTERVAL = 5  # seconds
REQUEST_TIMEOUT = 60  # seconds


def create_llm_prompt(title: str, content: str) -> str:
    """
    Create prompt for LLM to generate metadata.
    """
    # Truncate content to avoid token limits
    truncated_content = truncate_content(content, max_length=4000)
    
    prompt = f"""You are a reading assistant. Analyze this article and respond with ONLY valid JSON in this exact format:
{{
  "summary": "2-3 sentence summary of the article",
  "key_points": ["point 1", "point 2", "point 3"],
  "category": "single category like Technology, Science, Business, etc.",
  "tags": ["tag1", "tag2", "tag3"],
  "estimated_read_minutes": 5
}}

Article title: {title or "No title"}
Article text: {truncated_content}

Respond ONLY with the JSON object, no other text."""
    
    return prompt


def call_ollama(prompt: str) -> dict:
    """
    Call Ollama API and return parsed JSON response.
    Raises exception on failure.
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    
    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            response = client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            # Extract the response text
            response_text = result.get("response", "")
            
            # Parse JSON from response
            metadata = json.loads(response_text)
            
            # Validate with Pydantic
            validated = LLMMetadata(**metadata)
            
            return validated.model_dump()
            
    except httpx.TimeoutException:
        raise Exception("Ollama request timed out")
    except httpx.HTTPError as e:
        raise Exception(f"Ollama HTTP error: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON response from Ollama: {str(e)}")
    except Exception as e:
        raise Exception(f"Ollama error: {str(e)}")


def get_or_create_tag(db: Session, tag_name: str) -> Tag:
    """
    Get existing tag or create new one.
    """
    tag = db.query(Tag).filter(Tag.name == tag_name.lower().strip()).first()
    
    if not tag:
        tag = Tag(name=tag_name.lower().strip())
        db.add(tag)
        db.flush()  # Flush to get ID without committing
    
    return tag


def process_bookmark(db: Session, job: ProcessingJob) -> bool:
    """
    Process a single bookmark with Ollama.
    Returns True on success, False on failure.
    """
    bookmark = job.bookmark
    
    try:
        print(f"Processing bookmark {bookmark.id}: {bookmark.title}")
        
        # Check if content exists
        if not bookmark.content_text or len(bookmark.content_text.strip()) < 50:
            raise Exception("Insufficient content to process")
        
        # Update job status to processing
        job.status = 'processing'
        bookmark.processing_status = 'processing'
        db.commit()
        
        # Create prompt
        prompt = create_llm_prompt(bookmark.title, bookmark.content_text)
        
        # Call Ollama
        print(f"  Calling Ollama for bookmark {bookmark.id}...")
        start_time = time.time()
        metadata = call_ollama(prompt)
        elapsed = time.time() - start_time
        print(f"  Ollama responded in {elapsed:.1f}s")
        
        # Update bookmark with metadata
        bookmark.summary = metadata['summary']
        bookmark.key_points = metadata['key_points']
        bookmark.category = metadata['category']
        bookmark.estimated_read_minutes = metadata['estimated_read_minutes']
        bookmark.processed_at = datetime.utcnow()
        
        # Add tags
        bookmark.tags.clear()  # Clear existing tags
        for tag_name in metadata['tags']:
            if tag_name and len(tag_name.strip()) > 0:
                tag = get_or_create_tag(db, tag_name)
                bookmark.tags.append(tag)
        
        # Update status
        bookmark.processing_status = 'completed'
        bookmark.error_message = None
        job.status = 'completed'
        job.error_message = None
        
        db.commit()
        
        print(f"✅ Successfully processed bookmark {bookmark.id}")
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error processing bookmark {bookmark.id}: {error_msg}")
        
        # Update job with error
        job.attempts += 1
        job.error_message = error_msg
        job.updated_at = datetime.utcnow()
        
        # Mark as failed if max retries reached
        if job.attempts >= MAX_RETRIES:
            job.status = 'failed'
            bookmark.processing_status = 'failed'
            bookmark.error_message = error_msg
            print(f"  Bookmark {bookmark.id} failed after {MAX_RETRIES} attempts")
        else:
            # Reset to pending for retry
            job.status = 'pending'
            bookmark.processing_status = 'pending'
            print(f"  Will retry bookmark {bookmark.id} (attempt {job.attempts}/{MAX_RETRIES})")
        
        db.commit()
        return False


def get_next_job(db: Session) -> ProcessingJob | None:
    """
    Get the next pending job to process.
    Uses SELECT FOR UPDATE to avoid race conditions.
    """
    try:
        # Find oldest pending job
        job = db.query(ProcessingJob).filter(
            ProcessingJob.status == 'pending'
        ).order_by(
            ProcessingJob.created_at.asc()
        ).with_for_update(skip_locked=True).first()
        
        return job
    except Exception as e:
        print(f"Error getting next job: {e}")
        return None


def run_worker():
    """
    Main worker loop.
    Continuously polls for pending jobs and processes them.
    """
    print("🚀 Starting Recall worker...")
    print(f"   Model: {MODEL_NAME}")
    print(f"   Poll interval: {POLL_INTERVAL}s")
    print(f"   Max retries: {MAX_RETRIES}")
    print()
    
    while True:
        db = SessionLocal()
        
        try:
            # Get next job
            job = get_next_job(db)
            
            if job:
                # Process the job
                process_bookmark(db, job)
            else:
                # No jobs available, wait before polling again
                time.sleep(POLL_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Worker stopped by user")
            break
        except Exception as e:
            print(f"❌ Worker error: {e}")
            time.sleep(POLL_INTERVAL)
        finally:
            db.close()


if __name__ == "__main__":
    run_worker()
