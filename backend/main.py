import sys
from pathlib import Path

# Añadimos la carpeta 'src' al path de Python para que los imports 
# relativos sigan funcionando correctamente (ej. 'from modules.search...')
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastapi import FastAPI
from modules.search.search_router import router

app = FastAPI(
    title="Metabuscador Semántico — Ontología Fútbol",
    version="1.0.0"
)
app.include_router(router)

@app.get("/health")
async def health():
    return {"status": "ok"}
