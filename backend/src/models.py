from pydantic import BaseModel
from typing import Any, Optional

class SearchRequest(BaseModel):
    query: str
    language: str = "es"

class SearchResponse(BaseModel):
    query: str
    intent: str
    answer: str
    data: Optional[Any] = None
    found: bool = True
