class DBpediaQueryBuilder:
    @staticmethod
    def build_label_filter(entity: str, label_var: str = "?label") -> str:
        """
        Genera un filtro SPARQL IN ultra optimizado con variaciones de capitalización.
        Esto permite realizar un index lookup instantáneo en lugar de escaneos completos lentos.
        """
        entity_clean = entity.strip()
        variations = [
            entity_clean, 
            entity_clean.title(), 
            entity_clean.upper(), 
            entity_clean.capitalize()
        ]
        
        # Variación inteligente para acrónimos deportivos
        words = entity_clean.split()
        smart_words = []
        for w in words:
            if w.lower() in ("fc", "psg", "dt", "vs", "rcd", "real", "as", "ac"):
                smart_words.append(w.upper())
            else:
                smart_words.append(w.capitalize())
        variations.append(" ".join(smart_words))
        
        # Añadir variaciones específicas para clubes de fútbol populares si aplica
        if "barcelona" in entity_clean.lower() and "fc barcelona" not in variations:
            variations.append("FC Barcelona")
        if "real madrid" in entity_clean.lower() and "real madrid cf" not in variations:
            variations.append("Real Madrid CF")
            
        # Limpieza y eliminación de duplicados
        variations = sorted(list(set(v.replace('"', '\\"') for v in variations if v)))
        
        # Construimos la lista de literales para el filtro IN de SPARQL
        literals = []
        for v in variations:
            literals.append(f'"{v}"@es')
            literals.append(f'"{v}"@en')
            literals.append(f'"{v}"')
            
        literals_str = ", ".join(literals)
        return f"FILTER({label_var} IN ({literals_str}))"

    @staticmethod
    def build(intent: str, entity: str) -> str:
        """
        Retorna la consulta SPARQL correspondiente para DBpedia según el intent y la entidad dada.
        Usa index lookups de alto rendimiento para evitar timeouts en el endpoint de DBpedia.
        """
        entity_lower = entity.lower().strip()
        label_filter = DBpediaQueryBuilder.build_label_filter(entity_lower, "?label")

        if intent in ("info_jugador", "info_fecha_nacimiento"):
            return f"""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?player ?label ?birthDate ?positionLabel ?number ?teamLabel ?nationalityLabel WHERE {{
  ?player a dbo:SoccerPlayer .
  ?player rdfs:label ?label .
  {label_filter}
  
  OPTIONAL {{ ?player dbo:birthDate ?birthDate . }}
  OPTIONAL {{ 
    ?player dbo:position ?position . 
    ?position rdfs:label ?positionLabel .
    FILTER(lang(?positionLabel) = "es" || lang(?positionLabel) = "en")
  }}
  OPTIONAL {{
    ?player dbo:number ?num1 .
  }}
  OPTIONAL {{
    ?player dbp:jerseyNumber ?num2 .
  }}
  OPTIONAL {{
    ?player dbp:shirtNumber ?num3 .
  }}
  BIND(COALESCE(?num1, ?num2, ?num3, "Sin dorsal") AS ?number)

  OPTIONAL {{ 
    ?player dbo:team ?team . 
    ?team rdfs:label ?teamLabel .
    FILTER(lang(?teamLabel) = "es" || lang(?teamLabel) = "en")
  }}
  OPTIONAL {{ 
    ?player dbo:nationality ?nationality . 
    ?nationality rdfs:label ?nationalityLabel .
    FILTER(lang(?nationalityLabel) = "es" || lang(?nationalityLabel) = "en")
  }}
  
  FILTER(lang(?label) = "es" || lang(?label) = "en")
}}
ORDER BY strlen(str(?label))
LIMIT 1
"""

        elif intent in ("info_equipo", "capitan_equipo"):
            return f"""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?club ?label ?stadiumLabel ?managerLabel ?cityLabel ?leagueLabel WHERE {{
  ?club a dbo:SoccerClub .
  ?club rdfs:label ?label .
  {label_filter}
  
  OPTIONAL {{ 
    ?club dbo:ground ?stadium . 
    ?stadium rdfs:label ?stadiumLabel .
    FILTER(lang(?stadiumLabel) = "es" || lang(?stadiumLabel) = "en")
  }}
  OPTIONAL {{ 
    ?club dbo:manager ?manager . 
    ?manager rdfs:label ?managerLabel .
    FILTER(lang(?managerLabel) = "es" || lang(?managerLabel) = "en")
  }}
  OPTIONAL {{ 
    ?club dbo:city ?city . 
    ?city rdfs:label ?cityLabel .
    FILTER(lang(?cityLabel) = "es" || lang(?cityLabel) = "en")
  }}
  OPTIONAL {{ 
    ?club dbo:league ?league . 
    ?league rdfs:label ?leagueLabel .
    FILTER(lang(?leagueLabel) = "es" || lang(?leagueLabel) = "en")
  }}
  
  FILTER(lang(?label) = "es" || lang(?label) = "en")
}}
ORDER BY strlen(str(?label))
LIMIT 1
"""

        elif intent == "jugadores_equipo":
            club_filter = DBpediaQueryBuilder.build_label_filter(entity_lower, "?clubLabel")
            return f"""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?playerLabel ?number ?positionLabel WHERE {{
  ?club a dbo:SoccerClub .
  ?club rdfs:label ?clubLabel .
  {club_filter}
  
  ?player a dbo:SoccerPlayer ;
          dbo:team ?club ;
          rdfs:label ?playerLabel .
  FILTER(lang(?playerLabel) = "es" || lang(?playerLabel) = "en")
  
  OPTIONAL {{ ?player dbo:number ?number . }}
  OPTIONAL {{ 
    ?player dbo:position ?position . 
    ?position rdfs:label ?positionLabel .
    FILTER(lang(?positionLabel) = "es" || lang(?positionLabel) = "en")
  }}
}}
LIMIT 30
"""

        elif intent in ("estadios", "estadios_ubicacion"):
            return f"""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?stadium ?label ?capacity ?locationLabel WHERE {{
  ?stadium a dbo:Stadium .
  ?stadium rdfs:label ?label .
  {label_filter}
  
  OPTIONAL {{ ?stadium dbo:capacity ?capacity . }}
  OPTIONAL {{ 
    ?stadium dbo:location ?location . 
    ?location rdfs:label ?locationLabel .
    FILTER(lang(?locationLabel) = "es" || lang(?locationLabel) = "en")
  }}
  
  FILTER(lang(?label) = "es" || lang(?label) = "en")
}}
ORDER BY strlen(str(?label))
LIMIT 1
"""

        elif intent == "info_entrenador":
            return f"""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?manager ?label ?birthDate ?teamLabel WHERE {{
  ?manager a ?type .
  FILTER(?type = dbo:SoccerManager || ?type = dbo:SportsManager)
  ?manager rdfs:label ?label .
  {label_filter}
  
  OPTIONAL {{ ?manager dbo:birthDate ?birthDate . }}
  OPTIONAL {{ 
    ?manager dbo:team ?team . 
    ?team rdfs:label ?teamLabel .
    FILTER(lang(?teamLabel) = "es" || lang(?teamLabel) = "en")
  }}
  
  FILTER(lang(?label) = "es" || lang(?label) = "en")
}}
ORDER BY strlen(str(?label))
LIMIT 1
"""

        elif intent == "jugadores_nacionalidad":
            nat_filter = DBpediaQueryBuilder.build_label_filter(entity_lower, "?natLabel")
            return f"""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?playerLabel ?teamLabel WHERE {{
  ?player a dbo:SoccerPlayer ;
          rdfs:label ?playerLabel ;
          dbo:nationality ?nationality .
  FILTER(lang(?playerLabel) = "es" || lang(?playerLabel) = "en")
  
  ?nationality rdfs:label ?natLabel .
  {nat_filter}
  
  OPTIONAL {{ 
    ?player dbo:team ?team . 
    ?team rdfs:label ?teamLabel .
    FILTER(lang(?teamLabel) = "es" || lang(?teamLabel) = "en")
  }}
}}
LIMIT 20
"""

        elif intent == "equipos_por_pais":
            loc_filter = DBpediaQueryBuilder.build_label_filter(entity_lower, "?locLabel")
            return f"""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?clubLabel ?stadiumLabel WHERE {{
  ?club a dbo:SoccerClub ;
        rdfs:label ?clubLabel ;
        dbo:ground ?stadium .
  FILTER(lang(?clubLabel) = "es" || lang(?clubLabel) = "en")
  
  ?stadium dbo:location ?location .
  ?location rdfs:label ?locLabel .
  {loc_filter}
  
  OPTIONAL {{ 
    ?stadium rdfs:label ?stadiumLabel .
    FILTER(lang(?stadiumLabel) = "es" || lang(?stadiumLabel) = "en")
  }}
}}
LIMIT 20
"""

        else:
            # Fallback general si no encaja en deportes específicos o es una entidad general
            return f"""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?subject ?label ?comment ?abstract WHERE {{
  ?subject rdfs:label ?label .
  {label_filter}
  
  OPTIONAL {{ 
    ?subject rdfs:comment ?comment .
    FILTER(lang(?comment) = "es")
  }}
  OPTIONAL {{ 
    ?subject dbo:abstract ?abstract .
    FILTER(lang(?abstract) = "es")
  }}
  OPTIONAL {{
    ?subject rdfs:comment ?comment_en .
    FILTER(lang(?comment_en) = "en")
  }}
  OPTIONAL {{ 
    ?subject dbo:abstract ?abstract_en .
    FILTER(lang(?abstract_en) = "en")
  }}
  
  FILTER(lang(?label) = "es" || lang(?label) = "en")
}}
ORDER BY strlen(str(?label))
LIMIT 1
"""
