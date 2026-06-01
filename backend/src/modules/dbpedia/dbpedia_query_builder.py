import unicodedata

from .football_dicts import (
    CLUB_URI_MAP,
    STADIUM_URI_MAP,
    CITY_CLUBS,
    CLUB_PRIMARY_STADIUM,
)


def _resolve_stadium_uri(entity_lower: str) -> str | None:
    if entity_lower in STADIUM_URI_MAP:
        return f"<{STADIUM_URI_MAP[entity_lower]}>"
    return None


def _resolve_club_uri(entity_lower: str):
    if entity_lower in CLUB_URI_MAP:
        return f"<{CLUB_URI_MAP[entity_lower]}>"

    def _build_candidate(name: str, suffix: str) -> str:
        slug = "_".join(w.capitalize() for w in name.split())
        return f"<http://dbpedia.org/resource/{slug}{suffix}>"

    return [_build_candidate(entity_lower, s) for s in ("_F.C.", "_FC", "_CF", "_S.C.", "")]


def _build_club_pattern(entity_lower: str):
    result = _resolve_club_uri(entity_lower)
    if isinstance(result, str):
        return f"BIND({result} AS ?club)", ""
    if isinstance(result, list):
        return f"VALUES ?club {{ {' '.join(result)} }}", ""
    label_filter = DBpediaQueryBuilder.build_label_filter(entity_lower, "?clubLabel")
    return "?club a dbo:SoccerClub .", f"?club rdfs:label ?clubLabel . {label_filter}"


