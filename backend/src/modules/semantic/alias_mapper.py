# alias_mapper.py — refactorizado

import json, os

_MAP_PATH = os.path.join(os.path.dirname(__file__), "..", "dbpedia", "club_uris.json")
_CLUB_URI_MAP: dict = {}
if os.path.exists(_MAP_PATH):
    with open(_MAP_PATH, encoding="utf-8") as f:
        _CLUB_URI_MAP = json.load(f)

# Aliases que NO están en club_uris.json (apodos, abreviaciones, etc.)
ALIASES = {
    "barça":     "fc barcelona",
    "barca":     "fc barcelona",
    "merengues": "real madrid",
    "bayer":     "bayern munchen",
    "champions": "uefa champions league",
    "clasico":   "__real_madrid_vs_barcelona__",
}

class AliasMapper:
    @staticmethod
    def resolve(name: str) -> str:
        if not name:
            return ""
        name = name.lower().strip()
        # 1. Alias manual primero
        if name in ALIASES:
            return ALIASES[name]
        # 2. Si está directamente en el mapa de clubes, ya es canónico
        if name in _CLUB_URI_MAP:
            return name
        return name

    @staticmethod
    def get_all_club_names() -> list[str]:
        """Todos los nombres conocidos: JSON + aliases que apuntan a clubes."""
        from_json = list(_CLUB_URI_MAP.keys())
        from_aliases = [k for k, v in ALIASES.items() if v in _CLUB_URI_MAP or v in from_json]
        return list(dict.fromkeys(from_json + from_aliases))