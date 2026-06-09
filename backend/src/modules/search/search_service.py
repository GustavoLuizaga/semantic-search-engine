import os
from src.modules.semantic.local_semantic_parser import LocalSemanticParser
from src.modules.semantic.ontology_matcher import OntologyMatcher
from src.modules.sparql.sparql_builder import SPARQLBuilder
from src.modules.sparql.sparql_executor import SPARQLExecutor
from src.models import SearchResponse

_HERE    = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
OWX_PATH = os.path.join(_BACKEND, "ontologia-futbol.owl")
if not os.path.exists(OWX_PATH):
    OWX_PATH = os.path.join(os.getcwd(), "ontologia-futbol.owl")

print(f"[search_service] OWX: {OWX_PATH} | exists={os.path.exists(OWX_PATH)}")

# ── Inicialización única ───────────────────────────────────────────────────
executor = SPARQLExecutor(OWX_PATH)
matcher  = OntologyMatcher(executor)


# ── Translation Helpers ────────────────────────────────────────────────────
def translate_pos(pos: str, lang: str) -> str:
    if not pos:
        return ""
    pos_lower = pos.lower().strip()
    mapeo = {
        "en": {
            "delantero": "forward",
            "mediocampista": "midfielder",
            "portero": "goalkeeper",
            "defensa": "defender"
        },
        "fr": {
            "delantero": "attaquant",
            "mediocampista": "milieu",
            "portero": "gardien de but",
            "defensa": "défenseur"
        }
    }
    return mapeo.get(lang, {}).get(pos_lower, pos)


def translate_nac(nac: str, lang: str) -> str:
    if not nac:
        return ""
    nac_lower = nac.lower().strip()
    mapeo = {
        "en": {
            "española": "Spanish",
            "alemana": "German",
            "francesa": "French",
            "italiana": "Italian",
            "colombiana": "Colombian",
            "argentina": "Argentinian",
            "brasileña": "Brazilian",
            "uruguaya": "Uruguayan",
            "inglesa": "English",
            "portuguesa": "Portuguese",
            "croata": "Croatian",
            "polaca": "Polish"
        },
        "fr": {
            "española": "espagnole",
            "alemana": "allemande",
            "francesa": "française",
            "italiana": "italienne",
            "colombiana": "colombienne",
            "argentina": "argentine",
            "brasileña": "brésilienne",
            "uruguaya": "uruguayenne",
            "inglesa": "anglaise",
            "portuguesa": "portugaise",
            "croata": "croate",
            "polaca": "polonaise"
        }
    }
    return mapeo.get(lang, {}).get(nac_lower, nac)


def translate_pais(pais: str, lang: str) -> str:
    if not pais:
        return ""
    p_lower = pais.lower().strip()
    mapeo = {
        "en": {
            "españa": "Spain",
            "alemania": "Germany",
            "francia": "France",
            "italia": "Italy",
            "colombia": "Colombia",
            "argentina": "Argentina",
            "brasil": "Brazil",
            "uruguay": "Uruguay",
            "inglaterra": "England",
            "portugal": "Portugal",
            "croacia": "Croatia",
            "polonia": "Poland"
        },
        "fr": {
            "españa": "Espagne",
            "alemania": "Allemagne",
            "francia": "France",
            "italia": "Italie",
            "colombia": "Colombie",
            "argentina": "Argentine",
            "brasil": "Brésil",
            "uruguay": "Uruguay",
            "inglaterra": "Angleterre",
            "portugal": "Portugal",
            "croacia": "Croatie",
            "polonia": "Pologne"
        }
    }
    return mapeo.get(lang, {}).get(p_lower, pais)


def translate_entity(val: str, lang: str) -> str:
    if not val:
        return val
    val_lower = val.lower().strip()
    mapeo = {
        "en": {
            "fc barcelona": "FC Barcelona",
            "bayern munchen": "Bayern Munich",
            "santiago bernabéu": "Santiago Bernabeu Stadium",
            "copa del rey": "King's Cup",
            "españa": "Spain",
            "alemania": "Germany",
            "francia": "France",
            "inglaterra": "England",
            "madrid": "Madrid",
            "munich": "Munich",
            "múnich": "Munich"
        },
        "fr": {
            "fc barcelona": "FC Barcelone",
            "bayern munchen": "Bayern Munich",
            "santiago bernabéu": "Stade Santiago Bernabéu",
            "copa del rey": "Coupe du Roi",
            "españa": "Espagne",
            "alemania": "Allemagne",
            "francia": "France",
            "inglaterra": "Angleterre",
            "madrid": "Madrid",
            "munich": "Munich",
            "múnich": "Munich"
        }
    }
    return mapeo.get(lang, {}).get(val_lower, val)


def _fmt_fecha(f_str: str) -> str:
    if not f_str or f_str == "Sin fecha":
        return ""
    return f_str.split("T")[0]


# ── Data Key Translations ──────────────────────────────────────────────────
# Maps Spanish key names → translated key names per language
_KEY_MAP = {
    # partido / resultado
    "local":           {"en": "home",         "fr": "domicile"},
    "visitante":       {"en": "away",          "fr": "visiteur"},
    "goles_local":     {"en": "home_goals",    "fr": "buts_domicile"},
    "goles_visitante": {"en": "away_goals",    "fr": "buts_visiteur"},
    "fecha":           {"en": "date",          "fr": "date"},
    "estadio":         {"en": "stadium",       "fr": "stade"},
    "arbitro":         {"en": "referee",       "fr": "arbitre"},
    "competicion":     {"en": "competition",   "fr": "compétition"},
    # jugador
    "nombre":          {"en": "name",          "fr": "nom"},
    "dorsal":          {"en": "number",        "fr": "numéro"},
    "posicion":        {"en": "position",      "fr": "poste"},
    "nacionalidad":    {"en": "nationality",   "fr": "nationalité"},
    "equipo":          {"en": "team",          "fr": "équipe"},
    "goles":           {"en": "goals",         "fr": "buts"},
    "capitan":         {"en": "captain",       "fr": "capitaine"},
    # equipo
    "ciudad":          {"en": "city",          "fr": "ville"},
    "pais":            {"en": "country",       "fr": "pays"},
    "entrenador":      {"en": "coach",         "fr": "entraîneur"},
    "liga":            {"en": "league",        "fr": "ligue"},
    # estadio
    "capacidad":       {"en": "capacity",      "fr": "capacité"},
    # tarjeta
    "tipo":            {"en": "type",          "fr": "type"},
    "jugador":         {"en": "player",        "fr": "joueur"},
    "minuto":          {"en": "minute",        "fr": "minute"},
    "tiempo":          {"en": "period",        "fr": "période"},
    "motivo":          {"en": "reason",        "fr": "motif"},
    # sustituciones
    "entra":           {"en": "enters",        "fr": "entre"},
    "sale":            {"en": "exits",         "fr": "sort"},
    # goles detalle
    "anotador":        {"en": "scorer",        "fr": "buteur"},
    "asistidor":       {"en": "assister",      "fr": "passeur"},
    "asistencias":     {"en": "assists",       "fr": "passes_décisives"},
    # goleadores ranking
    "total":           {"en": "total",         "fr": "total"},
    # fecha nacimiento
    "fecha_nacimiento": {"en": "birth_date",   "fr": "date_naissance"},
    # titular
    "es_titular":      {"en": "is_starter",    "fr": "est_titulaire"},
    # torneos
    "torneos":         {"en": "tournaments",   "fr": "tournois"},
    # entrenador
    "goleador":        {"en": "goalscorer",    "fr": "buteur"},
}


def translate_data_keys(data, lang: str):
    """Recursively rename Spanish keys in data dicts/lists to the target language."""
    if lang == "es" or not data:
        return data
    if isinstance(data, list):
        return [translate_data_keys(item, lang) for item in data]
    if isinstance(data, dict):
        new = {}
        for k, v in data.items():
            translated_key = _KEY_MAP.get(k, {}).get(lang, k)
            new[translated_key] = translate_data_keys(v, lang)
        return new
    return data


def _resumir_lista(nombres: list, lang: str = "es") -> str:
    if not nombres:
        return ""
    if lang == "en":
        and_word = "and"
        more_word = "more"
    elif lang == "fr":
        and_word = "et"
        more_word = "plus"
    else:
        and_word = "y"
        more_word = "más"
        
    if len(nombres) > 5:
        return ", ".join(nombres[:5]) + f" {and_word} {len(nombres) - 5} {more_word}"
    if len(nombres) > 1:
        return ", ".join(nombres[:-1]) + f" {and_word} {nombres[-1]}"
    return nombres[0]


