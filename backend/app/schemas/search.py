from typing import List, Optional
from pydantic import BaseModel

class SearchResultItem(BaseModel):
    title: str
    url: str
    snippet: str

class WebSearchRequest(BaseModel):
    query: str
    max_results: int = 5
    conversation_id: Optional[str] = None

class WebSearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]
    count: int
