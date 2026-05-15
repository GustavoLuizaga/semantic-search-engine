import os
from src.modules.ontology.ontology_loader import OntologyLoader
from src.modules.ontology.ontology_indexer import OntologyIndexer
from src.modules.semantic.semantic_parser import SemanticParser
from src.modules.semantic.ontology_matcher import OntologyMatcher
from src.modules.sparql.sparql_builder import SPARQLBuilder
from src.modules.sparql.sparql_executor import SPARQLExecutor
from src.models import SearchResponse

# ── Resolver ruta del OWX ──────────────────────────────────────────────────
_HERE    = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
OWX_PATH = os.path.join(_BACKEND, "ontologia-futbol-finalV2.owx")
if not os.path.exists(OWX_PATH):
    OWX_PATH = os.path.join(os.getcwd(), "ontologia-futbol-finalV2.owx")

print(f"[search_service] OWX: {OWX_PATH} | exists={os.path.exists(OWX_PATH)}")

# ── Inicialización única (al arrancar) ─────────────────────────────────────
loader   = OntologyLoader(OWX_PATH)
indexer  = OntologyIndexer(loader)
matcher  = OntologyMatcher(indexer)
executor = SPARQLExecutor(OWX_PATH)   # puede tener warnings, se usa como fallback

# ── Helpers ────────────────────────────────────────────────────────────────
def _fmt_fecha(raw: str) -> str:
    if raw and "T" in raw:
        return raw.split("T")[0]
    return raw or "?"

def _nombre(ind_id: str) -> str:
    return indexer.nombre(ind_id) if ind_id else "?"

def _resultado_de_partido(partido_id: str):
    """Busca resultado_N cuyo resultadoDe apunta a partido_id."""
    for subj, obj_list in loader.obj_props.items():
        for prop, obj in obj_list:
            if prop == "resultadoDe" and obj == partido_id:
                return subj
    return None

def _goles_partido(partido_id: str):
    res_id = _resultado_de_partido(partido_id)
    if res_id:
        p = loader.data_props.get(res_id, {})
        return str(p.get("tieneGolesLocal", "?")), str(p.get("tieneGolesVisitante", "?"))
    return "?", "?"

def _info_partido(partido_id: str) -> dict:
    """Construye dict completo de un partido desde el loader (sin SPARQL)."""
    props_p  = loader.data_props.get(partido_id, {})
    eq_loc_id  = indexer.get_obj(partido_id, "tieneEquipoLocal")
    eq_vis_id  = indexer.get_obj(partido_id, "tieneEquipoVisitante")
    est_id     = indexer.get_obj(partido_id, "seJuegaEn")
    arb_id     = indexer.get_obj(partido_id, "esArbitradoPor")
    comp_id    = indexer.get_obj(partido_id, "perteneceA")
    temp_id    = indexer.get_obj(partido_id, "correspondeA")

    eq_loc  = _nombre(eq_loc_id)  if eq_loc_id  else "Equipo no especificado"
    eq_vis  = _nombre(eq_vis_id)  if eq_vis_id  else "Equipo no especificado"
    estadio = _nombre(est_id)     if est_id     else "?"
    arbitro = _nombre(arb_id)     if arb_id     else "?"
    comp    = _nombre(comp_id)    if comp_id    else "?"

    temp_inicio, temp_fin = "?", "?"
    if temp_id:
        tp = loader.data_props.get(temp_id, {})
        temp_inicio = str(tp.get("tieneAñoInicio", "?"))
        temp_fin    = str(tp.get("tieneAñoFin",    "?"))
    temporada = f"{temp_inicio}/{temp_fin}" if temp_inicio != "?" else "?"

    fecha_raw = props_p.get("tieneFecha", "?")
    fecha     = _fmt_fecha(fecha_raw)
    gl, gv    = _goles_partido(partido_id)

    return {
        "partido_id":       partido_id,
        "equipo_local":     eq_loc,
        "equipo_visitante": eq_vis,
        "goles_local":      gl,
        "goles_visitante":  gv,
        "fecha":            fecha,
        "estadio":          estadio,
        "arbitro":          arbitro,
        "competicion":      comp,
        "temporada":        temporada,
    }

