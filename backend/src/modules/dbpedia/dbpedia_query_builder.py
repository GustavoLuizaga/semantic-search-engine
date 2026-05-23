import json
import os
import unicodedata
import urllib.parse

# Carga el JSON una sola vez (al nivel del módulo, no dentro del método)
_CLUB_URI_MAP = {}
_STADIUM_URI_MAP = {}
_MAP_PATH = os.path.join(os.path.dirname(__file__), "club_uris.json")
_STADIUM_MAP_PATH = os.path.join(os.path.dirname(__file__), "stadium_uris.json")
if os.path.exists(_MAP_PATH):
    with open(_MAP_PATH, encoding="utf-8") as f:
        _CLUB_URI_MAP = json.load(f)
if os.path.exists(_STADIUM_MAP_PATH):
    with open(_STADIUM_MAP_PATH, encoding="utf-8") as f:
        _STADIUM_URI_MAP = json.load(f)

_CITY_CLUBS = {}
_CITY_CLUBS_PATH = os.path.join(os.path.dirname(__file__), "city_clubs.json")
if os.path.exists(_CITY_CLUBS_PATH):
    with open(_CITY_CLUBS_PATH, encoding="utf-8") as f:
        _CITY_CLUBS = json.load(f)

# Estadio principal conocido por club (cuando DBpedia lista varios grounds)
_CLUB_PRIMARY_STADIUM = {
    "http://dbpedia.org/resource/FC_Barcelona": "http://dbpedia.org/resource/Camp_Nou",
    "http://dbpedia.org/resource/Real_Madrid_CF": "http://dbpedia.org/resource/Santiago_Bernabéu_Stadium",
    "http://dbpedia.org/resource/Manchester_United_F.C.": "http://dbpedia.org/resource/Old_Trafford",
    "http://dbpedia.org/resource/Manchester_City_F.C.": "http://dbpedia.org/resource/City_of_Manchester_Stadium",
    "http://dbpedia.org/resource/Liverpool_F.C.": "http://dbpedia.org/resource/Anfield",
    "http://dbpedia.org/resource/Arsenal_F.C.": "http://dbpedia.org/resource/Emirates_Stadium",
    "http://dbpedia.org/resource/Chelsea_F.C.": "http://dbpedia.org/resource/Stamford_Bridge_(stadium)",
}


def _resolve_stadium_uri(entity_lower: str) -> str | None:
    if entity_lower in _STADIUM_URI_MAP:
        return f"<{_STADIUM_URI_MAP[entity_lower]}>"
    return None
        
def _resolve_club_uri(entity_lower: str) -> str | None:
    """
    Intenta resolver la URI del club en este orden:
    1. Mapa manual (club_uris.json)
    2. Construcción automática tipo DBpedia: 'manchester city' → Manchester_City_F.C.
    3. None → fallback a búsqueda por label (lento)
    """
    # 1. Mapa manual
    if entity_lower in _CLUB_URI_MAP:
        uri = _CLUB_URI_MAP[entity_lower]
        return f"<{uri}>"

    # 2. Heurística automática: capitaliza palabras y reemplaza espacios por _
    #    Prueba variantes comunes de sufijo en DBpedia
    def _build_candidate(name: str, suffix: str) -> str:
        slug = "_".join(w.capitalize() for w in name.split())
        return f"<http://dbpedia.org/resource/{slug}{suffix}>"

    suffixes = ["_F.C.", "_FC", "_CF", "_S.C.", ""]
    # Los devolvemos todos; la query SPARQL usará VALUES para probarlos
    candidates = [_build_candidate(entity_lower, s) for s in suffixes]
    return candidates  # lista → señal de que hay que usar VALUES


