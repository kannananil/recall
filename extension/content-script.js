// Content script for Recall extension
// This runs on every page but does nothing unless triggered

console.log('Recall content script loaded');

// Listen for messages from popup or background
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'EXTRACT_CONTENT') {
    try {
      const content = extractContent();
      sendResponse({ success: true, content });
    } catch (error) {
      sendResponse({ success: false, error: error.message });
    }
    return true;
  }
});

// Extract page content
function extractContent() {
  // Get page title
  const title = document.title;
  
  // Get page URL
  const url = window.location.href;
  
  // Extract main content
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
    .substring(0, 50000);
  
  return {
    url,
    title,
    content_text: contentText
  };
}
