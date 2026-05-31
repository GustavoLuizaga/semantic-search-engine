"""Detección de intents de estadios solo para el módulo DBpedia."""
import re

from src.modules.semantic.alias_mapper import AliasMapper
from src.modules.semantic.semantic_parser import SemanticParser

# Frases que no identifican un club concreto
_INVALID_TEAM_ENTITIES = frozenset({
    "",
    "un equipo",
    "el equipo",
    "un club",
    "el club",
    "equipo",
    "club",
    "algun equipo",
    "algún equipo",
})

_TEAM_STADIUM_PHRASES = {
    "es": (
        "donde juega local el",
        "dónde juega local el",
        "donde juega el",
        "dónde juega el",
        "donde juega local",
        "dónde juega local",
        "donde juega",
        "dónde juega",
        "en que estadio juega el",
        "en qué estadio juega el",
        "en que estadio juega",
        "en qué estadio juega",
        "cual es el estadio del equipo",
        "cuál es el estadio del equipo",
        "cual es el estadio del",
        "cuál es el estadio del",
        "cual es el estadio de",
        "cuál es el estadio de",
        "estadio local del",
        "estadio local de",
        "estadio del equipo",
        "estadio del",
        "estadio de",
    ),
    "en": (
        "where does",
        "where do",
        "stadium of",
        "home stadium of",
        "home ground of",
        "what stadium does",
        "what is the stadium of",
        "what is the home stadium of",
        "where does the",
        "where do the",
    ),
    "fr": (
        "où joue le",
        "où joue la",
        "stade de",
        "stade du",
        "quel est le stade de",
        "quel est le stade du",
        "stade local de",
        "stade local du",
    ),
}



def _extract_team_for_stadium(query: str, lang: str = "es") -> list[str]:
    """Extrae el nombre del club en preguntas tipo estadio/dónde juega."""
    q = query.lower().strip().strip("¿?!")
    phrases = _TEAM_STADIUM_PHRASES.get(lang, _TEAM_STADIUM_PHRASES["es"])

    for pref in sorted(phrases, key=len, reverse=True):
        if pref in q:
            q = q.split(pref, 1)[-1].strip()
            break

    m = re.search(
        r"\bestadio\s+(?:del|de(?:l)?(?:\s+equipo)?|de los)\s+(.+?)(?:\?|$)",
        q,
    )
    if m:
        q = m.group(1).strip()

    m = re.search(
        r"(?:donde|dónde)\s+juega(?:\s+local)?\s+(?:el|la|los|las)?\s*(.+?)(?:\?|$)",
        query.lower().strip(),
    )
    if m:
        q = m.group(1).strip()

    q = re.sub(r"\s+", " ", q).strip(" ¿?!,.")
    for noise in ("play?", "plays?", "play", "plays", "joue?", "joue"):
        q = q.replace(noise, "").strip()
    q = re.sub(r"\s+", " ", q).strip(" ¿?!,.")
    if q in _INVALID_TEAM_ENTITIES:
        return []

    resolved = AliasMapper.resolve(q)
    if resolved in _INVALID_TEAM_ENTITIES:
        return []
    
    
    return [resolved] if resolved else []



def _is_team_stadium_query(q: str, lang: str = "es") -> bool:
    phrases = _TEAM_STADIUM_PHRASES.get(lang, _TEAM_STADIUM_PHRASES["es"])
    return any(p in q for p in phrases)


def resolve_stadium_intent(query: str, default_intent: str, default_entities: list, lang: str = "es") -> tuple[str, list]:
    """
    Ajusta intent/entidades para consultas de estadios en DBpedia.
    No modifica el parser global; solo refina antes de construir SPARQL.
    """
    q = query.lower().strip()

    # Listado global (prioridad sobre estadios_ubicacion por keyword "estadios de")
    list_keywords = (
        "todos los estadios",
        "estadios registrados",
        "estadios de futbol",
        "estadios de fútbol",
        "estadios de futbol registrados",
        "estadios de fútbol registrados",
        "lista de estadios",
        "listado de estadios",
        "cuales son los estadios",
        "cuáles son los estadios",
        "que estadios hay registrados",
        "qué estadios hay registrados",
        "estadios hay registrados",
        "cuales son los estadios de",
        "cuáles son los estadios de",
    )
    if any(kw in q for kw in list_keywords):
        return "todos_estadios", []

    # Estadios por ciudad/país (solo si no es listado global)
    if default_intent == "estadios_ubicacion":
        return default_intent, default_entities

    # Estadio local de un equipo (con o sin la palabra "estadio")
    if _is_team_stadium_query(q, lang):
        entities = _extract_team_for_stadium(query, lang)
        if entities:
            return "estadio_equipo", entities
        return "estadio_equipo", []

    # Pregunta explícita por estadio con nombre conocido o entidad extraída
    if default_intent == "estadios" and default_entities:
        return "estadios", default_entities

    return default_intent, default_entities