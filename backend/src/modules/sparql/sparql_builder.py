PREFIX = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/valer/ontologies/2026/2/ontologia_futbol/>
"""


class SPARQLBuilder:

    @staticmethod
    def query_partido_entre(eq_a_id: str, eq_b_id: str) -> str:
        """Partidos donde eq_a juega contra eq_b (en cualquier rol)."""
        return PREFIX + f"""
        SELECT ?partido ?golesLocal ?golesVisitante ?fecha
               ?estadio_nombre ?arbitro_nombre ?comp_nombre
               ?eq_local_nom ?eq_visitante_nom
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
            OPTIONAL {{ ?partido :tieneEquipoLocal ?eql . ?eql :tieneNombre ?eq_local_nom }}
            OPTIONAL {{ ?partido :tieneEquipoVisitante ?eqv . ?eqv :tieneNombre ?eq_visitante_nom }}
            OPTIONAL {{ ?partido :seJuegaEn ?est . ?est :tieneNombre ?estadio_nombre }}
            OPTIONAL {{ ?partido :esArbitradoPor ?arb . ?arb :tieneNombre ?arbitro_nombre }}
            OPTIONAL {{ ?partido :perteneceA ?comp . ?comp :tieneNombre ?comp_nombre }}
            OPTIONAL {{
                ?res :resultadoDe ?partido .
                ?res :tieneGolesLocal ?golesLocal ;
                     :tieneGolesVisitante ?golesVisitante .
            }}
        }}
        """

    @staticmethod
    def query_partidos_de_equipo(eq_id: str) -> str:
        """Todos los partidos donde un equipo participó (como local o visitante)."""
        return PREFIX + f"""
        SELECT ?partido ?golesLocal ?golesVisitante ?fecha
               ?estadio_nombre ?arbitro_nombre ?comp_nombre
               ?eq_local_nom ?eq_visitante_nom
        WHERE {{
            {{
                ?partido a :Partido ;
                         :tieneEquipoLocal :{eq_id} .
            }} UNION {{
                ?partido a :Partido ;
                         :tieneEquipoVisitante :{eq_id} .
            }}
            OPTIONAL {{ ?partido :tieneFecha ?fecha }}
            OPTIONAL {{ ?partido :tieneEquipoLocal ?eql . ?eql :tieneNombre ?eq_local_nom }}
            OPTIONAL {{ ?partido :tieneEquipoVisitante ?eqv . ?eqv :tieneNombre ?eq_visitante_nom }}
            OPTIONAL {{ ?partido :seJuegaEn ?est . ?est :tieneNombre ?estadio_nombre }}
            OPTIONAL {{ ?partido :esArbitradoPor ?arb . ?arb :tieneNombre ?arbitro_nombre }}
            OPTIONAL {{ ?partido :perteneceA ?comp . ?comp :tieneNombre ?comp_nombre }}
            OPTIONAL {{
                ?res :resultadoDe ?partido .
                ?res :tieneGolesLocal ?golesLocal ;
                     :tieneGolesVisitante ?golesVisitante .
            }}
        }}
        ORDER BY ?fecha
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
    def query_info_equipo(eq_id: str) -> str:
        """Info completa de un equipo: ciudad, país, estadio, entrenador, liga."""
        return PREFIX + f"""
        SELECT ?nombre ?ciudad ?pais ?estadio_nombre ?entrenador_nombre ?comp_nombre
        WHERE {{
            :{eq_id} :tieneNombre ?nombre .
            OPTIONAL {{ :{eq_id} :tieneCiudad ?ciudad }}
            OPTIONAL {{ :{eq_id} :tienePais ?pais }}
            OPTIONAL {{ :{eq_id} :tieneEstadio ?est . ?est :tieneNombre ?estadio_nombre }}
            OPTIONAL {{ :{eq_id} :esDirigidoPor ?dt . ?dt :tieneNombre ?entrenador_nombre }}
            OPTIONAL {{ :{eq_id} :perteneceA ?comp . ?comp :tieneNombre ?comp_nombre }}
        }}
        """

    @staticmethod
    def query_jugador_por_dorsal(dorsal: str, eq_id: str = None) -> str:
        """Jugador que lleva un dorsal específico, opcionalmente filtrado por equipo."""
        if eq_id:
            filtro_eq = f"?jug :juegaEn :{eq_id} ."
        else:
            filtro_eq = ""

        return PREFIX + f"""
        SELECT ?nombre ?equipo_nombre ?posicion
        WHERE {{
            ?jug a :Jugador ;
                 :tieneNombre ?nombre ;
                 :tieneDorsal {dorsal} .
            {filtro_eq}
            OPTIONAL {{ ?jug :juegaEn ?eq . ?eq :tieneNombre ?equipo_nombre }}
            OPTIONAL {{ ?jug :tienePosicion ?posicion }}
        }}
        LIMIT 1
        """

    @staticmethod
    def query_jugadores_nacionalidad(nacionalidad: str) -> str:
        return PREFIX + f"""
        SELECT ?nombre ?nacionalidad ?equipo_nombre ?posicion
        WHERE {{
            ?jug a :Jugador ;
                 :tieneNombre ?nombre ;
                 :tieneNacionalidad ?nacionalidad .
            OPTIONAL {{ ?jug :juegaEn ?eq . ?eq :tieneNombre ?equipo_nombre }}
            OPTIONAL {{ ?jug :tienePosicion ?posicion }}
            FILTER(CONTAINS(LCASE(str(?nacionalidad)), "{nacionalidad.lower()}"))
        }}
        ORDER BY ?nombre
        """

    @staticmethod
    def query_equipos_por_pais(pais: str) -> str:
        return PREFIX + f"""
        SELECT ?nombre ?ciudad ?estadio_nombre ?pais_res
        WHERE {{
            ?eq a :Equipo ;
                :tieneNombre ?nombre .
            OPTIONAL {{ ?eq :tienePais ?pais_attr }}
            OPTIONAL {{ ?eq :tieneNacionalidad ?nac }}
            OPTIONAL {{ ?eq :tieneCiudad ?ciudad }}
            OPTIONAL {{ ?eq :tieneEstadio ?est . ?est :tieneNombre ?estadio_nombre }}
            BIND(COALESCE(?pais_attr, ?nac) AS ?pais_res)
            FILTER(CONTAINS(LCASE(str(?pais_attr)), "{pais.lower()}") || CONTAINS(LCASE(str(?nac)), "{pais.lower()}"))
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
    def query_todos_estadios() -> str:
        """Lista todos los estadios con su info básica."""
        return PREFIX + """
        SELECT ?nombre ?capacidad ?ciudad ?pais
        WHERE {
            ?est a :Estadio ;
                 :tieneNombre ?nombre .
            OPTIONAL { ?est :tieneCapacidad ?capacidad }
            OPTIONAL { ?est :tieneCiudad ?ciudad }
            OPTIONAL { ?est :tienePais ?pais }
        }
        ORDER BY ?nombre
        """

    @staticmethod
    def query_estadios_por_ubicacion(ubicacion: str) -> str:
        return PREFIX + f"""
        SELECT ?nombre ?capacidad ?ciudad ?pais
        WHERE {{
            ?est a :Estadio ;
                 :tieneNombre ?nombre .
            OPTIONAL {{ ?est :tieneCapacidad ?capacidad }}
            OPTIONAL {{ ?est :tieneCiudad ?ciudad }}
            OPTIONAL {{ ?est :tienePais ?pais }}
            FILTER(
                CONTAINS(LCASE(str(?ciudad)), "{ubicacion.lower()}") || 
                CONTAINS(LCASE(str(?pais)), "{ubicacion.lower()}")
            )
        }}
        ORDER BY ?nombre
        """

    @staticmethod
    def query_capitan_equipo(eq_id: str) -> str:
        return PREFIX + f"""
        SELECT ?nombre ?dorsal ?posicion
        WHERE {{
            ?jug a :Jugador ;
                 :juegaEn :{eq_id} ;
                 :esCapitan true ;
                 :tieneNombre ?nombre .
            OPTIONAL {{ ?jug :tieneDorsal ?dorsal }}
            OPTIONAL {{ ?jug :tienePosicion ?posicion }}
        }}
        """

    @staticmethod
    def query_partidos_por_competicion(comp_nombre: str) -> str:
        return PREFIX + f"""
        SELECT ?partido ?fecha ?eq_local_nom ?eq_visitante_nom ?goles_local ?goles_visitante ?compName
        WHERE {{
            ?partido a :Partido ;
                     :perteneceA ?comp .
            ?comp :tieneNombre ?compName .
            OPTIONAL {{ ?partido :tieneFecha ?fecha }}
            OPTIONAL {{ ?partido :tieneEquipoLocal ?eql . ?eql :tieneNombre ?eq_local_nom }}
            OPTIONAL {{ ?partido :tieneEquipoVisitante ?eqv . ?eqv :tieneNombre ?eq_visitante_nom }}
            OPTIONAL {{
                ?res :resultadoDe ?partido .
                ?res :tieneGolesLocal ?goles_local ;
                     :tieneGolesVisitante ?goles_visitante .
            }}
            FILTER(CONTAINS(LCASE(str(?compName)), "{comp_nombre.lower()}"))
        }}
        ORDER BY ?fecha
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
        LIMIT 10
        """

    @staticmethod
    def query_todos_partidos() -> str:
        return PREFIX + """
        SELECT ?partido ?fecha ?eq_local_nom ?eq_visitante_nom
               ?goles_local ?goles_visitante ?comp_nombre
        WHERE {
            ?partido a :Partido .
            OPTIONAL { ?partido :tieneFecha ?fecha }
            OPTIONAL { ?partido :tieneEquipoLocal ?eql . ?eql :tieneNombre ?eq_local_nom }
            OPTIONAL { ?partido :tieneEquipoVisitante ?eqv . ?eqv :tieneNombre ?eq_visitante_nom }
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
    def query_todos_los_equipos() -> str:
        return PREFIX + """
        SELECT ?nombre ?ciudad ?pais ?estadio_nombre
        WHERE {
            ?equipo a :Equipo .
            ?equipo :tieneNombre ?nombre .
            OPTIONAL { ?equipo :tieneCiudad ?ciudad }
            OPTIONAL { ?equipo :tienePais ?pais }
            OPTIONAL { ?equipo :tieneEstadio ?est . ?est :tieneNombre ?estadio_nombre }
        }
        ORDER BY ?nombre
        """

    @staticmethod
    def query_todos_los_jugadores() -> str:
        return PREFIX + """
        SELECT ?nombre ?nacionalidad ?posicion ?equipo_nombre
        WHERE {
            ?jug a :Jugador .
            ?jug :tieneNombre ?nombre .
            OPTIONAL { ?jug :tieneNacionalidad ?nacionalidad }
            OPTIONAL { ?jug :tienePosicion ?posicion }
            OPTIONAL { ?jug :juegaEn ?eq . ?eq :tieneNombre ?equipo_nombre }
        }
        ORDER BY ?nombre
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

    @staticmethod
    def query_fecha_nacimiento(persona_id: str) -> str:
        return PREFIX + f"""
        SELECT ?nombre ?fecha_nacimiento
        WHERE {{
            :{persona_id} :tieneNombre ?nombre .
            :{persona_id} :tieneFechaNacimiento ?fecha_nacimiento .
        }}
        """

    @staticmethod
    def query_es_titular(jugador_id: str) -> str:
        return PREFIX + f"""
        SELECT ?nombre ?es_titular ?equipo_nombre
        WHERE {{
            :{jugador_id} :tieneNombre ?nombre .
            OPTIONAL {{ :{jugador_id} :esTitular ?es_titular }}
            OPTIONAL {{ :{jugador_id} :juegaEn ?eq . ?eq :tieneNombre ?equipo_nombre }}
        }}
        """

    @staticmethod
    def query_torneos_internacionales() -> str:
        return PREFIX + """
        SELECT ?nombre ?comp_clase
        WHERE {
            ?comp a :TorneoInternacional .
            ?comp :tieneNombre ?nombre .
            BIND("TorneoInternacional" AS ?comp_clase)
        }
        ORDER BY ?nombre
        """

    @staticmethod
    def query_asistencia_gol(jugador_id: str) -> str:
        return PREFIX + f"""
        SELECT ?asistidor_nom ?minuto ?tiempo ?goleador_nom
        WHERE {{
            ?gol a :Gol ;
                 :goleador :{jugador_id} ;
                 :asistencia ?asistidor .
            :{jugador_id} :tieneNombre ?goleador_nom .
            ?asistidor :tieneNombre ?asistidor_nom .
            OPTIONAL {{ ?gol :tieneMinuto ?minuto }}
            OPTIONAL {{ ?gol :tieneTiempo ?tiempo }}
        }}
        ORDER BY ?tiempo ?minuto
        """

    @staticmethod
    def query_tarjeta_por_motivo(motivo: str) -> str:
        return PREFIX + f"""
        SELECT ?nombre_jugador ?motivo_exacto ?minuto ?tiempo ?tipo_tarjeta
        WHERE {{
            ?tar a ?clase ;
                 :motivoTarjeta ?motivo_exacto ;
                 :recibeTarjeta ?jug .
            ?jug :tieneNombre ?nombre_jugador .
            OPTIONAL {{ ?tar :tieneMinuto ?minuto }}
            OPTIONAL {{ ?tar :tieneTiempo ?tiempo }}
            FILTER(CONTAINS(LCASE(str(?motivo_exacto)), LCASE(str("{motivo}"))))
            BIND(IF(EXISTS {{ ?tar a :TarjetaRoja }}, "Roja", "Amarilla") AS ?tipo_tarjeta)
        }}
        """

    @staticmethod
    def query_gol_propia_puerta() -> str:
        return PREFIX + """
        SELECT ?nombre_jugador ?minuto ?tiempo
        WHERE {
            ?gol a :GolEnPropiaPorteria ;
                 :goleador ?jug .
            ?jug :tieneNombre ?nombre_jugador .
            OPTIONAL { ?gol :tieneMinuto ?minuto }
            OPTIONAL { ?gol :tieneTiempo ?tiempo }
        }
        """

    @staticmethod
    def query_gol_de_penal() -> str:
        return PREFIX + """
        SELECT ?nombre_jugador ?minuto ?tiempo
        WHERE {
            ?gol a :GolDePenal ;
                 :goleador ?jug .
            ?jug :tieneNombre ?nombre_jugador .
            OPTIONAL { ?gol :tieneMinuto ?minuto }
            OPTIONAL { ?gol :tieneTiempo ?tiempo }
        }
        """
        
    @staticmethod
    def query_jugadores_por_posicion(posicion: str) -> str:
        """Jugadores que juegan en una posición dada."""
        return PREFIX + f"""
        SELECT ?nombre ?equipo_nombre ?dorsal ?nacionalidad
        WHERE {{
            ?jug a :Jugador ;
                 :tieneNombre ?nombre ;
                 :tienePosicion ?pos .
            FILTER(LCASE(str(?pos)) = "{posicion.lower()}")
            OPTIONAL {{ ?jug :juegaEn ?eq . ?eq :tieneNombre ?equipo_nombre }}
            OPTIONAL {{ ?jug :tieneDorsal ?dorsal }}
            OPTIONAL {{ ?jug :tieneNacionalidad ?nacionalidad }}
        }}
        ORDER BY ?nombre
        """

    @staticmethod
    def query_todos_entrenadores() -> str:
        """Lista todos los entrenadores con su equipo actual."""
        return PREFIX + """
        SELECT ?nombre ?nacionalidad ?fecha_nac ?equipo_nombre
        WHERE {
            ?dt a :Entrenador ;
                :tieneNombre ?nombre .
            OPTIONAL { ?dt :tieneNacionalidad ?nacionalidad }
            OPTIONAL { ?dt :tieneFechaNacimiento ?fecha_nac }
            OPTIONAL { ?eq :esDirigidoPor ?dt . ?eq :tieneNombre ?equipo_nombre }
        }
        ORDER BY ?nombre
        """

    @staticmethod
    def query_info_entrenador(dt_id: str) -> str:
        """Info de un entrenador específico y el equipo que dirige."""
        return PREFIX + f"""
        SELECT ?nombre ?nacionalidad ?fecha_nac ?equipo_nombre
        WHERE {{
            :{dt_id} a :Entrenador ;
                     :tieneNombre ?nombre .
            OPTIONAL {{ :{dt_id} :tieneNacionalidad ?nacionalidad }}
            OPTIONAL {{ :{dt_id} :tieneFechaNacimiento ?fecha_nac }}
            OPTIONAL {{ ?eq :esDirigidoPor :{dt_id} . ?eq :tieneNombre ?equipo_nombre }}
        }}
        """