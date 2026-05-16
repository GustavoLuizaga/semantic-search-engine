import os
from src.modules.semantic.semantic_parser import SemanticParser
from src.modules.semantic.ontology_matcher import OntologyMatcher
from src.modules.sparql.sparql_builder import SPARQLBuilder
from src.modules.sparql.sparql_executor import SPARQLExecutor
from src.models import SearchResponse

_HERE    = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
OWX_PATH = os.path.join(_BACKEND, "ontologia-futbol.ttl")
if not os.path.exists(OWX_PATH):
    OWX_PATH = os.path.join(os.getcwd(), "ontologia-futbol.ttl")

print(f"[search_service] OWX: {OWX_PATH} | exists={os.path.exists(OWX_PATH)}")

# ── Inicialización única ───────────────────────────────────────────────────
executor = SPARQLExecutor(OWX_PATH)
matcher  = OntologyMatcher(executor)

# ── Helpers ────────────────────────────────────────────────────────────────
def _fmt_fecha(f_str: str) -> str:
    if not f_str or f_str == "Sin fecha":
        return ""
    return f_str.split("T")[0]

def _resumir_lista(nombres: list, total_label: str = "") -> str:
    if not nombres:
        return ""
    if len(nombres) > 5:
        return ", ".join(nombres[:5]) + f" y {len(nombres) - 5} más"
    if len(nombres) > 1:
        return ", ".join(nombres[:-1]) + f" y {nombres[-1]}"
    return nombres[0]


