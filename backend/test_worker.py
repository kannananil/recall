"""
Test script for the background worker.
"""
from database import SessionLocal
from models import ProcessingJob, Bookmark
from worker import process_bookmark

def test_worker_processing():
    """Test processing a single bookmark."""
    db = SessionLocal()
    
    try:
        # Get first pending job
        job = db.query(ProcessingJob).filter(
            ProcessingJob.status == 'pending'
        ).first()
        
        if not job:
            print("❌ No pending jobs found")
            return
        
        print(f"🚀 Testing worker with bookmark {job.bookmark_id}")
        print(f"   Title: {job.bookmark.title}")
        print(f"   URL: {job.bookmark.url}")
        print()
        
        # Process the bookmark
        success = process_bookmark(db, job)
        
        if success:
            # Refresh bookmark to get updated data
            db.refresh(job.bookmark)
            
            print("\n✅ Worker test successful!")
            print(f"   Status: {job.bookmark.processing_status}")
            print(f"   Summary: {job.bookmark.summary[:100]}...")
            print(f"   Category: {job.bookmark.category}")
            print(f"   Tags: {[tag.name for tag.name in job.bookmark.tags]}")
            print(f"   Key Points: {len(job.bookmark.key_points)} points")
            print(f"   Read Time: {job.bookmark.estimated_read_minutes} minutes")
        else:
            print("\n❌ Worker processing failed")
            print(f"   Error: {job.error_message}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_worker_processing()
