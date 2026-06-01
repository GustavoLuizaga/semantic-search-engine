from fastapi import APIRouter
from src.models import SearchRequest, SearchResponse
from src.modules.search.search_service import search_service
from src.modules.dbpedia.dbpedia_service import dbpedia_service

router = APIRouter()

@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    return search_service.execute(request.query, request.language)

@router.post("/search/dbpedia", response_model=SearchResponse)
async def search_dbpedia(request: SearchRequest):
    print(f"Consulta desd el front='{request.query}', lenguaje usadado :V ='{request.language}'")
    return dbpedia_service.execute(request.query, request.language)

