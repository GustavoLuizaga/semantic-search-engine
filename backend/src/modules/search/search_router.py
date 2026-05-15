from fastapi import APIRouter
from src.models import SearchRequest, SearchResponse
from src.modules.search.search_service import search_service

router = APIRouter()

@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    return search_service.execute(request.query)
