"""
Utility functions for Recall application.
"""
from urllib.parse import urlparse, urlunparse
from typing import Optional
import re


def normalize_url(url: str) -> str:
    """
    Normalize URL for deduplication.
    - Convert to lowercase
    - Remove www. prefix
    - Remove trailing slashes
    - Remove common tracking parameters
    - Remove fragment identifiers
    """
    try:
        parsed = urlparse(url.lower().strip())
        
        # Remove www. from hostname
        hostname = parsed.hostname or ""
        if hostname.startswith("www."):
            hostname = hostname[4:]
        
        # Remove trailing slash from path
        path = parsed.path.rstrip("/") if parsed.path else ""
        
        # Common tracking parameters to remove
        tracking_params = {
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
            'fbclid', 'gclid', 'msclkid', 'mc_cid', 'mc_eid',
            'ref', 'source', '_hsenc', '_hsmi'
        }
        
        # Filter out tracking parameters
        if parsed.query:
            params = []
            for param in parsed.query.split('&'):
                if '=' in param:
                    key = param.split('=')[0]
                    if key not in tracking_params:
                        params.append(param)
            query = '&'.join(params)
        else:
            query = ''
        
        # Reconstruct URL without fragment
        normalized = urlunparse((
            parsed.scheme,
            hostname,
            path,
            parsed.params,
            query,
            ''  # Remove fragment
        ))
        
        return normalized
    except Exception:
        # If normalization fails, return original URL lowercased
        return url.lower().strip()


def extract_domain(url: str) -> Optional[str]:
    """
    Extract domain from URL.
    Returns hostname without www. prefix.
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        if hostname.startswith("www."):
            hostname = hostname[4:]
        return hostname if hostname else None
    except Exception:
        return None


def truncate_content(content: str, max_length: int = 4000) -> str:
    """
    Truncate content to maximum length for LLM processing.
    Tries to break at sentence boundaries when possible.
    """
    if len(content) <= max_length:
        return content
    
    # Try to break at last period before max_length
    truncated = content[:max_length]
    last_period = truncated.rfind('.')
    
    if last_period > max_length * 0.8:  # If period is in last 20%
        return truncated[:last_period + 1]
    
    return truncated + "..."


def clean_text(text: Optional[str]) -> Optional[str]:
    """
    Clean extracted text by removing excessive whitespace.
    """
    if not text:
        return None
    
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text if text else None
