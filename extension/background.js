// Background service worker for Recall extension

// Listen for extension installation
chrome.runtime.onInstalled.addListener(() => {
  console.log('Recall extension installed');
});

// Handle messages from content scripts or popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Received message:', message);
  
  if (message.type === 'SAVE_BOOKMARK') {
    // Forward to API
    fetch('http://127.0.0.1:8000/api/bookmarks', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(message.data)
    })
    .then(response => response.json())
    .then(data => sendResponse({ success: true, data }))
    .catch(error => sendResponse({ success: false, error: error.message }));
    
    return true; // Keep message channel open for async response
  }
});
