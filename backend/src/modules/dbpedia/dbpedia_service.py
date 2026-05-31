from src.modules.semantic.semantic_parser import SemanticParser
from src.modules.dbpedia.dbpedia_executor import DBpediaExecutor
from src.modules.dbpedia.dbpedia_query_builder import DBpediaQueryBuilder
from src.modules.dbpedia.dbpedia_stadium_resolver import resolve_stadium_intent
from src.models import SearchResponse


def _fetch_stadium_capacity(stadium_uri: str) -> str | None:
    """Obtiene la capacidad máxima desde dbp:capacity / dbp:seatingCapacity."""
    if not stadium_uri:
        return None
    q = f"""
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT (MAX(?capNum) AS ?capacity) WHERE {{
  <{stadium_uri}> dbp:capacity ?capVal .
  FILTER(REGEX(STR(?capVal), "^[0-9]+$"))
  BIND(xsd:integer(?capVal) AS ?capNum)
}}
"""
    rows = DBpediaExecutor.query(q)
    cap = rows[0].get("capacity") if rows else None
    if cap:
        return cap
    q2 = f"""
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT (MAX(?capNum) AS ?capacity) WHERE {{
  <{stadium_uri}> dbp:seatingCapacity ?capVal .
  FILTER(REGEX(STR(?capVal), "^[0-9]+$"))
  BIND(xsd:integer(?capVal) AS ?capNum)
}}
"""
    rows2 = DBpediaExecutor.query(q2)
    return rows2[0].get("capacity") if rows2 else None


def _capacity_from_row(row: dict) -> str | None:
    """Capacidad ya traída por SPARQL (dbp:capacity o dbp:seatingCapacity)."""
    return row.get("capacity") or row.get("seatingCapacity")


def _format_capacity(cap) -> str | None:
    if cap is None or cap == "":
        return None
    try:
        n = int(float(str(cap).replace(",", "")))
        return f"{n:,}".replace(",", ".")
    except (ValueError, TypeError):
        return str(cap)


def _format_opening_date(raw) -> str | None:
    if not raw:
        return None
    s = str(raw)
    if "T" in s:
        return s.split("T")[0]
    return s[:10] if len(s) >= 10 else s


def _stadium_data_from_row(row: dict, fallback_name: str = "", language: str = "es") -> dict:
    cap_raw = row.get("capacity") or _fetch_stadium_capacity(row.get("stadium", ""))
    cap_fmt = _format_capacity(cap_raw)
    return {
        "nombre": row.get("label", fallback_name),
        "capacidad": cap_fmt or cap_raw,
        "ubicacion": row.get("locationLabel") or _t(language, "desconocido"),
        "equipo_local": row.get("clubLabel") or row.get("clubs"),
        "fecha_inauguracion": _format_opening_date(row.get("openingDate")),
        "imagen": row.get("thumbnail"),
    }


def _stadium_answer_text(data: dict, intro: str, language: str = "es") -> str:
    parts = [intro]
    if data.get("ubicacion") and data["ubicacion"] != _t(language, "desconocido"):
        parts.append(_t(language, "ubicacion", val=data["ubicacion"]))
    if data.get("capacidad"):
        parts.append(_t(language, "capacidad", val=data["capacidad"]))
    if data.get("equipo_local"):
        parts.append(_t(language, "equipo_local", val=data["equipo_local"]))
    if data.get("fecha_inauguracion"):
        parts.append(_t(language, "inauguracion", val=data["fecha_inauguracion"]))
    return " ".join(parts)


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


def _t(language: str, key: str, **kwargs) -> str:
    """Obtiene el template en el idioma pedido (fallback a 'es')."""
    lang = language if language in TEMPLATES else "es"
    tmpl = TEMPLATES[lang].get(key, TEMPLATES["es"].get(key, key))
    return tmpl.format(**kwargs) if kwargs else tmpl


