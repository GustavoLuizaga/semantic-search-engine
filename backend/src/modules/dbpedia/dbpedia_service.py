from src.modules.semantic.semantic_parser import SemanticParser
from src.modules.dbpedia.dbpedia_executor import DBpediaExecutor
from src.modules.dbpedia.dbpedia_query_builder import DBpediaQueryBuilder
from src.models import SearchResponse

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
        
        # Mostramos los resultados del parseo, puedes borrarme no es importante, solo para debug
        # print(f"[DBPEDIA SERVICE] Parser detectó intent={intent!r} y entidades={entities}")
        
        # Identificamos el nombre principal de la entidad a buscar
        entity = entities[0] if entities else query_str.strip(" ¿?!")
        
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
    # Función auxiliar para sacar el texto limpio del JSON de SPARQL
                

    
                nombre  = row.get("label",        entity)
                estadio = row.get("stadiumLabel", "Desconocido")
                director = row.get("managerLabel","Desconocido")
                ciudad  = row.get("cityLabel",    "Desconocida")
                liga    = row.get("leagueLabel",  "Desconocida")
                pais    = row.get("countryLabel", "Desconocido")
    
                answer = (f"Según DBpedia, el equipo {nombre} juega local en el estadio {estadio}, "
                f"es dirigido por {director}, tiene sede en {ciudad} y participa en {liga}.")
    
                data = {
                "nombre": nombre,
                "estadio": estadio,
                "entrenador": director,
                "ciudad": ciudad,
                "liga": liga
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
                
            elif intent in ("estadios", "estadios_ubicacion"):
                nombre = row.get("label", entity)
                cap = row.get("capacity", "Desconocida")
                loc = row.get("locationLabel", "Desconocida")
                
                answer = f"Según DBpedia, el estadio {nombre} está ubicado en {loc} y tiene capacidad para {cap} espectadores."
                data = {
                    "nombre": nombre,
                    "capacidad": cap,
                    "ubicacion": loc
                }
                
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
