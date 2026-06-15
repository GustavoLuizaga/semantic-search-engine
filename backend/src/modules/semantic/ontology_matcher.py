from .semantic_parser import ParsedQuery
from .alias_mapper import AliasMapper

class OntologyMatcher:
    def __init__(self, executor):
        # Ahora recibe el ejecutor de SPARQL en lugar del indexer
        self.executor = executor

    def _find_id_by_name(self, name: str, class_filter: str = None) -> str:
        """Busca el ID de una entidad usando SPARQL puro y búsqueda por tokens."""
        if not name:
            return None
        
        canonical_name = AliasMapper.resolve(name)
        tokens = [t for t in canonical_name.split() if len(t) > 2]
        if not tokens:
            tokens = [canonical_name]
            
        regex_filters = " && ".join([f'regex(str(?nombre), "{t}", "i")' for t in tokens])
        
        NS = "http://www.semanticweb.org/valer/ontologies/2026/2/ontologia_futbol/"

        if class_filter:
            # MAGIA SEMÁNTICA: rdf:type/rdfs:subClassOf* busca la clase y TODAS sus subclases (ej. Delantero es Jugador)
            query = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX : <{NS}>
            SELECT ?id WHERE {{
                ?id rdf:type/rdfs:subClassOf* :{class_filter} .
                {{ ?id :tieneNombre ?nombre }} UNION {{ ?id rdfs:label ?nombre }}
                FILTER({regex_filters})
            }} LIMIT 1
            """
        else:
            query = f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX : <{NS}>
            SELECT ?id WHERE {{
                {{ ?id :tieneNombre ?nombre }} UNION {{ ?id rdfs:label ?nombre }}
                FILTER({regex_filters})
            }} LIMIT 1
            """

        res = self.executor.query(query)
        if res:
            full_iri = res[0].get("id", "")
            # El TTL usa / como separador de namespace (no #)
            NS_BASE = "http://www.semanticweb.org/valer/ontologies/2026/2/ontologia_futbol/"
            if full_iri.startswith(NS_BASE):
                return full_iri[len(NS_BASE):]
            if "#" in full_iri:
                return full_iri.split("#")[-1]
            return full_iri
        return None

    def match(self, parsed: ParsedQuery):
        intent = parsed.intent
        entities = parsed.entities

        if intent in ("resultado_partido", "goles_partido"):
            return self._match_partido(entities)

        elif intent in ("jugadores_equipo", "info_equipo", "capitan_equipo"):
            return self._match_equipo(entities)

        elif intent == "info_jugador":
            return self._match_jugador(entities)

        elif intent == "estadios":
            return self._match_estadio(entities)

        elif intent == "estadios_ubicacion":
            return {"ubicacion": entities[0] if entities else ""}

        elif intent == "partidos_competicion":
            return {"competicion": entities[0] if entities else ""}

        elif intent == "jugador_por_dorsal":
            dorsal = entities[0] if len(entities) > 0 else ""
            equipo = entities[1] if len(entities) > 1 else ""
            eq_id = self._find_id_by_name(equipo, "Equipo") if equipo else None
            return {"dorsal": dorsal, "equipo_id": eq_id}

        elif intent in ("jugadores_nacionalidad", "equipos_por_pais"):
            return {"nacionalidad": entities[0] if entities else ""}

        elif intent in ("info_fecha_nacimiento", "es_titular", "asistencia_gol"):
            return self._match_persona(entities) if intent == "info_fecha_nacimiento" else self._match_jugador(entities)

        elif intent == "tarjeta_por_motivo":
            return {"motivo": entities[0] if entities else ""}

        elif intent == "partidos_fecha":
            return {"fecha": entities[0] if entities else ""}

        elif intent in ("torneos_internacionales", "gol_propia_puerta", "gol_de_penal", "goleadores_ranking"):
            return {}
        
        elif intent == "jugadores_posicion":
            posicion = entities[0] if len(entities) > 0 else ""
            equipo_nombre = entities[1] if len(entities) > 1 else ""
            eq_id = self._find_id_by_name(equipo_nombre, "Equipo") if equipo_nombre else None
            return {"posicion": posicion, "equipo_id": eq_id}

        elif intent == "info_entrenador":
            return self._match_entrenador(entities)
        
        return None

    def _match_persona(self, entities: list):
        for ent in entities:
            per_id = self._find_id_by_name(ent, "Persona")
            if per_id:
                return {"persona_id": per_id}
        return None

    def _match_equipo(self, entities: list):
        for ent in entities:
            eq_id = self._find_id_by_name(ent, "Equipo")
            if eq_id:
                return {"equipo_id": eq_id}
        # Sin fallback amplio: no queremos confundir equipos con jugadores u otras clases
        return None

    def _match_jugador(self, entities: list):
        for ent in entities:
            # Buscará Jugador, Delantero, Defensa, etc., gracias a la query jerárquica
            jug_id = self._find_id_by_name(ent, "Jugador")
            if jug_id:
                return {"jugador_id": jug_id}
        # Sin fallback amplio: no queremos confundir jugadores con equipos u otras clases
        return None

    def _match_estadio(self, entities: list):
        for ent in entities:
            est_id = self._find_id_by_name(ent, "Estadio")
            if est_id:
                return {"estadio_id": est_id}
        return None

    def _match_partido(self, entities: list):
        if len(entities) >= 2:
            eq_a = self._find_id_by_name(entities[0], "Equipo")
            eq_b = self._find_id_by_name(entities[1], "Equipo")
            return {"eq_a": eq_a, "eq_b": eq_b}
        elif len(entities) == 1:
            eq_a = self._find_id_by_name(entities[0], "Equipo")
            return {"eq_a": eq_a, "eq_b": None}
        return None
    
    def _match_entrenador(self, entities: list):
        for ent in entities:
            if not ent:
                continue
            dt_id = self._find_id_by_name(ent, "Entrenador")
            if dt_id:
                return {"entrenador_id": dt_id}
        # Sin nombre concreto → listar todos
        return {}