import { useState, useEffect } from 'react'
import './App.css'

interface Bookmark {
  id: number
  url: string
  title: string | null
  domain: string | null
  summary: string | null
  key_points: string[] | null
  category: string | null
  estimated_read_minutes: number | null
  processing_status: string
  error_message: string | null
  saved_at: string
  processed_at: string | null
  tags: Array<{id: number, name: string}>
}

interface Stats {
  total_bookmarks: number
  pending: number
  processing: number
  completed: number
  failed: number
}

const API_URL = 'http://127.0.0.1:8000/api'

function App() {
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(true)
  const [selectedBookmark, setSelectedBookmark] = useState<Bookmark | null>(null)

  // Fetch bookmarks
  const fetchBookmarks = async () => {
    try {
      const response = await fetch(`${API_URL}/bookmarks`)
      const data = await response.json()
      setBookmarks(data.bookmarks)
    } catch (error) {
      console.error('Error fetching bookmarks:', error)
    }
  }

  // Fetch stats
  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_URL}/stats`)
      const data = await response.json()
      setStats(data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  // Search bookmarks
  const handleSearch = async (query: string) => {
    if (!query.trim()) {
      fetchBookmarks()
      return
    }

    try {
      const response = await fetch(`${API_URL}/search?q=${encodeURIComponent(query)}`)
      const data = await response.json()
      setBookmarks(data.bookmarks)
    } catch (error) {
      console.error('Error searching:', error)
    }
  }

  // Initial load
  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      await Promise.all([fetchBookmarks(), fetchStats()])
      setLoading(false)
    }
    loadData()

    // Refresh every 10 seconds
    const interval = setInterval(() => {
      fetchBookmarks()
      fetchStats()
    }, 10000)

    return () => clearInterval(interval)
  }, [])

  // Handle search input
  useEffect(() => {
    const timer = setTimeout(() => {
      handleSearch(searchQuery)
    }, 300)

    return () => clearTimeout(timer)
  }, [searchQuery])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✅'
      case 'pending': return '⏳'
      case 'processing': return '⚙️'
      case 'failed': return '❌'
      default: return '❓'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#27ae60'
      case 'pending': return '#f39c12'
      case 'processing': return '#3498db'
      case 'failed': return '#e74c3c'
      default: return '#95a5a6'
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading Recall...</p>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1>📚 Recall</h1>
          <p className="tagline">Your local-first AI reading assistant</p>
        </div>
        
        {stats && (
          <div className="stats">
            <div className="stat">
              <span className="stat-value">{stats.total_bookmarks}</span>
              <span className="stat-label">Total</span>
            </div>
            <div className="stat">
              <span className="stat-value">{stats.completed}</span>
              <span className="stat-label">Processed</span>
            </div>
            <div className="stat">
              <span className="stat-value">{stats.pending + stats.processing}</span>
              <span className="stat-label">Pending</span>
            </div>
          </div>
        )}
      </header>

      <div className="search-container">
        <input
          type="text"
          className="search-input"
          placeholder="Search bookmarks..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <main className="main">
        {bookmarks.length === 0 ? (
          <div className="empty-state">
            <p className="empty-icon">📭</p>
            <h2>No bookmarks yet</h2>
            <p>Save your first article using the browser extension!</p>
          </div>
        ) : (
          <div className="bookmarks-grid">
            {bookmarks.map((bookmark) => (
              <div
                key={bookmark.id}
                className="bookmark-card"
                onClick={() => setSelectedBookmark(bookmark)}
              >
                <div className="bookmark-header">
                  <span
                    className="status-badge"
                    style={{ backgroundColor: getStatusColor(bookmark.processing_status) }}
                  >
                    {getStatusIcon(bookmark.processing_status)} {bookmark.processing_status}
                  </span>
                  <span className="bookmark-date">{formatDate(bookmark.saved_at)}</span>
                </div>

                <h3 className="bookmark-title">{bookmark.title || 'Untitled'}</h3>
                
                {bookmark.domain && (
                  <p className="bookmark-domain">{bookmark.domain}</p>
                )}

                {bookmark.summary && (
                  <p className="bookmark-summary">{bookmark.summary}</p>
                )}

                {bookmark.category && (
                  <span className="category-badge">{bookmark.category}</span>
                )}

                {bookmark.tags && bookmark.tags.length > 0 && (
                  <div className="tags">
                    {bookmark.tags.map((tag) => (
                      <span key={tag.id} className="tag">#{tag.name}</span>
                    ))}
                  </div>
                )}

                {bookmark.estimated_read_minutes && (
                  <p className="read-time">📖 {bookmark.estimated_read_minutes} min read</p>
                )}
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Bookmark Detail Modal */}
      {selectedBookmark && (
        <div className="modal-overlay" onClick={() => setSelectedBookmark(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setSelectedBookmark(null)}>×</button>
            
            <h2>{selectedBookmark.title || 'Untitled'}</h2>
            
            {selectedBookmark.domain && (
              <p className="modal-domain">{selectedBookmark.domain}</p>
            )}

            <a href={selectedBookmark.url} target="_blank" rel="noopener noreferrer" className="modal-link">
              Open Original →
            </a>

            {selectedBookmark.summary && (
              <div className="modal-section">
                <h3>Summary</h3>
                <p>{selectedBookmark.summary}</p>
              </div>
            )}

            {selectedBookmark.key_points && selectedBookmark.key_points.length > 0 && (
              <div className="modal-section">
                <h3>Key Points</h3>
                <ul>
                  {selectedBookmark.key_points.map((point, idx) => (
                    <li key={idx}>{point}</li>
                  ))}
                </ul>
              </div>
            )}

            {selectedBookmark.tags && selectedBookmark.tags.length > 0 && (
              <div className="modal-section">
                <h3>Tags</h3>
                <div className="tags">
                  {selectedBookmark.tags.map((tag) => (
                    <span key={tag.id} className="tag">#{tag.name}</span>
                  ))}
                </div>
              </div>
            )}

            {selectedBookmark.error_message && (
              <div className="modal-section error">
                <h3>Error</h3>
                <p>{selectedBookmark.error_message}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default App