T = {
    "es": {
        "no_entidades_equipos": "No pude identificar los equipos en tu consulta.",
        "no_partidos": "No encontré partidos para esos equipos.",
        "resultado_fmt": "El resultado fue {local} {goles_local} - {goles_visitante} {visitante}.",
        "cant_partidos": "Se encontraron {cant} partidos.",
        
        "jugador_goles": "{nom} tiene {total} gol(es) registrado(s) en la ontología.",
        "no_partido_jugador": "No pude identificar el partido o jugador en tu consulta.",
        "partido_no_encontrado": "No se encontró el partido.",
        "no_detalle_goles": "No hay detalle de goles registrado para ese partido.",
        "cant_goles_partido": "En el partido {local} vs {vis} se registraron {cant} gol(es).",
        
        "no_equipo": "No pude identificar el equipo en tu consulta.",
        "no_jugadores_equipo": "No hay jugadores registrados para ese equipo.",
        "plantilla_fmt": "La plantilla del {eq_nom} tiene {cant} jugadores, entre ellos: {lista}.",
        
        "no_info_equipo": "No encontré información para ese equipo.",
        "entrenador_de": "El entrenador del {nom} es {dt}.",
        "estadio_de": "El estadio del {nom} es el {estadio}.",
        "liga_de": "El {nom} juega en la {liga}.",
        "ciudad_de": "El {nom} es de {ciudad}, {pais}.",
        "info_equipo_completa": "El {nom} es un equipo de {ciudad}, {pais}, dirigido por {dt}. Juega como local en el {estadio} y participa en la {liga}.",
        
        "no_jugador": "No pude identificar al jugador en tu consulta.",
        "no_info_jugador": "No encontré información para ese jugador.",
        "posicion_de": "{nom} juega en la posición de {pos}.",
        "equipo_de": "{nom} juega en el {eq_nom}.",
        "nacionalidad_de": "La nacionalidad de {nom} es {nac}.",
        "dorsal_de": "{nom} usa el dorsal #{dor}.",
        "goles_de": "{nom} tiene {goles} goles registrados.",
        "info_jugador_completa": "{nom} es un jugador de nacionalidad {nac} que juega de {pos} en el {eq_nom}{cap_str}. Usa el dorsal #{dor} y tiene {goles} goles registrados.",
        "capitan_label": " (capitán)",
        
        "no_dorsal": "No pude identificar el número de dorsal.",
        "no_jugador_dorsal": "No encontré un jugador con ese dorsal.",
        "jugador_dorsal_fmt": "El jugador que lleva el dorsal #{dorsal} en el {eq_nom} es {nom}.",
        
        "no_nacionalidad": "No pude identificar la nacionalidad en tu consulta.",
        "no_jugadores_nacionalidad": "No encontré jugadores con esa nacionalidad.",
        "jugadores_nacionalidad_fmt": "Se encontraron {cant} jugadores con nacionalidad {nac_display}, entre ellos: {lista}.",
        
        "no_pais": "No pude identificar el país en tu consulta.",
        "no_equipos_pais": "No encontré equipos del país '{nac}'.",
        "equipos_pais_fmt": "Encontré {cant} equipos de {nac}: {lista}.",
        
        "no_estadios": "No hay estadios registrados.",
        "estadios_registrados": "Hay {cant} estadios registrados: {lista}.",
        "no_info_estadio": "No encontré información para ese estadio.",
        "capacidad_estadio": "La capacidad del estadio {nom} es de {cap} espectadores.",
        "ubicacion_estadio": "El estadio {nom} está ubicado en {ciu}, {pai}.",
        "info_estadio_completa": "El estadio {nom} está en {ciu}, {pai}, con capacidad para {cap} espectadores.",
        
        "no_ubicacion": "No pude identificar la ubicación en tu consulta.",
        "no_estadios_ubicacion": "No encontré estadios registrados en {ubicacion}.",
        "estadios_ubicacion_fmt": "Se encontraron {cant} estadio(s) en {ubicacion}: {lista}.",
        
        "no_arbitros": "No hay árbitros registrados.",
        "arbitros_registrados": "Hay {cant} árbitros registrados: {lista}.",
        
        "no_tarjetas": "No hay tarjetas registradas.",
        "tarjetas_registradas": "Se encontraron {cant} tarjetas registradas en total.",
        
        "no_sustituciones": "No hay sustituciones registradas.",
        "sustituciones_registradas": "Se encontraron {cant} sustituciones registradas.",
        
        "no_goles_ranking": "No hay registros de goles.",
        "goleadores_ranking_fmt": "Top goleadores: {lista}.",
        
        "no_competicion": "No pude identificar la competición en tu consulta.",
        "no_partidos_competicion": "No encontré partidos registrados para la competición {comp}.",
        "partidos_competicion_fmt": "Se encontraron {cant} partido(s) de la competición {comp_name}.",
        
        "no_todos_partidos": "No se encontraron partidos registrados.",
        "todos_partidos_fmt": "Se encontraron {cant} partidos registrados.",
        
        "no_todos_equipos": "No hay equipos registrados.",
        "todos_equipos_fmt": "Hay {cant} equipos registrados: {lista}.",
        
        "no_todos_jugadores": "No hay jugadores registrados.",
        "todos_jugadores_fmt": "Hay {cant} jugadores registrados: {lista}.",
        
        "no_capitan": "No encontré un capitán registrado para ese equipo.",
        "capitan_fmt": "El capitán del {eq_nom} es {nom} (Dorsal #{dor}, {pos}).",
        
        "no_persona": "No pude identificar a la persona en tu consulta.",
        "no_fecha_nacimiento": "No encontré la fecha de nacimiento para esa persona.",
        "fecha_nacimiento_fmt": "La fecha de nacimiento de {nom} es el {fecha}.",
        
        "no_info_titularidad": "No encontré información de titularidad para ese jugador.",
        "es_titular_fmt": "Sí, {nom} es un jugador titular en el {eq_nom}.",
        "no_es_titular_fmt": "No, {nom} no figura como titular o no hay datos confirmados.",
        
        "no_torneos_internacionales": "No hay torneos internacionales registrados.",
        "torneos_internacionales_fmt": "Hay {cant} torneos internacionales registrados: {lista}.",
        
        "no_asistencias": "No encontré registros de asistencias para los goles de este jugador.",
        "asistencia_unica_fmt": "{asistidor} le dio la asistencia a {goleador} en el minuto {minuto} ({tiempo}).",
        "asistencias_multiples_fmt": "Se encontraron {cant} asistencias para los goles de {goleador}, dadas por: {lista}.",
        
        "no_motivo_tarjeta": "No pude identificar el motivo de la tarjeta en tu consulta.",
        "no_tarjetas_motivo": "No encontré jugadores con tarjetas por el motivo '{motivo}'.",
        "tarjetas_motivo_fmt": "Se encontraron {cant} tarjetas por motivos similares a '{motivo}'. Jugadores amonestados/expulsados: {lista}.",
        
        "no_goles_propia_puerta": "No hay goles en propia puerta registrados.",
        "goles_propia_puerta_fmt": "Se encontraron {cant} goles en propia puerta, anotados por: {lista}.",
        
        "no_goles_penal": "No hay goles de penal registrados.",
        "goles_penal_fmt": "Se encontraron {cant} goles de penal, anotados por: {lista}.",
        
        "no_posicion": "No pude identificar la posición en tu consulta.",
        "no_jugadores_posicion": "No encontré jugadores que jueguen de {posicion}.",
        "jugadores_posicion_fmt": "Hay {cant} jugadores de posición {posicion}: {lista}.",
        
        "no_entrenadores": "No hay entrenadores registrados.",
        "entrenadores_registrados": "Hay {cant} entrenadores registrados: {lista}.",
        "no_info_entrenador": "No encontré información para ese entrenador.",
        "entrenador_equipo": "{nom} dirige al {equipo}.",
        "entrenador_nacionalidad": "{nom} es de nacionalidad {nac}.",
        "entrenador_nacimiento": "{nom} nació el {fecha}.",
        "info_entrenador_completa": "{nom} es un entrenador de nacionalidad {nac}, nacido el {fecha}. Actualmente dirige al {equipo}.",
        
        "error_procesando": "Error procesando la consulta: {error}",
        "fallback_respuesta": "No se encontraron resultados para tu consulta."
    },
    "en": {
        "no_entidades_equipos": "I couldn't identify the teams in your query.",
        "no_partidos": "I didn't find any matches for those teams.",
        "resultado_fmt": "The result was {local} {goles_local} - {goles_visitante} {visitante}.",
        "cant_partidos": "Found {cant} matches.",
        
        "jugador_goles": "{nom} has {total} goal(s) registered in the ontology.",
        "no_partido_jugador": "I couldn't identify the match or player in your query.",
        "partido_no_encontrado": "Match not found.",
        "no_detalle_goles": "No goal details registered for that match.",
        "cant_goles_partido": "In the match {local} vs {vis}, {cant} goal(s) were registered.",
        
        "no_equipo": "I couldn't identify the team in your query.",
        "no_jugadores_equipo": "No players registered for that team.",
        "plantilla_fmt": "The squad of {eq_nom} has {cant} players, including: {lista}.",
        
        "no_info_equipo": "I didn't find information for that team.",
        "entrenador_de": "The coach of {nom} is {dt}.",
        "estadio_de": "The stadium of {nom} is {estadio}.",
        "liga_de": "{nom} plays in {liga}.",
        "ciudad_de": "{nom} is from {ciudad}, {pais}.",
        "info_equipo_completa": "{nom} is a team from {ciudad}, {pais}, managed by {dt}. It plays home games at {estadio} and participates in {liga}.",
        
        "no_jugador": "I couldn't identify the player in your query.",
        "no_info_jugador": "I didn't find information for that player.",
        "posicion_de": "{nom} plays as a {pos}.",
        "equipo_de": "{nom} plays for {eq_nom}.",
        "nacionalidad_de": "{nom}'s nationality is {nac}.",
        "dorsal_de": "{nom} wears number #{dor}.",
        "goles_de": "{nom} has {goles} registered goals.",
        "info_jugador_completa": "{nom} is a player of {nac} nationality who plays as a {pos} for {eq_nom}{cap_str}. He wears number #{dor} and has {goles} registered goals.",
        "capitan_label": " (captain)",
        
        "no_dorsal": "I couldn't identify the shirt number.",
        "no_jugador_dorsal": "I didn't find a player with that number.",
        "jugador_dorsal_fmt": "The player who wears number #{dorsal} at {eq_nom} is {nom}.",
        
        "no_nacionalidad": "I couldn't identify the nationality in your query.",
        "no_jugadores_nacionalidad": "I didn't find players with that nationality.",
        "jugadores_nacionalidad_fmt": "Found {cant} players with nationality {nac_display}, including: {lista}.",
        
        "no_pais": "I couldn't identify the country in your query.",
        "no_equipos_pais": "I didn't find teams from country '{nac}'.",
        "equipos_pais_fmt": "Found {cant} teams from {nac}: {lista}.",
        
        "no_estadios": "No registered stadiums found.",
        "estadios_registrados": "There are {cant} registered stadiums: {lista}.",
        "no_info_estadio": "I didn't find information for that stadium.",
        "capacidad_estadio": "The capacity of the stadium {nom} is {cap} spectators.",
        "ubicacion_estadio": "The stadium {nom} is located in {ciu}, {pai}.",
        "info_estadio_completa": "The stadium {nom} is in {ciu}, {pai}, with a capacity of {cap} spectators.",
        
        "no_ubicacion": "I couldn't identify the location in your query.",
        "no_estadios_ubicacion": "No registered stadiums found in {ubicacion}.",
        "estadios_ubicacion_fmt": "Found {cant} stadium(s) in {ubicacion}: {lista}.",
        
        "no_arbitros": "No registered referees found.",
        "arbitros_registrados": "There are {cant} registered referees: {lista}.",
        
        "no_tarjetas": "No registered cards found.",
        "tarjetas_registradas": "Found {cant} cards registered in total.",
        
        "no_sustituciones": "No registered substitutions found.",
        "sustituciones_registradas": "Found {cant} registered substitutions.",
        
        "no_goles_ranking": "No goal records found.",
        "goleadores_ranking_fmt": "Top scorers: {lista}.",
        
        "no_competicion": "I couldn't identify the competition in your query.",
        "no_partidos_competicion": "No registered matches found for competition {comp}.",
        "partidos_competicion_fmt": "Found {cant} match(es) from competition {comp_name}.",
        
        "no_todos_partidos": "No registered matches found.",
        "todos_partidos_fmt": "Found {cant} registered matches.",
        
        "no_todos_equipos": "No registered teams found.",
        "todos_equipos_fmt": "There are {cant} registered teams: {lista}.",
        
        "no_todos_jugadores": "No registered players found.",
        "todos_jugadores_fmt": "There are {cant} registered players: {lista}.",
        
        "no_capitan": "No registered captain found for that team.",
        "capitan_fmt": "The captain of {eq_nom} is {nom} (Number #{dor}, {pos}).",
        
        "no_persona": "I couldn't identify the person in your query.",
        "no_fecha_nacimiento": "I didn't find the date of birth for that person.",
        "fecha_nacimiento_fmt": "{nom}'s date of birth is {fecha}.",
        
        "no_info_titularidad": "I didn't find starting line-up info for that player.",
        "es_titular_fmt": "Yes, {nom} is a starting player for {eq_nom}.",
        "no_es_titular_fmt": "No, {nom} is not listed as a starter or there is no confirmed data.",
        
        "no_torneos_internacionales": "No registered international tournaments found.",
        "torneos_internacionales_fmt": "There are {cant} registered international tournaments: {lista}.",
        
        "no_asistencias": "No assist records found for this player's goals.",
        "asistencia_unica_fmt": "{asistidor} assisted {goleador} in minute {minuto} ({tiempo}).",
        "asistencias_multiples_fmt": "Found {cant} assists for {goleador}'s goals, provided by: {lista}.",
        
        "no_motivo_tarjeta": "I couldn't identify the card motive in your query.",
        "no_tarjetas_motivo": "I didn't find players with cards for motive '{motivo}'.",
        "tarjetas_motivo_fmt": "Found {cant} cards for motives similar to '{motivo}'. Booked/sent-off players: {lista}.",
        
        "no_goles_propia_puerta": "No own goals registered.",
        "goles_propia_puerta_fmt": "Found {cant} own goals, scored by: {lista}.",
        
        "no_goles_penal": "No penalty goals registered.",
        "goles_penal_fmt": "Found {cant} penalty goals, scored by: {lista}.",
        
        "no_posicion": "I couldn't identify the position in your query.",
        "no_jugadores_posicion": "No players found playing as {posicion}.",
        "jugadores_posicion_fmt": "There are {cant} players in the position of {posicion}: {lista}.",
        
        "no_entrenadores": "No registered coaches found.",
        "entrenadores_registrados": "There are {cant} registered coaches: {lista}.",
        "no_info_entrenador": "I didn't find information for that coach.",
        "entrenador_equipo": "{nom} manages {equipo}.",
        "entrenador_nacionalidad": "{nom} is of {nac} nationality.",
        "entrenador_nacimiento": "{nom} was born on {fecha}.",
        "info_entrenador_completa": "{nom} is a coach of {nac} nationality, born on {fecha}. He currently manages {equipo}.",
        
        "error_procesando": "Error processing query: {error}",
        "fallback_respuesta": "No results were found for your query."
    },
    "fr": {
        "no_entidades_equipos": "Je n'ai pas pu identifier les équipes dans votre requête.",
        "no_partidos": "Je n'ai pas trouvé de matchs pour ces équipes.",
        "resultado_fmt": "Le résultat était {local} {goles_local} - {goles_visitante} {visitante}.",
        "cant_partidos": "{cant} matchs ont été trouvés.",
        
        "jugador_goles": "{nom} a {total} but(s) enregistré(s) dans l'ontologie.",
        "no_partido_jugador": "Je n'ai pas pu identifier le match ou le joueur dans votre requête.",
        "partido_no_encontrado": "Match non trouvé.",
        "no_detalle_goles": "Aucun détail de but enregistré pour ce match.",
        "cant_goles_partido": "Dans le match {local} contre {vis}, {cant} but(s) ont été enregistrés.",
        
        "no_equipo": "Je n'ai pas pu identifier l'équipe dans votre requête.",
        "no_jugadores_equipo": "Aucun joueur enregistré pour cette équipe.",
        "plantilla_fmt": "L'effectif de {eq_nom} compte {cant} joueurs, dont : {lista}.",
        
        "no_info_equipo": "Je n'ai pas trouvé d'informations pour cette équipe.",
        "entrenador_de": "L'entraîneur de {nom} est {dt}.",
        "estadio_de": "Le stade de {nom} est {estadio}.",
        "liga_de": "{nom} joue en {liga}.",
        "ciudad_de": "{nom} est de {ciudad}, {pais}.",
        "info_equipo_completa": "{nom} est une équipe de {ciudad}, {pais}, entraînée par {dt}. Elle joue ses matchs à domicile au {estadio} et participe à {liga}.",
        
        "no_jugador": "Je n'ai pas pu identifier le joueur dans votre requête.",
        "no_info_jugador": "Je n'ai pas trouvé d'informations pour ce joueur.",
        "posicion_de": "{nom} joue au poste de {pos}.",
        "equipo_de": "{nom} joue au {eq_nom}.",
        "nacionalidad_de": "La nationalité de {nom} est {nac}.",
        "dorsal_de": "{nom} porte le numéro #{dor}.",
        "goles_de": "{nom} a {goles} buts enregistrés.",
        "info_jugador_completa": "{nom} est un joueur de nationalité {nac} qui joue comme {pos} au {eq_nom}{cap_str}. Il porte le numéro #{dor} et a {goles} buts enregistrés.",
        "capitan_label": " (capitaine)",
        
        "no_dorsal": "Je n'ai pas pu identifier le numéro de maillot.",
        "no_jugador_dorsal": "Je n'ai pas trouvé de joueur avec ce numéro.",
        "jugador_dorsal_fmt": "Le joueur qui porte le numéro #{dorsal} au {eq_nom} est {nom}.",
        
        "no_nacionalidad": "Je n'ai pas pu identifier la nationalité dans votre requête.",
        "no_jugadores_nacionalidad": "Je n'ai pas trouvé de joueurs de cette nationalité.",
        "jugadores_nacionalidad_fmt": "Trouvé {cant} joueurs de nationalité {nac_display}, dont : {lista}.",
        
        "no_pais": "Je n'ai pas pu identifier le pays dans votre requête.",
        "no_equipos_pais": "Je n'ai pas trouvé d'équipes du pays '{nac}'.",
        "equipos_pais_fmt": "Trouvé {cant} équipes de {nac}: {lista}.",
        
        "no_estadios": "Aucun stade enregistré trouvé.",
        "estadios_registrados": "Il y a {cant} stades enregistrés : {lista}.",
        "no_info_estadio": "Je n'ai pas trouvé d'informations pour ce stade.",
        "capacidad_estadio": "La capacité du stade {nom} est de {cap} spectateurs.",
        "ubicacion_estadio": "Le stade {nom} est situé à {ciu}, {pai}.",
        "info_estadio_completa": "Le stade {nom} est à {ciu}, {pai}, avec une capacité de {cap} spectateurs.",
        
        "no_ubicacion": "Je n'ai pas pu identifier le lieu dans votre requête.",
        "no_estadios_ubicacion": "Aucun stade enregistré trouvé à {ubicacion}.",
        "estadios_ubicacion_fmt": "Trouvé {cant} stade(s) à {ubicacion} : {lista}.",
        
        "no_arbitros": "Aucun arbitre enregistré trouvé.",
        "arbitros_registrados": "Il y a {cant} arbitres enregistrés : {lista}.",
        
        "no_tarjetas": "Aucune carton enregistré trouvé.",
        "tarjetas_registradas": "Trouvé {cant} cartons enregistrés au total.",
        
        "no_sustituciones": "Aucune substitution enregistrée trouvée.",
        "sustituciones_registradas": "Trouvé {cant} substitutions enregistrées.",
        
        "no_goles_ranking": "Aucun enregistrement de but trouvé.",
        "goleadores_ranking_fmt": "Meilleurs buteurs : {lista}.",
        
        "no_competicion": "Je n'ai pas pu identifier la compétition dans votre requête.",
        "no_partidos_competicion": "Aucun match enregistré trouvé pour la compétition {comp}.",
        "partidos_competicion_fmt": "Trouvé {cant} match(s) de la compétition {comp_name}.",
        
        "no_todos_partidos": "Aucun match enregistré trouvé.",
        "todos_partidos_fmt": "Trouvé {cant} matchs enregistrés.",
        
        "no_todos_equipos": "Aucune équipe enregistrée trouvée.",
        "todos_equipos_fmt": "Il y a {cant} équipes enregistrées : {lista}.",
        
        "no_todos_jugadores": "Aucun joueur enregistré trouvé.",
        "todos_jugadores_fmt": "Il y a {cant} joueurs enregistrés : {lista}.",
        
        "no_capitan": "Aucun capitaine enregistré trouvé pour cette équipe.",
        "capitan_fmt": "Le capitaine du {eq_nom} est {nom} (Numéro #{dor}, {pos}).",
        
        "no_persona": "Je n'ai pas pu identifier la personne dans votre requête.",
        "no_fecha_nacimiento": "Je n'ai pas trouvé la date de naissance de cette personne.",
        "fecha_nacimiento_fmt": "La date de naissance de {nom} est le {fecha}.",
        
        "no_info_titularidad": "Je n'ai pas trouvé d'infos de titularisation pour ce joueur.",
        "es_titular_fmt": "Oui, {nom} est un joueur titulaire au {eq_nom}.",
        "no_es_titular_fmt": "Non, {nom} ne figure pas comme titulaire ou il n'y a pas de données confirmées.",
        
        "no_torneos_internacionales": "Aucun tournoi international enregistré trouvé.",
        "torneos_internacionales_fmt": "Il y a {cant} tournois internationaux enregistrés : {lista}.",
        
        "no_asistencias": "Aucun enregistrement de passe décisive trouvé pour les buts de ce joueur.",
        "asistencia_unica_fmt": "{asistidor} a fait la passe décisive à {goleador} à la minute {minuto} ({tiempo}).",
        "asistencias_multiples_fmt": "Trouvé {cant} passes décisives pour les buts de {goleador}, données por: {lista}.",
        
        "no_motivo_tarjeta": "Je n'ai pas pu identifier le motif du carton dans votre requête.",
        "no_tarjetas_motivo": "Je n'ai pas trouvé de joueurs avec des cartons pour le motif '{motivo}'.",
        "tarjetas_motivo_fmt": "Trouvé {cant} cartons pour des motifs similaires à '{motivo}'. Joueurs avertis/expulsés : {lista}.",
        
        "no_goles_propia_puerta": "Aucun but contre son camp enregistré.",
        "goles_propia_puerta_fmt": "Trouvé {cant} buts contre son camp, marqués par : {lista}.",
        
        "no_goles_penal": "Aucun but sur penalty enregistré.",
        "goles_penal_fmt": "Trouvé {cant} buts sur penalty, marqués par : {lista}.",
        
        "no_posicion": "Je n'ai pas pu identifier la position dans votre requête.",
        "no_jugadores_posicion": "Aucun joueur trouvé jouant comme {posicion}.",
        "jugadores_posicion_fmt": "Il y a {cant} joueurs au poste de {posicion} : {lista}.",
        
        "no_entrenadores": "Aucun entraîneur enregistré trouvé.",
        "entrenadores_registrados": "Il y a {cant} entraîneurs enregistrés : {lista}.",
        "no_info_entrenador": "Je n'ai pas trouvé d'informations pour cet entraîneur.",
        "entrenador_equipo": "{nom} entraîne le {equipo}.",
        "entrenador_nacionalidad": "{nom} est de nationalité {nac}.",
        "entrenador_nacimiento": "{nom} est né le {fecha}.",
        "info_entrenador_completa": "{nom} est un entraîneur de nationalité {nac}, né le {fecha}. Il entraîne actuellement le {equipo}.",
        
        "error_procesando": "Erreur lors du traitement de la requête : {error}",
        "fallback_respuesta": "Aucun résultat n'a été trouvé pour votre requête."
    }
}


