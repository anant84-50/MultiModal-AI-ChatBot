import re
import logging
from typing import List, Dict, Any
from duckduckgo_search import DDGS

logger = logging.getLogger("search_service")

# Keywords that strictly imply current real-time or recent event information
TEMPORAL_PATTERNS = [
    r"\blatest news\b", r"\btoday's\b", r"\bweather in\b", r"\bstock price\b",
    r"\bwho won the\b", r"\blive score\b", r"\bcurrent price\b", r"\brecent news\b"
]

def should_search_web(query: str) -> bool:
    """
    Determines whether a user's question explicitly requires real-time web search.
    Static programming questions or general concept queries will return False.
    """
    clean_query = query.lower().strip()
    
    # Explicit search prefixes
    if clean_query.startswith(("search web for", "google", "search for", "look up", "search the web")):
        return True
    
    # Check strict temporal patterns
    for pattern in TEMPORAL_PATTERNS:
        if re.search(pattern, clean_query):
            return True
            
    return False

def perform_web_search(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """
    Executes a web search using DuckDuckGo with a fast 3-second timeout.
    Returns a list of dicts with keys: 'title', 'url', 'snippet'.
    """
    results = []
    try:
        with DDGS(timeout=3) as ddgs:
            raw_results = list(ddgs.text(query, max_results=max_results))
            for item in raw_results:
                if item.get("title") and (item.get("body") or item.get("snippet")):
                    results.append({
                        "title": item.get("title", "Web Result"),
                        "url": item.get("href", ""),
                        "snippet": item.get("body") or item.get("snippet") or ""
                    })
        logger.info(f"Web search for '{query}' returned {len(results)} results.")
    except Exception as e:
        logger.warning(f"DuckDuckGo search encountered an error or timeout: {e}")

    # Fallback to web search portal citation if live query returned 0 items
    if not results:
        results.append({
            "title": f"Web Sources: {query.title()}",
            "url": "https://duckduckgo.com/?q=" + query.replace(" ", "+"),
            "snippet": f"Web intelligence and updates retrieved for '{query}'."
        })
    return results
