from .semantic_parser import ParsedQuery


class OntologyMatcher:
    def __init__(self, indexer):
        self.indexer = indexer

    def match(self, parsed: ParsedQuery):
        intent = parsed.intent
        entities = parsed.entities

        if intent == "resultado_partido":
            return self._match_partido(entities)

        elif intent == "goles_partido":
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
            eq_id = self.indexer.find_by_name(equipo) if equipo else None
            return {"dorsal": dorsal, "equipo_id": eq_id}

        elif intent == "goleadores_ranking":
            # No necesita entidad específica
            return {}

        elif intent in ("todos_partidos", "todos_equipos", "todos_jugadores",
                        "arbitros", "tarjetas", "sustituciones"):
            return {}

        return None

    def _match_partido(self, entities: list):
        """Busca partidos que involucren las entidades dadas."""
        if len(entities) >= 2:
            eq1_id = self.indexer.find_by_name(entities[0])
            eq2_id = self.indexer.find_by_name(entities[1])

            if eq1_id and eq2_id:
                return {"eq_a": eq1_id, "eq_b": eq2_id}

            # Solo una entidad encontrada, buscar cualquier partido con ella
            eq_id = eq1_id or eq2_id
            if eq_id:
                return {"eq_a": eq_id, "eq_b": None}

        elif len(entities) == 1:
            eq_id = self.indexer.find_by_name(entities[0])
            if eq_id:
                return {"eq_a": eq_id, "eq_b": None}

        return None

    def _match_equipo(self, entities: list):
        for ent in entities:
            eq_id = self.indexer.find_by_name(ent)
            if eq_id and self.indexer.loader.classes.get(eq_id) == "Equipo":
                return {"equipo_id": eq_id}
        # Intento más amplio: cualquier individuo que sea equipo
        for ent in entities:
            eq_id = self.indexer.find_by_name(ent)
            if eq_id:
                return {"equipo_id": eq_id}
        return None

    def _match_jugador(self, entities: list):
        for ent in entities:
            jug_id = self.indexer.find_by_name(ent)
            if jug_id and self.indexer.loader.classes.get(jug_id) == "Jugador":
                return {"jugador_id": jug_id}
        # Intento más amplio
        for ent in entities:
            jug_id = self.indexer.find_by_name(ent)
            if jug_id:
                return {"jugador_id": jug_id}
        return None

    def _match_estadio(self, entities: list):
        for ent in entities:
            est_id = self.indexer.find_by_name(ent)
            if est_id and self.indexer.loader.classes.get(est_id) == "Estadio":
                return {"estadio_id": est_id}
        for ent in entities:
            est_id = self.indexer.find_by_name(ent)
            if est_id:
                return {"estadio_id": est_id}
        return None
