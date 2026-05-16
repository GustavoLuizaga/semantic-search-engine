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
                ?id :tieneNombre ?nombre .
                FILTER({regex_filters})
            }} LIMIT 1
            """
        else:
            query = f"""
            PREFIX : <{NS}>
            SELECT ?id WHERE {{
                ?id :tieneNombre ?nombre .
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

        elif intent in ("jugadores_equipo", "info_equipo"):
            return self._match_equipo(entities)

        elif intent == "info_jugador":
            return self._match_jugador(entities)

        elif intent == "estadios":
            return self._match_estadio(entities)

        elif intent == "jugador_por_dorsal":
            dorsal = entities[0] if len(entities) > 0 else ""
            equipo = entities[1] if len(entities) > 1 else ""
            eq_id = self._find_id_by_name(equipo, "Equipo") if equipo else None
            return {"dorsal": dorsal, "equipo_id": eq_id}

        elif intent == "jugadores_nacionalidad":
            return {"nacionalidad": entities[0] if entities else ""}

        elif intent == "goleadores_ranking":
            return {}

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