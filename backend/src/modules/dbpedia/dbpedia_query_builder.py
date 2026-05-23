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

SELECT ?player ?label ?birthDate ?positionLabel ?number ?teamLabel ?birthPlace ?height ?thumbnail ?currentClubLabel (GROUP_CONCAT(DISTINCT ?allTeamLabel; separator=", ") AS ?allTeams) WHERE {{
  ?player a dbo:SoccerPlayer .
  ?player rdfs:label ?label .
  {label_filter}
  
  OPTIONAL {{ ?player dbo:birthDate ?birthDate . }}
  OPTIONAL {{ 
    ?player dbo:position ?position . 
    ?position rdfs:label ?positionLabel .
    FILTER(lang(?positionLabel) = "es" || lang(?positionLabel) = "en")
  }}
  OPTIONAL {{ ?player dbo:number ?number . }}

  OPTIONAL {{ 
    ?player dbo:team ?team . 
    ?team rdfs:label ?teamLabel .
    FILTER(lang(?teamLabel) = "es" || lang(?teamLabel) = "en")
  }}
  OPTIONAL {{ 
    ?player dbp:birthPlace ?birthPlace . FILTER(lang(?birthPlace) = "en")
  }}
  OPTIONAL {{ ?player dbo:height ?height . }}
  OPTIONAL {{ ?player dbo:thumbnail ?thumbnail . }}
  OPTIONAL {{
    ?player dbp:currentclub ?currentClub .
    ?currentClub rdfs:label ?currentClubLabel .
    FILTER(lang(?currentClubLabel) = "es" || lang(?currentClubLabel) = "en")
  }}
  OPTIONAL {{
    ?player dbo:team ?allTeam .
    ?allTeam rdfs:label ?allTeamLabel .
    FILTER(lang(?allTeamLabel) = "es" || lang(?allTeamLabel) = "en")
  }}
  
  FILTER(lang(?label) = "es" || lang(?label) = "en")
}}
GROUP BY ?player ?label ?birthDate ?positionLabel ?number ?teamLabel ?birthPlace ?height ?thumbnail ?currentClubLabel
ORDER BY strlen(str(?label))
LIMIT 1
"""

        elif intent in ("info_equipo", "capitan_equipo"):
    
            CLUB_URI_MAP = {
                "real madrid":         "<http://dbpedia.org/resource/Real_Madrid_CF>",
                "fc barcelona":        "<http://dbpedia.org/resource/FC_Barcelona>",
                "barcelona":           "<http://dbpedia.org/resource/FC_Barcelona>",
                "bayern munchen":      "<http://dbpedia.org/resource/FC_Bayern_Munich>",
                "bayern":              "<http://dbpedia.org/resource/FC_Bayern_Munich>",
                "paris saint-germain": "<http://dbpedia.org/resource/Paris_Saint-Germain_F.C.>",
                "psg":                 "<http://dbpedia.org/resource/Paris_Saint-Germain_F.C.>",
                "liverpool fc":        "<http://dbpedia.org/resource/Liverpool_F.C.>",
                "liverpool":           "<http://dbpedia.org/resource/Liverpool_F.C.>",
            }
            uri = CLUB_URI_MAP.get(entity_lower)
       
            if uri:
                club_pattern = f"BIND({uri} AS ?club)"
                label_pattern = ""
            else:
                club_pattern = "?club a dbo:SoccerClub ."
                label_pattern = f"?club rdfs:label ?clubLabel . {DBpediaQueryBuilder.build_label_filter(entity_lower, '?clubLabel')}"
            return f"""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT DISTINCT ?label ?stadiumLabel ?managerLabel ?chairmanLabel ?capacity ?founded ?thumbnail ?allNicks WHERE {{
  {club_pattern}
  {label_pattern}
  
  OPTIONAL {{ ?club rdfs:label ?labelES . FILTER(lang(?labelES) = "es") }}
  OPTIONAL {{ ?club rdfs:label ?labelEN . FILTER(lang(?labelEN) = "en") }}
  OPTIONAL {{ ?club rdfs:label ?labelAny . }}
  BIND(COALESCE(?labelES, ?labelEN, ?labelAny) AS ?label)

  OPTIONAL {{
    ?club dbo:ground ?stadium .
    OPTIONAL {{ ?stadium rdfs:label ?stadiumES . FILTER(lang(?stadiumES) = "es") }}
    OPTIONAL {{ ?stadium rdfs:label ?stadiumEN . FILTER(lang(?stadiumEN) = "en") }}
    OPTIONAL {{ ?stadium rdfs:label ?stadiumAny . }}
    BIND(COALESCE(?stadiumES, ?stadiumEN, ?stadiumAny) AS ?stadiumLabel)
  }}
  OPTIONAL {{
    ?club dbo:manager ?manager .
    OPTIONAL {{ ?manager rdfs:label ?managerES . FILTER(lang(?managerES) = "es") }}
    OPTIONAL {{ ?manager rdfs:label ?managerEN . FILTER(lang(?managerEN) = "en") }}
    OPTIONAL {{ ?manager rdfs:label ?managerAny . }}
    BIND(COALESCE(?managerES, ?managerEN, ?managerAny) AS ?managerLabel)
  }}
  OPTIONAL {{
    ?club dbo:chairman ?chairman .
    OPTIONAL {{ ?chairman rdfs:label ?chairmanES . FILTER(lang(?chairmanES) = "es") }}
    OPTIONAL {{ ?chairman rdfs:label ?chairmanEN . FILTER(lang(?chairmanEN) = "en") }}
    OPTIONAL {{ ?chairman rdfs:label ?chairmanAny . }}
    BIND(COALESCE(?chairmanES, ?chairmanEN, ?chairmanAny) AS ?chairmanLabel)
  }}
  OPTIONAL {{
    ?club dbo:capacity ?capacity .
  }}
  OPTIONAL {{
    ?club dbo:formationDate ?founded .
  }}
  OPTIONAL {{
    ?club dbo:thumbnail ?thumbnail .
  }}
  OPTIONAL {{
    SELECT ?club (GROUP_CONCAT(DISTINCT ?nick; SEPARATOR=", ") AS ?allNicks) WHERE {{
      {{ ?club foaf:nick ?nick . }}
      UNION
      {{ ?club dbp:nickname ?nick . }}
    }} GROUP BY ?club
  }}
}}
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
