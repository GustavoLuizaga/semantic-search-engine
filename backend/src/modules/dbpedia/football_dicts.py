"""
football_dicts.py
=================
Diccionarios centralizados del módulo DBpedia.
Pega aquí tus datos — la lógica vive en los otros archivos.
"""

import json
import os

# ── JSONs externos (se cargan desde los .json del mismo directorio) ────────
# No tocar — se cargan automáticamente.

_DBPEDIA_DIR = os.path.dirname(__file__)

def _load_json(filename: str) -> dict:
    path = os.path.join(_DBPEDIA_DIR, filename)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}

CLUB_URI_MAP: dict      = _load_json("club_uris.json")
STADIUM_URI_MAP: dict   = _load_json("stadium_uris.json")
CITY_CLUBS: dict        = _load_json("city_clubs.json")


# ── Estadio principal por club ─────────────────────────────────────────────
# Cuando DBpedia lista varios grounds, se usa este para elegir el principal.
# Pega aquí tus entradas: "URI_club": "URI_estadio"

CLUB_PRIMARY_STADIUM: dict[str, str] = {
        "http://dbpedia.org/resource/FC_Barcelona": "http://dbpedia.org/resource/Camp_Nou",
    "http://dbpedia.org/resource/Real_Madrid_CF": "http://dbpedia.org/resource/Santiago_Bernabéu_Stadium",
    "http://dbpedia.org/resource/Manchester_United_F.C.": "http://dbpedia.org/resource/Old_Trafford",
    "http://dbpedia.org/resource/Manchester_City_F.C.": "http://dbpedia.org/resource/City_of_Manchester_Stadium",
    "http://dbpedia.org/resource/Liverpool_F.C.": "http://dbpedia.org/resource/Anfield",
    "http://dbpedia.org/resource/Arsenal_F.C.": "http://dbpedia.org/resource/Emirates_Stadium",
    "http://dbpedia.org/resource/Chelsea_F.C.": "http://dbpedia.org/resource/Stamford_Bridge_(stadium)",
}


# ── Frases por idioma para detectar "estadio de un equipo" ────────────────
# Estructura: { "código_idioma": (frase1, frase2, ...) }

