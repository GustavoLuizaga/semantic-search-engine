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


def _stadium_data_from_row(row: dict, fallback_name: str = "") -> dict:
    cap_raw = row.get("capacity") or _fetch_stadium_capacity(row.get("stadium", ""))
    cap_fmt = _format_capacity(cap_raw)
    return {
        "nombre": row.get("label", fallback_name),
        "capacidad": cap_fmt or cap_raw,
        "ubicacion": row.get("locationLabel") or "Desconocida",
        "equipo_local": row.get("clubLabel") or row.get("clubs"),
        "fecha_inauguracion": _format_opening_date(row.get("openingDate")),
        "imagen": row.get("thumbnail"),
    }


def _stadium_answer_text(data: dict, intro: str) -> str:
    parts = [intro]
    if data.get("ubicacion") and data["ubicacion"] != "Desconocida":
        parts.append(f"Ubicación: {data['ubicacion']}.")
    if data.get("capacidad"):
        parts.append(f"Capacidad: {data['capacidad']} espectadores.")
    if data.get("equipo_local"):
        parts.append(f"Equipo local: {data['equipo_local']}.")
    if data.get("fecha_inauguracion"):
        parts.append(f"Inauguración: {data['fecha_inauguracion']}.")
    return " ".join(parts)


class DBpediaService:
    def execute(self, query_str: str) -> SearchResponse:
        
        
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
               answer="Esta consulta requiere datos específicos de partidos que DBpedia no tiene. Prueba con la ontología local.",
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
                answer=(
                    "Indica el nombre del equipo, por ejemplo: "
                    "«¿Dónde juega el Manchester United?» o «Estadio del Real Madrid»."
                ),
                data=None,
                found=False,
            )

        # 2. Construcción y ejecución
        query_sparql = DBpediaQueryBuilder.build(intent, entity)
        resultados = DBpediaExecutor.query(query_sparql)
        
        answer = "No encontré resultados en DBpedia para tu consulta."
        data = None
        found = False
        
        # 3. Mapeo y formateo de resultados según el intent
        if resultados:
            found = True
            row = resultados[0]  # El primer resultado relevante (ordenado por similitud/longitud)
            
            if intent in ("info_jugador", "info_fecha_nacimiento"):
                nombre = row.get("label", entity)
                birth_place = row.get("birthPlace", "")
                nac = birth_place.split(",")[-1].strip() if birth_place else "Desconocida"
                pos = row.get("posicionES") or row.get("positionLabel", "Desconocida")
                dorsal = row.get("number", "Sin dorsal")
                birth = row.get("birthDate", "No registrada")
                
                # Nuevos campos del jugador
                estatura = f"{row.get('height')} m" if row.get('height') else "Desconocida"
                foto = row.get("thumbnail", "")
                equipo_actual = row.get("currentClubLabel") or row.get("teamLabel", "Ninguno")
                
                all_teams_raw = row.get("allTeams", "")
                equipos_lista = sorted(list(set([t.strip() for t in all_teams_raw.split(",") if t.strip()]))) if all_teams_raw else []
                
                if intent == "info_fecha_nacimiento":
                    answer = f"Según DBpedia, la fecha de nacimiento de {nombre} es el {birth}."
                else:
                    alt_str = f" y mide {estatura}" if estatura != "Desconocida" else ""
                    answer = (f"Según DBpedia, {nombre} es un jugador de nacionalidad {nac} que juega de {pos} "
                              f"en el {equipo_actual}. Usa el dorsal #{dorsal}, nació el {birth}{alt_str}.")
                
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
                estadio = row.get("stadiumLabel", "Desconocido")
                director = row.get("managerLabel", "Desconocido")
                presidente = row.get("chairmanLabel", "Desconocido")
                capacidad = row.get("capacity")
                fundacion = row.get("founded", "Desconocida")
                logo = row.get("thumbnail", "")

                # Limpieza de apodos
                apodos_raw = row.get("allNicks", "")
                apodos_list = []
                if apodos_raw:
                    nicks = [n.strip() for n in apodos_raw.split(",") if n.strip()]
                    seen = set()
                    for n in nicks:
                        if n.lower() not in seen:
                            seen.add(n.lower())
                            apodos_list.append(n)

                apodos_str = f" (conocido como {', '.join(apodos_list)})" if apodos_list else ""
                capacidad_str = f" (capacidad: {int(capacidad):,} espectadores)" if capacidad and capacidad.isdigit() else ""

                answer_parts = [f"Según DBpedia, el equipo {nombre}{apodos_str}"]
                if fundacion != "Desconocida":
                    answer_parts.append(f"fue fundado el {fundacion}.")
                else:
                    answer_parts.append("es un club histórico.")

                answer_parts.append(f"Juega local en el estadio {estadio}{capacidad_str}.")

                dir_pres = []
                if director != "Desconocido":
                    dir_pres.append(f"es dirigido por {director}")
                if presidente != "Desconocido":
                    dir_pres.append(f"presidido por {presidente}")

                if dir_pres:
                    answer_parts.append("Actualmente, " + " y ".join(dir_pres) + ".")

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
                    nombres_res += f" y {len(nombres) - 6} jugadores más"
                
                answer = f"Según DBpedia, algunos jugadores registrados en la plantilla de este equipo son: {nombres_res}."
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
                    resumen += f" y {len(nombres) - 8} más"
                answer = (
                    f"Según DBpedia, hay {len(estadios)} estadios de fútbol de clubes "
                    f"profesionales en el catálogo, por ejemplo: {resumen}."
                )
                data = estadios

            elif intent == "estadio_equipo":
                data = _stadium_data_from_row(row, entity)
                equipo = data.get("equipo_local") or entity
                intro = (
                    f"Según DBpedia, el estadio local del {equipo} es el {data['nombre']}."
                )
                answer = _stadium_answer_text(data, intro)

            elif intent == "estadios":
                data = _stadium_data_from_row(row, entity)
                intro = f"Según DBpedia, información del estadio {data['nombre']}:"
                answer = _stadium_answer_text(data, intro)

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
                    resumen += f" y {len(nombres) - 8} más"
                with_cap = [e for e in estadios if e.get("capacidad")]
                cap_hint = ""
                if with_cap:
                    ej = with_cap[0]
                    cap_hint = (
                        f" Ej.: {ej['nombre']} ({ej['capacidad']} espectadores)."
                    )
                answer = (
                    f"En DBpedia encontré {len(estadios)} estadio(s) de fútbol en {entity}: "
                    f"{resumen}.{cap_hint}"
                )
                data = estadios
                
            elif intent == "info_entrenador":
                nombre = row.get("label", entity)
                birth = row.get("birthDate", "No registrada")
                equipo = row.get("teamLabel", "Sin equipo/Retirado")
                
                answer = f"Según DBpedia, el entrenador {nombre} nació el {birth} y dirige o dirigió al equipo {equipo}."
                data = {
                    "nombre": nombre,
                    "fecha_nacimiento": birth,
                    "equipo": equipo
                }
                
            elif intent == "jugadores_nacionalidad":
                jugadores = []
                for r in resultados:
                    p_nom = r.get("playerLabel")
                    p_team = r.get("teamLabel", "Sin equipo")
                    if p_nom:
                        jugadores.append({"nombre": p_nom, "equipo": p_team})
                
                nombres = [j["nombre"] for j in jugadores]
                nombres_res = ", ".join(nombres[:8])
                if len(nombres) > 8:
                    nombres_res += f" y {len(nombres) - 8} más"
                
                answer = f"En DBpedia encontré varios futbolistas con esa nacionalidad, incluyendo a: {nombres_res}."
                data = jugadores
                
            elif intent == "equipos_por_pais":
                equipos = []
                for r in resultados:
                    eq_nom = r.get("clubLabel")
                    eq_est = r.get("stadiumLabel", "Desconocido")
                    if eq_nom:
                        equipos.append({"nombre": eq_nom, "estadio": eq_est})
                        
                nombres = [e["nombre"] for e in equipos]
                nombres_res = ", ".join(nombres[:8])
                if len(equipos) > 8:
                    nombres_res += f" y {len(equipos) - 8} más"
                    
                answer = f"En DBpedia encontré varios clubes de fútbol de ese país, incluyendo a: {nombres_res}."
                data = equipos
                
            else:
                # Mapeo general (Fallback) usando comment/abstract de DBpedia
                nombre = row.get("label", entity)
                abstract = row.get("abstract") or row.get("comment") or "No hay descripción disponible en DBpedia."
                
                answer = f"**{nombre}** (según DBpedia): {abstract}"
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
