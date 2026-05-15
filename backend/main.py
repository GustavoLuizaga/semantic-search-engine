from fastapi import FastAPI
from src.modules.search.search_router import router

app = FastAPI(
    title="Metabuscador Semántico — Ontología Fútbol",
    version="1.0.0"
)
app.include_router(router)

@app.get("/health")
async def health():
    return {"status": "ok"}