def _goles_de_partido(partido_id: str) -> list:
    """Retorna lista de dicts de goles de un partido desde el loader."""
    goles = []
    # buscar todos los individuos que tienen esParteDe → partido_id
    for ind_id, obj_list in loader.obj_props.items():
        es_parte = False
        for prop, obj in obj_list:
            if prop == "esParteDe" and obj == partido_id:
                es_parte = True
                break
        if not es_parte:
            continue
        # Es un evento de este partido — ¿es un Gol?
        cls = loader.classes.get(ind_id, "")
        if "Gol" not in cls and cls not in ("Gol", "GolDeJuegoAbierto", "GolDePenal", "GolEnPropiaPorteria"):
            continue

        props_g  = loader.data_props.get(ind_id, {})
        gol_id   = indexer.get_obj(ind_id, "goleador")
        asist_id = indexer.get_obj(ind_id, "asistencia")
        minuto   = str(props_g.get("tieneMinuto", "?"))
        tiempo   = props_g.get("tieneTiempo", "")
        goles.append({
            "gol_id":    ind_id,
            "anotador":  _nombre(gol_id)   if gol_id   else "?",
            "asistidor": _nombre(asist_id) if asist_id else "",
            "minuto":    minuto,
            "tiempo":    tiempo,
            "tipo":      cls,
        })
    return goles

def _sustituciones_de_partido(partido_id: str) -> list:
    """Retorna sustituciones de un partido."""
    sust = []
    for ind_id, obj_list in loader.obj_props.items():
        for prop, obj in obj_list:
            if prop == "esParteDe" and obj == partido_id:
                if loader.classes.get(ind_id) == "Sustitucion":
                    props_s = loader.data_props.get(ind_id, {})
                    entra_id = indexer.get_obj(ind_id, "jugadorEntra")
                    sale_id  = indexer.get_obj(ind_id, "jugadorSale")
                    sust.append({
                        "entra": _nombre(entra_id) if entra_id else "?",
                        "sale":  _nombre(sale_id)  if sale_id  else "?",
                        "minuto": str(props_s.get("tieneMinuto", "?")),
                        "tiempo": props_s.get("tieneTiempo", ""),
                    })
    return sust


