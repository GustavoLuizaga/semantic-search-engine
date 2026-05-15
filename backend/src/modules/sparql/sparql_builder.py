PREFIX = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/valer/ontologies/2026/2/ontologia_futbol#>
"""


class SPARQLBuilder:

    @staticmethod
    def query_partido_entre(eq_a_id: str, eq_b_id: str) -> str:
        """Busca partidos donde eq_a es local y eq_b es visitante O viceversa."""
        return PREFIX + f"""
        SELECT ?partido ?golesLocal ?golesVisitante ?fecha ?estadio_nombre ?arbitro_nombre ?comp_nombre ?temp_inicio ?temp_fin
        WHERE {{
            {{
                ?partido a :Partido ;
                         :tieneEquipoLocal :{eq_a_id} ;
                         :tieneEquipoVisitante :{eq_b_id} .
            }} UNION {{
                ?partido a :Partido ;
                         :tieneEquipoLocal :{eq_b_id} ;
                         :tieneEquipoVisitante :{eq_a_id} .
            }}
            OPTIONAL {{ ?partido :tieneFecha ?fecha }}
            OPTIONAL {{ ?partido :seJuegaEn ?est . ?est :tieneNombre ?estadio_nombre }}
            OPTIONAL {{ ?partido :esArbitradoPor ?arb . ?arb :tieneNombre ?arbitro_nombre }}
            OPTIONAL {{ ?partido :perteneceA ?comp . ?comp :tieneNombre ?comp_nombre }}
            OPTIONAL {{
                ?partido :correspondeA ?temp .
                ?temp :tieneAñoInicio ?temp_inicio ;
                      :tieneAñoFin ?temp_fin .
            }}
            OPTIONAL {{
                ?res :resultadoDe ?partido .
                ?res :tieneGolesLocal ?golesLocal ;
                     :tieneGolesVisitante ?golesVisitante .
            }}
        }}
        """

    @staticmethod
    def query_jugadores_equipo(eq_id: str) -> str:
        return PREFIX + f"""
        SELECT ?nombre ?posicion ?dorsal ?esCapitan ?esTitular
        WHERE {{
            ?jug a :Jugador ;
                 :juegaEn :{eq_id} ;
                 :tieneNombre ?nombre .
            OPTIONAL {{ ?jug :tienePosicion ?posicion }}
            OPTIONAL {{ ?jug :tieneDorsal ?dorsal }}
            OPTIONAL {{ ?jug :esCapitan ?esCapitan }}
            OPTIONAL {{ ?jug :esTitular ?esTitular }}
        }}
        ORDER BY ?nombre
        """

    @staticmethod
    def query_goles_partido(partido_id: str) -> str:
        return PREFIX + f"""
        SELECT ?gol_tipo ?minuto ?tiempo ?anotador_nom ?asistidor_nom
        WHERE {{
            ?gol :esParteDe :{partido_id} ;
                 :goleador ?anotador .
            ?anotador :tieneNombre ?anotador_nom .
            OPTIONAL {{ ?gol :tieneMinuto ?minuto }}
            OPTIONAL {{ ?gol :tieneTiempo ?tiempo }}
            OPTIONAL {{ ?gol :asistencia ?asist . ?asist :tieneNombre ?asistidor_nom }}
        }}
        ORDER BY ?tiempo ?minuto
        """

    @staticmethod
    def query_goles_jugador(jugador_id: str) -> str:
        return PREFIX + f"""
        SELECT (COUNT(?gol) AS ?total)
        WHERE {{
            ?gol :goleador :{jugador_id} .
        }}
        """

    @staticmethod
    def query_info_jugador(jugador_id: str) -> str:
        return PREFIX + f"""
        SELECT ?nombre ?equipo_nombre ?nacionalidad ?posicion ?dorsal ?esCapitan
        WHERE {{
            :{jugador_id} :tieneNombre ?nombre .
            OPTIONAL {{ :{jugador_id} :juegaEn ?eq . ?eq :tieneNombre ?equipo_nombre }}
            OPTIONAL {{ :{jugador_id} :tieneNacionalidad ?nacionalidad }}
            OPTIONAL {{ :{jugador_id} :tienePosicion ?posicion }}
            OPTIONAL {{ :{jugador_id} :tieneDorsal ?dorsal }}
            OPTIONAL {{ :{jugador_id} :esCapitan ?esCapitan }}
        }}
        """

    @staticmethod
    def query_jugadores_nacionalidad(nacionalidad: str) -> str:
        return PREFIX + f"""
        SELECT ?nombre ?nacionalidad ?equipo_nombre ?posicion
        WHERE {{
            ?jug a :Jugador ;
                 :tieneNombre ?nombre ;
                 :tieneNacionalidad ?nac .
            OPTIONAL {{ ?jug :juegaEn ?eq . ?eq :tieneNombre ?equipo_nombre }}
            OPTIONAL {{ ?jug :tienePosicion ?posicion }}
            FILTER(CONTAINS(LCASE(?nac), "{nacionalidad.lower()}"))
        }}
        ORDER BY ?nombre
        """

    @staticmethod
    def query_info_estadio(estadio_id: str) -> str:
        return PREFIX + f"""
        SELECT ?nombre ?capacidad ?ciudad ?pais
        WHERE {{
            :{estadio_id} :tieneNombre ?nombre .
            OPTIONAL {{ :{estadio_id} :tieneCapacidad ?capacidad }}
            OPTIONAL {{ :{estadio_id} :tieneCiudad ?ciudad }}
            OPTIONAL {{ :{estadio_id} :tienePais ?pais }}
        }}
        """

    @staticmethod
    def query_arbitros() -> str:
        return PREFIX + """
        SELECT ?nombre ?nacionalidad
        WHERE {
            ?arb a :Arbitro ;
                 :tieneNombre ?nombre .
            OPTIONAL { ?arb :tieneNacionalidad ?nacionalidad }
        }
        ORDER BY ?nombre
        """

    @staticmethod
    def query_todas_tarjetas() -> str:
        """Obtiene todas las tarjetas (rojas y amarillas) con el jugador."""
        return PREFIX + """
        SELECT ?tipo_clase ?nombre_jugador ?minuto ?tiempo ?motivo
        WHERE {
            ?tar :recibeTarjeta ?jug .
            ?jug :tieneNombre ?nombre_jugador .
            OPTIONAL { ?tar :tieneMinuto ?minuto }
            OPTIONAL { ?tar :tieneTiempo ?tiempo }
            OPTIONAL { ?tar :motivoTarjeta ?motivo }
            BIND(IF(EXISTS { ?tar a :TarjetaRoja }, "Roja", "Amarilla") AS ?tipo_clase)
        }
        """

    @staticmethod
    def query_tarjetas_rojas() -> str:
        """Solo tarjetas rojas."""
        return PREFIX + """
        SELECT ?nombre_jugador ?minuto ?tiempo ?motivo
        WHERE {
            ?tar a :TarjetaRoja ;
                 :recibeTarjeta ?jug .
            ?jug :tieneNombre ?nombre_jugador .
            OPTIONAL { ?tar :tieneMinuto ?minuto }
            OPTIONAL { ?tar :tieneTiempo ?tiempo }
            OPTIONAL { ?tar :motivoTarjeta ?motivo }
        }
        """

    @staticmethod
    def query_sustituciones() -> str:
        return PREFIX + """
        SELECT ?entra_nom ?sale_nom ?minuto ?tiempo
        WHERE {
            ?sus a :Sustitucion ;
                 :jugadorEntra ?entra ;
                 :jugadorSale ?sale .
            ?entra :tieneNombre ?entra_nom .
            ?sale :tieneNombre ?sale_nom .
            OPTIONAL { ?sus :tieneMinuto ?minuto }
            OPTIONAL { ?sus :tieneTiempo ?tiempo }
        }
        ORDER BY ?tiempo ?minuto
        """

    @staticmethod
    def query_maximo_goleador() -> str:
        return PREFIX + """
        SELECT ?nombre (COUNT(?gol) AS ?goles)
        WHERE {
            ?gol :goleador ?jug .
            ?jug :tieneNombre ?nombre .
        }
        GROUP BY ?nombre ?jug
        ORDER BY DESC(?goles)
        LIMIT 5
        """

    @staticmethod
    def query_todos_partidos() -> str:
        return PREFIX + """
        SELECT ?partido ?fecha ?eq_local_nom ?eq_visitante_nom ?goles_local ?goles_visitante ?comp_nombre
        WHERE {
            ?partido a :Partido .
            OPTIONAL { ?partido :tieneFecha ?fecha }
            OPTIONAL { ?partido :tieneEquipoLocal ?eq_local . ?eq_local :tieneNombre ?eq_local_nom }
            OPTIONAL { ?partido :tieneEquipoVisitante ?eq_vis . ?eq_vis :tieneNombre ?eq_visitante_nom }
            OPTIONAL { ?partido :perteneceA ?comp . ?comp :tieneNombre ?comp_nombre }
            OPTIONAL {
                ?res :resultadoDe ?partido .
                ?res :tieneGolesLocal ?goles_local ;
                     :tieneGolesVisitante ?goles_visitante .
            }
        }
        ORDER BY ?fecha
        """

    @staticmethod
    def query_all(clase: str) -> str:
        return PREFIX + f"""
        SELECT ?ind ?nombre
        WHERE {{
            ?ind a :{clase} .
            OPTIONAL {{ ?ind :tieneNombre ?nombre }}
        }}
        ORDER BY ?nombre
        """
