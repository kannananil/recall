"""
Simple test script to verify API functionality.
"""
import httpx
import json
from main import app
from database import init_db
from fastapi.testclient import TestClient

# Initialize database before creating client
init_db()

client = TestClient(app)

def test_root():
    """Test root endpoint."""
    response = client.get("/")
    print("✅ Root endpoint:", response.json())
    assert response.status_code == 200

def test_create_bookmark():
    """Test creating a bookmark."""
    bookmark_data = {
        "url": "https://fastapi.tiangolo.com/tutorial/first-steps/",
        "title": "First Steps - FastAPI",
        "content_text": "FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints. The key features are: Fast: Very high performance, on par with NodeJS and Go (thanks to Starlette and Pydantic). Fast to code: Increase the speed to develop features by about 200% to 300%. Fewer bugs: Reduce about 40% of human (developer) induced errors."
    }
    
    response = client.post("/api/bookmarks", json=bookmark_data)
    print("✅ Create bookmark:", response.status_code)
    print("   Response:", json.dumps(response.json(), indent=2))
    assert response.status_code == 201
    return response.json()

def test_list_bookmarks():
    """Test listing bookmarks."""
    response = client.get("/api/bookmarks")
    print("✅ List bookmarks:", response.status_code)
    data = response.json()
    print(f"   Total: {data['total']} bookmarks")
    assert response.status_code == 200

def test_search():
    """Test search functionality."""
    response = client.get("/api/search?q=FastAPI")
    print("✅ Search:", response.status_code)
    data = response.json()
    print(f"   Found: {data['total']} results for query '{data['query']}'")
    assert response.status_code == 200

def test_stats():
    """Test stats endpoint."""
    response = client.get("/api/stats")
    print("✅ Stats:", response.status_code)
    print("   Stats:", json.dumps(response.json(), indent=2))
    assert response.status_code == 200

if __name__ == "__main__":
    print("🧪 Testing Recall API...\n")
    
    try:
        test_root()
        bookmark = test_create_bookmark()
        test_list_bookmarks()
        test_search()
        test_stats()
        
        print("\n✅ All API tests passed!")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
