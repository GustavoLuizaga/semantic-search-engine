from fastapi import APIRouter, Request
from src.models import SearchRequest, SearchResponse
from src.modules.search.search_service import search_service
from src.modules.dbpedia.dbpedia_service import dbpedia_service
from src.modules.dbpedia.dbpedia_executor import DBpediaExecutor

router = APIRouter()


# ── Ontología local ────────────────────────────────────────────────────────
@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    return search_service.execute(request.query, request.language)


# ── DBpedia con modo online/offline ────────────────────────────────────────
@router.post("/search/dbpedia", response_model=SearchResponse)
async def search_dbpedia(request: SearchRequest, raw_request: Request):
    # 1. Detectar el modo: primero el header, luego el campo del body
    mode_header = raw_request.headers.get("X-DBpedia-Mode", "").lower().strip()
    mode_body   = getattr(request, "mode", None) or ""
    mode        = mode_header or mode_body.lower().strip() or "online"

    if mode not in ("online", "offline"):
        mode = "online"

    print(f"[ROUTER] /search/dbpedia | query='{request.query}' | lang='{request.language}' | mode='{mode}'")
    print(f"se esta usando el modo {'OFFLINE' if mode == 'offline' else 'ONLINE'} para DBpedia")

    return dbpedia_service.execute(request.query, request.language, mode=mode)


@router.get("/search/dbpedia/offline-status")
async def offline_status():
    """
    El frontend puede llamar este endpoint para saber si Fuseki
    está disponible antes de mostrar el toggle offline.
    """
    available = DBpediaExecutor.is_offline_available()
    return {
        "offline_available": available,
        "fuseki_endpoint": DBpediaExecutor.ENDPOINT_OFFLINE,
    }