# ── Service ────────────────────────────────────────────────────────────────
class SearchService:

    def execute(self, query_str: str) -> SearchResponse:
        print(f"\n{'='*60}")
        print(f"[QUERY] {query_str!r}")

        # 1. Parseo semántico
        parsed = SemanticParser.parse(query_str)
        print(f"[PARSER] intent={parsed.intent!r}  entities={parsed.entities}")

        # 2. Matching de entidades
        matched = matcher.match(parsed) or {}
        print(f"[MATCHER] matched={matched}")

        intent = parsed.intent
        answer = "No se encontraron resultados para tu consulta."
        data   = None
        found  = False   # ← 'found' para coincidir con el modelo Pydantic

        dispatch = {
            "resultado_partido":      lambda: self._resultado_partido(matched),
            "goles_partido":          lambda: self._goles_partido(matched, parsed),
            "jugadores_equipo":       lambda: self._jugadores_equipo(matched),
            "info_equipo":            lambda: self._info_equipo(matched, parsed),
            "info_jugador":           lambda: self._info_jugador(matched, parsed),
            "jugador_por_dorsal":     lambda: self._jugador_por_dorsal(matched),
            "jugadores_nacionalidad": lambda: self._jugadores_nacionalidad(matched),
            "estadios":               lambda: self._info_estadio(matched, parsed),
            "arbitros":               lambda: self._arbitros(),
            "tarjetas":               lambda: self._tarjetas(),
            "sustituciones":          lambda: self._sustituciones(),
            "goleadores_ranking":     lambda: self._goleadores_ranking(),
            "todos_partidos":         lambda: self._todos_partidos(),
            "todos_equipos":          lambda: self._todos_equipos(),
            "todos_jugadores":        lambda: self._todos_jugadores(),
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
                answer = f"Error procesando la consulta: {e}"
        else:
            print(f"[SERVICE] intent desconocido: {intent!r}")

        print(f"{'='*60}\n")

        # ⚠️ 'found' (no 'success') para coincidir con el modelo Pydantic
        return SearchResponse(
            query=query_str,
            intent=intent,
            answer=answer,
            data=data,
            found=found,
        )

    # ── resultado_partido ──────────────────────────────────────────────────
    @staticmethod
    def _resultado_partido(matched: dict):
        eq_a = matched.get("eq_a")
        eq_b = matched.get("eq_b")
        print(f"  [resultado_partido] eq_a={eq_a!r}  eq_b={eq_b!r}")

        if not eq_a:
            return "No pude identificar los equipos en tu consulta.", None, False

        query = (SPARQLBuilder.query_partido_entre(eq_a, eq_b)
                 if eq_b else SPARQLBuilder.query_partidos_de_equipo(eq_a))

        resultados = executor.query(query)
        print(f"  [resultado_partido] filas SPARQL={len(resultados)}")

        if not resultados:
            return "No encontré partidos para esos equipos.", None, False

        data = []
        for fila in resultados:
            data.append({
                "local":           fila.get("eq_local_nom", "?"),
                "visitante":       fila.get("eq_visitante_nom", "?"),
                "goles_local":     fila.get("golesLocal", fila.get("goles_local", "?")),
                "goles_visitante": fila.get("golesVisitante", fila.get("goles_visitante", "?")),
                "fecha":           _fmt_fecha(fila.get("fecha", "")),
                "estadio":         fila.get("estadio_nombre", "?"),
                "arbitro":         fila.get("arbitro_nombre", "?"),
                "competicion":     fila.get("comp_nombre", "?"),
            })

        if len(data) == 1:
            i = data[0]
            answer = (f"El resultado fue {i['local']} {i['goles_local']} "
                      f"- {i['goles_visitante']} {i['visitante']}.")
        else:
            answer = f"Se encontraron {len(data)} partidos."

        return answer, data[0] if len(data) == 1 else data, True

    # ── goles_partido ──────────────────────────────────────────────────────
    @staticmethod
    def _goles_partido(matched: dict, parsed):
        print(f"  [goles_partido] matched={matched}")

        # Caso 1: buscar goles de un jugador detectado en la query raw
        # El matcher para goles_partido devuelve eq_a/eq_b, no jugador_id,
        # así que buscamos el jugador directamente contra la ontología.
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
                answer  = f"{nom} tiene {total} gol(es) registrado(s) en la ontología."
                return answer, {"jugador": nom, "goles": total}, True

        # Caso 2: goles detallados de un partido entre equipos
        eq_a = matched.get("eq_a")
        eq_b = matched.get("eq_b")
        print(f"  [goles_partido] buscando partido eq_a={eq_a!r} eq_b={eq_b!r}")

        if not eq_a:
            return "No pude identificar el partido o jugador en tu consulta.", None, False

        partidos_q = (SPARQLBuilder.query_partido_entre(eq_a, eq_b)
                      if eq_b else SPARQLBuilder.query_partidos_de_equipo(eq_a))
        partidos   = executor.query(partidos_q)
        print(f"  [goles_partido] partidos encontrados={len(partidos)}")

        if not partidos:
            return "No se encontró el partido.", None, False

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
            return "No hay detalle de goles registrado para ese partido.", None, False

        local  = partidos[0].get("eq_local_nom", "?")
        vis    = partidos[0].get("eq_visitante_nom", "?")
        answer = f"En el partido {local} vs {vis} se registraron {len(all_goles)} gol(es)."
        return answer, all_goles, True

    # ── jugadores_equipo ───────────────────────────────────────────────────
    @staticmethod
    def _jugadores_equipo(matched: dict):
        eq_id = matched.get("equipo_id") if matched else None
        print(f"  [jugadores_equipo] eq_id={eq_id!r}")

        if not eq_id:
            return "No pude identificar el equipo en tu consulta.", None, False

        resultados = executor.query(SPARQLBuilder.query_jugadores_equipo(eq_id))
        print(f"  [jugadores_equipo] jugadores={len(resultados)}")

        if not resultados:
            return "No hay jugadores registrados para ese equipo.", None, False

        eq_info = executor.query(SPARQLBuilder.query_info_equipo(eq_id))
        eq_nom  = eq_info[0].get("nombre", eq_id) if eq_info else eq_id

        data    = [{"nombre":   f.get("nombre", "?"),
                    "dorsal":   f.get("dorsal", "?"),
                    "posicion": f.get("posicion", "?"),
                    "capitan":  f.get("esCapitan", "false")}
                   for f in resultados]
        nombres = [d["nombre"] for d in data]
        answer  = (f"La plantilla del {eq_nom} tiene {len(data)} jugadores, "
                   f"entre ellos: {_resumir_lista(nombres)}.")
        return answer, data, True

    # ── info_equipo ────────────────────────────────────────────────────────
    @staticmethod
    def _info_equipo(matched: dict, parsed):
        eq_id = matched.get("equipo_id") if matched else None
        print(f"  [info_equipo] eq_id={eq_id!r}")

        if not eq_id:
            return "No pude identificar el equipo en tu consulta.", None, False

        resultados = executor.query(SPARQLBuilder.query_info_equipo(eq_id))
        print(f"  [info_equipo] filas={len(resultados)}  raw={resultados}")

        if not resultados:
            return "No encontré información para ese equipo.", None, False

        fila    = resultados[0]
        nom     = fila.get("nombre", eq_id)
        ciudad  = fila.get("ciudad", "?")
        pais    = fila.get("pais", "?")
        estadio = fila.get("estadio_nombre", "?")
        dt      = fila.get("entrenador_nombre", "?")
        liga    = fila.get("comp_nombre", "?")

        q = parsed.raw.lower()
        if any(k in q for k in ["entrena", "entrenador"]):
            answer = f"El entrenador del {nom} es {dt}."
        elif "estadio" in q:
            answer = f"El estadio del {nom} es el {estadio}."
        elif any(k in q for k in ["liga", "competicion", "competición"]):
            answer = f"El {nom} juega en la {liga}."
        elif any(k in q for k in ["ciudad", "pais", "país", "de donde", "dónde"]):
            answer = f"El {nom} es de {ciudad}, {pais}."
        else:
            answer = (f"El {nom} es un equipo de {ciudad}, {pais}, dirigido por {dt}. "
                      f"Juega como local en el {estadio} y participa en la {liga}.")

        data = {"nombre": nom, "ciudad": ciudad, "pais": pais,
                "estadio": estadio, "entrenador": dt, "liga": liga}
        return answer, data, True

    # ── info_jugador ───────────────────────────────────────────────────────
    @staticmethod
    def _info_jugador(matched: dict, parsed):
        jug_id = matched.get("jugador_id") if matched else None
        print(f"  [info_jugador] jug_id={jug_id!r}")

        if not jug_id:
            return "No pude identificar el jugador en tu consulta.", None, False

        resultados = executor.query(SPARQLBuilder.query_info_jugador(jug_id))
        print(f"  [info_jugador] filas={len(resultados)}  raw={resultados}")

        if not resultados:
            return "No encontré información para ese jugador.", None, False

        fila   = resultados[0]
        nom    = fila.get("nombre", jug_id)
        eq_nom = fila.get("equipo_nombre", "?")
        nac    = fila.get("nacionalidad", "?")
        pos    = fila.get("posicion", "?")
        dor    = fila.get("dorsal", "?")
        cap    = str(fila.get("esCapitan", "false")).lower() == "true"

        goles_r = executor.query(SPARQLBuilder.query_goles_jugador(jug_id))
        goles   = int(goles_r[0].get("total", 0)) if goles_r else 0
        print(f"  [info_jugador] goles={goles}")

        q = parsed.raw.lower()
        if any(k in q for k in ["posicion", "posición", "de que juega", "de qué juega"]):
            answer = f"{nom} juega en la posición de {pos}."
        elif any(k in q for k in ["equipo", "donde juega", "dónde juega"]):
            answer = f"{nom} juega en el {eq_nom}."
        elif any(k in q for k in ["nacionalidad", "de donde es", "de dónde es", "pais", "país"]):
            answer = f"La nacionalidad de {nom} es {nac}."
        elif any(k in q for k in ["dorsal", "numero", "número", "camiseta"]):
            answer = f"{nom} usa el dorsal #{dor}."
        elif "goles" in q:
            answer = f"{nom} tiene {goles} goles registrados."
        else:
            cap_str = " (capitán)" if cap else ""
            answer  = (f"{nom} es un jugador de nacionalidad {nac} que juega de {pos} "
                       f"en el {eq_nom}{cap_str}. Usa el dorsal #{dor} y tiene {goles} goles registrados.")

        data = {"nombre": nom, "dorsal": dor, "posicion": pos,
                "nacionalidad": nac, "equipo": eq_nom, "goles": goles, "capitan": cap}
        return answer, data, True

    # ── jugador_por_dorsal ─────────────────────────────────────────────────
    @staticmethod
    def _jugador_por_dorsal(matched: dict):
        dorsal = matched.get("dorsal")
        eq_id  = matched.get("equipo_id")
        print(f"  [jugador_por_dorsal] dorsal={dorsal!r}  eq_id={eq_id!r}")

        if not dorsal:
            return "No pude identificar el número de dorsal.", None, False

        resultados = executor.query(SPARQLBuilder.query_jugador_por_dorsal(dorsal, eq_id))
        print(f"  [jugador_por_dorsal] filas={len(resultados)}")

        if not resultados:
            return "No encontré un jugador con ese dorsal.", None, False

        fila   = resultados[0]
        nom    = fila.get("nombre", "?")
        eq_nom = fila.get("equipo_nombre", "?")
        answer = f"El jugador que lleva el dorsal #{dorsal} en el {eq_nom} es {nom}."
        return answer, {"nombre": nom, "dorsal": dorsal, "equipo": eq_nom}, True

    # ── jugadores_nacionalidad ─────────────────────────────────────────────
    @staticmethod
    def _jugadores_nacionalidad(matched: dict):
        nac = (matched.get("nacionalidad") or "").strip()
        print(f"  [jugadores_nacionalidad] nac_raw={nac!r}")

        if not nac:
            return "No pude identificar la nacionalidad en tu consulta.", None, False

        mapeo = {
            "española": "españa", "español": "españa",
            "inglesa":  "inglaterra", "ingles": "inglaterra", "inglés": "inglaterra",
            "francesa": "francia",   "frances": "francia",   "francés": "francia",
            "brasileña": "brasil",   "brasileño": "brasil",
            "alemana":  "alemania",  "aleman": "alemania",   "alemán": "alemania",
            "argentina": "argentina","argentino": "argentina",
            "portuguesa": "portugal","portugues": "portugal","portugués": "portugal",
            "italiana":  "italia",   "italiano": "italia",
            "uruguaya":  "uruguay",  "uruguayo": "uruguay",
            "colombiana": "colombia","colombiano": "colombia",
            "croata":    "croacia",
        }
        nac_query = mapeo.get(nac.lower(), nac)
        print(f"  [jugadores_nacionalidad] nac_query={nac_query!r}")

        resultados = executor.query(SPARQLBuilder.query_jugadores_nacionalidad(nac_query))
        print(f"  [jugadores_nacionalidad] jugadores={len(resultados)}")

        if not resultados:
            return "No encontré jugadores con esa nacionalidad.", None, False

        data = [{"nombre":       f.get("nombre", "?"),
                 "nacionalidad": f.get("nacionalidad", nac),
                 "equipo":       f.get("equipo_nombre", "?"),
                 "posicion":     f.get("posicion", "?")}
                for f in resultados]

        nombres     = [d["nombre"] for d in data]
        nac_display = data[0]["nacionalidad"]
        answer = (f"Se encontraron {len(data)} jugadores con nacionalidad {nac_display}, "
                  f"entre ellos: {_resumir_lista(nombres)}.")
        return answer, data, True

    # ── info_estadio ───────────────────────────────────────────────────────
    @staticmethod
    def _info_estadio(matched: dict, parsed):
        est_id = matched.get("estadio_id") if matched else None
        print(f"  [info_estadio] est_id={est_id!r}")

        if not est_id:
            resultados = executor.query(SPARQLBuilder.query_todos_estadios())
            print(f"  [info_estadio] todos: filas={len(resultados)}")
            if not resultados:
                return "No hay estadios registrados.", None, False
            data    = [{"nombre":    f.get("nombre", "?"), "capacidad": f.get("capacidad", "?"),
                        "ciudad":    f.get("ciudad", "?"), "pais":      f.get("pais", "?")}
                       for f in resultados]
            nombres = [d["nombre"] for d in data]
            answer  = f"Hay {len(data)} estadios registrados: {_resumir_lista(nombres)}."
            return answer, data, True

        resultados = executor.query(SPARQLBuilder.query_info_estadio(est_id))
        print(f"  [info_estadio] filas={len(resultados)}")

        if not resultados:
            return "No encontré información para ese estadio.", None, False

        fila   = resultados[0]
        nom    = fila.get("nombre", est_id)
        cap    = fila.get("capacidad", "?")
        ciu    = fila.get("ciudad", "?")
        pai    = fila.get("pais", "?")

        q = parsed.raw.lower()
        if any(k in q for k in ["capacidad", "aforo", "cuantos entran", "cuántos entran"]):
            answer = f"La capacidad del estadio {nom} es de {cap} espectadores."
        elif any(k in q for k in ["donde esta", "dónde está", "ciudad", "ubicacion", "ubicación"]):
            answer = f"El estadio {nom} está ubicado en {ciu}, {pai}."
        else:
            answer = f"El estadio {nom} está en {ciu}, {pai}, con capacidad para {cap} espectadores."

        return answer, {"nombre": nom, "capacidad": cap, "ciudad": ciu, "pais": pai}, True

    # ── arbitros ───────────────────────────────────────────────────────────
    @staticmethod
    def _arbitros():
        resultados = executor.query(SPARQLBuilder.query_arbitros())
        print(f"  [arbitros] filas={len(resultados)}")
        if not resultados:
            return "No hay árbitros registrados.", None, False
        data    = [{"nombre": f.get("nombre", "?"), "nacionalidad": f.get("nacionalidad", "?")}
                   for f in resultados]
        nombres = [d["nombre"] for d in data]
        answer  = f"Hay {len(data)} árbitros registrados: {_resumir_lista(nombres)}."
        return answer, data, True

    # ── tarjetas ───────────────────────────────────────────────────────────
    @staticmethod
    def _tarjetas():
        resultados = executor.query(SPARQLBuilder.query_todas_tarjetas())
        print(f"  [tarjetas] filas={len(resultados)}")
        if not resultados:
            return "No hay tarjetas registradas.", None, False
        data = [{"tipo":    f.get("tipo_clase", "?"), "jugador": f.get("nombre_jugador", "?"),
                 "minuto":  f.get("minuto", "?"),     "tiempo":  f.get("tiempo", ""),
                 "motivo":  f.get("motivo", "")}
                for f in resultados]
        answer = f"Se encontraron {len(data)} tarjetas registradas en total."
        return answer, data, True

    # ── sustituciones ──────────────────────────────────────────────────────
    @staticmethod
    def _sustituciones():
        resultados = executor.query(SPARQLBuilder.query_sustituciones())
        print(f"  [sustituciones] filas={len(resultados)}")
        if not resultados:
            return "No hay sustituciones registradas.", None, False
        data = [{"entra":  f.get("entra_nom", "?"), "sale":   f.get("sale_nom",  "?"),
                 "minuto": f.get("minuto", "?"),     "tiempo": f.get("tiempo", "")}
                for f in resultados]
        answer = f"Se encontraron {len(data)} sustituciones registradas."
        return answer, data, True

    # ── goleadores_ranking ─────────────────────────────────────────────────
    @staticmethod
    def _goleadores_ranking():
        resultados = executor.query(SPARQLBuilder.query_maximo_goleador())
        print(f"  [goleadores_ranking] filas={len(resultados)}")
        if not resultados:
            return "No hay registros de goles.", None, False
        data   = [{"jugador": f.get("nombre", "?"), "goles": int(f.get("goles", 0))}
                  for f in resultados]
        top3   = ", ".join(f"{d['jugador']} ({d['goles']})" for d in data[:3])
        answer = f"Top goleadores: {top3}."
        return answer, data, True

    # ── todos_partidos ─────────────────────────────────────────────────────
    @staticmethod
    def _todos_partidos():
        resultados = executor.query(SPARQLBuilder.query_todos_partidos())
        print(f"  [todos_partidos] filas={len(resultados)}")
        if not resultados:
            return "No se encontraron partidos registrados.", None, False
        data = [{"fecha":           _fmt_fecha(f.get("fecha", "")),
                 "local":           f.get("eq_local_nom", "?"),
                 "visitante":       f.get("eq_visitante_nom", "?"),
                 "goles_local":     f.get("goles_local", "-"),
                 "goles_visitante": f.get("goles_visitante", "-"),
                 "competicion":     f.get("comp_nombre", "?")}
                for f in resultados]
        answer = f"Se encontraron {len(data)} partidos registrados."
        return answer, data, True

    # ── todos_equipos ──────────────────────────────────────────────────────
    @staticmethod
    def _todos_equipos():
        resultados = executor.query(SPARQLBuilder.query_todos_los_equipos())
        print(f"  [todos_equipos] filas={len(resultados)}")
        if not resultados:
            return "No hay equipos registrados.", None, False
        data   = [f["nombre"] for f in resultados if "nombre" in f]
        answer = f"Hay {len(data)} equipos registrados: {_resumir_lista(data)}."
        return answer, data, True

    # ── todos_jugadores ────────────────────────────────────────────────────
    @staticmethod
    def _todos_jugadores():
        resultados = executor.query(SPARQLBuilder.query_todos_los_jugadores())
        print(f"  [todos_jugadores] filas={len(resultados)}")
        if not resultados:
            return "No hay jugadores registrados.", None, False
        data   = [f["nombre"] for f in resultados if "nombre" in f]
        answer = f"Hay {len(data)} jugadores registrados: {_resumir_lista(data)}."
        return answer, data, True


# Instancia global compartida por el Router
search_service = SearchService()