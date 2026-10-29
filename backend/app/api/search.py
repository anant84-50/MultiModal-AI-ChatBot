from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import WebSearch
from app.schemas.search import WebSearchRequest, WebSearchResponse, SearchResultItem
from app.services.search_service import perform_web_search

router = APIRouter(prefix="/search", tags=["search"])

@router.post("", response_model=WebSearchResponse)
def execute_search(req: WebSearchRequest, db: Session = Depends(get_db)):
    """Executes a web search and optionally stores query results in the conversation history."""
    results_raw = perform_web_search(req.query, max_results=req.max_results)
    
    results = [
        SearchResultItem(
            title=item["title"],
            url=item["url"],
            snippet=item["snippet"]
        ) for item in results_raw
    ]

    # Save to web_searches table if conversation_id provided
    if req.conversation_id:
        search_record = WebSearch(
            conversation_id=req.conversation_id,
            query=req.query,
            results=results_raw
        )
        db.add(search_record)
        db.commit()

    return WebSearchResponse(
        query=req.query,
        results=results,
        count=len(results)
    )