class DBpediaService:
    def execute(self, query_str: str, language: str = "es") -> SearchResponse:
        
        
        
        INTENTS_SIN_SOPORTE = {
        "resultado_partido", "goles_partido", "todos_partidos",
        "goleadores_ranking", "todos_jugadores", "todos_equipos",
        "tarjetas", "sustituciones", "arbitros", "jugador_por_dorsal"
        }
       # print(f"\n{'='*60}")
       # print(f"[DBPEDIA SERVICE] Recibiendo consulta: {query_str!r}")
        
        # 1. Parseo semántico para detectar intent y entidades
        parsed = SemanticParser.parse(query_str)
        intent = parsed.intent
        if intent in INTENTS_SIN_SOPORTE:
           return SearchResponse(
               query=query_str,
               intent=intent,
               answer=_t(language, "no_support"),
               data=None,
               found=False
           )
        entities = parsed.entities
        intent, entities = resolve_stadium_intent(query_str, intent, entities)

        entity = entities[0] if entities else query_str.strip(" ¿?!")

        if intent == "estadio_equipo" and (
            not entities
            or entity.lower().strip() in {"", "un equipo", "el equipo", "un club", "el club"}
        ):
            return SearchResponse(
                query=query_str,
                intent=intent,
                answer=_t(language, "ask_team"),
                data=None,
                found=False,
            )

        # 2. Construcción y ejecución
        query_sparql = DBpediaQueryBuilder.build(intent, entity, language)
        resultados = DBpediaExecutor.query(query_sparql)
        
        answer = _t(language, "no_results")
        data = None
        found = False
        
        # 3. Mapeo y formateo de resultados según el intent
        if resultados:
            found = True
            row = resultados[0]  # El primer resultado relevante (ordenado por similitud/longitud)
            
            if intent in ("info_jugador", "info_fecha_nacimiento"):
                nombre = row.get("label", entity)
                birth_place = row.get("birthPlace", "")
                nac = birth_place.split(",")[-1].strip() if birth_place else _t(language, "desconocido")
                pos = row.get("posicionES") or row.get("positionLabel") or _t(language, "desconocido")
                dorsal = row.get("number") or _t(language, "sin_dorsal")
                birth = row.get("birthDate", "No registrada")
                
                estatura = f"{row.get('height')} m" if row.get('height') else _t(language, "desconocido")
                foto = row.get("thumbnail", "")
                equipo_actual = row.get("currentClubLabel") or row.get("teamLabel") or _t(language, "sin_equipo")
                
                all_teams_raw = row.get("allTeams", "")
                equipos_lista = sorted(list(set([t.strip() for t in all_teams_raw.split(",") if t.strip()]))) if all_teams_raw else []
                
                if intent == "info_fecha_nacimiento":
                    answer = _t(language, "fecha_nacimiento", nombre=nombre, birth=birth)
                else:
                    alt_str = _t(language, "alt_str", estatura=estatura) if estatura != _t(language, "desconocido") else ""
                    answer = _t(language, "jugador", nombre=nombre, nac=nac, pos=pos,
                                equipo=equipo_actual, dorsal=dorsal, birth=birth, alt=alt_str)
                
                data = {
                    "nombre": nombre,
                    "nacionalidad": nac,
                    "posicion": pos,
                    "equipo": equipo_actual,
                    "dorsal": dorsal,
                    "fecha_nacimiento": birth,
                    "estatura": estatura,
                    "foto": foto,
                    "equipos_trayectoria": equipos_lista
                }
                
            elif intent in ("info_equipo", "capitan_equipo"):
                nombre = row.get("label", entity)
                estadio = row.get("stadiumLabel") or _t(language, "desconocido")
                director = row.get("managerLabel") or _t(language, "desconocido")
                presidente = row.get("chairmanLabel") or _t(language, "desconocido")
                capacidad = row.get("capacity")
                fundacion = row.get("founded") or _t(language, "desconocido")
                logo = row.get("thumbnail", "")

                apodos_raw = row.get("allNicks", "")
                apodos_list = []
                if apodos_raw:
                    nicks = [n.strip() for n in apodos_raw.split(",") if n.strip()]
                    seen = set()
                    for n in nicks:
                        if n.lower() not in seen:
                            seen.add(n.lower())
                            apodos_list.append(n)

                apodos_str = _t(language, "apodos_str", nicks=", ".join(apodos_list)) if apodos_list else ""
                capacidad_str = f" ({_t(language, 'capacidad', val=f'{int(capacidad):,}')})" if capacidad and capacidad.isdigit() else ""

                answer_parts = [_t(language, "equipo_intro", nombre=nombre, apodos=apodos_str)]
                if fundacion != _t(language, "desconocido"):
                    answer_parts.append(_t(language, "equipo_fundado", fundacion=fundacion))
                else:
                    answer_parts.append(_t(language, "equipo_historico"))

                answer_parts.append(_t(language, "equipo_estadio", estadio=estadio, capacidad=capacidad_str))

                dir_pres = []
                desc = _t(language, "desconocido")
                if director != desc:
                    dir_pres.append(_t(language, "dirigido_por", director=director))
                if presidente != desc:
                    dir_pres.append(_t(language, "presidido_por", presidente=presidente))

                if dir_pres:
                    answer_parts.append(_t(language, "equipo_gestion", gestion=" y ".join(dir_pres)))

                answer = " ".join(answer_parts)

                data = {
                    "nombre": nombre,
                    "estadio": estadio,
                    "capacidad_estadio": capacidad,
                    "entrenador": director,
                    "presidente": presidente,
                    "fecha_fundacion": fundacion,
                    "apodos": apodos_list,
                    "logo": logo
                }
                
            elif intent == "jugadores_equipo":
                jugadores = []
                for r in resultados:
                    p_nom = r.get("playerLabel")
                    p_num = r.get("number", "-")
                    p_pos = r.get("positionLabel", "-")
                    if p_nom:
                        jugadores.append({"nombre": p_nom, "dorsal": p_num, "posicion": p_pos})
                
                nombres = [j["nombre"] for j in jugadores]
                nombres_res = ", ".join(nombres[:6])
                if len(nombres) > 6:
                    nombres_res += f" {_t(language, 'y_mas', n=len(nombres) - 6)}"
                
                answer = _t(language, "jugadores_equipo", nombres=nombres_res)
                data = jugadores
                
            elif intent == "todos_estadios":
                estadios = []
                seen = set()
                for r in resultados:
                    nom = r.get("label")
                    club = r.get("clubLabel")
                    key = r.get("club") or r.get("stadium") or (club, nom)
                    if not nom or key in seen:
                        continue
                    seen.add(key)
                    estadios.append({
                        "nombre": nom,
                        "capacidad": _format_capacity(_capacity_from_row(r)),
                        "ubicacion": r.get("locationLabel"),
                        "equipo_local": r.get("clubLabel"),
                    })
                nombres = [e["nombre"] for e in estadios]
                resumen = ", ".join(nombres[:8])
                if len(nombres) > 8:
                    resumen += f" {_t(language, 'y_mas', n=len(nombres) - 8)}"
                answer = _t(language, "todos_estadios", n=len(estadios), resumen=resumen)
                data = estadios

            elif intent == "estadio_equipo":
                data = _stadium_data_from_row(row, entity, language)
                equipo = data.get("equipo_local") or entity
                intro = _t(language, "estadio_equipo", equipo=equipo, nombre=data["nombre"])
                answer = _stadium_answer_text(data, intro, language)

            elif intent == "estadios":
                data = _stadium_data_from_row(row, entity, language)
                intro = _t(language, "estadio_info", nombre=data["nombre"])
                answer = _stadium_answer_text(data, intro, language)

            elif intent == "estadios_ubicacion":
                estadios = []
                seen = set()
                for r in resultados:
                    nom = r.get("label")
                    key = r.get("stadium") or nom
                    if not nom or key in seen:
                        continue
                    seen.add(key)
                    estadios.append({
                        "nombre": nom,
                        "capacidad": _format_capacity(_capacity_from_row(r)),
                        "ubicacion": r.get("locationLabel") or entity,
                        "equipo_local": r.get("clubLabel"),
                    })
                nombres = [e["nombre"] for e in estadios]
                resumen = ", ".join(nombres[:8])
                if len(nombres) > 8:
                    resumen += f" {_t(language, 'y_mas', n=len(nombres) - 8)}"
                with_cap = [e for e in estadios if e.get("capacidad")]
                cap_hint = ""
                if with_cap:
                    ej = with_cap[0]
                    cap_hint = _t(language, "cap_hint", nombre=ej["nombre"], cap=ej["capacidad"])
                answer = _t(language, "estadios_ubicacion", n=len(estadios), lugar=entity,
                            resumen=resumen, cap_hint=cap_hint)
                data = estadios
                
            elif intent == "info_entrenador":
                nombre = row.get("label", entity)
                birth = row.get("birthDate", "No registrada")
                equipo = row.get("teamLabel") or _t(language, "sin_equipo")
                
                answer = _t(language, "entrenador", nombre=nombre, birth=birth, equipo=equipo)
                data = {
                    "nombre": nombre,
                    "fecha_nacimiento": birth,
                    "equipo": equipo
                }
                
            elif intent == "jugadores_nacionalidad":
                jugadores = []
                for r in resultados:
                    p_nom = r.get("playerLabel")
                    p_team = r.get("teamLabel") or _t(language, "sin_equipo")
                    if p_nom:
                        jugadores.append({"nombre": p_nom, "equipo": p_team})
                
                nombres = [j["nombre"] for j in jugadores]
                nombres_res = ", ".join(nombres[:8])
                if len(nombres) > 8:
                    nombres_res += f" {_t(language, 'y_mas', n=len(nombres) - 8)}"
                
                answer = _t(language, "nacionalidad", nombres=nombres_res)
                data = jugadores
                
            elif intent == "equipos_por_pais":
                equipos = []
                for r in resultados:
                    eq_nom = r.get("clubLabel")
                    eq_est = r.get("stadiumLabel") or _t(language, "desconocido")
                    if eq_nom:
                        equipos.append({"nombre": eq_nom, "estadio": eq_est})
                        
                nombres = [e["nombre"] for e in equipos]
                nombres_res = ", ".join(nombres[:8])
                if len(equipos) > 8:
                    nombres_res += f" {_t(language, 'y_mas', n=len(equipos) - 8)}"
                    
                answer = _t(language, "equipos_pais", nombres=nombres_res)
                data = equipos
                
            else:
                nombre = row.get("label", entity)
                abstract = row.get("abstract") or row.get("comment") or _t(language, "no_results")
                
                answer = _t(language, "abstract", nombre=nombre, abstract=abstract)
                data = {
                    "nombre": nombre,
                    "descripcion": abstract,
                    "uri": row.get("subject")
                }
        
        # Pudes borrarme, solo para debug, muestra un resumen del resultado final antes de devolverlo
        print(f"[DBPEDIA SERVICE] Finalizado: found={found}  answer_len={len(answer)}")
        print(f"{'='*60}\n")
        
        return SearchResponse(
            query=query_str,
            intent=intent,
            answer=answer,
            data=data,
            found=found
        )

dbpedia_service = DBpediaService()