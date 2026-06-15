import re
from .alias_mapper import AliasMapper
#from dbpedia.country_names import COUNTRY_NAMES, normalize_country


EQUIPOS_CONOCIDOS = AliasMapper.get_all_club_names()

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

# ── Catálogo unificado de personas (jugadores + entrenadores + árbitros) ──
# Ordenados por longitud descendente para búsqueda más específica primero
PERSONAS_CONOCIDAS = sorted([
    # Jugadores - nombres completos
    "jude bellingham", "vinícius júnior", "vinicius junior", "robert lewandowski",
    "kylian mbappé", "kylian mbappe", "ousmane dembélé", "ousmane dembele",
    "leroy sané", "leroy sane", "joshua kimmich", "luka modric", "alisson becker",
    "rodrygo goes", "harry kane",
    # Jugadores - nombres cortos/únicos
    "bellingham", "vinícius", "vinicius", "lewandowski", "kane",
    "mbappé", "mbappe", "dembélé", "dembele", "sané", "sane",
    "gavi", "kimmich", "pedri", "rodrygo", "modric", "alisson",
    "jude", "kylian", "ousmane", "leroy", "joshua", "luka",
    # Entrenadores
    "carlo ancelotti", "ancelotti", "xavi hernandez", "xavi",
    "thomas tuchel", "tuchel", "jürgen klopp", "jurgen klopp", "klopp",
    "luis enrique",
    # Árbitros
    "antonio mateu lahoz", "felix zwayer", "clément turpin", "clement turpin",
    "daniele orsato", "wilmar roldán", "wilmar roldan", "néstor pitana",
    "nestor pitana", "raphael claus", "andrés cunha", "andres cunha",
    "jesús gil manzano", "jesus gil manzano",
], key=len, reverse=True)


# ── Mapa de países/nacionalidades (ES/EN/FR) → valor canónico de la ontología ─
PAISES_Y_NACIONALIDADES = {
    # Español
    "española": "Española", "español": "Española", "españa": "Española",
    "alemana": "Alemana", "alemán": "Alemana", "alemania": "Alemana",
    "francesa": "Francesa", "francés": "Francesa", "francia": "Francesa",
    "brasileña": "Brasileña", "brasileño": "Brasileña", "brasil": "Brasileña",
    "inglesa": "Inglesa", "inglés": "Inglesa", "inglaterra": "Inglesa",
    "italiana": "Italiana", "italiano": "Italiana", "italia": "Italiana",
    "polaca": "Polaca", "polaco": "Polaca", "polonia": "Polaca",
    "croata": "Croata", "croacia": "Croata",
    "colombiana": "Colombiana", "colombiano": "Colombiana", "colombia": "Colombiana",
    "argentina": "Argentina", "argentino": "Argentina",
    "uruguaya": "Uruguaya", "uruguayo": "Uruguaya", "uruguay": "Uruguaya",
    "portuguesa": "Portuguesa", "portugués": "Portuguesa", "portugal": "Portuguesa",
    # Inglés
    "spanish": "Española", "spain": "Española",
    "german": "Alemana", "germany": "Alemana",
    "french": "Francesa", "france": "Francesa",
    "brazilian": "Brasileña", "brazil": "Brasileña",
    "english": "Inglesa", "england": "Inglesa",
    "italian": "Italiana", "italy": "Italiana",
    "polish": "Polaca", "poland": "Polaca",
    "croatian": "Croata", "croatia": "Croata",
    "colombian": "Colombiana",
    "argentinian": "Argentina",
    "uruguayan": "Uruguaya",
    "portuguese": "Portuguesa",
    # Francés
    "espagnole": "Española", "espagnol": "Española", "espagne": "Española",
    "allemande": "Alemana", "allemand": "Alemana", "allemagne": "Alemana",
    "française": "Francesa", "français": "Francesa",
    "brésilienne": "Brasileña", "brésilien": "Brasileña", "brésiliens": "Brasileña",
    "brésil": "Brasileña",
    "anglaise": "Inglesa", "anglais": "Inglesa", "angleterre": "Inglesa",
    "italienne": "Italiana", "italien": "Italiana", "italie": "Italiana",
    "polonaise": "Polaca", "polonais": "Polaca", "pologne": "Polaca",
    "croate": "Croata", "croatie": "Croata",
    "colombienne": "Colombiana", "colombien": "Colombiana",
    "argentin": "Argentina", "argentine": "Argentina",
    "uruguayenne": "Uruguaya", "uruguayen": "Uruguaya",
    "portugaise": "Portuguesa", "portugais": "Portuguesa",
    
     "germany":       "alemania",
    "german":        "alemania",
    "spain":         "españa",
    "spanish":       "españa",
    "france":        "francia",
    "french":        "francia",
    "england":       "inglaterra",
    "english":       "inglaterra",
    "uk":            "inglaterra",
    "britain":       "inglaterra",
    "italy":         "italia",
    "italian":       "italia",
    "portugal":      "portugal",
    "portuguese":    "portugal",
    "netherlands":   "países bajos",
    "dutch":         "países bajos",
    "holland":       "países bajos",
    "brazil":        "brasil",
    "brazilian":     "brasil",
    "argentina":     "argentina",
    "argentine":     "argentina",
    "argentinian":   "argentina",
    "mexico":        "méxico",
    "mexican":       "méxico",
    "usa":           "estados unidos",
    "united states": "estados unidos",
    "american":      "estados unidos",
    # Francés → español
    "allemagne":     "alemania",
    "allemand":      "alemania",
    "allemands":     "alemania",
    "allemandes":    "alemania",
    "espagne":       "españa",
    "espagnol":      "españa",
    "espagnols":     "españa",
    "espagnoles":    "españa",
    "angleterre":    "inglaterra",
    "anglais":       "inglaterra",
    "anglaises":     "inglaterra",
    "italie":        "italia",
    "italien":       "italia",
    "italiens":      "italia",
    "italiennes":    "italia",
    "pays-bas":      "países bajos",
    "néerlandais":   "países bajos",
    "brésil":        "brasil",
    "brésilien":     "brasil",
    "brésiliens":    "brasil",
    "brésiliennes":  "brasil",
    "mexique":       "méxico",
    "mexicain":      "méxico",
    "mexicains":     "méxico",
    "mexicaines":    "méxico",
    "états-unis":    "estados unidos",
    "américain":     "estados unidos",
    "américains":    "estados unidos",
    # Alemán → español (bonus)
    "deutschland":   "alemania",
    "spanien":       "españa",
    "frankreich":    "francia",
    "italien":       "italia",
    "brasilien":     "brasil",
    "niederlande":   "países bajos",
    
    
}