TEAM_STADIUM_PHRASES: dict[str, tuple] = {
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


# ── Traducción de nombres de países a español ──────────────────────────────
# Usado para normalizar entidades antes de armar el SPARQL.
# Pega aquí tus entradas: "nombre_en_cualquier_idioma": "nombre_en_español"

PAISES_Y_NACIONALIDADES: dict[str, str] = {
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
    "mundial":        "fifa world cup",
    "world cup":      "fifa world cup",
    "copa del mundo": "fifa world cup",
    "coupe du monde": "fifa world cup",
    "weltmeisterschaft": "fifa world cup",
}


# ── Aliases de clubes ──────────────────────────────────────────────────────
# Apodos y variantes → nombre canónico.
# Pega aquí tus entradas: "apodo": "nombre canónico"

ALIASES: dict[str, str] = {
     "barça":     "fc barcelona",
    "barca":     "fc barcelona",
    "fc barcelone": "fc barcelona",
    "barcelone": "fc barcelona",
    "merengues": "real madrid",
    "real":      "real madrid",
    "bayer":     "bayern munchen",
    "bayern de munich": "bayern munchen",
    "bayern de múnich": "bayern munchen",
    "bayern munich": "bayern munchen",
    "champions": "uefa champions league",
    "champions league": "uefa champions league",
    "uefa champions league": "uefa champions league",
    "clasico":   "__real_madrid_vs_barcelona__",
    "coupe du roi": "copa del rey",
    "king's cup": "copa del rey",
}


TEMPLATES = {
    "es": {
        "no_results":        "No encontré resultados en DBpedia para tu consulta.",
        "no_support":        "Esta consulta requiere datos específicos de partidos que DBpedia no tiene. Prueba con la ontología local.",
        "ask_team":          "Indica el nombre del equipo, por ejemplo: «¿Dónde juega el Manchester United?» o «Estadio del Real Madrid».",
        "jugador":           "Según DBpedia, {nombre} es un jugador de nacionalidad {nac} que juega de {pos} en el {equipo}. Usa el dorsal #{dorsal}, nació el {birth}{alt}.",
        "alt_str":           " y mide {estatura}",
        "fecha_nacimiento":  "Según DBpedia, la fecha de nacimiento de {nombre} es el {birth}.",
        "equipo_intro":      "Según DBpedia, el equipo {nombre}{apodos}",
        "apodos_str":        " (conocido como {nicks})",
        "equipo_fundado":    "fue fundado el {fundacion}.",
        "equipo_historico":  "es un club histórico.",
        "equipo_estadio":    "Juega local en el estadio {estadio}{capacidad}.",
        "equipo_gestion":    "Actualmente, {gestion}.",
        "dirigido_por":      "es dirigido por {director}",
        "presidido_por":     "presidido por {presidente}",
        "jugadores_equipo":  "Según DBpedia, algunos jugadores registrados en la plantilla de este equipo son: {nombres}.",
        "todos_estadios":    "Según DBpedia, hay {n} estadios de fútbol de clubes profesionales en el catálogo, por ejemplo: {resumen}.",
        "estadio_equipo":    "Según DBpedia, el estadio local del {equipo} es el {nombre}.",
        "estadio_info":      "Según DBpedia, información del estadio {nombre}:",
        "estadios_ubicacion":"En DBpedia encontré {n} estadio(s) de fútbol en {lugar}: {resumen}.{cap_hint}",
        "cap_hint":          " Ej.: {nombre} ({cap} espectadores).",
        "ubicacion":         "Ubicación: {val}.",
        "capacidad":         "Capacidad: {val} espectadores.",
        "equipo_local":      "Equipo local: {val}.",
        "inauguracion":      "Inauguración: {val}.",
        "entrenador":        "Según DBpedia, el entrenador {nombre} nació el {birth} y dirige o dirigió al equipo {equipo}.",
        "nacionalidad":      "En DBpedia encontré varios futbolistas con esa nacionalidad, incluyendo a: {nombres}.",
        "equipos_pais":      "En DBpedia encontré varios clubes de fútbol de ese país, incluyendo a: {nombres}.",
        "desconocido":       "Desconocida",
        "sin_equipo":        "Sin equipo/Retirado",
        "sin_dorsal":        "Sin dorsal",
        "y_mas":             "y {n} más",
        "abstract":          "{nombre} (según DBpedia): {abstract}",
    },
    "en": {
        "no_results":        "No results found in DBpedia for your query.",
        "no_support":        "This query requires specific match data that DBpedia does not have. Try the local ontology.",
        "ask_team":          "Please specify the team name, e.g.: «Where does Manchester United play?» or «Real Madrid stadium».",
        "jugador":           "According to DBpedia, {nombre} is a {nac} player who plays as {pos} for {equipo}. He wears #{dorsal} and was born on {birth}{alt}.",
        "alt_str":           " and is {estatura} tall",
        "fecha_nacimiento":  "According to DBpedia, {nombre}'s date of birth is {birth}.",
        "equipo_intro":      "According to DBpedia, the club {nombre}{apodos}",
        "apodos_str":        " (also known as {nicks})",
        "equipo_fundado":    "was founded on {fundacion}.",
        "equipo_historico":  "is a historic club.",
        "equipo_estadio":    "They play home games at {estadio}{capacidad}.",
        "equipo_gestion":    "Currently, {gestion}.",
        "dirigido_por":      "managed by {director}",
        "presidido_por":     "chaired by {presidente}",
        "jugadores_equipo":  "According to DBpedia, some players registered in this team's squad are: {nombres}.",
        "todos_estadios":    "According to DBpedia, there are {n} football stadiums of professional clubs in the catalogue, for example: {resumen}.",
        "estadio_equipo":    "According to DBpedia, {equipo}'s home stadium is {nombre}.",
        "estadio_info":      "According to DBpedia, information about {nombre} stadium:",
        "estadios_ubicacion":"DBpedia found {n} football stadium(s) in {lugar}: {resumen}.{cap_hint}",
        "cap_hint":          " E.g.: {nombre} ({cap} spectators).",
        "ubicacion":         "Location: {val}.",
        "capacidad":         "Capacity: {val} spectators.",
        "equipo_local":      "Home team: {val}.",
        "inauguracion":      "Opened: {val}.",
        "entrenador":        "According to DBpedia, coach {nombre} was born on {birth} and manages or managed {equipo}.",
        "nacionalidad":      "DBpedia found several footballers with that nationality, including: {nombres}.",
        "equipos_pais":      "DBpedia found several football clubs from that country, including: {nombres}.",
        "desconocido":       "Unknown",
        "sin_equipo":        "No team/Retired",
        "sin_dorsal":        "No number",
        "y_mas":             "and {n} more",
        "abstract":          "{nombre} (from DBpedia): {abstract}",
    },
    "fr": {
        "no_results":        "Aucun résultat trouvé dans DBpedia pour votre requête.",
        "no_support":        "Cette requête nécessite des données de matchs spécifiques que DBpedia ne possède pas. Essayez l'ontologie locale.",
        "ask_team":          "Veuillez indiquer le nom de l'équipe, par exemple : «Où joue Manchester United ?» ou «Stade du Real Madrid».",
        "jugador":           "Selon DBpedia, {nombre} est un joueur de nationalité {nac} qui joue comme {pos} à {equipo}. Il porte le #{dorsal} et est né le {birth}{alt}.",
        "alt_str":           " et mesure {estatura}",
        "fecha_nacimiento":  "Selon DBpedia, la date de naissance de {nombre} est le {birth}.",
        "equipo_intro":      "Selon DBpedia, le club {nombre}{apodos}",
        "apodos_str":        " (aussi connu sous le nom de {nicks})",
        "equipo_fundado":    "a été fondé le {fundacion}.",
        "equipo_historico":  "est un club historique.",
        "equipo_estadio":    "Il joue à domicile au stade {estadio}{capacidad}.",
        "equipo_gestion":    "Actuellement, {gestion}.",
        "dirigido_por":      "est entraîné par {director}",
        "presidido_por":     "présidé par {presidente}",
        "jugadores_equipo":  "Selon DBpedia, quelques joueurs enregistrés dans l'effectif de cette équipe sont : {nombres}.",
        "todos_estadios":    "Selon DBpedia, il y a {n} stades de football de clubs professionnels dans le catalogue, par exemple : {resumen}.",
        "estadio_equipo":    "Selon DBpedia, le stade domicile de {equipo} est {nombre}.",
        "estadio_info":      "Selon DBpedia, informations sur le stade {nombre} :",
        "estadios_ubicacion":"DBpedia a trouvé {n} stade(s) de football à {lugar} : {resumen}.{cap_hint}",
        "cap_hint":          " Ex. : {nombre} ({cap} spectateurs).",
        "ubicacion":         "Emplacement : {val}.",
        "capacidad":         "Capacité : {val} spectateurs.",
        "equipo_local":      "Équipe locale : {val}.",
        "inauguracion":      "Inauguration : {val}.",
        "entrenador":        "Selon DBpedia, l'entraîneur {nombre} est né le {birth} et entraîne ou a entraîné {equipo}.",
        "nacionalidad":      "DBpedia a trouvé plusieurs footballeurs de cette nationalité, notamment : {nombres}.",
        "equipos_pais":      "DBpedia a trouvé plusieurs clubs de football de ce pays, notamment : {nombres}.",
        "desconocido":       "Inconnu",
        "sin_equipo":        "Sans équipe/Retraité",
        "sin_dorsal":        "Sans numéro",
        "y_mas":             "et {n} de plus",
        "abstract":          "{nombre} (selon DBpedia) : {abstract}",
    },
}


FIFA_CODE_TO_NAME: dict[str, dict[str, str]] = {
    "ARG": {"es": "Argentina",       "en": "Argentina",    "fr": "Argentine"},
    "FRA": {"es": "Francia",         "en": "France",       "fr": "France"},
    "CRO": {"es": "Croacia",         "en": "Croatia",      "fr": "Croatie"},
    "MAR": {"es": "Marruecos",       "en": "Morocco",      "fr": "Maroc"},
    "BRA": {"es": "Brasil",          "en": "Brazil",       "fr": "Brésil"},
    "ENG": {"es": "Inglaterra",      "en": "England",      "fr": "Angleterre"},
    "ESP": {"es": "España",          "en": "Spain",        "fr": "Espagne"},
    "GER": {"es": "Alemania",        "en": "Germany",      "fr": "Allemagne"},
    "POR": {"es": "Portugal",        "en": "Portugal",     "fr": "Portugal"},
    "ITA": {"es": "Italia",          "en": "Italy",        "fr": "Italie"},
    "NED": {"es": "Países Bajos",    "en": "Netherlands",  "fr": "Pays-Bas"},
    "BEL": {"es": "Bélgica",         "en": "Belgium",      "fr": "Belgique"},
    "URU": {"es": "Uruguay",         "en": "Uruguay",      "fr": "Uruguay"},
    "MEX": {"es": "México",          "en": "Mexico",       "fr": "Mexique"},
    "USA": {"es": "Estados Unidos",  "en": "United States","fr": "États-Unis"},
    "JPN": {"es": "Japón",           "en": "Japan",        "fr": "Japon"},
    "KOR": {"es": "Corea del Sur",   "en": "South Korea",  "fr": "Corée du Sud"},
    "AUS": {"es": "Australia",       "en": "Australia",    "fr": "Australie"},
    "SEN": {"es": "Senegal",         "en": "Senegal",      "fr": "Sénégal"},
    "CMR": {"es": "Camerún",         "en": "Cameroon",     "fr": "Cameroun"},
    "GHA": {"es": "Ghana",           "en": "Ghana",        "fr": "Ghana"},
    "QAT": {"es": "Qatar",           "en": "Qatar",        "fr": "Qatar"},
    "KSA": {"es": "Arabia Saudita",  "en": "Saudi Arabia", "fr": "Arabie saoudite"},
    "IRN": {"es": "Irán",            "en": "Iran",         "fr": "Iran"},
    "POL": {"es": "Polonia",         "en": "Poland",       "fr": "Pologne"},
    "DEN": {"es": "Dinamarca",       "en": "Denmark",      "fr": "Danemark"},
    "SUI": {"es": "Suiza",           "en": "Switzerland",  "fr": "Suisse"},
    "SRB": {"es": "Serbia",          "en": "Serbia",       "fr": "Serbie"},
    "WAL": {"es": "Gales",           "en": "Wales",        "fr": "Pays de Galles"},
    "CAN": {"es": "Canadá",          "en": "Canada",       "fr": "Canada"},
    "ECU": {"es": "Ecuador",         "en": "Ecuador",      "fr": "Équateur"},
    "CRC": {"es": "Costa Rica",      "en": "Costa Rica",   "fr": "Costa Rica"},
    "TUN": {"es": "Túnez",           "en": "Tunisia",      "fr": "Tunisie"},
    # Ganadores históricos adicionales
    "ITA": {"es": "Italia",          "en": "Italy",        "fr": "Italie"},
    "WGE": {"es": "Alemania Occ.",   "en": "West Germany", "fr": "Allemagne de l'Ouest"},
    "TCH": {"es": "Checoslovaquia",  "en": "Czechoslovakia","fr": "Tchécoslovaquie"},
    "HUN": {"es": "Hungría",         "en": "Hungary",      "fr": "Hongrie"},
    "SWE": {"es": "Suecia",          "en": "Sweden",       "fr": "Suède"},
}

def resolve_fifa_code(code: str, language: str = "es") -> str:
    """Convierte código FIFA al nombre en el idioma pedido. Fallback al código mismo."""
    entry = FIFA_CODE_TO_NAME.get(code.upper().strip())
    if entry:
        return entry.get(language) or entry.get("en") or code
    return code


# Años válidos de Copa del Mundo FIFA
WC_YEARS: frozenset[int] = frozenset({
    1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966,
    1970, 1974, 1978, 1982, 1986, 1990, 1994, 1998,
    2002, 2006, 2010, 2014, 2018, 2022, 2026,
})