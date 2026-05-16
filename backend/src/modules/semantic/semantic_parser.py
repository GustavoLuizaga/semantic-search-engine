import re
from .alias_mapper import AliasMapper

# ── Catálogos de nombres reales de la ontología ───────────────────────────
# Usados para detectar el intent correcto antes de caer al fallback.
# Actualizar aquí si se agregan individuos a la ontología.

EQUIPOS_CONOCIDOS = [
    "real madrid", "fc barcelona", "barcelona", "bayern munchen", "bayern",
    "paris saint-germain", "psg", "liverpool fc", "liverpool",
    # aliases (deben coincidir con alias_mapper)
    "barça", "barca", "madrid", "merengues", "bayer",
]

JUGADORES_CONOCIDOS = [
    # apellidos
    "bellingham", "vinícius", "vinicius", "lewandowski", "kane",
    "mbappé", "mbappe", "dembélé", "dembele", "sané", "sane",
    "gavi", "kimmich", "pedri", "rodrygo", "modric", "alisson",
    # nombres propios que son únicos
    "jude", "kylian", "ousmane", "leroy", "joshua", "luka",
    # nombres completos
    "harry kane", "jude bellingham", "vinícius júnior", "vinicius junior",
    "robert lewandowski", "kylian mbappé", "ousmane dembélé",
    "leroy sané", "joshua kimmich", "luka modric", "alisson becker",
    "rodrygo goes",
]

ESTADIOS_CONOCIDOS = [
    "bernabéu", "bernabeu", "santiago bernabéu", "camp nou", "allianz arena",
    "anfield", "parc des princes", "metropolitano", "old trafford",
    "maracaná", "maracana", "monumental", "groupama",
]

