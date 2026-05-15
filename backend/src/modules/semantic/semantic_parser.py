import re
from .alias_mapper import AliasMapper

# Nombres de jugadores conocidos para detección
JUGADORES_CONOCIDOS = [
    "bellingham", "vinícius", "vinicius", "lewandowski", "kane",
    "mbappé", "mbappe", "dembélé", "dembele", "sané", "sane",
    "gavi", "kimmich", "pedri", "rodrygo", "modric", "alisson",
    "jude", "harry", "kylian", "ousmane", "leroy", "joshua",
    "luka", "robert",
]


class ParsedQuery:
    def __init__(self, intent: str, entities: list, raw: str):
        self.intent = intent
        self.entities = entities
        self.raw = raw

    def __repr__(self):
        return f"ParsedQuery(intent={self.intent!r}, entities={self.entities!r})"


class SemanticParser:
    # Orden de prioridad: más específico primero
    INTENTS = [
        ("goleadores_ranking",  ["máximo goleador", "maximo goleador", "ranking goles", "quién marcó más", "quien marcó más", "quien marcó mas"]),
        ("todos_partidos",      ["todos los partidos", "lista partidos", "partidos jugados", "lista todos los partidos"]),
        ("todos_equipos",       ["todos los equipos", "qué equipos hay", "que equipos hay", "equipos hay"]),
        ("todos_jugadores",     ["todos los jugadores", "lista jugadores"]),
        ("resultado_partido",   ["resultado", "marcador", "ganó", "ganó", "perdio", "perdio", "empató", "empato", "vs", "contra"]),
        ("goles_partido",       ["quién anotó", "quien anoto", "quien metió", "goleadores del partido",
                                 "cuántos goles marcó", "cuantos goles marcó", "cuantos goles marco", "goles marcó"]),
        ("jugadores_nacionalidad", ["nacionalidad", "país", "pais", "jugadores de ", "jugador de ", "jugadores son de", "jugador es de"]),
        ("jugadores_equipo",    ["jugadores", "plantilla", "quiénes juegan en", "quienes juegan en"]),
        ("info_equipo",         ["información de", "estadio de", "entrenador de", "datos del equipo",
                                 "entrena al", "entrena a", "quien entrena", "quién entrena"]),
        ("tarjetas",            ["tarjeta", "amonestado", "expulsado", "amarilla", "roja"]),
        ("sustituciones",       ["sustitución", "sustituciones", "cambio", "entró", "salió", "cambios"]),
        ("arbitros",            ["árbitro", "arbitro", "árbitros", "arbitros"]),
        ("estadios",            ["estadio", "capacidad", "aforo"]),
        ("jugador_por_dorsal",  ["dorsal", "numero", "número", "camiseta", "lleva el"]),
        ("info_jugador",        []),  # Fallback / detectado por nombre
    ]

    @staticmethod
    def parse(query: str) -> "ParsedQuery":
        q_lower = query.lower()
        intent = "info_jugador"

        # Detectar intent por keywords
        for intnt, keywords in SemanticParser.INTENTS:
            if keywords and any(kw in q_lower for kw in keywords):
                intent = intnt
                break

        # Si no se detectó intent, verificar si hay nombre de jugador
        if intent == "info_jugador":
            tiene_jugador = any(j in q_lower for j in JUGADORES_CONOCIDOS)
            if not tiene_jugador:
                # No hay jugador, intent genérico
                pass

        entities = SemanticParser._extract_entities(q_lower, intent)
        return ParsedQuery(intent, entities, query)

    @staticmethod
    def _extract_entities(q_lower: str, intent: str) -> list:
        """Extrae entidades según el intent detectado."""

        if intent == "resultado_partido":
            return SemanticParser._extract_partido_entities(q_lower)

        elif intent == "goles_partido":
            # Puede buscar goles de un jugador específico o partido
            return SemanticParser._extract_partido_entities(q_lower)

        elif intent in ("jugadores_equipo", "info_equipo"):
            return SemanticParser._extract_equipo_entities(q_lower, intent)

        elif intent in ("estadios",):
            return SemanticParser._extract_estadio_entities(q_lower)

        elif intent == "info_jugador":
            return SemanticParser._extract_jugador_entities(q_lower)

        elif intent == "jugador_por_dorsal":
            return SemanticParser._extract_dorsal_entities(q_lower)

        elif intent == "jugadores_nacionalidad":
            return SemanticParser._extract_nacionalidad_entities(q_lower)

        elif intent in ("goleadores_ranking", "todos_partidos", "todos_equipos",
                        "todos_jugadores", "arbitros", "tarjetas", "sustituciones"):
            return []

        return [AliasMapper.resolve(q_lower.strip(" ¿?!"))]

    @staticmethod
    def _extract_partido_entities(q_lower: str) -> list:
        """Extrae equipos de una query de partido."""
        # Patrón "X vs Y" o "X contra Y"
        match = re.search(r'(.+?)\s+(?:vs\.?|contra)\s+(.+?)(?:\?|$)', q_lower)
        if match:
            raw1 = match.group(1).strip()
            raw2 = match.group(2).strip(" ¿?!")
            # Limpiar keywords de intent del grupo 1
            for kw in ["resultado", "marcador", "partido de", "partido", "¿cuál es el", "cuál es el",
                       "quién ganó el", "quien ganó el"]:
                raw1 = raw1.replace(kw, "").strip()
            e1 = AliasMapper.resolve(raw1.strip(" ¿?!"))
            e2 = AliasMapper.resolve(raw2.strip(" ¿?!"))
            if e1 and e2:
                return [e1, e2]

        # Patrón "entre X y Y"
        match2 = re.search(r'entre\s+(.+?)\s+y\s+(.+?)(?:\?|$)', q_lower)
        if match2:
            e1 = AliasMapper.resolve(match2.group(1).strip(" ¿?!"))
            e2 = AliasMapper.resolve(match2.group(2).strip(" ¿?!"))
            if e1 and e2:
                return [e1, e2]

        # Fallback: buscar alias de equipos en la query
        teams_found = []
        from .alias_mapper import ALIASES
        for alias, canonical in ALIASES.items():
            if alias in q_lower:
                if canonical not in teams_found:
                    teams_found.append(canonical)
        # También buscar nombres completos
        team_names = ["real madrid", "fc barcelona", "barcelona", "bayern munchen",
                      "paris saint-germain", "liverpool fc"]
        for tn in team_names:
            if tn in q_lower and tn not in teams_found:
                teams_found.append(AliasMapper.resolve(tn))

        return list(dict.fromkeys(teams_found))  # Eliminar duplicados manteniendo orden

    @staticmethod
    def _extract_equipo_entities(q_lower: str, intent: str) -> list:
        """Extrae nombre de equipo para jugadores/info de equipo."""
        cleaned = q_lower
        keywords_to_remove = {
            "jugadores_equipo": ["jugadores del", "jugadores de los", "jugadores de", "plantilla del",
                                 "plantilla de los", "plantilla de", "quiénes juegan en",
                                 "quienes juegan en", "jugadores", "plantilla", "dime la"],
            "info_equipo": ["información de", "datos del equipo", "datos de", "entrenador de",
                            "estadio de", "entrena al", "entrena a", "quien entrena al",
                            "quién entrena al", "quien entrena", "quién entrena",
                            "información del", "datos del"],
        }
        for kw in sorted(keywords_to_remove.get(intent, []), key=len, reverse=True):
            cleaned = cleaned.replace(kw, "")
        cleaned = cleaned.strip(" ¿?!,")
        entity  = AliasMapper.resolve(cleaned) if cleaned else ""
        return [entity] if entity else []

    @staticmethod
    def _extract_estadio_entities(q_lower: str) -> list:
        """Extrae nombre de estadio."""
        cleaned = q_lower
        # Ordenar por longitud desc para quitar frases largas primero
        kws = ["cuánta capacidad tiene el", "cuanta capacidad tiene el", "capacidad del",
               "capacidad de", "aforo del", "aforo de", "dame información del",
               "dame informacion del", "información del", "información de",
               "informacion del", "estadio"]
        for kw in sorted(kws, key=len, reverse=True):
            cleaned = cleaned.replace(kw, "")
        cleaned = cleaned.strip(" ¿?!,")
        return [cleaned] if cleaned else []

    @staticmethod
    def _extract_jugador_entities(q_lower: str) -> list:
        """Extrae nombre de jugador."""
        cleaned = q_lower
        kws = ["dame información de", "dame informacion de", "¿quién es", "quien es",
               "quién es", "información de", "informacion de"]
        for kw in sorted(kws, key=len, reverse=True):
            cleaned = cleaned.replace(kw, "")
        cleaned = cleaned.strip(" ¿?!,")
        return [cleaned] if cleaned else [q_lower.strip(" ¿?!")]

    @staticmethod
    def _extract_dorsal_entities(q_lower: str) -> list:
        """Extrae el número de dorsal y el equipo."""
        # Buscar número
        match_num = re.search(r'\b(\d+)\b', q_lower)
        dorsal = match_num.group(1) if match_num else ""
        
        # Fallback: buscar alias de equipos en la query
        teams_found = []
        from .alias_mapper import ALIASES
        for alias, canonical in ALIASES.items():
            if alias in q_lower:
                if canonical not in teams_found:
                    teams_found.append(canonical)
        # También buscar nombres completos
        team_names = ["real madrid", "fc barcelona", "barcelona", "bayern munchen",
                      "paris saint-germain", "liverpool fc"]
        for tn in team_names:
            if tn in q_lower and tn not in teams_found:
                teams_found.append(AliasMapper.resolve(tn))
                
        team = teams_found[0] if teams_found else ""
        return [dorsal, team]

    @staticmethod
    def _extract_nacionalidad_entities(q_lower: str) -> list:
        """Extrae la nacionalidad de la query."""
        cleaned = q_lower
        kws = ["jugadores con nacionalidad", "jugador con nacionalidad", "nacionalidad", 
               "del pais", "del país", "jugadores son de", "jugador es de", "jugadores de", "jugador de"]
        for kw in sorted(kws, key=len, reverse=True):
            if kw in cleaned:
                # Tomar lo que sigue después de la keyword
                parts = cleaned.split(kw)
                if len(parts) > 1:
                    cleaned = parts[-1].strip(" ¿?!,")
                break
        return [cleaned] if cleaned else [q_lower]