# ── Service ────────────────────────────────────────────────────────────────
class SearchService:

    def execute(self, query_str: str, language: str = "es") -> SearchResponse:
        lang = (language or "es").lower().strip()
        if lang not in ("es", "en", "fr"):
            lang = "es"

        print(f"\n{'='*60}")
        print(f"[QUERY] {query_str!r} | lang={lang}")

        # 1. Parseo semántico
        parsed = LocalSemanticParser.parse(query_str, lang)
        print(f"[PARSER] intent={parsed.intent!r}  entities={parsed.entities}")

        # 2. Matching de entidades
        matched = matcher.match(parsed) or {}
        print(f"[MATCHER] matched={matched}")

        intent = parsed.intent
        answer = T[lang]["fallback_respuesta"]
        data   = None
        found  = False   # ← 'found' para coincidir con el modelo Pydantic

        dispatch = {
            "resultado_partido":      lambda: self._resultado_partido(matched, lang),
            "goles_partido":          lambda: self._goles_partido(matched, parsed, lang),
            "jugadores_equipo":       lambda: self._jugadores_equipo(matched, lang),
            "info_equipo":            lambda: self._info_equipo(matched, parsed, lang),
            "info_jugador":           lambda: self._info_jugador(matched, parsed, lang),
            "jugador_por_dorsal":     lambda: self._jugador_por_dorsal(matched, lang),
            "jugadores_nacionalidad": lambda: self._jugadores_nacionalidad(matched, lang),
            "estadios":               lambda: self._info_estadio(matched, parsed, lang),
            "arbitros":               lambda: self._arbitros(lang),
            "tarjetas":               lambda: self._tarjetas(lang),
            "sustituciones":          lambda: self._sustituciones(lang),
            "goleadores_ranking":     lambda: self._goleadores_ranking(lang),
            "todos_partidos":         lambda: self._todos_partidos(lang),
            "todos_equipos":          lambda: self._todos_equipos(lang),
            "todos_jugadores":        lambda: self._todos_jugadores(lang),
            "capitan_equipo":         lambda: self._capitan_equipo(matched, lang),
            "estadios_ubicacion":     lambda: self._estadios_ubicacion(matched, lang),
            "partidos_competicion":   lambda: self._partidos_competicion(matched, lang),
            "info_fecha_nacimiento":  lambda: self._info_fecha_nacimiento(matched, lang),
            "es_titular":             lambda: self._es_titular(matched, lang),
            "torneos_internacionales":lambda: self._torneos_internacionales(lang),
            "asistencia_gol":         lambda: self._asistencia_gol(matched, lang),
            "tarjeta_por_motivo":     lambda: self._tarjeta_por_motivo(matched, lang),
            "gol_propia_puerta":      lambda: self._gol_propia_puerta(lang),
            "gol_de_penal":           lambda: self._gol_de_penal(lang),
            "equipos_por_pais":       lambda: self._equipos_por_pais(matched, lang),
            "jugadores_posicion":     lambda: self._jugadores_posicion(matched, lang),
            "info_entrenador":        lambda: self._info_entrenador(matched, parsed, lang),
        }

        fn = dispatch.get(intent)
        if fn:
            try:
                answer, data, found = fn()
                print(f"[SERVICE] found={found}  answer={answer!r}")
            except Exception as e:
                import traceback
                print(f"[SERVICE ERROR] {e}")
                traceback.print_exc()
                answer = T[lang]["error_procesando"].format(error=str(e))
        else:
            print(f"[SERVICE] intent desconocido: {intent!r}")

        print(f"{'='*60}\n")

        return SearchResponse(
            query=query_str,
            intent=intent,
            answer=answer,
            data=data,
            found=found,
        )

    # ── resultado_partido ──────────────────────────────────────────────────
    @staticmethod
    def _resultado_partido(matched: dict, lang: str):
        eq_a = matched.get("eq_a")
        eq_b = matched.get("eq_b")
        print(f"  [resultado_partido] eq_a={eq_a!r}  eq_b={eq_b!r}")

        if not eq_a:
            return T[lang]["no_entidades_equipos"], None, False

        query = (SPARQLBuilder.query_partido_entre(eq_a, eq_b)
                 if eq_b else SPARQLBuilder.query_partidos_de_equipo(eq_a))

        resultados = executor.query(query)
        print(f"  [resultado_partido] filas SPARQL={len(resultados)}")

        if not resultados:
            return T[lang]["no_partidos"], None, False

        data = []
        for fila in resultados:
            local_nom = translate_entity(fila.get("eq_local_nom", "?"), lang)
            visitante_nom = translate_entity(fila.get("eq_visitante_nom", "?"), lang)
            estadio_nom = translate_entity(fila.get("estadio_nombre", "?"), lang)
            comp_nom = translate_entity(fila.get("comp_nombre", "?"), lang)
            data.append({
                "local":           local_nom,
                "visitante":       visitante_nom,
                "goles_local":     fila.get("golesLocal", fila.get("goles_local", "?")),
                "goles_visitante": fila.get("golesVisitante", fila.get("goles_visitante", "?")),
                "fecha":           _fmt_fecha(fila.get("fecha", "")),
                "estadio":         estadio_nom,
                "arbitro":         fila.get("arbitro_nombre", "?"),
                "competicion":     comp_nom,
            })

        if len(data) == 1:
            i = data[0]
            answer = T[lang]["resultado_fmt"].format(
                local=i['local'],
                goles_local=i['goles_local'],
                goles_visitante=i['goles_visitante'],
                visitante=i['visitante']
            )
        else:
            answer = T[lang]["cant_partidos"].format(cant=len(data))

        result = data[0] if len(data) == 1 else data
        return answer, translate_data_keys(result, lang), True

    # ── goles_partido ──────────────────────────────────────────────────────
    @staticmethod
    def _goles_partido(matched: dict, parsed, lang: str):
        print(f"  [goles_partido] matched={matched}")

        q_lower = parsed.raw.lower()
        todos_jug = executor.query(f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX : <http://www.semanticweb.org/valer/ontologies/2026/2/ontologia_futbol/>
            SELECT ?id ?nombre WHERE {{
                ?id rdf:type :Jugador ; :tieneNombre ?nombre .
            }}
        """)
        for fila in todos_jug:
            nom = fila.get("nombre", "")
            if nom and nom.lower() in q_lower:
                NS_BASE = "http://www.semanticweb.org/valer/ontologies/2026/2/ontologia_futbol/"
                raw_id = fila.get("id", "")
                jug_id = raw_id[len(NS_BASE):] if raw_id.startswith(NS_BASE) else raw_id.split("#")[-1]
                print(f"  [goles_partido] jugador detectado: {nom!r} → {jug_id!r}")
                goles_r = executor.query(SPARQLBuilder.query_goles_jugador(jug_id))
                total   = int(goles_r[0].get("total", 0)) if goles_r else 0
                answer  = T[lang]["jugador_goles"].format(nom=nom, total=total)
                return answer, translate_data_keys({"jugador": nom, "goles": total}, lang), True

        eq_a = matched.get("eq_a")
        eq_b = matched.get("eq_b")
        print(f"  [goles_partido] buscando partido eq_a={eq_a!r} eq_b={eq_b!r}")

        if not eq_a:
            return T[lang]["no_partido_jugador"], None, False

        partidos_q = (SPARQLBuilder.query_partido_entre(eq_a, eq_b)
                      if eq_b else SPARQLBuilder.query_partidos_de_equipo(eq_a))
        partidos   = executor.query(partidos_q)
        print(f"  [goles_partido] partidos encontrados={len(partidos)}")

        if not partidos:
            return T[lang]["partido_no_encontrado"], None, False

        NS_BASE = "http://www.semanticweb.org/valer/ontologies/2026/2/ontologia_futbol/"
        partido_iris = list({f.get("partido", "") for f in partidos if f.get("partido")})
        all_goles = []
        for iri in partido_iris:
            p_id = iri[len(NS_BASE):] if iri.startswith(NS_BASE) else (iri.split("#")[-1] if "#" in iri else iri)
            print(f"  [goles_partido] goles de partido {p_id!r}")
            goles_r = executor.query(SPARQLBuilder.query_goles_partido(p_id))
            print(f"  [goles_partido] → {len(goles_r)} goles")
            for g in goles_r:
                all_goles.append({
                    "anotador":  g.get("anotador_nom", "?"),
                    "asistidor": g.get("asistidor_nom", ""),
                    "minuto":    g.get("minuto", "?"),
                    "tiempo":    g.get("tiempo", ""),
                })

        if not all_goles:
            return T[lang]["no_detalle_goles"], None, False

        local  = translate_entity(partidos[0].get("eq_local_nom", "?"), lang)
        vis    = translate_entity(partidos[0].get("eq_visitante_nom", "?"), lang)
        answer = T[lang]["cant_goles_partido"].format(local=local, vis=vis, cant=len(all_goles))
        return answer, translate_data_keys(all_goles, lang), True

    # ── jugadores_equipo ───────────────────────────────────────────────────
    @staticmethod
    def _jugadores_equipo(matched: dict, lang: str):
        eq_id = matched.get("equipo_id") if matched else None
        print(f"  [jugadores_equipo] eq_id={eq_id!r}")

        if not eq_id:
            return T[lang]["no_equipo"], None, False

        resultados = executor.query(SPARQLBuilder.query_jugadores_equipo(eq_id))
        print(f"  [jugadores_equipo] jugadores={len(resultados)}")

        if not resultados:
            return T[lang]["no_jugadores_equipo"], None, False

        eq_info = executor.query(SPARQLBuilder.query_info_equipo(eq_id))
        eq_nom  = eq_info[0].get("nombre", eq_id) if eq_info else eq_id
        eq_nom = translate_entity(eq_nom, lang)

        data    = []
        for f in resultados:
            pos = translate_pos(f.get("posicion", "?"), lang)
            data.append({
                "nombre":   f.get("nombre", "?"),
                "dorsal":   f.get("dorsal", "?"),
                "posicion": pos,
                "capitan":  f.get("esCapitan", "false")
            })
            
        nombres = [d["nombre"] for d in data]
        answer  = T[lang]["plantilla_fmt"].format(eq_nom=eq_nom, cant=len(data), lista=_resumir_lista(nombres, lang))
        return answer, translate_data_keys(data, lang), True

    # ── info_equipo ────────────────────────────────────────────────────────
    @staticmethod
    def _info_equipo(matched: dict, parsed, lang: str):
        eq_id = matched.get("equipo_id") if matched else None
        print(f"  [info_equipo] eq_id={eq_id!r}")

        if not eq_id:
            return T[lang]["no_equipo"], None, False

        resultados = executor.query(SPARQLBuilder.query_info_equipo(eq_id))
        print(f"  [info_equipo] filas={len(resultados)}  raw={resultados}")

        if not resultados:
            return T[lang]["no_info_equipo"], None, False

        fila    = resultados[0]
        nom     = translate_entity(fila.get("nombre", eq_id), lang)
        ciudad  = translate_entity(fila.get("ciudad", "?"), lang)
        pais    = translate_pais(fila.get("pais", "?"), lang)
        estadio = translate_entity(fila.get("estadio_nombre", "?"), lang)
        dt      = fila.get("entrenador_nombre", "?")
        liga    = translate_entity(fila.get("comp_nombre", "?"), lang)

        q = parsed.raw.lower()
        if any(k in q for k in ["entrena", "entrenador", "coach", "trainer", "entraîneur", "entraineur"]):
            answer = T[lang]["entrenador_de"].format(nom=nom, dt=dt)
        elif any(k in q for k in ["estadio", "stadium", "stade"]):
            answer = T[lang]["estadio_de"].format(nom=nom, estadio=estadio)
        elif any(k in q for k in ["liga", "competicion", "competición", "league", "compétition"]):
            answer = T[lang]["liga_de"].format(nom=nom, liga=liga)
        elif any(k in q for k in ["ciudad", "pais", "país", "de donde", "dónde", "city", "country", "where", "ville"]):
            answer = T[lang]["ciudad_de"].format(nom=nom, ciudad=ciudad, pais=pais)
        else:
            answer = T[lang]["info_equipo_completa"].format(nom=nom, ciudad=ciudad, pais=pais, dt=dt, estadio=estadio, liga=liga)

        data = {"nombre": nom, "ciudad": ciudad, "pais": pais,
                "estadio": estadio, "entrenador": dt, "liga": liga}
        return answer, translate_data_keys(data, lang), True

    # ── info_jugador ───────────────────────────────────────────────────────
    @staticmethod
    def _info_jugador(matched: dict, parsed, lang: str):
        jug_id = matched.get("jugador_id") if matched else None
        print(f"  [info_jugador] jug_id={jug_id!r}")

        if not jug_id:
            return T[lang]["no_jugador"], None, False

        resultados = executor.query(SPARQLBuilder.query_info_jugador(jug_id))
        print(f"  [info_jugador] filas={len(resultados)}  raw={resultados}")

        if not resultados:
            return T[lang]["no_info_jugador"], None, False

        fila   = resultados[0]
        nom    = fila.get("nombre", jug_id)
        eq_nom = translate_entity(fila.get("equipo_nombre", "?"), lang)
        nac    = translate_nac(fila.get("nacionalidad", "?"), lang)
        pos    = translate_pos(fila.get("posicion", "?"), lang)
        dor    = fila.get("dorsal", "?")
        cap    = str(fila.get("esCapitan", "false")).lower() == "true"

        goles_r = executor.query(SPARQLBuilder.query_goles_jugador(jug_id))
        goles   = int(goles_r[0].get("total", 0)) if goles_r else 0
        print(f"  [info_jugador] goles={goles}")

        q = parsed.raw.lower()
        if any(k in q for k in ["posicion", "posición", "de que juega", "de qué juega", "position", "poste"]):
            answer = T[lang]["posicion_de"].format(nom=nom, pos=pos)
        elif any(k in q for k in ["equipo", "donde juega", "dónde juega", "team", "club"]):
            answer = T[lang]["equipo_de"].format(nom=nom, eq_nom=eq_nom)
        elif any(k in q for k in ["nacionalidad", "de donde es", "de dónde es", "pais", "país", "nationality", "pays"]):
            answer = T[lang]["nacionalidad_de"].format(nom=nom, nac=nac)
        elif any(k in q for k in ["dorsal", "numero", "número", "camiseta", "number", "numéro", "maillot"]):
            answer = T[lang]["dorsal_de"].format(nom=nom, dor=dor)
        elif "goles" in q or "goals" in q or "buts" in q:
            answer = T[lang]["goles_de"].format(nom=nom, goles=goles)
        else:
            cap_str = T[lang]["capitan_label"] if cap else ""
            answer  = T[lang]["info_jugador_completa"].format(nom=nom, nac=nac, pos=pos, eq_nom=eq_nom, cap_str=cap_str, dor=dor, goles=goles)

        data = {"nombre": nom, "dorsal": dor, "posicion": pos,
                "nacionalidad": nac, "equipo": eq_nom, "goles": goles, "capitan": cap}
        return answer, translate_data_keys(data, lang), True

    # ── jugador_por_dorsal ─────────────────────────────────────────────────
    @staticmethod
    def _jugador_por_dorsal(matched: dict, lang: str):
        dorsal = matched.get("dorsal")
        eq_id  = matched.get("equipo_id")
        print(f"  [jugador_por_dorsal] dorsal={dorsal!r}  eq_id={eq_id!r}")

        if not dorsal:
            return T[lang]["no_dorsal"], None, False

        resultados = executor.query(SPARQLBuilder.query_jugador_por_dorsal(dorsal, eq_id))
        print(f"  [jugador_por_dorsal] filas={len(resultados)}")

        if not resultados:
            return T[lang]["no_jugador_dorsal"], None, False

        fila   = resultados[0]
        nom    = fila.get("nombre", "?")
        eq_nom = translate_entity(fila.get("equipo_nombre", "?"), lang)
        answer = T[lang]["jugador_dorsal_fmt"].format(dorsal=dorsal, eq_nom=eq_nom, nom=nom)
        return answer, translate_data_keys({"nombre": nom, "dorsal": dorsal, "equipo": eq_nom}, lang), True

    # ── jugadores_nacionalidad ─────────────────────────────────────────────
    @staticmethod
    def _jugadores_nacionalidad(matched: dict, lang: str):
        nac = (matched.get("nacionalidad") or "").strip()
        print(f"  [jugadores_nacionalidad] nac_raw={nac!r}")

        if not nac:
            return T[lang]["no_nacionalidad"], None, False

        mapeo = {
            "españa": "española", "español": "española", "española": "española",
            "inglaterra": "inglesa", "ingles": "inglesa", "inglés": "inglesa", "inglesa": "inglesa",
            "francia": "francesa", "frances": "francesa", "francés": "francesa", "francesa": "francesa",
            "brasil": "brasileña", "brasileño": "brasileña", "brasileña": "brasileña",
            "alemania": "alemana", "aleman": "alemana", "alemán": "alemana", "alemana": "alemana",
            "argentina": "argentina", "argentino": "argentina",
            "portugal": "portuguesa", "portugues": "portuguesa", "portugués": "portuguesa", "portuguesa": "portuguesa",
            "italia": "italiana", "italiano": "italiana", "italiana": "italiana",
            "uruguay": "uruguaya", "uruguayo": "uruguaya", "uruguaya": "uruguaya",
            "colombia": "colombiana", "colombiano": "colombiana", "colombiana": "colombiana",
            "croacia": "croata", "croata": "croata",
            "polonia": "polaca", "polaco": "polaca", "polaca": "polaca"
        }
        nac_query = mapeo.get(nac.lower(), nac)
        print(f"  [jugadores_nacionalidad] nac_query={nac_query!r}")

        resultados = executor.query(SPARQLBuilder.query_jugadores_nacionalidad(nac_query))
        print(f"  [jugadores_nacionalidad] jugadores={len(resultados)}")

        if not resultados:
            return T[lang]["no_jugadores_nacionalidad"], None, False

        data = []
        for f in resultados:
            pos = translate_pos(f.get("posicion", "?"), lang)
            data.append({
                "nombre":       f.get("nombre", "?"),
                "nacionalidad": translate_nac(f.get("nacionalidad", nac), lang),
                "equipo":       translate_entity(f.get("equipo_nombre", "?"), lang),
                "posicion":     pos
            })

        nombres     = [d["nombre"] for d in data]
        nac_display = data[0]["nacionalidad"]
        answer = T[lang]["jugadores_nacionalidad_fmt"].format(cant=len(data), nac_display=nac_display, lista=_resumir_lista(nombres, lang))
        return answer, translate_data_keys(data, lang), True

    # ── equipos_por_pais ──────────────────────────────────────────────────
    @staticmethod
    def _equipos_por_pais(matched: dict, lang: str):
        nac = (matched.get("nacionalidad") or "").strip()
        print(f"  [equipos_por_pais] nac_raw={nac!r}")

        if not nac:
            return T[lang]["no_pais"], None, False

        mapeo = {
            "española": "españa", "español": "españa", "españa": "españa",
            "inglesa": "inglaterra", "ingles": "inglaterra", "inglaterra": "inglaterra",
            "francesa": "francia", "frances": "francia", "francia": "francia",
            "brasileña": "brasil", "brasileño": "brasil", "brasil": "brasil",
            "alemana": "alemania", "aleman": "alemania", "alemania": "alemania",
            "argentina": "argentina", "argentino": "argentina",
            "portuguesa": "portugal", "portugues": "portugal", "portugal": "portugal",
            "italiana": "italia", "italiano": "italia", "italia": "italia",
            "uruguaya": "uruguay", "uruguayo": "uruguay", "uruguay": "uruguay",
            "colombiana": "colombia", "colombiano": "colombia", "colombia": "colombia",
            "croata": "croacia", "croacia": "croacia",
            "polaca": "polonia", "polaco": "polonia", "polonia": "polonia"
        }
        nac_query = mapeo.get(nac.lower(), nac)

        resultados = executor.query(SPARQLBuilder.query_equipos_por_pais(nac_query))
        if not resultados:
            return T[lang]["no_equipos_pais"].format(nac=nac), None, False

        data = []
        for f in resultados:
            data.append({
                "nombre":  translate_entity(f.get("nombre", ""), lang),
                "ciudad":  translate_entity(f.get("ciudad", "?"), lang),
                "estadio": translate_entity(f.get("estadio_nombre", "?"), lang)
            })
            
        nombres = [d["nombre"] for d in data if d["nombre"]]
        pais_display = translate_pais(nac_query, lang)
        
        answer = T[lang]["equipos_pais_fmt"].format(cant=len(nombres), nac=pais_display, lista=_resumir_lista(nombres, lang))
        return answer, translate_data_keys(data, lang), True

    # ── info_estadio ───────────────────────────────────────────────────────
    @staticmethod
    def _info_estadio(matched: dict, parsed, lang: str):
        est_id = matched.get("estadio_id") if matched else None
        print(f"  [info_estadio] est_id={est_id!r}")

        if not est_id:
            resultados = executor.query(SPARQLBuilder.query_todos_estadios())
            print(f"  [info_estadio] todos: filas={len(resultados)}")
            if not resultados:
                return T[lang]["no_estadios"], None, False
                
            data = []
            for f in resultados:
                data.append({
                    "nombre":    translate_entity(f.get("nombre", "?"), lang),
                    "capacidad": f.get("capacidad", "?"),
                    "ciudad":    translate_entity(f.get("ciudad", "?"), lang),
                    "pais":      translate_pais(f.get("pais", "?"), lang)
                })
            nombres = [d["nombre"] for d in data]
            answer  = T[lang]["estadios_registrados"].format(cant=len(data), lista=_resumir_lista(nombres, lang))
            return answer, translate_data_keys(data, lang), True

        resultados = executor.query(SPARQLBuilder.query_info_estadio(est_id))
        print(f"  [info_estadio] filas={len(resultados)}")

        if not resultados:
            return T[lang]["no_info_estadio"], None, False

        fila   = resultados[0]
        nom    = translate_entity(fila.get("nombre", est_id), lang)
        cap    = fila.get("capacidad", "?")
        ciu    = translate_entity(fila.get("ciudad", "?"), lang)
        pai    = translate_pais(fila.get("pais", "?"), lang)

        q = parsed.raw.lower()
        if any(k in q for k in ["capacidad", "aforo", "cuantos entran", "cuántos entran", "capacity", "attendance", "spectators"]):
            answer = T[lang]["capacidad_estadio"].format(nom=nom, cap=cap)
        elif any(k in q for k in ["donde esta", "dónde está", "ciudad", "ubicacion", "ubicación", "where is", "located", "où", "situé"]):
            answer = T[lang]["ubicacion_estadio"].format(nom=nom, ciu=ciu, pai=pai)
        else:
            answer = T[lang]["info_estadio_completa"].format(nom=nom, ciu=ciu, pai=pai, cap=cap)

        return answer, translate_data_keys({"nombre": nom, "capacidad": cap, "ciudad": ciu, "pais": pai}, lang), True

    # ── estadios_ubicacion ─────────────────────────────────────────────────
    @staticmethod
    def _estadios_ubicacion(matched: dict, lang: str):
        ubicacion = (matched.get("ubicacion") or "").strip()
        print(f"  [estadios_ubicacion] ubicacion={ubicacion!r}")

        if not ubicacion:
            return T[lang]["no_ubicacion"], None, False

        resultados = executor.query(SPARQLBuilder.query_estadios_por_ubicacion(ubicacion))
        print(f"  [estadios_ubicacion] filas={len(resultados)}")

        if not resultados:
            return T[lang]["no_estadios_ubicacion"].format(ubicacion=ubicacion), None, False

        data = []
        for f in resultados:
            data.append({
                "nombre":    translate_entity(f.get("nombre", "?"), lang),
                "capacidad": f.get("capacidad", "?"),
                "ciudad":    translate_entity(f.get("ciudad", "?"), lang),
                "pais":      translate_pais(f.get("pais", "?"), lang)
            })
        
        nombres = [d["nombre"] for d in data]
        answer  = T[lang]["estadios_ubicacion_fmt"].format(cant=len(data), ubicacion=translate_entity(ubicacion, lang), lista=_resumir_lista(nombres, lang))
        return answer, translate_data_keys(data, lang), True

    # ── arbitros ───────────────────────────────────────────────────────────
    @staticmethod
    def _arbitros(lang: str):
        resultados = executor.query(SPARQLBuilder.query_arbitros())
        print(f"  [arbitros] filas={len(resultados)}")
        if not resultados:
            return T[lang]["no_arbitros"], None, False
            
        data = []
        for f in resultados:
            data.append({
                "nombre": f.get("nombre", "?"),
                "nacionalidad": translate_nac(f.get("nacionalidad", "?"), lang)
            })
        nombres = [d["nombre"] for d in data]
        answer  = T[lang]["arbitros_registrados"].format(cant=len(data), lista=_resumir_lista(nombres, lang))
        return answer, translate_data_keys(data, lang), True

    # ── tarjetas ───────────────────────────────────────────────────────────
    @staticmethod
    def _tarjetas(lang: str):
        resultados = executor.query(SPARQLBuilder.query_todas_tarjetas())
        print(f"  [tarjetas] filas={len(resultados)}")
        if not resultados:
            return T[lang]["no_tarjetas"], None, False
        data = []
        for f in resultados:
            data.append({
                "tipo":    translate_entity(f.get("tipo_clase", "?"), lang),
                "jugador": f.get("nombre_jugador", "?"),
                "minuto":  f.get("minuto", "?"),
                "tiempo":  f.get("tiempo", ""),
                "motivo":  f.get("motivo", "")
            })
        answer = T[lang]["tarjetas_registradas"].format(cant=len(data))
        return answer, translate_data_keys(data, lang), True

    # ── sustituciones ──────────────────────────────────────────────────────
    @staticmethod
    def _sustituciones(lang: str):
        resultados = executor.query(SPARQLBuilder.query_sustituciones())
        print(f"  [sustituciones] filas={len(resultados)}")
        if not resultados:
            return T[lang]["no_sustituciones"], None, False
        data = [{"entra":  f.get("entra_nom", "?"), "sale":   f.get("sale_nom",  "?"),
                 "minuto": f.get("minuto", "?"),     "tiempo": f.get("tiempo", "")}
                for f in resultados]
        answer = T[lang]["sustituciones_registradas"].format(cant=len(data))
        return answer, translate_data_keys(data, lang), True

    # ── goleadores_ranking ─────────────────────────────────────────────────
    @staticmethod
    def _goleadores_ranking(lang: str):
        resultados = executor.query(SPARQLBuilder.query_maximo_goleador())
        print(f"  [goleadores_ranking] filas={len(resultados)}")
        if not resultados:
            return T[lang]["no_goles_ranking"], None, False
        data   = [{"jugador": f.get("nombre", "?"), "goles": int(f.get("goles", 0))}
                  for f in resultados]
        top3   = ", ".join(f"{d['jugador']} ({d['goles']})" for d in data[:3])
        answer = T[lang]["goleadores_ranking_fmt"].format(lista=top3)
        return answer, translate_data_keys(data, lang), True

    # ── partidos_competicion ───────────────────────────────────────────────
    @staticmethod
    def _partidos_competicion(matched: dict, lang: str):
        comp = (matched.get("competicion") or "").strip()
        print(f"  [partidos_competicion] comp={comp!r}")

        if not comp:
            return T[lang]["no_competicion"], None, False

        resultados = executor.query(SPARQLBuilder.query_partidos_por_competicion(comp))
        print(f"  [partidos_competicion] filas={len(resultados)}")

        if not resultados:
            return T[lang]["no_partidos_competicion"].format(comp=comp), None, False

        data = []
        for f in resultados:
            data.append({
                "fecha":           _fmt_fecha(f.get("fecha", "")),
                "local":           translate_entity(f.get("eq_local_nom", "?"), lang),
                "visitante":       translate_entity(f.get("eq_visitante_nom", "?"), lang),
                "goles_local":     f.get("goles_local", "-"),
                "goles_visitante": f.get("goles_visitante", "-"),
                "competicion":     translate_entity(f.get("compName", "?"), lang)
            })

        comp_name = data[0]["competicion"]
        answer = T[lang]["partidos_competicion_fmt"].format(cant=len(data), comp_name=comp_name)
        return answer, translate_data_keys(data, lang), True

    # ── todos_partidos ─────────────────────────────────────────────────────
    @staticmethod
    def _todos_partidos(lang: str):
        resultados = executor.query(SPARQLBuilder.query_todos_partidos())
        print(f"  [todos_partidos] filas={len(resultados)}")
        if not resultados:
            return T[lang]["no_todos_partidos"], None, False
        data = []
        for f in resultados:
            data.append({
                "fecha":           _fmt_fecha(f.get("fecha", "")),
                "local":           translate_entity(f.get("eq_local_nom", "?"), lang),
                "visitante":       translate_entity(f.get("eq_visitante_nom", "?"), lang),
                "goles_local":     f.get("goles_local", "-"),
                "goles_visitante": f.get("goles_visitante", "-"),
                "competicion":     translate_entity(f.get("comp_nombre", "?"), lang)
            })
        answer = T[lang]["todos_partidos_fmt"].format(cant=len(data))
        return answer, translate_data_keys(data, lang), True

    # ── todos_equipos ──────────────────────────────────────────────────────
    @staticmethod
    def _todos_equipos(lang: str):
        resultados = executor.query(SPARQLBuilder.query_todos_los_equipos())
        print(f"  [todos_equipos] filas={len(resultados)}")
        if not resultados:
            return T[lang]["no_todos_equipos"], None, False

        data = []
        for f in resultados:
            data.append({
                "nombre":  translate_entity(f.get("nombre", "?"), lang),
                "ciudad":  translate_entity(f.get("ciudad", "?"), lang),
                "pais":    translate_pais(f.get("pais", "?"), lang),
                "estadio": translate_entity(f.get("estadio_nombre", "?"), lang)
            })

        nombres = [d["nombre"] for d in data]
        answer  = T[lang]["todos_equipos_fmt"].format(cant=len(data), lista=_resumir_lista(nombres, lang))
        return answer, translate_data_keys(data, lang), True

    # ── todos_jugadores ────────────────────────────────────────────────────
    @staticmethod
    def _todos_jugadores(lang: str):
        resultados = executor.query(SPARQLBuilder.query_todos_los_jugadores())
        print(f"  [todos_jugadores] filas={len(resultados)}")
        if not resultados:
            return T[lang]["no_todos_jugadores"], None, False

        data = []
        for f in resultados:
            data.append({
                "nombre":       f.get("nombre", "?"),
                "nacionalidad": translate_nac(f.get("nacionalidad", "?"), lang),
                "posicion":     translate_pos(f.get("posicion", "?"), lang),
                "equipo":       translate_entity(f.get("equipo_nombre", "?"), lang)
            })

        nombres = [d["nombre"] for d in data]
        answer  = T[lang]["todos_jugadores_fmt"].format(cant=len(data), lista=_resumir_lista(nombres, lang))
        return answer, translate_data_keys(data, lang), True

    # ── capitan_equipo ─────────────────────────────────────────────────────
    @staticmethod
    def _capitan_equipo(matched: dict, lang: str):
        eq_id = matched.get("equipo_id")
        print(f"  [capitan_equipo] eq_id={eq_id!r}")
        
        if not eq_id:
            return T[lang]["no_equipo"], None, False

        resultados = executor.query(SPARQLBuilder.query_capitan_equipo(eq_id))
        print(f"  [capitan_equipo] filas={len(resultados)}")
        
        if not resultados:
            return T[lang]["no_capitan"], None, False

        fila = resultados[0]
        nom = fila.get("nombre", "?")
        dor = fila.get("dorsal", "?")
        pos = translate_pos(fila.get("posicion", "?"), lang)
        
        eq_info = executor.query(SPARQLBuilder.query_info_equipo(eq_id))
        eq_nom  = eq_info[0].get("nombre", eq_id) if eq_info else eq_id
        eq_nom = translate_entity(eq_nom, lang)

        answer = T[lang]["capitan_fmt"].format(eq_nom=eq_nom, nom=nom, dor=dor, pos=pos)
        return answer, translate_data_keys({"nombre": nom, "dorsal": dor, "posicion": pos, "equipo": eq_nom}, lang), True

    # ── info_fecha_nacimiento ──────────────────────────────────────────────
    @staticmethod
    def _info_fecha_nacimiento(matched: dict, lang: str):
        per_id = matched.get("persona_id")
        print(f"  [info_fecha_nacimiento] per_id={per_id!r}")
        if not per_id:
            return T[lang]["no_persona"], None, False

        resultados = executor.query(SPARQLBuilder.query_fecha_nacimiento(per_id))
        if not resultados:
            return T[lang]["no_fecha_nacimiento"], None, False

        fila = resultados[0]
        nom = fila.get("nombre", per_id)
        fecha_raw = fila.get("fecha_nacimiento", "")
        fecha = _fmt_fecha(fecha_raw)
        
        answer = T[lang]["fecha_nacimiento_fmt"].format(nom=nom, fecha=fecha)
        return answer, translate_data_keys({"nombre": nom, "fecha_nacimiento": fecha}, lang), True

    # ── es_titular ─────────────────────────────────────────────────────────
    @staticmethod
    def _es_titular(matched: dict, lang: str):
        jug_id = matched.get("jugador_id")
        if not jug_id:
            return T[lang]["no_jugador"], None, False

        resultados = executor.query(SPARQLBuilder.query_es_titular(jug_id))
        if not resultados:
            return T[lang]["no_info_titularidad"], None, False

        fila = resultados[0]
        nom = fila.get("nombre", jug_id)
        es_titular = str(fila.get("es_titular", "false")).lower() == "true"
        eq_nom = translate_entity(fila.get("equipo_nombre", "su equipo"), lang)

        if es_titular:
            answer = T[lang]["es_titular_fmt"].format(nom=nom, eq_nom=eq_nom)
        else:
            answer = T[lang]["no_es_titular_fmt"].format(nom=nom, eq_nom=eq_nom)
            
        return answer, translate_data_keys({"nombre": nom, "es_titular": es_titular, "equipo": eq_nom}, lang), True

    # ── torneos_internacionales ────────────────────────────────────────────
    @staticmethod
    def _torneos_internacionales(lang: str):
        resultados = executor.query(SPARQLBuilder.query_torneos_internacionales())
        if not resultados:
            return T[lang]["no_torneos_internacionales"], None, False
            
        data = []
        for f in resultados:
            data.append({
                "nombre": translate_entity(f.get("nombre", "?"), lang),
                "tipo":   translate_entity(f.get("comp_clase", "?"), lang)
            })
        nombres = [d["nombre"] for d in data]
        answer = T[lang]["torneos_internacionales_fmt"].format(cant=len(data), lista=_resumir_lista(nombres, lang))
        return answer, translate_data_keys(data, lang), True

    # ── asistencia_gol ─────────────────────────────────────────────────────
    @staticmethod
    def _asistencia_gol(matched: dict, lang: str):
        jug_id = matched.get("jugador_id")
        if not jug_id:
            return T[lang]["no_jugador"], None, False

        resultados = executor.query(SPARQLBuilder.query_asistencia_gol(jug_id))
        if not resultados:
            return T[lang]["no_asistencias"], None, False

        data = [{"asistidor": f.get("asistidor_nom", "?"), "goleador": f.get("goleador_nom", "?"), "minuto": f.get("minuto", "?"), "tiempo": f.get("tiempo", "?")} for f in resultados]
        
        if len(data) == 1:
            i = data[0]
            answer = T[lang]["asistencia_unica_fmt"].format(asistidor=i['asistidor'], goleador=i['goleador'], minuto=i['minuto'], tiempo=i['tiempo'])
        else:
            nombres = [d["asistidor"] for d in data]
            answer = T[lang]["asistencias_multiples_fmt"].format(cant=len(data), goleador=data[0]['goleador'], lista=_resumir_lista(nombres, lang))
            
        return answer, translate_data_keys(data, lang), True

    # ── tarjeta_por_motivo ─────────────────────────────────────────────────
    @staticmethod
    def _tarjeta_por_motivo(matched: dict, lang: str):
        motivo = matched.get("motivo", "").strip()
        if not motivo:
            return T[lang]["no_motivo_tarjeta"], None, False

        resultados = executor.query(SPARQLBuilder.query_tarjeta_por_motivo(motivo))
        if not resultados:
            return T[lang]["no_tarjetas_motivo"].format(motivo=motivo), None, False

        data = []
        for f in resultados:
            data.append({
                "jugador": f.get("nombre_jugador", "?"),
                "motivo":  f.get("motivo_exacto", "?"),
                "tipo":    translate_entity(f.get("tipo_tarjeta", "?"), lang),
                "minuto":  f.get("minuto", "?"),
                "tiempo":  f.get("tiempo", "?")
            })
        nombres = [d["jugador"] for d in data]
        answer = T[lang]["tarjetas_motivo_fmt"].format(cant=len(data), motivo=motivo, lista=_resumir_lista(nombres, lang))
        return answer, translate_data_keys(data, lang), True

    # ── gol_propia_puerta ──────────────────────────────────────────────────
    @staticmethod
    def _gol_propia_puerta(lang: str):
        resultados = executor.query(SPARQLBuilder.query_gol_propia_puerta())
        if not resultados:
            return T[lang]["no_goles_propia_puerta"], None, False

        data = [{"jugador": f.get("nombre_jugador", "?"), "minuto": f.get("minuto", "?"), "tiempo": f.get("tiempo", "?")} for f in resultados]
        nombres = [d["jugador"] for d in data]
        answer = T[lang]["goles_propia_puerta_fmt"].format(cant=len(data), lista=_resumir_lista(nombres, lang))
        return answer, translate_data_keys(data, lang), True

    # ── gol_de_penal ───────────────────────────────────────────────────────
    @staticmethod
    def _gol_de_penal(lang: str):
        resultados = executor.query(SPARQLBuilder.query_gol_de_penal())
        if not resultados:
            return T[lang]["no_goles_penal"], None, False

        data = [{"jugador": f.get("nombre_jugador", "?"), "minuto": f.get("minuto", "?"), "tiempo": f.get("tiempo", "?")} for f in resultados]
        nombres = [d["jugador"] for d in data]
        answer = T[lang]["goles_penal_fmt"].format(cant=len(data), lista=_resumir_lista(nombres, lang))
        return answer, translate_data_keys(data, lang), True

    # ── jugadores_posicion ─────────────────────────────────────────────────
    @staticmethod
    def _jugadores_posicion(matched: dict, lang: str):
        posicion = (matched.get("posicion") or "").strip()
        print(f"  [jugadores_posicion] posicion={posicion!r}")

        if not posicion:
            return T[lang]["no_posicion"], None, False

        resultados = executor.query(SPARQLBuilder.query_jugadores_por_posicion(posicion))
        print(f"  [jugadores_posicion] jugadores={len(resultados)}")

        if not resultados:
            return T[lang]["no_jugadores_posicion"].format(posicion=posicion), None, False

        data = []
        for f in resultados:
            data.append({
                "nombre":       f.get("nombre", "?"),
                "equipo":       translate_entity(f.get("equipo_nombre", "?"), lang),
                "dorsal":       f.get("dorsal", "?"),
                "nacionalidad": translate_nac(f.get("nacionalidad", "?"), lang)
            })

        nombres = [d["nombre"] for d in data]
        pos_display = translate_pos(posicion, lang)
        answer  = T[lang]["jugadores_posicion_fmt"].format(cant=len(data), posicion=pos_display, lista=_resumir_lista(nombres, lang))
        return answer, translate_data_keys(data, lang), True

    # ── info_entrenador ────────────────────────────────────────────────────
    @staticmethod
    def _info_entrenador(matched: dict, parsed, lang: str):
        dt_id = matched.get("entrenador_id") if matched else None
        print(f"  [info_entrenador] dt_id={dt_id!r}")

        if not dt_id:
            resultados = executor.query(SPARQLBuilder.query_todos_entrenadores())
            print(f"  [info_entrenador] todos: filas={len(resultados)}")
            if not resultados:
                return T[lang]["no_entrenadores"], None, False
            data    = []
            for f in resultados:
                data.append({
                    "nombre":      f.get("nombre", "?"),
                    "nacionalidad": translate_nac(f.get("nacionalidad", "?"), lang),
                    "equipo":      translate_entity(f.get("equipo_nombre", "?"), lang)
                })
            nombres = [f"{d['nombre']} ({d['equipo']})" for d in data]
            answer  = T[lang]["entrenadores_registrados"].format(cant=len(data), lista=_resumir_lista(nombres, lang))
            return answer, translate_data_keys(data, lang), True

        resultados = executor.query(SPARQLBuilder.query_info_entrenador(dt_id))
        print(f"  [info_entrenador] filas={len(resultados)}")

        if not resultados:
            return T[lang]["no_info_entrenador"], None, False

        fila    = resultados[0]
        nom     = fila.get("nombre", dt_id)
        nac     = translate_nac(fila.get("nacionalidad", "?"), lang)
        fecha   = _fmt_fecha(fila.get("fecha_nac", ""))
        equipo  = translate_entity(fila.get("equipo_nombre", "?"), lang)

        q = parsed.raw.lower()
        if any(k in q for k in ["equipo", "dirige", "donde trabaja", "team", "manage", "directs", "club"]):
            answer = T[lang]["entrenador_equipo"].format(nom=nom, equipo=equipo)
        elif any(k in q for k in ["nacionalidad", "de donde", "país", "pais", "nationality", "pays"]):
            answer = T[lang]["entrenador_nacionalidad"].format(nom=nom, nac=nac)
        elif any(k in q for k in ["nacimiento", "cumpleaños", "edad", "cuándo nació", "born", "birth", "né"]):
            answer = T[lang]["entrenador_nacimiento"].format(nom=nom, fecha=fecha)
        else:
            answer = T[lang]["info_entrenador_completa"].format(nom=nom, nac=nac, fecha=fecha, equipo=equipo)

        data = {"nombre": nom, "nacionalidad": nac,
                "fecha_nacimiento": fecha, "equipo": equipo}
        return answer, translate_data_keys(data, lang), True
    
# Instancia global compartida por el Router
search_service = SearchService()