ENTRENADORES_CONOCIDOS = [
    "ancelotti", "carlo ancelotti", "xavi", "xavi hernandez",
    "tuchel", "thomas tuchel", "klopp", "jürgen klopp", "luis enrique",
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
        ("goleadores_ranking",  ["máximo goleador", "maximo goleador", "ranking goles",
                                  "quién marcó más", "quien marcó más", "quien marcó mas",
                                  "top goleador", "mejor goleador"]),
        ("partidos_competicion",["partidos de la", "partidos del", "partidos en la", "partidos jugados en"]),
        ("todos_partidos",      ["todos los partidos", "lista partidos", "partidos jugados",
                                  "lista todos los partidos"]),
        ("todos_equipos",       ["todos los equipos", "qué equipos hay", "que equipos hay",
                                  "equipos hay", "lista equipos"]),
        ("todos_jugadores",     ["todos los jugadores", "lista jugadores"]),
        ("resultado_partido",   ["resultado", "marcador", "ganó", "gano", "perdió", "perdio",
                                  "empató", "empato", "vs", "contra"]),
        ("gol_propia_puerta",   ["gol en propia puerta", "gol en contra", "propia puerta"]),
        ("gol_de_penal",        ["gol de penal", "anotó de penal", "anoto de penal", "gol de penalti"]),
        ("goles_partido",       ["quién anotó", "quien anoto", "quien metió", "quien metio",
                                  "goleadores del partido", "cuántos goles marcó",
                                  "cuantos goles marcó", "cuantos goles marco", "goles marcó"]),
        ("jugadores_nacionalidad", ["jugadores de nacionalidad", "jugador de nacionalidad",
                                     "jugadores con nacionalidad", "jugadores son de",
                                     "jugador es de"]),
        ("capitan_equipo",      ["capitán del", "capitan del", "capitán de", "capitan de",
                                  "quien es el capitan", "quién es el capitán"]),
        ("jugadores_equipo",    ["jugadores del", "jugadores de", "plantilla del", "plantilla de",
                                  "quiénes juegan en", "quienes juegan en"]),
        ("info_equipo",         ["entrenador de", "entrenador del", "datos del equipo",
                                  "entrena al", "entrena a", "quien entrena", "quién entrena",
                                  "estadio del", "estadio de", "ciudad del", "ciudad de",
                                  "información del equipo", "informacion del equipo"]),
        ("tarjetas",            ["tarjeta", "amonestado", "expulsado", "amarilla", "roja"]),
        ("sustituciones",       ["sustitución", "sustitucion", "sustituciones", "cambio",
                                  "entró", "entro", "salió", "salio", "cambios"]),
        ("arbitros",            ["árbitro", "arbitro", "árbitros", "arbitros"]),
        ("estadios_ubicacion",  ["estadios en", "estadios de", "estadio en", "estadio de",
                                  "que estadios hay en", "qué estadios hay en", "estadios del"]),
        ("estadios",            ["estadio", "capacidad", "aforo"]),
        ("jugador_por_dorsal",  ["dorsal", "numero", "número", "camiseta", "lleva el"]),
        ("info_fecha_nacimiento", ["cuándo nació", "cuando nacio", "fecha de nacimiento"]),
        ("es_titular",          ["es titular", "jugadores titulares", "es un jugador titular", "titular"]),
        ("torneos_internacionales", ["torneos internacionales", "competiciones internacionales", "tipo de torneo"]),
        ("asistencia_gol",      ["asistencia de gol", "asistencia para el gol", "asistencia de", "dio la asistencia", "asistencia para"]),
        ("asistencia_gol",      ["asistencia de gol", "asistencia para el gol", "asistencia de", "dio la asistencia", "asistencia para"]),
        ("tarjeta_por_motivo",  ["tarjeta por", "amonestado por", "expulsado por"]),
        ("equipos_por_pais",    ["equipos de un pais", "equipos de un país", "equipos del país", "equipos del pais", "equipos de españa", "equipos de alemania", "equipos de francia", "qué equipos son de", "que equipos son de", "equipos de nacionalidad", "equipos por pais", "equipos de inglaterra", "equipos de argentina", "equipos de brasil"]),
        # info_equipo e info_jugador se detectan por catálogo de nombres (ver abajo)
    ]

    @staticmethod
    def parse(query: str) -> "ParsedQuery":
        q_lower = query.lower().strip()

        # ── 1. Detectar intent por keywords ──────────────────────────────
        intent = None
        for intnt, keywords in SemanticParser.INTENTS:
            if keywords and any(kw in q_lower for kw in keywords):
                intent = intnt
                break

        # ── 2. Si no hay keyword, detectar por catálogo de nombres ───────
        if intent is None:
            tiene_equipo    = any(e in q_lower for e in EQUIPOS_CONOCIDOS)
            tiene_jugador   = any(j in q_lower for j in JUGADORES_CONOCIDOS)
            tiene_estadio   = any(s in q_lower for s in ESTADIOS_CONOCIDOS)
            tiene_entrenador = any(t in q_lower for t in ENTRENADORES_CONOCIDOS)

            if tiene_estadio:
                intent = "estadios"
            elif tiene_entrenador:
                intent = "info_equipo"   # busca el equipo del entrenador
            elif tiene_equipo and not tiene_jugador:
                intent = "info_equipo"
            elif tiene_jugador:
                intent = "info_jugador"
            else:
                # Último fallback: intentar como jugador (el matcher fallará limpiamente)
                intent = "info_jugador"

        # ── 3. Extraer entidades ──────────────────────────────────────────
        entities = SemanticParser._extract_entities(q_lower, intent)
        return ParsedQuery(intent, entities, query)

    # ── Dispatch de extracción ────────────────────────────────────────────
    @staticmethod
    def _extract_entities(q_lower: str, intent: str) -> list:
        if intent in ("resultado_partido", "goles_partido"):
            return SemanticParser._extract_partido_entities(q_lower)

        elif intent in ("jugadores_equipo", "info_equipo", "capitan_equipo"):
            return SemanticParser._extract_equipo_entities(q_lower, intent)

        elif intent == "estadios":
            return SemanticParser._extract_estadio_entities(q_lower)

        elif intent == "estadios_ubicacion":
            return SemanticParser._extract_ubicacion_entities(q_lower)

        elif intent == "partidos_competicion":
            return SemanticParser._extract_competicion_entities(q_lower)

        elif intent == "info_jugador" or intent in ("info_fecha_nacimiento", "es_titular", "asistencia_gol"):
            return SemanticParser._extract_jugador_entities(q_lower)

        elif intent == "jugador_por_dorsal":
            return SemanticParser._extract_dorsal_entities(q_lower)

        elif intent in ("jugadores_nacionalidad", "equipos_por_pais"):
            return SemanticParser._extract_nacionalidad_entities(q_lower)

        elif intent == "tarjeta_por_motivo":
            return SemanticParser._extract_motivo_tarjeta(q_lower)

        elif intent in ("goleadores_ranking", "todos_partidos", "todos_equipos",
                        "todos_jugadores", "arbitros", "tarjetas", "sustituciones",
                        "torneos_internacionales", "gol_propia_puerta", "gol_de_penal"):
            return []

        return [AliasMapper.resolve(q_lower.strip(" ¿?!"))]

    # ── Extractores ───────────────────────────────────────────────────────

    @staticmethod
    def _extract_partido_entities(q_lower: str) -> list:
        """Extrae equipos de una query de partido."""
        # Patrón "X vs Y" o "X contra Y"
        match = re.search(r'(.+?)\s+(?:vs\.?|contra)\s+(.+?)(?:\?|$)', q_lower)
        if match:
            raw1 = match.group(1).strip()
            raw2 = match.group(2).strip(" ¿?!")
            for kw in ["resultado", "marcador", "partido de", "partido",
                        "¿cuál es el", "cuál es el", "quién ganó el", "quien ganó el"]:
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

        # Fallback: detectar equipos por catálogo
        teams_found = []
        from .alias_mapper import ALIASES
        for alias, canonical in ALIASES.items():
            if alias in q_lower and canonical not in teams_found:
                teams_found.append(canonical)
        for tn in EQUIPOS_CONOCIDOS:
            resolved = AliasMapper.resolve(tn)
            if tn in q_lower and resolved not in teams_found:
                teams_found.append(resolved)

        return list(dict.fromkeys(teams_found))

    @staticmethod
    def _extract_equipo_entities(q_lower: str, intent: str) -> list:
        """Extrae nombre de equipo."""
        cleaned = q_lower
        keywords_to_remove = {
            "jugadores_equipo": [
                "jugadores del", "jugadores de los", "jugadores de",
                "plantilla del", "plantilla de los", "plantilla de",
                "quiénes juegan en", "quienes juegan en",
                "jugadores", "plantilla", "dime la",
            ],
            "capitan_equipo": [
                "quien es el capitan del", "quién es el capitán del",
                "quien es el capitan de", "quién es el capitán de",
                "capitán del", "capitan del", "capitán de", "capitan de",
                "quien es el capitan", "quién es el capitán", "del equipo", "equipo",
            ],
            "info_equipo": [
                "información del equipo", "informacion del equipo",
                "datos del equipo", "datos de",
                "entrenador del", "entrenador de",
                "estadio del", "estadio de",
                "entrena al", "entrena a",
                "quien entrena al", "quién entrena al",
                "quien entrena", "quién entrena",
                "información del", "informacion del",
                "ciudad del", "ciudad de",
            ],
        }
        for kw in sorted(keywords_to_remove.get(intent, []), key=len, reverse=True):
            cleaned = cleaned.replace(kw, "")
        cleaned = cleaned.strip(" ¿?!,")
        entity = AliasMapper.resolve(cleaned) if cleaned else ""
        return [entity] if entity else []

    @staticmethod
    def _extract_estadio_entities(q_lower: str) -> list:
        """Extrae nombre de estadio."""
        cleaned = q_lower
        kws = [
            "cuánta capacidad tiene el", "cuanta capacidad tiene el",
            "capacidad del", "capacidad de", "aforo del", "aforo de",
            "dame información del", "dame informacion del",
            "información del", "información de", "informacion del",
            "estadio",
        ]
        for kw in sorted(kws, key=len, reverse=True):
            cleaned = cleaned.replace(kw, "")
        cleaned = cleaned.strip(" ¿?!,")
        return [cleaned] if cleaned else []

    @staticmethod
    def _extract_jugador_entities(q_lower: str) -> list:
        """Extrae nombre de jugador."""
        cleaned = q_lower
        kws = [
            "dame información de", "dame informacion de",
            "¿quién es", "quien es", "quién es",
            "información de", "informacion de",
            "el jugador", "jugador",
            "de qué juega", "de que juega", 
            "en qué posición juega", "en que posicion juega",
            "en qué equipo juega", "en que equipo juega", "dónde juega", "donde juega",
            "de dónde es", "de donde es", "nacionalidad de",
            "qué dorsal lleva", "que dorsal lleva", "dorsal de", "número de", "numero de",
            "cuándo nació el entrenador", "cuando nacio el entrenador",
            "cuándo nació el árbitro", "cuando nacio el arbitro",
            "cuándo nació el", "cuando nacio el",
            "cuándo nació", "cuando nacio",
            "fecha de nacimiento del entrenador", "fecha de nacimiento del árbitro",
            "fecha de nacimiento del", "fecha de nacimiento de",
            "es titular el jugador", "es titular el", "es titular", "jugadores titulares", "es un jugador titular", "titular",
            "quién le dio la asistencia de gol a", "quien le dio la asistencia de gol a",
            "quién le dio la asistencia a", "quien le dio la asistencia a",
            "asistencia de gol a", "asistencia para el gol de", "asistencia de", "dio la asistencia a", "asistencia para",
            "el entrenador", "entrenador", "el árbitro", "árbitro", "el arbitro", "arbitro"
        ]
        for kw in sorted(kws, key=len, reverse=True):
            cleaned = cleaned.replace(kw, "")
        cleaned = cleaned.strip(" ¿?!,")
        return [cleaned] if cleaned else [q_lower.strip(" ¿?!")]

    @staticmethod
    def _extract_dorsal_entities(q_lower: str) -> list:
        """Extrae número de dorsal y equipo."""
        match_num = re.search(r'\b(\d+)\b', q_lower)
        dorsal = match_num.group(1) if match_num else ""

        teams_found = []
        from .alias_mapper import ALIASES
        for alias, canonical in ALIASES.items():
            if alias in q_lower and canonical not in teams_found:
                teams_found.append(canonical)
        for tn in EQUIPOS_CONOCIDOS:
            resolved = AliasMapper.resolve(tn)
            if tn in q_lower and resolved not in teams_found:
                teams_found.append(resolved)

        team = teams_found[0] if teams_found else ""
        return [dorsal, team]

    @staticmethod
    def _extract_nacionalidad_entities(q_lower: str) -> list:
        """Extrae la nacionalidad de la query."""
        cleaned = q_lower
        kws = [
            "jugadores con nacionalidad", "jugador con nacionalidad",
            "jugadores de nacionalidad", "jugador de nacionalidad",
            "nacionalidad", "del pais", "del país",
            "jugadores son de", "jugador es de",
            "jugadores de", "jugador de",
            "cuales son los equipos de un pais por ejemplo", "equipos de un pais por ejemplo",
            "cuales son los equipos de un país por ejemplo", "equipos de un país por ejemplo",
            "equipos de un pais", "equipos de un país", "equipos del país", "equipos del pais",
            "qué equipos son de", "que equipos son de", "equipos de nacionalidad", "equipos por pais",
            "cuales son los equipos de", "cuáles son los equipos de", "equipos de", "equipo de"
        ]
        for kw in sorted(kws, key=len, reverse=True):
            if kw in cleaned:
                parts = cleaned.split(kw)
                if len(parts) > 1:
                    cleaned = parts[-1].strip(" ¿?!,")
                break
        return [cleaned] if cleaned else [q_lower]

    @staticmethod
    def _extract_ubicacion_entities(q_lower: str) -> list:
        """Extrae la ubicación (ciudad o país) para buscar estadios."""
        cleaned = q_lower
        kws = [
            "que estadios hay en", "qué estadios hay en",
            "estadios en", "estadio en", "estadios de", "estadio de", "estadios del"
        ]
        for kw in sorted(kws, key=len, reverse=True):
            if kw in cleaned:
                parts = cleaned.split(kw)
                if len(parts) > 1:
                    cleaned = parts[-1].strip(" ¿?!,")
                break
        return [cleaned] if cleaned else [q_lower]

    @staticmethod
    def _extract_competicion_entities(q_lower: str) -> list:
        """Extrae el nombre de la competición."""
        cleaned = q_lower
        kws = [
            "partidos jugados en la", "partidos jugados en el", "partidos jugados en",
            "partidos de la", "partidos del", "partidos de",
            "partidos en la", "partidos en el", "partidos en"
        ]
        for kw in sorted(kws, key=len, reverse=True):
            if kw in cleaned:
                parts = cleaned.split(kw)
                if len(parts) > 1:
                    cleaned = parts[-1].strip(" ¿?!,")
                break
        
        # Mapeo básico de competiciones
        if "liga" in cleaned and "la liga" not in cleaned:
            cleaned = cleaned.replace("liga", "la liga")
            
        return [cleaned] if cleaned else [q_lower]

    @staticmethod
    def _extract_motivo_tarjeta(q_lower: str) -> list:
        cleaned = q_lower
        kws = ["tarjeta por", "amonestado por", "expulsado por"]
        for kw in kws:
            if kw in cleaned:
                parts = cleaned.split(kw)
                if len(parts) > 1:
                    cleaned = parts[-1].strip(" ¿?!,")
                break
        return [cleaned] if cleaned else [q_lower]