class ParsedQuery:
    def __init__(self, intent: str, entities: list, raw: str):
        self.intent = intent
        self.entities = entities
        self.raw = raw

    def __repr__(self):
        return f"ParsedQuery(intent={self.intent!r}, entities={self.entities!r})"


class LocalSemanticParser:
    # Palabras clave de nacimiento multi-idioma para re-clasificación
    _BIRTH_WORDS = {
        "nacimiento", "nació", "nacio", "birth", "born", "naissance", "née",
    }

    INTENTS_BY_LANG = {
        "es": [
            ("goleadores_ranking",  ["máximo goleador", "maximo goleador", "ranking goles",
                                      "quién marcó más", "quien marcó más", "quien marcó mas",
                                      "top goleador", "mejor goleador"]),
            ("partidos_competicion", ["partidos de la", "partidos del", "partidos en la", "partidos jugados en"]),
            ("todos_partidos",      ["todos los partidos", "lista partidos", "partidos jugados",
                                      "lista todos los partidos"]),
            ("jugadores_nacionalidad", ["jugadores de nacionalidad", "jugador de nacionalidad",
                                         "jugadores con nacionalidad", "jugadores son de",
                                         "jugador es de"]),
            ("equipos_por_pais",    ["equipos de un pais", "equipos de un país", "equipos del país", "equipos del pais", "equipos de españa", "equipos de alemania", "equipos de francia", "qué equipos son de", "que equipos son de", "equipos de nacionalidad", "equipos por pais", "equipos de inglaterra", "equipos de argentina", "equipos de brasil"]),
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
            ("capitan_equipo",      ["capitán del", "capitan del", "capitán de", "capitan de",
                                      "quien es el capitan", "quién es el capitán"]),
            ("jugadores_equipo",    ["jugadores del", "jugadores de", "plantilla del", "plantilla de",
                                      "quiénes juegan en", "quienes juegan en"]),
            ("info_equipo",         ["entrenador de", "entrenador del", "datos del equipo",
                                      "entrena al", "entrena a", "quien entrena", "quién entrena",
                                      "estadio del", "estadio de", "ciudad del", "ciudad de",
                                      "información del equipo", "informacion del equipo"]),
            ("tarjeta_por_motivo",  ["tarjeta por", "amonestado por", "expulsado por"]),
            ("tarjetas",            ["tarjeta", "tarjetas", "amonestado", "expulsado", "amarilla", "roja"]),
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
            ("jugadores_posicion",  ["delanteros", "mediocampistas", "porteros", "defensas",
                                      "jugadores de posición", "jugadores que juegan de",
                                      "qué delanteros", "que delanteros"]),
            ("info_entrenador",     ["entrenador", "entrenadores", "técnico", "tecnico",
                                      "DT", "quien dirige", "quién dirige"]),
        ],
        "en": [
            ("goleadores_ranking",  ["top scorer", "best scorer", "ranking goals", "most goals", "who scored most", "who scored the most", "goal ranking"]),
            ("partidos_competicion",["matches of the", "matches of", "matches in the", "games in the", "played in"]),
            ("todos_partidos",      ["all matches", "list of matches", "played matches", "all games"]),
            ("jugadores_nacionalidad", ["players of nationality", "player of nationality", "players with nationality",
                                        "players are from", "player is from", "players from",
                                        "which players are", "players who are", "players are"]),
            ("equipos_por_pais",    ["teams of a country", "teams from", "teams of spain", "teams of germany", "teams of france", "which teams are from", "teams by country", "teams of england", "teams of argentina", "teams of brazil"]),
            ("todos_equipos",       ["all teams", "what teams", "which teams", "list of teams", "teams list"]),
            ("todos_jugadores",     ["all players", "list of players", "all the players", "who are all the players", "which players"]),
            # goles_partido BEFORE resultado_partido so "how many goals did" wins over "score"/"result"
            ("gol_propia_puerta",   ["own goal", "own goals", "self goal"]),
            ("gol_de_penal",        ["penalty goal", "scored a penalty", "from penalty", "penalty kick", "penalties"]),
            ("goles_partido",       ["who scored", "scorers of the match", "how many goals did", "goals scored by", "goals in the match"]),
            ("resultado_partido",   ["result", "score", "won", "lost", "drew", "vs", "against"]),
            ("capitan_equipo",      ["captain of", "who is the captain"]),
            ("jugadores_equipo",    ["players of", "squad of", "roster of", "who plays in", "team of"]),
            # estadios_ubicacion and estadios BEFORE info_equipo so "capacity"/"stadium" wins
            ("estadios_ubicacion",  ["stadiums in", "stadium in", "what stadiums are in", "stadiums of"]),
            ("estadios",            ["stadium", "capacity", "attendance", "spectators"]),
            ("info_equipo",         ["coach of", "trainer of", "who coaches", "city of", "information of the team", "info of the team", "information of", "info of"]),
            ("tarjeta_por_motivo",  ["card for", "booked for", "sent off for", "carded for", "booked for rough", "rough play"]),
            ("tarjetas",            ["card", "cards", "booked", "sent off", "yellow", "red", "show the cards", "show cards"]),
            ("sustituciones",       ["substitution", "substitutions", "change", "changes", "came on", "went off", "substituted"]),
            ("arbitros",            ["referee", "referees"]),
            ("jugador_por_dorsal",  ["shirt number", "dorsal", "wears number", "wears the shirt"]),
            ("info_fecha_nacimiento", ["when was he born", "when was born", "date of birth",
                                       "birth date", "birthday", "born on", "born"]),
            ("es_titular",          ["is starter", "starting players", "is a starter", "starter", "starting"]),
            ("torneos_internacionales", ["international tournaments", "international competitions", "tournament type"]),
            ("asistencia_gol",      ["who assisted", "who gave the assist", "gave the assist", "assist for", "assist to", "assisted", "assists", "assist"]),
            ("jugadores_posicion",  ["forwards", "midfielders", "goalkeepers", "defenders", "players of position", "players who play as", "what forwards"]),
            ("info_entrenador",     ["coach", "manager", "trainer", "who manages", "who directs"]),
        ],
        "fr": [
            ("goleadores_ranking",  ["meilleur buteur", "classement des buteurs", "top buteur", "qui a marqué le plus", "classement buts"]),
            # partidos_competicion: include "matchs de l'" so 'Matchs de l'UEFA' is captured
            ("partidos_competicion",["matchs de l'", "matchs de la", "matchs du", "matchs en", "joués en"]),
            ("todos_partidos",      ["tous les matchs", "liste des matchs", "matchs joués"]),
            ("jugadores_nacionalidad", ["joueurs de nationalité", "joueur de nationalité", "joueurs sont de", "joueur est de",
                                        "quels joueurs sont", "joueurs d'", "joueurs sont"]),
            ("equipos_por_pais",    ["équipes d'un pays", "equipes d'un pays", "équipes de", "equipes de", "quelles équipes sont de", "quelles équipes viennent de", "quelles équipes viennent d'", "équipes viennent de", "équipes viennent d'"]),
            ("todos_equipos",       ["toutes les équipes", "quelles équipes", "liste des équipes", "tous les clubs"]),
            ("todos_jugadores",     ["tous les joueurs", "liste des joueurs", "quels sont tous les joueurs"]),
            # goles_partido BEFORE resultado_partido
            ("gol_propia_puerta",   ["but contre son camp", "csc", "propre but"]),
            ("gol_de_penal",        ["but sur penalty", "but sur pénalty", "pénalty", "penalty"]),
            ("goles_partido",       ["qui a marqué", "buteurs du match", "combien de buts a marqué", "combien de buts", "buts marqués"]),
            ("resultado_partido",   ["résultat", "score", "a gagné", "a perdu", "match nul", "vs", "contre"]),
            ("capitan_equipo",      ["capitaine de", "qui est le capitaine"]),
            ("jugadores_equipo",    ["joueurs de", "effectif de", "qui joue à", "qui joue au"]),
            # estadios BEFORE info_equipo so 'capacité'/'stade' wins
            ("estadios_ubicacion",  ["stades en", "stade en", "quels stades sont en", "stades de"]),
            ("estadios",            ["capacité", "affluence", "spectateurs"]),
            ("info_equipo",         ["qui entraîne", "qui entraine", "entraîneur de", "entraineur de",
                                      "stade du", "stade de l'", "stade de", "ville de", "informations sur l'équipe", "info sur l'équipe"]),
            ("tarjeta_por_motivo",  ["carton pour", "averti pour", "expulsé pour", "averti pour jeu dangereux", "jeu dangereux"]),
            ("tarjetas",            ["carton", "cartons", "averti", "expulsé", "jaune", "rouge", "montre les cartons"]),
            ("sustituciones",       ["substitution", "substitutions", "changement", "changements", "est entré", "est sorti", "remplacement", "remplacements", "remplacements effectués", "remplacements effectues"]),
            ("arbitros",            ["arbitre", "arbitres"]),
            ("jugador_por_dorsal",  ["numéro", "numero", "maillot", "porte le", "dorsal"]),
            ("info_fecha_nacimiento", ["quand est-il né", "quand est né", "date de naissance",
                                       "naissance de", "est né"]),
            ("es_titular",          ["est titulaire", "joueurs titulaires", "titulaire"]),
            ("torneos_internacionales", ["tournois internationaux", "compétitions internationales", "type de tournoi"]),
            ("asistencia_gol",      ["passe décisive", "passe decisive", "a fait la passe", "passe décisive pour"]),
            ("jugadores_posicion",  ["attaquants", "milieux", "gardiens", "défenseurs", "joueurs de position", "joueurs qui jouent comme", "quels attaquants"]),
            ("info_entrenador",     ["entraîneur", "entraineur", "technicien", "qui dirige", "coach"]),
        ]
    }

    @staticmethod
    def parse(query: str, language: str = "es") -> "ParsedQuery":
        lang = (language or "es").lower().strip()
        if len(lang) > 2:
            lang = lang[:2]

        q_lower = query.lower().strip()
        # Normalizar apóstrofes tipográficos/curvos a rectos
        q_lower = q_lower.replace("’", "'").replace("‘", "'").replace("`", "'")

        # Auto-detección inteligente de idioma por marcadores característicos
        fr_markers = [
            "matchs de", "quel est", "qui entraîne", "qui entraine", "joueurs de", "stade de", 
            "est-il", "quand est", "combien de", "meilleur buteur", "classement des", 
            "but contre son camp", "but sur", "passe décisive", "passe decisive", "remplacement"
        ]
        en_markers = [
            "what is", "how many", "who is", "who scored", "stadiums in", "stadium in", 
            "captain of", "squad of", "players of", "coach of", "is starter", "starting players",
            "which teams", "which players"
        ]
        if any(m in q_lower for m in fr_markers):
            lang = "fr"
        elif any(m in q_lower for m in en_markers):
            lang = "en"

        if lang not in LocalSemanticParser.INTENTS_BY_LANG:
            lang = "es"

        # ── 1. Detectar intent por keywords ──────────────────────────────
        intent = None
        for intnt, keywords in LocalSemanticParser.INTENTS_BY_LANG[lang]:
            if keywords:
                # Comprobar palabra completa usando límites de palabra si es alfanumérico
                matched = False
                for kw in keywords:
                    pattern = ""
                    if kw[0].isalnum() or kw[0] == '_':
                        pattern += r'\b'
                    pattern += re.escape(kw)
                    if kw[-1].isalnum() or kw[-1] == '_':
                        pattern += r'\b'
                    if re.search(pattern, q_lower):
                        matched = True
                        break
                if matched:
                    intent = intnt
                    break

        # ── 2. Si no hay keyword, detectar por catálogo de nombres ───────
        if intent is None:
            tiene_equipo     = any(e in q_lower for e in EQUIPOS_CONOCIDOS)
            tiene_jugador    = any(j in q_lower for j in JUGADORES_CONOCIDOS)
            tiene_estadio    = any(s in q_lower for s in ESTADIOS_CONOCIDOS)
            tiene_entrenador = any(t in q_lower for t in ENTRENADORES_CONOCIDOS)
            tiene_nacimiento = any(w in q_lower for w in LocalSemanticParser._BIRTH_WORDS)
            tiene_persona    = any(p in q_lower for p in PERSONAS_CONOCIDAS)

            if tiene_estadio:
                intent = "estadios"
            elif tiene_nacimiento and tiene_persona:
                # Consulta de fecha de nacimiento detectada por catálogo
                intent = "info_fecha_nacimiento"
            elif tiene_entrenador:
                intent = "info_equipo"   # busca el equipo del entrenador
            elif tiene_equipo and not tiene_jugador:
                intent = "info_equipo"
            elif tiene_jugador:
                intent = "info_jugador"
            else:
                # Último fallback: intentar como jugador (el matcher fallará limpiamente)
                intent = "info_jugador"

        # ── 2b. Re-clasificar info_fecha_nacimiento vía keywords si el intent
        #         fue detectado por catálogo como info_equipo (entrenador + nacimiento) ──
        if intent == "info_equipo":
            tiene_nacimiento = any(w in q_lower for w in LocalSemanticParser._BIRTH_WORDS)
            tiene_persona    = any(p in q_lower for p in PERSONAS_CONOCIDAS)
            if tiene_nacimiento and tiene_persona:
                intent = "info_fecha_nacimiento"

        # ── 2c. Re-clasificar: jugadores_equipo con país → jugadores_nacionalidad ─
        if intent == "jugadores_equipo":
            quick = q_lower
            for kw_clean in sorted([
                "jugadores de los", "jugadores de", "joueurs des", "joueurs de la",
                "joueurs de l'", "joueurs de", "joueurs d'",
                "players of the", "players of", "players from", "squad of", "roster of",
            ], key=len, reverse=True):
                quick = quick.replace(kw_clean, "").strip(" ¿?!,")
            if quick.strip() in PAISES_Y_NACIONALIDADES:
                intent = "jugadores_nacionalidad"

        # ── 2d. Re-clasificar: estadios/estadios_ubicacion con equipo → info_equipo ─
        if intent in ("estadios", "estadios_ubicacion"):
            tiene_equipo = any(e in q_lower for e in EQUIPOS_CONOCIDOS)
            tiene_estadio = any(s in q_lower for s in ESTADIOS_CONOCIDOS)
            if tiene_equipo and not tiene_estadio:
                intent = "info_equipo"

        # ── 3. Extraer entidades ──────────────────────────────────────────
        entities = LocalSemanticParser._extract_entities(q_lower, intent, lang)
        return ParsedQuery(intent, entities, query)

    # ── Dispatch de extracción ────────────────────────────────────────────
    @staticmethod
    def _extract_entities(q_lower: str, intent: str, lang: str) -> list:
        if intent in ("resultado_partido", "goles_partido"):
            return LocalSemanticParser._extract_partido_entities(q_lower, lang)

        elif intent in ("jugadores_equipo", "info_equipo", "capitan_equipo"):
            return LocalSemanticParser._extract_equipo_entities(q_lower, intent, lang)

        elif intent == "estadios":
            return LocalSemanticParser._extract_estadio_entities(q_lower, lang)

        elif intent == "estadios_ubicacion":
            return LocalSemanticParser._extract_ubicacion_entities(q_lower, lang)

        elif intent == "partidos_competicion":
            return LocalSemanticParser._extract_competicion_entities(q_lower, lang)

        elif intent == "info_jugador" or intent in ("info_fecha_nacimiento", "es_titular", "asistencia_gol"):
            return LocalSemanticParser._extract_jugador_entities(q_lower, lang)

        elif intent == "jugador_por_dorsal":
            return LocalSemanticParser._extract_dorsal_entities(q_lower, lang)

        elif intent in ("jugadores_nacionalidad", "equipos_por_pais"):
            return LocalSemanticParser._extract_nacionalidad_entities(q_lower, lang)

        elif intent == "tarjeta_por_motivo":
            return LocalSemanticParser._extract_motivo_tarjeta(q_lower, lang)

        elif intent in ("goleadores_ranking", "todos_partidos", "todos_equipos",
                        "todos_jugadores", "arbitros", "tarjetas", "sustituciones",
                        "torneos_internacionales", "gol_propia_puerta", "gol_de_penal"):
            return []

        elif intent == "jugadores_posicion":
            return LocalSemanticParser._extract_posicion_entities(q_lower, lang)

        elif intent == "info_entrenador":
            return LocalSemanticParser._extract_entrenador_entities(q_lower, lang)
        
        return [AliasMapper.resolve(q_lower.strip(" ¿?!"))]

    # ── Extractores ───────────────────────────────────────────────────────

    @staticmethod
    def _extract_partido_entities(q_lower: str, lang: str) -> list:
        """Extrae equipos de una query de partido."""
        # Patrón "X vs Y", "X contra Y" (ES/FR), "X against Y" (EN)
        patron_vs = r'(.+?)\s+(?:vs\.?|contra|against)\s+(.+?)(?:\?|$)'
        match = re.search(patron_vs, q_lower)
        if match:
            raw1 = match.group(1).strip()
            raw2 = match.group(2).strip(" ¿?!")
            kws_rem = [
                "resultado", "marcador", "partido de", "partido",
                "¿cuál es el", "cuál es el", "quién ganó el", "quien ganó el",
                "result", "score", "match between", "match", "who won the", "who won",
                "résultat", "score", "match entre", "match de", "qui a gagné le", "qui a gagné"
            ]
            for kw in kws_rem:
                raw1 = raw1.replace(kw, "").strip()
            e1 = AliasMapper.resolve(raw1.strip(" ¿?!"))
            e2 = AliasMapper.resolve(raw2.strip(" ¿?!"))
            if e1 and e2:
                return [e1, e2]

        # Patrón "entre X y Y" / "between X and Y" / "entre X et Y"
        patron_entre = r'(?:entre|between)\s+(.+?)\s+(?:y|and|et)\s+(.+?)(?:\?|$)'
        match2 = re.search(patron_entre, q_lower)
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
    def _extract_equipo_entities(q_lower: str, intent: str, lang: str) -> list:
        """Extrae nombre de equipo."""
        # PRIORIDAD 1: buscar equipo conocido directamente (más específico primero)
        for name in sorted(EQUIPOS_CONOCIDOS, key=len, reverse=True):
            if name in q_lower:
                resolved = AliasMapper.resolve(name)
                if resolved:
                    return [resolved]

        cleaned = q_lower
        keywords_to_remove = {
    "jugadores_equipo": [
        "jugadores del", "jugadores de los", "jugadores de",
        "plantilla del", "plantilla de los", "plantilla de",
        "quiénes juegan en", "quienes juegan en",
        "jugadores", "plantilla", "dime la",
        # EN
        "players of", "players in", "players for", "squad of", "squad for",
        # FR
        "joueurs du", "joueurs de", "effectif du", "effectif de",
    ],
    "capitan_equipo": [
        "quien es el capitan del", "quién es el capitán del",
        "quien es el capitan de", "quién es el capitán de",
        "capitán del", "capitan del", "capitán de", "capitan de",
        "quien es el capitan", "quién es el capitán", "del equipo", "equipo",
        # EN
        "who is the captain of", "who is the captain",
        "captain of the", "captain of",
        # FR
        "qui est le capitaine du", "qui est le capitaine de",
        "capitaine du", "capitaine de",
    ],
    "info_equipo": [
        "información del equipo", "informacion del equipo",
        "datos del equipo", "datos de",
        "entrenador del", "entrenador de",
        "estadio del", "estadio de",
        "cual es el estadio del", "cuál es el estadio del",
        "cual es el estadio de", "cuál es el estadio de",
        "donde juega el", "dónde juega el",
        "donde juega", "dónde juega",
        "entrena al", "entrena a",
        "quien entrena al", "quién entrena al",
        "quien entrena", "quién entrena",
        "información del", "informacion del",
        "ciudad del", "ciudad de",
        # EN
        "where does the", "where does",
        "where do the", "where do",
        "what stadium does the", "what stadium does",
        "what is the stadium of the", "what is the stadium of",
        "what is the home stadium of the", "what is the home stadium of",
        "home stadium of the", "home stadium of",
        "home ground of the", "home ground of",
        "manager of the", "manager of",
        "coach of the", "coach of",
        "who manages the", "who manages",
        "who coaches the", "who coaches",
        "information about the", "information about",
        "tell me about the", "tell me about",
        "city of the", "city of",
        "play?", "play", "plays?", "plays",
        # FR
        "où joue le", "où joue la", "où jouent les",
        "stade du", "stade de",
        "entraîneur du", "entraîneur de",
        "qui entraîne le", "qui entraîne",
        "informations sur le", "informations sur",
    ],
}

        kws = keywords_to_remove.get(intent, {}).get(lang, [])
        # También agregamos las de los otros idiomas para robustez
        for other_lang in ["es", "en", "fr"]:
            if other_lang != lang:
                kws += keywords_to_remove.get(intent, {}).get(other_lang, [])

        for kw in sorted(kws, key=len, reverse=True):
            cleaned = cleaned.replace(kw, "")
        cleaned = cleaned.strip(" ¿?!,")
        entity = AliasMapper.resolve(cleaned) if cleaned else ""
        return [entity] if entity else []

    @staticmethod
    def _extract_estadio_entities(q_lower: str, lang: str) -> list:
        """Extrae nombre de estadio."""
        # PRIORIDAD 1: buscar estadio conocido directamente (más específico primero)
        for name in sorted(ESTADIOS_CONOCIDOS, key=len, reverse=True):
            if name in q_lower:
                return [name]

        cleaned = q_lower
        kws = [
            "cuánta capacidad tiene el", "cuanta capacidad tiene el",
            "capacidad del", "capacidad de", "aforo del", "aforo de",
            "dame información del", "dame informacion del",
            "información del", "información de", "informacion del",
            "estadio",
            # EN
            "how much capacity has the", "capacity of the", "capacity of",
            "attendance of the", "spectators in the", "info of the",
            "stadium",
            # FR
            "quelle est la capacité du", "capacité du", "capacité de",
            "affluence du", "spectateurs du", "informations sur le",
            "stade"
        ]
        for kw in sorted(kws, key=len, reverse=True):
            cleaned = cleaned.replace(kw, "")
        cleaned = cleaned.strip(" ¿?!,")
        return [cleaned] if cleaned else []

    @staticmethod
    def _extract_jugador_entities(q_lower: str, lang: str) -> list:
        """Extrae nombre de jugador.
        Estrategia: primero busca nombre conocido directamente en la query,
        luego limpia keywords y retorna lo que queda.
        """
        # PRIORIDAD 1: buscar nombre conocido directamente (más específico primero)
        for name in PERSONAS_CONOCIDAS:
            if name in q_lower:
                return [name]

        # PRIORIDAD 2: limpiar keywords y retornar lo que queda
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
            "el entrenador", "entrenador", "el árbitro", "árbitro", "el arbitro", "arbitro",
            # EN
            "give me information about", "information about", "info about", "who is", "information of",
            "what position does", "which position does", "where does he play", "which team does",
            "where is", "from", "nationality of", "what number does", "number of", "shirt of",
            "when was the coach born", "when was the referee born", "when was born the",
            "when was born", "was born", "born on", "born",
            "date of birth of", "is the player starter", "is starter",
            "who assisted", "who gave the assist to", "assist to", "assist for", "assist of",
            "the coach", "coach", "the referee", "referee",
            "what", "which", "who", "where", "when", "is", "are", "the", "a", "an",
            "player", "players",
            # FR
            "donne-moi des informations sur", "informations sur", "infos sur", "qui est", "information de",
            "le joueur", "joueur", "à quel poste joue", "a quel poste joue", "où joue-t-il", "ou joue",
            "d'où vient", "d'ou vient",
            "la nationalité de", "nationalité de", "quel numéro porte", "numero de", "maillot de",
            "quand est né l'entraîneur", "quand est né l'arbitre", "quand est né",
            "date de naissance de", "est-ce que le joueur est titulaire", "est titulaire",
            "qui a fait la passe décisive à", "qui a fait la passe à", "passe décisive pour", "passe décisive de",
            "l'entraîneur", "entraineur", "l'arbitre", "arbitre",
            "est-il", "est-il un", "est-il un joueur",
        ]
        for kw in sorted(kws, key=len, reverse=True):
            cleaned = cleaned.replace(kw, "")
        cleaned = cleaned.strip(" ¿?!,")
        return [cleaned] if cleaned else [q_lower.strip(" ¿?!")]

    @staticmethod
    def _extract_dorsal_entities(q_lower: str, lang: str) -> list:
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
    def _extract_nacionalidad_entities(q_lower: str, lang: str) -> list:
        """Extrae la nacionalidad de la query y la normaliza al valor de la ontología."""
        cleaned = q_lower
        kws = [
            # ES
            "jugadores con nacionalidad", "jugador con nacionalidad",
            "jugadores de nacionalidad", "jugador de nacionalidad",
            "nacionalidad", "del pais", "del país",
            "jugadores son de", "jugador es de",
            "jugadores de", "jugador de",
            "cuales son los equipos de un pais por ejemplo", "equipos de un pais por ejemplo",
            "cuales son los equipos de un país por ejemplo", "equipos de un país por ejemplo",
            "equipos de un pais", "equipos de un país", "equipos del país", "equipos del pais",
            "qué equipos son de", "que equipos son de", "equipos de nacionalidad", "equipos por pais",
            "cuales son los equipos de", "cuáles son los equipos de", "equipos de", "equipo de",
            # EN
            "players with nationality", "player with nationality", "players of nationality",
            "which players are", "players who are", "players are from", "player is from",
            "players from", "players are", "players of", "player of",
            "nationality", "of the country",
            "teams of a country", "teams from", "which teams are from", "teams of", "team of",
            # FR
            "joueurs de nationalité", "joueur de nationalité",
            "quels joueurs sont", "joueurs sont de", "joueur est de",
            "joueurs d'", "joueurs de", "joueur de",
            "nationalité", "du pays",
            "équipes d'un pays", "equipes d'un pays", "quelles équipes sont de", "équipes de", "equipes de",
            "quelles équipes viennent de", "quelles équipes viennent d'", "equipes viennent de", "equipes viennent d'",
            "équipes viennent de", "équipes viennent d'", "viennent de", "viennent d'"
        ]
        for kw in sorted(kws, key=len, reverse=True):
            if kw in cleaned:
                parts = cleaned.split(kw)
                if len(parts) > 1:
                    candidate = parts[-1].strip(" ¿?!,")
                    if candidate:
                        cleaned = candidate
                break
        cleaned = cleaned.strip(" ¿?!,")

        # Normalizar al valor canónico de la ontología usando el mapa multi-idioma
        canonical = PAISES_Y_NACIONALIDADES.get(cleaned.lower(), cleaned)
        return [canonical] if canonical else [q_lower]

    @staticmethod
    def _extract_ubicacion_entities(q_lower: str, lang: str) -> list:
        """Extrae la ubicación (ciudad o país) para buscar estadios.
        Normaliza nombres de país en EN/FR a su valor canónico en español
        para que coincida con los datos de la ontología.
        """
        # Mapa: nombre de país/ciudad en EN o FR → nombre canónico usado en la ontología
        _UBICACION_NORM = {
            # EN
            "spain": "España", "england": "Inglaterra", "germany": "Alemania",
            "france": "Francia", "italy": "Italia", "brazil": "Brasil",
            "argentina": "Argentina", "portugal": "Portugal", "colombia": "Colombia",
            "madrid": "Madrid", "barcelona": "Barcelona", "munich": "Munich",
            "london": "Londres", "paris": "París",
            # FR
            "espagne": "España", "angleterre": "Inglaterra", "allemagne": "Alemania",
            "france": "Francia", "italie": "Italia", "brésil": "Brasil",
            "argentine": "Argentina", "colombie": "Colombia",
            "londres": "Londres", "paris": "París", "munich": "Munich",
        }

        cleaned = q_lower
        kws = [
            "que estadios hay en", "qué estadios hay en",
            "estadios en", "estadio en", "estadios de", "estadio de", "estadios del",
            # EN
            "what stadiums are in", "stadiums in", "stadium in", "stadiums of",
            # FR
            "quels stades sont en", "stades en", "stade en", "stades de"
        ]
        for kw in sorted(kws, key=len, reverse=True):
            if kw in cleaned:
                parts = cleaned.split(kw)
                if len(parts) > 1:
                    cleaned = parts[-1].strip(" ¿?!,")
                break
        cleaned = cleaned.strip(" ¿?!,")
        # Normalize country names from EN/FR to canonical ontology name
        normalized = _UBICACION_NORM.get(cleaned.lower(), cleaned)
        return [normalized] if normalized else [q_lower]

    @staticmethod
    def _extract_competicion_entities(q_lower: str, lang: str) -> list:
        """Extrae el nombre de la competición."""
        cleaned = q_lower
        kws = [
            "partidos jugados en la", "partidos jugados en el", "partidos jugados en",
            "partidos de la", "partidos del", "partidos de",
            "partidos en la", "partidos en el", "partidos en",
            # EN
            "matches played in the", "matches played in", "matches of the", "matches of", "matches in the", "matches in",
            # FR — include "matchs de l'" for e.g. "Matchs de l'UEFA Champions League"
            "matchs joués dans la", "matchs joués en", "matchs de l'", "matchs de la", "matchs du", "matchs en"
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
        if "champions" in cleaned and "uefa champions league" not in cleaned:
            cleaned = cleaned.replace("champions league", "uefa champions league")
            cleaned = cleaned.replace("champions", "uefa champions league")
        # Normalize UEFA Champions League references in French
        if "ligue des champions" in cleaned:
            cleaned = "uefa champions league"

        return [cleaned] if cleaned else [q_lower]

    @staticmethod
    def _extract_motivo_tarjeta(q_lower: str, lang: str) -> list:
        # 1. First try to find a known motivo phrase directly in the query
        known_motivos = [
            # ES (longer first)
            "juego brusco", "conducta violenta", "sujetar al rival",
            "conducta antideportiva", "mano", "falta",
            # EN
            "rough play", "dangerous play", "violent conduct",
            "holding the opponent", "holding", "unsporting behaviour",
            "unsporting behavior", "handball", "foul", "simulation",
            "time wasting", "dissent",
            # FR
            "jeu dangereux", "jeu brutal", "conduite violente",
            "retenir l'adversaire", "comportement antisportif",
            "main", "faute", "protestation",
        ]
        for m in known_motivos:
            if m in q_lower:
                return [m]

        # 2. Fall back to prefix stripping for generic patterns
        cleaned = q_lower
        kws = [
            "tarjeta por", "amonestado por", "expulsado por",
            "carded for", "sent off for", "booked for", "card for",
            "averti pour", "carton pour",
        ]
        for kw in kws:
            if kw in cleaned:
                parts = cleaned.split(kw)
                if len(parts) > 1:
                    cleaned = parts[-1].strip(" ¿?!,")
                break
        return [cleaned] if cleaned else [q_lower]
    
    @staticmethod
    def _extract_posicion_entities(q_lower: str, lang: str) -> list:
        """Detecta la posición pedida y la normaliza al valor de la ontología."""
        mapeo = {
            # ES
            "delantero": "Delantero", "delanteros": "Delantero",
            "mediocampista": "Mediocampista", "mediocampistas": "Mediocampista",
            "medio": "Mediocampista", "medios": "Mediocampista",
            "portero": "Portero", "porteros": "Portero",
            "arquero": "Portero", "arqueros": "Portero",
            "defensa": "Defensa", "defensas": "Defensa",
            # EN
            "forward": "Delantero", "forwards": "Delantero",
            "striker": "Delantero", "strikers": "Delantero",
            "midfielder": "Mediocampista", "midfielders": "Mediocampista",
            "goalkeeper": "Portero", "goalkeepers": "Portero",
            "keeper": "Portero", "keepers": "Portero",
            "defender": "Defensa", "defenders": "Defensa",
            # FR
            "attaquant": "Delantero", "attaquants": "Delantero",
            "milieu de terrain": "Mediocampista", "milieu": "Mediocampista", "milieux": "Mediocampista",
            "gardien de but": "Portero", "gardien": "Portero", "gardiens": "Portero",
            "défenseur": "Defensa", "defenseur": "Defensa", "défenseurs": "Defensa", "defenseurs": "Defensa"
        }
        for kw, valor in mapeo.items():
            if kw in q_lower:
                return [valor]
        return []

    @staticmethod
    def _extract_entrenador_entities(q_lower: str, lang: str) -> list:
        """Extrae nombre de entrenador si se menciona uno concreto."""
        # Primero busca en catálogo de personas
        for name in ENTRENADORES_CONOCIDOS:
            if name in q_lower:
                return [name]

        cleaned = q_lower
        kws = [
            "información del entrenador", "informacion del entrenador",
            "información de", "informacion de",
            "quien es el entrenador", "quién es el entrenador",
            "el entrenador", "entrenadores", "entrenador",
            "técnico", "tecnico", "quien dirige", "quién dirige",
            # EN
            "information of the coach", "info of the coach", "info about the coach",
            "who is the coach", "the coach", "coach", "manager", "who manages",
            # FR
            "informations sur l'entraîneur", "infos sur l'entraîneur", "qui est l'entraîneur",
            "l'entraîneur", "entraineur", "technicien", "qui dirige"
        ]
        for kw in sorted(kws, key=len, reverse=True):
            cleaned = cleaned.replace(kw, "")
        cleaned = cleaned.strip(" ¿?!,")
        return [cleaned] if cleaned else []