class DBpediaQueryBuilder:

    @staticmethod
    def build_label_filter(entity: str, label_var: str = "?label") -> str:
        entity_clean = entity.strip()
        variations = [entity_clean, entity_clean.title(), entity_clean.upper(), entity_clean.capitalize()]
        smart_words = []
        for w in entity_clean.split():
            smart_words.append(w.upper() if w.lower() in ("fc","psg","dt","vs","rcd","real","as","ac") else w.capitalize())
        variations.append(" ".join(smart_words))
        if "barcelona" in entity_clean.lower() and "fc barcelona" not in variations:
            variations.append("FC Barcelona")
        if "real madrid" in entity_clean.lower() and "real madrid cf" not in variations:
            variations.append("Real Madrid CF")
        variations = sorted(list(set(v.replace('"', '\\"') for v in variations if v)))
        literals = []
        for v in variations:
            literals += [f'"{v}"@es', f'"{v}"@en', f'"{v}"']
        return f"FILTER({label_var} IN ({', '.join(literals)}))"

    @staticmethod
    def _search_terms(entity: str) -> list[str]:
        def _strip(s):
            return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
        ec = entity.strip().lower()
        if not ec:
            return []
        terms = [ec, _strip(ec)]
        for w in ec.split():
            if len(w) > 2: terms += [w, _strip(w)]
            if len(w) > 4: terms += [w[:5], _strip(w)[:5]]
        return list(dict.fromkeys(t for t in terms if t))

    @staticmethod
    def build_contains_filter(entity: str, label_var: str = "?label") -> str:
        terms = DBpediaQueryBuilder._search_terms(entity)
        if not terms:
            return ""
        clauses = [f'CONTAINS(LCASE({label_var}), "{t.replace(chr(34), chr(92)+chr(34))}")' for t in terms]
        return f"FILTER({' || '.join(clauses)})"

    @staticmethod
    def _stadium_capacity_optionals() -> str:
        return """
  OPTIONAL { ?stadium dbp:capacity ?capacity . FILTER(REGEX(STR(?capacity), "^[0-9]+$")) }
  OPTIONAL { ?stadium dbp:seatingCapacity ?seatingCapacity . FILTER(REGEX(STR(?seatingCapacity), "^[0-9]+$")) }
"""

    @staticmethod
    def _stadium_detail_optionals(lang: str = "es") -> str:
        return f"""
  OPTIONAL {{
    ?stadium dbo:location ?location .
    OPTIONAL {{ ?location rdfs:label ?locationPref . FILTER(lang(?locationPref) = "{lang}") }}
    OPTIONAL {{ ?location rdfs:label ?locationEN . FILTER(lang(?locationEN) = "en") }}
    OPTIONAL {{ ?location rdfs:label ?locationAny . }}
    BIND(COALESCE(?locationPref, ?locationEN, ?locationAny) AS ?locationLabel)
  }}
  OPTIONAL {{ ?stadium dbo:openingDate ?openingDate . }}
  OPTIONAL {{ ?stadium dbo:thumbnail ?thumbnail . }}
"""

    @staticmethod
    def _stadium_name_filter(entity_lower: str, label_var: str = "?label") -> str:
        exact = DBpediaQueryBuilder.build_label_filter(entity_lower, label_var)
        partial = DBpediaQueryBuilder.build_contains_filter(entity_lower, label_var)
        return f"{{ {exact} }} UNION {{ {partial} }}" if partial else exact

    @staticmethod
    def build(intent: str, entity: str, language: str = "es") -> str:
        entity_lower = entity.lower().strip()
        lang = language.lower().strip() if language else "es"
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
  OPTIONAL {{ ?player dbo:position ?position . ?position rdfs:label ?positionLabel . FILTER(lang(?positionLabel) = "{lang}" || lang(?positionLabel) = "en") }}
  OPTIONAL {{ ?player dbo:number ?number . }}
  OPTIONAL {{ ?player dbo:team ?team . ?team rdfs:label ?teamLabel . FILTER(lang(?teamLabel) = "{lang}" || lang(?teamLabel) = "en") }}
  OPTIONAL {{ ?player dbp:birthPlace ?birthPlace . FILTER(lang(?birthPlace) = "en") }}
  OPTIONAL {{ ?player dbo:height ?height . }}
  OPTIONAL {{ ?player dbo:thumbnail ?thumbnail . }}
  OPTIONAL {{ ?player dbp:currentclub ?currentClub . ?currentClub rdfs:label ?currentClubLabel . FILTER(lang(?currentClubLabel) = "{lang}" || lang(?currentClubLabel) = "en") }}
  OPTIONAL {{ ?player dbo:team ?allTeam . ?allTeam rdfs:label ?allTeamLabel . FILTER(lang(?allTeamLabel) = "{lang}" || lang(?allTeamLabel) = "en") }}
  FILTER(lang(?label) = "{lang}" || lang(?label) = "en")
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
  OPTIONAL {{ ?club rdfs:label ?labelPref . FILTER(lang(?labelPref) = "{lang}") }}
  OPTIONAL {{ ?club rdfs:label ?labelEN . FILTER(lang(?labelEN) = "en") }}
  OPTIONAL {{ ?club rdfs:label ?labelAny . }}
  BIND(COALESCE(?labelPref, ?labelEN, ?labelAny) AS ?label)
  OPTIONAL {{ ?club dbo:ground ?stadium .
    OPTIONAL {{ ?stadium rdfs:label ?stadiumPref . FILTER(lang(?stadiumPref) = "{lang}") }}
    OPTIONAL {{ ?stadium rdfs:label ?stadiumEN . FILTER(lang(?stadiumEN) = "en") }}
    OPTIONAL {{ ?stadium rdfs:label ?stadiumAny . }}
    BIND(COALESCE(?stadiumPref, ?stadiumEN, ?stadiumAny) AS ?stadiumLabel) }}
  OPTIONAL {{ ?club dbo:manager ?manager .
    OPTIONAL {{ ?manager rdfs:label ?managerPref . FILTER(lang(?managerPref) = "{lang}") }}
    OPTIONAL {{ ?manager rdfs:label ?managerEN . FILTER(lang(?managerEN) = "en") }}
    OPTIONAL {{ ?manager rdfs:label ?managerAny . }}
    BIND(COALESCE(?managerPref, ?managerEN, ?managerAny) AS ?managerLabel) }}
  OPTIONAL {{ ?club dbo:chairman ?chairman .
    OPTIONAL {{ ?chairman rdfs:label ?chairmanPref . FILTER(lang(?chairmanPref) = "{lang}") }}
    OPTIONAL {{ ?chairman rdfs:label ?chairmanEN . FILTER(lang(?chairmanEN) = "en") }}
    OPTIONAL {{ ?chairman rdfs:label ?chairmanAny . }}
    BIND(COALESCE(?chairmanPref, ?chairmanEN, ?chairmanAny) AS ?chairmanLabel) }}
  OPTIONAL {{ ?club dbo:capacity ?capacity . }}
  OPTIONAL {{ ?club dbo:formationDate ?founded . }}
  OPTIONAL {{ ?club dbo:thumbnail ?thumbnail . }}
  OPTIONAL {{ SELECT ?club (GROUP_CONCAT(DISTINCT ?nick; SEPARATOR=", ") AS ?allNicks) WHERE {{
    {{ ?club foaf:nick ?nick . }} UNION {{ ?club dbp:nickname ?nick . }}
  }} GROUP BY ?club }}
}}
LIMIT 1
"""

        elif intent == "jugadores_equipo":
            club_filter = DBpediaQueryBuilder.build_label_filter(entity_lower, "?clubLabel")
            return f"""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?playerLabel ?number ?positionLabel WHERE {{
  ?club a dbo:SoccerClub . ?club rdfs:label ?clubLabel . {club_filter}
  ?player a dbo:SoccerPlayer ; dbo:team ?club ; rdfs:label ?playerLabel .
  FILTER(lang(?playerLabel) = "{lang}" || lang(?playerLabel) = "en")
  OPTIONAL {{ ?player dbo:number ?number . }}
  OPTIONAL {{ ?player dbo:position ?position . ?position rdfs:label ?positionLabel . FILTER(lang(?positionLabel) = "{lang}" || lang(?positionLabel) = "en") }}
}}
LIMIT 30
"""

        elif intent == "todos_estadios":
            club_uris = " ".join(f"<{u}>" for u in dict.fromkeys(CLUB_URI_MAP.values()))
            return f"""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?club ?stadium ?label ?locationLabel ?clubLabel ?capacity ?seatingCapacity WHERE {{
  VALUES ?club {{ {club_uris} }}
  ?club a dbo:SoccerClub .
  {{ SELECT ?club (SAMPLE(?s) AS ?stadium) WHERE {{ ?club dbo:ground ?s . }} GROUP BY ?club }}
  ?stadium rdfs:label ?label . FILTER(lang(?label) = "{lang}" || lang(?label) = "en")
  ?club rdfs:label ?clubLabel . FILTER(lang(?clubLabel) = "{lang}" || lang(?clubLabel) = "en")
  OPTIONAL {{ ?stadium dbo:location ?location . ?location rdfs:label ?locationLabel . FILTER(lang(?locationLabel) = "{lang}" || lang(?locationLabel) = "en") }}
  {DBpediaQueryBuilder._stadium_capacity_optionals()}
}}
ORDER BY ?clubLabel
"""

        elif intent == "estadio_equipo":
            club_pattern, label_pattern = _build_club_pattern(entity_lower)
            club_uri = CLUB_URI_MAP.get(entity_lower)
            primary = CLUB_PRIMARY_STADIUM.get(club_uri) if club_uri else None
            ground_clause = f"BIND(<{primary}> AS ?stadium)" if primary else "?club dbo:ground ?stadium ."
            return f"""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?stadium ?label ?locationLabel ?clubLabel ?openingDate ?thumbnail WHERE {{
  {club_pattern}
  {label_pattern}
  {ground_clause}
  ?club rdfs:label ?clubLabel . FILTER(lang(?clubLabel) = "{lang}" || lang(?clubLabel) = "en")
  ?stadium rdfs:label ?label . FILTER(lang(?label) = "{lang}" || lang(?label) = "en")
  {DBpediaQueryBuilder._stadium_detail_optionals(lang)}
}}
ORDER BY strlen(str(?label))
LIMIT 1
"""

        elif intent == "estadios":
            stadium_uri = _resolve_stadium_uri(entity_lower)
            stadium_pattern = f"BIND({stadium_uri} AS ?stadium)" if stadium_uri else "?stadium a dbo:Stadium ."
            name_filter = "" if stadium_uri else DBpediaQueryBuilder._stadium_name_filter(entity_lower, "?label")
            return f"""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?stadium ?label ?locationLabel ?openingDate ?thumbnail ?clubLabel WHERE {{
  {stadium_pattern}
  ?stadium rdfs:label ?label . FILTER(lang(?label) = "{lang}" || lang(?label) = "en")
  {name_filter}
  {DBpediaQueryBuilder._stadium_detail_optionals(lang)}
  OPTIONAL {{ ?clubTenant a dbo:SoccerClub ; dbo:ground ?stadium ; rdfs:label ?clubLabel . FILTER(lang(?clubLabel) = "{lang}" || lang(?clubLabel) = "en") }}
}}
ORDER BY strlen(str(?label))
LIMIT 1
"""

        elif intent == "estadios_ubicacion":
            def _strip(s):
                return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
            city_key = _strip(entity_lower).strip()
            uris = CITY_CLUBS.get(city_key)
            if uris:
                club_constraint = f"VALUES ?club {{ {' '.join(f'<{u}>' for u in uris)} }}"
            else:
                terms = DBpediaQueryBuilder._search_terms(entity_lower)
                escaped = [t.replace('"', '\\"') for t in terms[:3]]
                lp = " || ".join(f'CONTAINS(LCASE(?label), "{t}")' for t in escaped) or "false"
                club_constraint = f"""?club a dbo:SoccerClub .
  OPTIONAL {{ ?stadium dbo:location ?location . ?location rdfs:label ?locLabel . FILTER(lang(?locLabel) = "{lang}" || lang(?locLabel) = "en") }}
  FILTER(({lp}) || (BOUND(?locLabel) && ({lp.replace("?label", "?locLabel")})))"""
            return f"""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?stadium ?label ?locationLabel ?clubLabel ?capacity ?seatingCapacity WHERE {{
  {club_constraint}
  ?club dbo:ground ?stadium .
  ?stadium rdfs:label ?label . FILTER(lang(?label) = "{lang}" || lang(?label) = "en")
  OPTIONAL {{ ?stadium dbo:location ?location . ?location rdfs:label ?locationLabel . FILTER(lang(?locationLabel) = "{lang}" || lang(?locationLabel) = "en") }}
  ?club rdfs:label ?clubLabel . FILTER(lang(?clubLabel) = "{lang}" || lang(?clubLabel) = "en")
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
  ?manager a ?type . FILTER(?type = dbo:SoccerManager || ?type = dbo:SportsManager)
  ?manager rdfs:label ?label . {label_filter}
  OPTIONAL {{ ?manager dbo:birthDate ?birthDate . }}
  OPTIONAL {{ ?manager dbo:team ?team . ?team rdfs:label ?teamLabel . FILTER(lang(?teamLabel) = "{lang}" || lang(?teamLabel) = "en") }}
  FILTER(lang(?label) = "{lang}" || lang(?label) = "en")
}}
ORDER BY strlen(str(?label))
LIMIT 1
"""

        elif intent == "ganador_mundial":
         import re as _re
         year_match = _re.search(r"\b(19[3-9]\d|20[012]\d)\b", entity_lower)
         year = year_match.group(1) if year_match else entity_lower.strip()
         uri = f"http://dbpedia.org/resource/{year}_FIFA_World_Cup"
         # Nota: dbp:champion, dbp:second, dbp:third, dbp:fourth, dbp:country
         # son literales string tipo "ARG", "FRA" — NO recursos con rdfs:label.
         # El service los traduce con resolve_fifa_code() desde wc_codes.py.
         # dbp:topScorer y dbp:player son literales con markup de Wikipedia (se limpian en el service).
         return f"""
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX dbo: <http://dbpedia.org/ontology/>