def _build_club_pattern(entity_lower: str):
    result = _resolve_club_uri(entity_lower)

    if isinstance(result, str):
        # Hit exacto del mapa
        return f"BIND({result} AS ?club)", ""

    if isinstance(result, list):
        # Heurística: probamos candidatos con VALUES
        values = " ".join(result)
        return f"VALUES ?club {{ {values} }}", ""

    # Fallback: búsqueda por label (lento pero universal)
    label_filter = DBpediaQueryBuilder.build_label_filter(entity_lower, "?clubLabel")
    return (
        "?club a dbo:SoccerClub .",
        f"?club rdfs:label ?clubLabel . {label_filter}"
    )

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
    def _search_terms(entity: str) -> list[str]:
        """Términos de búsqueda parcial, incluyendo raíces sin acentos."""
        import unicodedata

        def _strip_accents(s: str) -> str:
            return "".join(
                c for c in unicodedata.normalize("NFD", s)
                if unicodedata.category(c) != "Mn"
            )

        entity_clean = entity.strip().lower()
        if not entity_clean:
            return []
        terms = [entity_clean, _strip_accents(entity_clean)]
        for w in entity_clean.split():
            if len(w) > 2:
                terms.append(w)
                terms.append(_strip_accents(w))
            if len(w) > 4:
                terms.append(w[:5])
                terms.append(_strip_accents(w)[:5])
        return list(dict.fromkeys(t for t in terms if t))

    @staticmethod
    def build_contains_filter(entity: str, label_var: str = "?label") -> str:
        """Búsqueda parcial por nombre (estadios con etiquetas largas o variantes)."""
        terms = DBpediaQueryBuilder._search_terms(entity)
        if not terms:
            return ""
        escaped = [t.replace('"', '\\"') for t in terms]
        clauses = [f'CONTAINS(LCASE({label_var}), "{t}")' for t in escaped]
        return f"FILTER({' || '.join(clauses)})"

    @staticmethod
    def _stadium_capacity_optionals() -> str:
        return """
  OPTIONAL {
    ?stadium dbp:capacity ?capacity .
    FILTER(REGEX(STR(?capacity), "^[0-9]+$"))
  }
  OPTIONAL {
    ?stadium dbp:seatingCapacity ?seatingCapacity .
    FILTER(REGEX(STR(?seatingCapacity), "^[0-9]+$"))
  }
"""

    @staticmethod
    def _stadium_detail_optionals() -> str:
        return """
  OPTIONAL {
    ?stadium dbo:location ?location .
    OPTIONAL { ?location rdfs:label ?locationES . FILTER(lang(?locationES) = "es") }
    OPTIONAL { ?location rdfs:label ?locationEN . FILTER(lang(?locationEN) = "en") }
    OPTIONAL { ?location rdfs:label ?locationAny . }
    BIND(COALESCE(?locationES, ?locationEN, ?locationAny) AS ?locationLabel)
  }
  OPTIONAL { ?stadium dbo:openingDate ?openingDate . }
  OPTIONAL { ?stadium dbo:thumbnail ?thumbnail . }
"""

    @staticmethod
    def _stadium_name_filter(entity_lower: str, label_var: str = "?label") -> str:
        exact = DBpediaQueryBuilder.build_label_filter(entity_lower, label_var)
        partial = DBpediaQueryBuilder.build_contains_filter(entity_lower, label_var)
        if partial:
            return f"{{ {exact} }} UNION {{ {partial} }}"
        return exact

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
       
            club_pattern, label_pattern = _build_club_pattern(entity_lower)
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

        elif intent == "todos_estadios":
            # Clubes del mapa manual → estadios relevantes sin escanear todo DBpedia
            club_uris = " ".join(f"<{u}>" for u in dict.fromkeys(_CLUB_URI_MAP.values()))
            return f"""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?club ?stadium ?label ?locationLabel ?clubLabel ?capacity ?seatingCapacity WHERE {{
  VALUES ?club {{ {club_uris} }}
  ?club a dbo:SoccerClub .
  {{
    SELECT ?club (SAMPLE(?s) AS ?stadium) WHERE {{
      ?club dbo:ground ?s .
    }} GROUP BY ?club
  }}
  ?stadium rdfs:label ?label .
  FILTER(lang(?label) = "es" || lang(?label) = "en")
  ?club rdfs:label ?clubLabel .
  FILTER(lang(?clubLabel) = "es" || lang(?clubLabel) = "en")
  OPTIONAL {{
    ?stadium dbo:location ?location .
    ?location rdfs:label ?locationLabel .
    FILTER(lang(?locationLabel) = "es" || lang(?locationLabel) = "en")
  }}
  {DBpediaQueryBuilder._stadium_capacity_optionals()}
}}
ORDER BY ?clubLabel
"""

        elif intent == "estadio_equipo":
            club_pattern, label_pattern = _build_club_pattern(entity_lower)
            # Si el club está en el mapa, preferir estadio principal conocido
            club_uri = _CLUB_URI_MAP.get(entity_lower)
            primary_stadium = _CLUB_PRIMARY_STADIUM.get(club_uri) if club_uri else None
            if primary_stadium:
                ground_clause = f"BIND(<{primary_stadium}> AS ?stadium)"
            else:
                ground_clause = "?club dbo:ground ?stadium ."
            return f"""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT ?stadium ?label ?locationLabel ?clubLabel ?openingDate ?thumbnail WHERE {{
  {club_pattern}
  {label_pattern}
  {ground_clause}
  ?club rdfs:label ?clubLabel .
  FILTER(lang(?clubLabel) = "es" || lang(?clubLabel) = "en")

  ?stadium rdfs:label ?label .
  FILTER(lang(?label) = "es" || lang(?label) = "en")
  {DBpediaQueryBuilder._stadium_detail_optionals()}
}}
ORDER BY strlen(str(?label))
LIMIT 1
"""

        elif intent == "estadios":
            stadium_uri = _resolve_stadium_uri(entity_lower)
            if stadium_uri:
                stadium_pattern = f"BIND({stadium_uri} AS ?stadium)"
                name_filter = ""
            else:
                stadium_pattern = "?stadium a dbo:Stadium ."
                name_filter = DBpediaQueryBuilder._stadium_name_filter(entity_lower, "?label")
            return f"""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT ?stadium ?label ?locationLabel ?openingDate ?thumbnail ?clubLabel WHERE {{
  {stadium_pattern}
  ?stadium rdfs:label ?label .
  FILTER(lang(?label) = "es" || lang(?label) = "en")
  {name_filter}
  {DBpediaQueryBuilder._stadium_detail_optionals()}
  OPTIONAL {{
    ?clubTenant a dbo:SoccerClub ;
                dbo:ground ?stadium ;
                rdfs:label ?clubLabel .
    FILTER(lang(?clubLabel) = "es" || lang(?clubLabel) = "en")
  }}
}}
ORDER BY strlen(str(?label))
LIMIT 1
"""

        elif intent == "estadios_ubicacion":
            def _strip_accents(s: str) -> str:
                return "".join(
                    c for c in unicodedata.normalize("NFD", s)
                    if unicodedata.category(c) != "Mn"
                )

            city_key = _strip_accents(entity_lower).strip()
            club_uris = _CITY_CLUBS.get(city_key)
            if club_uris:
                values = " ".join(f"<{u}>" for u in club_uris)
                club_constraint = f"VALUES ?club {{ {values} }}"
            else:
                club_constraint = "?club a dbo:SoccerClub ."
                terms = DBpediaQueryBuilder._search_terms(entity_lower)
                escaped = [t.replace('"', '\\"') for t in terms[:3]]
                label_part = " || ".join(
                    f'CONTAINS(LCASE(?label), "{t}")' for t in escaped
                ) or "false"
                club_constraint += f"""
  OPTIONAL {{
    ?stadium dbo:location ?location .
    ?location rdfs:label ?locLabel .
    FILTER(lang(?locLabel) = "es" || lang(?locLabel) = "en")
  }}
  FILTER(({label_part}) || (BOUND(?locLabel) && ({label_part.replace("?label", "?locLabel")})))
"""
            return f"""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT ?stadium ?label ?locationLabel ?clubLabel ?capacity ?seatingCapacity WHERE {{
  {club_constraint}
  ?club dbo:ground ?stadium .
  ?stadium rdfs:label ?label .
  FILTER(lang(?label) = "es" || lang(?label) = "en")
  OPTIONAL {{
    ?stadium dbo:location ?location .
    ?location rdfs:label ?locationLabel .
    FILTER(lang(?locationLabel) = "es" || lang(?locationLabel) = "en")
  }}
  ?club rdfs:label ?clubLabel .
  FILTER(lang(?clubLabel) = "es" || lang(?clubLabel) = "en")
  {DBpediaQueryBuilder._stadium_capacity_optionals()}
}}
ORDER BY ?label
LIMIT 15
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
