// Popup script for Recall extension

const saveButton = document.getElementById('saveButton');
const statusDiv = document.getElementById('status');

// Show status message
function showStatus(message, type) {
  statusDiv.textContent = message;
  statusDiv.className = `status ${type}`;
}

// Hide status message
function hideStatus() {
  statusDiv.className = 'status';
}

// Save current page
async function savePage() {
  try {
    saveButton.disabled = true;
    showStatus('Extracting article...', 'loading');
    
    // Get current tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab) {
      throw new Error('No active tab');
    }
    
    // Check if we can access the page
    if (tab.url.startsWith('chrome://') || tab.url.startsWith('chrome-extension://')) {
      throw new Error('Cannot save Chrome internal pages');
    }
    
    // Inject and execute content script
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      function: extractPageContent
    });
    
    if (!results || !results[0] || !results[0].result) {
      throw new Error('Failed to extract page content');
    }
    
    const pageData = results[0].result;
    
    // Add URL if not present
    pageData.url = pageData.url || tab.url;
    pageData.title = pageData.title || tab.title;
    
    showStatus('Saving to Recall...', 'loading');
    
    // Send to API
    const response = await fetch('http://127.0.0.1:8000/api/bookmarks', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(pageData)
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const result = await response.json();
    
    // Show success
    showStatus('✓ Saved successfully!', 'success');
    
    // Auto-hide success message after 2 seconds
    setTimeout(() => {
      hideStatus();
      saveButton.disabled = false;
    }, 2000);
    
  } catch (error) {
    console.error('Save error:', error);
    showStatus(`Error: ${error.message}`, 'error');
    saveButton.disabled = false;
  }
}

// Function to extract page content (runs in page context)
function extractPageContent() {
  try {
    // Get page title
    const title = document.title;
    
    // Get page URL
    const url = window.location.href;
    
    // Extract main content
    // Try to find article content using common selectors
    let contentText = '';
    
    // Common article selectors
    const selectors = [
      'article',
      '[role="main"]',
      'main',
      '.post-content',
      '.article-content',
      '.entry-content',
      '#content',
      '.content'
    ];
    
    for (const selector of selectors) {
      const element = document.querySelector(selector);
      if (element) {
        contentText = element.innerText;
        break;
      }
    }
    
    // If no article found, get body text
    if (!contentText || contentText.length < 100) {
      contentText = document.body.innerText;
    }
    
    // Clean up content
    contentText = contentText
      .replace(/\s+/g, ' ')
      .trim()
      .substring(0, 50000); // Limit to 50k chars
    
    return {
      url,
      title,
      content_text: contentText
    };
  } catch (error) {
    console.error('Content extraction error:', error);
    return {
      url: window.location.href,
      title: document.title,
      content_text: document.body.innerText.substring(0, 10000)
    };
  }
}

// Event listeners
saveButton.addEventListener('click', savePage);

// Initialize
hideStatus();