SELECT ?champion ?second ?third ?fourth ?host ?topScorer ?mvp ?attendance WHERE {{
  BIND(<{uri}> AS ?wc)
  OPTIONAL {{ ?wc dbp:champion   ?champion . }}
  OPTIONAL {{ ?wc dbp:second     ?second . }}
  OPTIONAL {{ ?wc dbp:third      ?third . }}
  OPTIONAL {{ ?wc dbp:fourth     ?fourth . }}
  OPTIONAL {{ ?wc dbp:country    ?host . }}
  OPTIONAL {{ ?wc dbp:topScorer  ?topScorer . FILTER(lang(?topScorer) = "en") }}
  OPTIONAL {{ ?wc dbp:player     ?mvp .       FILTER(lang(?mvp) = "en") }}
  OPTIONAL {{ ?wc dbp:attendance ?attendance . }}
}}
LIMIT 1
"""

        elif intent == "jugadores_nacionalidad":
            nat_filter = DBpediaQueryBuilder.build_label_filter(entity_lower, "?natLabel")
            return f"""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?playerLabel ?teamLabel WHERE {{
  ?player a dbo:SoccerPlayer ; rdfs:label ?playerLabel ; dbo:nationality ?nationality .
  FILTER(lang(?playerLabel) = "{lang}" || lang(?playerLabel) = "en")
  ?nationality rdfs:label ?natLabel . {nat_filter}
  OPTIONAL {{ ?player dbo:team ?team . ?team rdfs:label ?teamLabel . FILTER(lang(?teamLabel) = "{lang}" || lang(?teamLabel) = "en") }}
}}
LIMIT 20
"""

        elif intent == "equipos_por_pais":
            loc_filter = DBpediaQueryBuilder.build_label_filter(entity_lower, "?locLabel")
            return f"""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?clubLabel ?stadiumLabel WHERE {{
  ?club a dbo:SoccerClub ; rdfs:label ?clubLabel ; dbo:ground ?stadium .
  FILTER(lang(?clubLabel) = "{lang}" || lang(?clubLabel) = "en")
  ?stadium dbo:location ?location . ?location rdfs:label ?locLabel . {loc_filter}
  OPTIONAL {{ ?stadium rdfs:label ?stadiumLabel . FILTER(lang(?stadiumLabel) = "{lang}" || lang(?stadiumLabel) = "en") }}
}}
LIMIT 20
"""

        else:
            return f"""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?subject ?label ?comment ?abstract WHERE {{
  ?subject rdfs:label ?label . {label_filter}
  OPTIONAL {{ ?subject rdfs:comment ?comment . FILTER(lang(?comment) = "{lang}") }}
  OPTIONAL {{ ?subject dbo:abstract ?abstract . FILTER(lang(?abstract) = "{lang}") }}
  OPTIONAL {{ ?subject rdfs:comment ?comment_en . FILTER(lang(?comment_en) = "en") }}
  OPTIONAL {{ ?subject dbo:abstract ?abstract_en . FILTER(lang(?abstract_en) = "en") }}
  FILTER(lang(?label) = "{lang}" || lang(?label) = "en")
}}
ORDER BY strlen(str(?label))
LIMIT 1
"""