# ── Service ────────────────────────────────────────────────────────────────
class SearchService:

    @staticmethod
    def execute(query: str) -> SearchResponse:
        parsed = SemanticParser.parse(query)
        match  = matcher.match(parsed)
        intent = parsed.intent

        answer = "No encontré información para esa consulta."
        data   = None
        found  = False

        try:
            dispatch = {
                "resultado_partido":  lambda: SearchService._resultado_partido(match),
                "goles_partido":      lambda: SearchService._goles_partido(match, parsed),
                "jugadores_equipo":   lambda: SearchService._jugadores_equipo(match),
                "info_equipo":        lambda: SearchService._info_equipo(match, parsed),
                "info_jugador":       lambda: SearchService._info_jugador(match, parsed),
                "jugador_por_dorsal": lambda: SearchService._jugador_por_dorsal(match, parsed),
                "estadios":           lambda: SearchService._info_estadio(match, parsed),
                "arbitros":           lambda: SearchService._arbitros(),
                "tarjetas":           lambda: SearchService._tarjetas(),
                "sustituciones":      lambda: SearchService._sustituciones(),
                "goleadores_ranking": lambda: SearchService._goleadores_ranking(),
                "todos_partidos":     lambda: SearchService._todos_partidos(),
                "todos_equipos":      lambda: SearchService._todos_equipos(),
                "todos_jugadores":    lambda: SearchService._todos_jugadores(),
            }
            fn = dispatch.get(intent)
            if fn:
                answer, data, found = fn()
        except Exception as e:
            answer = f"Error procesando la consulta: {e}"

        return SearchResponse(query=query, intent=intent, answer=answer, data=data, found=found)

    # ─────────────────────────────────────────────────────────────────────
    @staticmethod
    def _resultado_partido(match):
        if not match or "eq_a" not in match:
            return "No encontré los equipos en la ontología.", None, False

        eq_a_id = match.get("eq_a")
        eq_b_id = match.get("eq_b")

        partidos_enc = []
        for p_id in indexer.clase_idx.get("Partido", []):
            loc_id = indexer.get_obj(p_id, "tieneEquipoLocal")
            vis_id = indexer.get_obj(p_id, "tieneEquipoVisitante")
            objs = {loc_id, vis_id}
            if eq_b_id:
                if eq_a_id in objs and eq_b_id in objs:
                    partidos_enc.append(p_id)
            else:
                if eq_a_id in objs:
                    partidos_enc.append(p_id)

        if not partidos_enc:
            return "No encontré partidos entre esos equipos.", None, False

        blocks = []
        results = []
        for p_id in partidos_enc:
            i = _info_partido(p_id)
            results.append(i)
            loc, vis = i["equipo_local"], i["equipo_visitante"]
            gl, gv   = i["goles_local"], i["goles_visitante"]
            blocks.append(
                f"{loc} {gl} - {gv} {vis}\n"
                f"Fecha: {i['fecha']} | Competición: {i['competicion']} ({i['temporada']})\n"
                f"Estadio: {i['estadio']} | Árbitro: {i['arbitro']}"
            )

        answer = "\n\n".join(blocks)
        data   = results[0] if len(results) == 1 else results
        return answer, data, True

    @staticmethod
    def _goles_partido(match, parsed):
        import unicodedata
        def norm(s): return unicodedata.normalize('NFKD', s.lower()).encode('ascii', 'ignore').decode('ascii')

        # Primero intentar buscar por jugador específico en la query raw
        q_norm = norm(parsed.raw)
        for jug_id in indexer.clase_idx.get("Jugador", []):
            nom = _nombre(jug_id)
            if nom and norm(nom) in q_norm:
                count = sum(
                    1 for ind_id, obj_list in loader.obj_props.items()
                    for prop, obj in obj_list if prop == "goleador" and obj == jug_id
                )
                return (
                    f"{nom} tiene {count} gol(es) registrado(s) en la ontología.",
                    {"jugador": nom, "goles": count}, True
                )

        if match and "eq_a" in match:
            eq_a_id = match["eq_a"]
            eq_b_id = match.get("eq_b")
            partidos = []
            for p_id in indexer.clase_idx.get("Partido", []):
                loc_id = indexer.get_obj(p_id, "tieneEquipoLocal")
                vis_id = indexer.get_obj(p_id, "tieneEquipoVisitante")
                objs   = {loc_id, vis_id}
                if eq_b_id:
                    if eq_a_id in objs and eq_b_id in objs:
                        partidos.append(p_id)
                else:
                    if eq_a_id in objs:
                        partidos.append(p_id)

            if partidos:
                lines = []
                all_goles = []
                for p_id in partidos:
                    info  = _info_partido(p_id)
                    goles = _goles_de_partido(p_id)
                    lines.append(
                        f"{info['equipo_local']} {info['goles_local']} - "
                        f"{info['goles_visitante']} {info['equipo_visitante']}"
                    )
                    if goles:
                        for g in goles:
                            asis = f" (asiste: {g['asistidor']})" if g['asistidor'] else ""
                            lines.append(f"  Gol: {g['anotador']}{asis} | Min {g['minuto']} {g['tiempo']}")
                            all_goles.append(g)
                    else:
                        lines.append("  (Sin detalle de goles registrados)")
                return "\n".join(lines), all_goles, True

        return "No encontré información de goles.", None, False

    @staticmethod
    def _jugadores_equipo(match):
        if not match or "equipo_id" not in match:
            return "No encontré el equipo especificado.", None, False
        eq_id  = match["equipo_id"]
        nom_eq = _nombre(eq_id)

        jugadores = [
            j_id for j_id in indexer.clase_idx.get("Jugador", [])
            if eq_id in [o for p, o in loader.obj_props.get(j_id, []) if p == "juegaEn"]
        ]
        if not jugadores:
            return f"No encontré jugadores para {nom_eq}.", None, False

        lines = [f"Plantilla — {nom_eq}:"]
        data  = []
        for j_id in sorted(jugadores, key=lambda x: loader.data_props.get(x, {}).get("tieneNombre", x)):
            props = loader.data_props.get(j_id, {})
            nom   = props.get("tieneNombre", j_id)
            pos   = props.get("tienePosicion", "?")
            dor   = str(props.get("tieneDorsal", "?"))
            cap_v = str(props.get("esCapitan", "false")).lower()
            cap   = " (Capitán)" if cap_v == "true" else ""
            lines.append(f"  {nom} | #{dor} | {pos}{cap}")
            data.append({"nombre": nom, "dorsal": dor, "posicion": pos})
        return "\n".join(lines), data, True

    @staticmethod
    def _info_equipo(match, parsed):
        if not match or "equipo_id" not in match:
            return "No encontré el equipo especificado.", None, False
        eq_id  = match["equipo_id"]
        props  = loader.data_props.get(eq_id, {})
        nom    = props.get("tieneNombre", eq_id)
        ciudad = props.get("tieneCiudad", "?")
        pais   = props.get("tienePais", "?")

        est_id   = indexer.get_obj(eq_id, "tieneEstadio")
        est_nom  = _nombre(est_id) if est_id else "?"
        dt_id    = indexer.get_obj(eq_id, "esDirigidoPor")
        dt_nom   = _nombre(dt_id) if dt_id else "?"
        comp_id  = indexer.get_obj(eq_id, "perteneceA")
        comp_nom = _nombre(comp_id) if comp_id else "?"

        # Respuesta directa según la pregunta
        q = parsed.raw.lower()
        if "entrena" in q or "entrenador" in q:
            answer = f"El entrenador del {nom} es {dt_nom}."
        elif "estadio" in q:
            answer = f"El estadio del {nom} es el {est_nom}."
        elif "liga" in q or "competicion" in q or "competición" in q:
            answer = f"El {nom} juega en la {comp_nom}."
        elif "ciudad" in q or "de donde es" in q or "de dónde es" in q or "pais" in q or "país" in q:
            answer = f"El {nom} es de {ciudad}, {pais}."
        else:
            answer = (
                f"Equipo: {nom}\n"
                f"Ciudad: {ciudad}, {pais}\n"
                f"Estadio: {est_nom}\n"
                f"Entrenador: {dt_nom}\n"
                f"Liga: {comp_nom}"
            )
            
        data = {"nombre": nom, "ciudad": ciudad, "pais": pais,
                "estadio": est_nom, "entrenador": dt_nom, "liga": comp_nom}
        return answer, data, True

    @staticmethod
    def _info_jugador(match, parsed):
        if not match or "jugador_id" not in match:
            return "No encontré al jugador especificado.", None, False
        jug_id = match["jugador_id"]
        props  = loader.data_props.get(jug_id, {})
        nom    = props.get("tieneNombre", jug_id)
        nac    = props.get("tieneNacionalidad", "?")
        pos    = props.get("tienePosicion", "?")
        dor    = str(props.get("tieneDorsal", "?"))
        cap    = " (Capitán)" if str(props.get("esCapitan", "false")).lower() == "true" else ""

        eq_id  = indexer.get_obj(jug_id, "juegaEn")
        eq_nom = _nombre(eq_id) if eq_id else "?"

        # Contar goles
        count = sum(
            1 for ind_id, obj_list in loader.obj_props.items()
            for prop, obj in obj_list if prop == "goleador" and obj == jug_id
        )

        q = parsed.raw.lower()
        if "posicion" in q or "posición" in q or "de que juega" in q or "de qué juega" in q:
            answer = f"{nom} juega en la posición de {pos}."
        elif "equipo" in q or "donde juega" in q or "dónde juega" in q:
            answer = f"{nom} juega en el equipo {eq_nom}."
        elif "nacionalidad" in q or "de donde es" in q or "de dónde es" in q or "pais" in q or "país" in q:
            answer = f"La nacionalidad de {nom} es {nac}."
        elif "dorsal" in q or "numero" in q or "número" in q or "camiseta" in q:
            answer = f"{nom} usa el dorsal #{dor}."
        elif "goles" in q:
            answer = f"{nom} tiene {count} goles registrados."
        else:
            answer = (
                f"Jugador: {nom}{cap} | #{dor}\n"
                f"Posición: {pos}\n"
                f"Nacionalidad: {nac}\n"
                f"Equipo: {eq_nom}\n"
                f"Goles registrados: {count}"
            )

        data = {"nombre": nom, "dorsal": dor, "posicion": pos,
                "nacionalidad": nac, "equipo": eq_nom, "goles": count}
        return answer, data, True

    @staticmethod
    def _jugador_por_dorsal(match, parsed):
        if not match or not match.get("dorsal"):
            return "No entendí qué número de dorsal estás buscando.", None, False
        
        dorsal = match["dorsal"]
        eq_id = match.get("equipo_id")
        
        # Buscar en todos los jugadores
        for j_id in indexer.clase_idx.get("Jugador", []):
            props = loader.data_props.get(j_id, {})
            dor = str(props.get("tieneDorsal", ""))
            
            if dor == dorsal:
                # Comprobar equipo si se especificó
                jug_eq_id = indexer.get_obj(j_id, "juegaEn")
                if eq_id and jug_eq_id != eq_id:
                    continue
                
                # Jugador encontrado
                nom = props.get("tieneNombre", j_id)
                eq_nom = _nombre(jug_eq_id) if jug_eq_id else "?"
                
                answer = f"El jugador que lleva el dorsal #{dorsal} en el {eq_nom} es {nom}."
                data = {"nombre": nom, "dorsal": dorsal, "equipo": eq_nom}
                return answer, data, True
                
        # Si no lo encontró
        eq_text = f" en el {_nombre(eq_id)}" if eq_id else ""
        return f"No se encontró un jugador con el dorsal #{dorsal}{eq_text}.", None, False

    @staticmethod
    def _info_estadio(match, parsed):
        if not match or "estadio_id" not in match:
            # Listar todos los estadios
            estadios = indexer.clase_idx.get("Estadio", [])
            lines = ["Estadios registrados:"]
            data  = []
            for e_id in sorted(estadios):
                p   = loader.data_props.get(e_id, {})
                nom = p.get("tieneNombre", e_id)
                cap = str(p.get("tieneCapacidad", "?"))
                ciu = p.get("tieneCiudad", "?")
                pai = p.get("tienePais", "?")
                lines.append(f"  - {nom} | {ciu}, {pai} | Cap: {cap}")
                data.append({"nombre": nom, "capacidad": cap, "ciudad": ciu, "pais": pai})
            return "\n".join(lines), data, bool(estadios)

        est_id = match["estadio_id"]
        props  = loader.data_props.get(est_id, {})
        nom    = props.get("tieneNombre", est_id)
        cap    = str(props.get("tieneCapacidad", "?"))
        ciu    = props.get("tieneCiudad", "?")
        pai    = props.get("tienePais", "?")
        
        q = parsed.raw.lower()
        if "capacidad" in q or "aforo" in q or "cuantos entran" in q or "cuántos entran" in q:
            answer = f"La capacidad del estadio {nom} es de {cap} espectadores."
        elif "donde esta" in q or "dónde está" in q or "ciudad" in q or "ubicacion" in q or "ubicación" in q:
            answer = f"El estadio {nom} está ubicado en {ciu}, {pai}."
        else:
            answer = (
                f"Estadio: {nom}\n"
                f"Capacidad: {cap}\n"
                f"Ubicación: {ciu}, {pai}"
            )
            
        data = {"nombre": nom, "capacidad": cap, "ciudad": ciu, "pais": pai}
        return answer, data, True

    @staticmethod
    def _arbitros():
        arbs = indexer.clase_idx.get("Arbitro", [])
        if not arbs:
            return "No se encontraron árbitros.", None, False
        lines = ["Árbitros registrados:"]
        data  = []
        for a_id in sorted(arbs, key=lambda x: loader.data_props.get(x, {}).get("tieneNombre", x)):
            p   = loader.data_props.get(a_id, {})
            nom = p.get("tieneNombre", a_id)
            nac = p.get("tieneNacionalidad", "?")
            lines.append(f"  - {nom} ({nac})")
            data.append({"nombre": nom, "nacionalidad": nac})
        return "\n".join(lines), data, True

    @staticmethod
    def _tarjetas():
        lines = ["Tarjetas registradas:"]
        data  = []
        clases_tarjeta = {"TarjetaAmarilla": "Amarilla", "TarjetaRoja": "Roja"}
        for cls, emoji in clases_tarjeta.items():
            for t_id in indexer.clase_idx.get(cls, []):
                jug_id = indexer.get_obj(t_id, "recibeTarjeta")
                nom    = _nombre(jug_id) if jug_id else "?"
                props  = loader.data_props.get(t_id, {})
                mins   = str(props.get("tieneMinuto", "?"))
                tiem   = props.get("tieneTiempo", "")
                motiv  = props.get("motivoTarjeta", "")
                lines.append(f"  {emoji} → {nom} | Min {mins} {tiem} | {motiv}")
                data.append({"tipo": cls, "jugador": nom, "minuto": mins,
                             "tiempo": tiem, "motivo": motiv})
        if len(lines) == 1:
            return "No se encontraron tarjetas.", None, False
        return "\n".join(lines), data, True

    @staticmethod
    def _sustituciones():
        sust_ids = indexer.clase_idx.get("Sustitucion", [])
        if not sust_ids:
            return "No se encontraron sustituciones.", None, False
        lines = ["Sustituciones registradas:"]
        data  = []
        for s_id in sorted(sust_ids):
            entra_id = indexer.get_obj(s_id, "jugadorEntra")
            sale_id  = indexer.get_obj(s_id, "jugadorSale")
            props    = loader.data_props.get(s_id, {})
            entra    = _nombre(entra_id) if entra_id else "?"
            sale     = _nombre(sale_id)  if sale_id  else "?"
            mins     = str(props.get("tieneMinuto", "?"))
            tiem     = props.get("tieneTiempo", "")
            lines.append(f"  - Entra: {entra} | Sale: {sale} | Min {mins} {tiem}")
            data.append({"entra": entra, "sale": sale, "minuto": mins, "tiempo": tiem})
        return "\n".join(lines), data, True

    @staticmethod
    def _goleadores_ranking():
        """Cuenta goles por jugador desde las object properties."""
        conteo: dict[str, int] = {}
        for ind_id, obj_list in loader.obj_props.items():
            for prop, obj in obj_list:
                if prop == "goleador":
                    conteo[obj] = conteo.get(obj, 0) + 1

        if not conteo:
            return "No se encontraron goleadores.", None, False

        ranking = sorted(conteo.items(), key=lambda x: -x[1])
        lines = ["Ranking de Goleadores:"]
        data  = []
        for i, (jug_id, goles) in enumerate(ranking, 1):
            nom = _nombre(jug_id)
            lines.append(f"  {i}. {nom} — {goles} gol(es)")
            data.append({"jugador": nom, "goles": goles})
        return "\n".join(lines), data, True

    @staticmethod
    def _todos_partidos():
        partidos = indexer.clase_idx.get("Partido", [])
        if not partidos:
            return "No se encontraron partidos.", None, False
        lines = [f"Partidos registrados ({len(partidos)}):"]
        data  = []
        for p_id in sorted(partidos):
            i = _info_partido(p_id)
            loc, vis = i["equipo_local"], i["equipo_visitante"]
            gl, gv   = i["goles_local"], i["goles_visitante"]
            lines.append(f"  - {loc} {gl}-{gv} {vis} | {i['competicion']} | {i['fecha']}")
            data.append(i)
        return "\n".join(lines), data, True

    @staticmethod
    def _todos_equipos():
        equipos = indexer.clase_idx.get("Equipo", [])
        if not equipos:
            return "No se encontraron equipos.", None, False
        lines = [f"Equipos registrados ({len(equipos)}):"]
        data  = []
        for eq_id in sorted(equipos):
            nom = _nombre(eq_id)
            lines.append(f"  - {nom}")
            data.append(nom)
        return "\n".join(lines), data, True

    @staticmethod
    def _todos_jugadores():
        jugadores = indexer.clase_idx.get("Jugador", [])
        if not jugadores:
            return "No se encontraron jugadores.", None, False
        lines = [f"Jugadores registrados ({len(jugadores)}):"]
        data  = []
        for j_id in sorted(jugadores, key=lambda x: loader.data_props.get(x, {}).get("tieneNombre", x)):
            nom = _nombre(j_id)
            lines.append(f"  - {nom}")
            data.append(nom)
        return "\n".join(lines), data, True


# Singleton
search_service = SearchService()
