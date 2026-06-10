"""
descargar_dbpedia_futbol.py
============================
Descarga datos de fútbol desde DBpedia y los guarda como un
archivo Turtle (.ttl) listo para cargar en Apache Jena Fuseki.

Uso:
    pip install requests
    python descargar_dbpedia_futbol.py

Genera: dbpedia_futbol_offline.ttl
"""

import urllib.request
import urllib.parse
import json
import time
import os

ENDPOINT = "https://dbpedia.org/sparql"
OUTPUT_FILE = "dbpedia_futbol_offline.ttl"

# Prefijos Turtle que irán al inicio del archivo
TTL_PREFIXES = """@prefix dbo:  <http://dbpedia.org/ontology/> .
@prefix dbp:  <http://dbpedia.org/property/> .
@prefix dbr:  <http://dbpedia.org/resource/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

"""

# ──────────────────────────────────────────────────────────────
# Equipos que queremos descargar (los mismos del CLUB_URI_MAP
# de football_dicts.py de tu proyecto).
# Podés ampliar esta lista con cualquier URI de DBpedia.
# ──────────────────────────────────────────────────────────────
CLUB_URIS = [
    "http://dbpedia.org/resource/FC_Barcelona",
    "http://dbpedia.org/resource/Real_Madrid_CF",
    "http://dbpedia.org/resource/Manchester_United_F.C.",
    "http://dbpedia.org/resource/Manchester_City_F.C.",
    "http://dbpedia.org/resource/Liverpool_F.C.",
    "http://dbpedia.org/resource/Chelsea_F.C.",
    "http://dbpedia.org/resource/Arsenal_F.C.",
    "http://dbpedia.org/resource/Tottenham_Hotspur_F.C.",
    "http://dbpedia.org/resource/Bayern_Munich",
    "http://dbpedia.org/resource/Borussia_Dortmund",
    "http://dbpedia.org/resource/Juventus_F.C.",
    "http://dbpedia.org/resource/A.C._Milan",
    "http://dbpedia.org/resource/Inter_Milan",
    "http://dbpedia.org/resource/Paris_Saint-Germain_F.C.",
    "http://dbpedia.org/resource/Atlético_Madrid",
    "http://dbpedia.org/resource/Sevilla_FC",
]

def sparql_query(sparql_str: str) -> list[dict]:
    """Ejecuta SPARQL en DBpedia y retorna lista de dicts."""
    params = {
        "query": sparql_str,
        "format": "application/sparql-results+json"
    }
    url = f"{ENDPOINT}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "SemanticSearchEngine/1.0 OfflineBuilder",
            "Accept": "application/sparql-results+json"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        bindings = data.get("results", {}).get("bindings", [])
        return [{k: v.get("value") for k, v in row.items()} for row in bindings]
    except Exception as e:
        print(f"  [ERROR] {e}")
        return []


def escape_ttl(s: str) -> str:
    """Escapa comillas y backslashes para strings Turtle."""
    if s is None:
        return ""
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "")


def uri_to_ttl(uri: str) -> str:
    return f"<{uri}>"


# ──────────────────────────────────────────────────────────────
# QUERIES SPARQL para cada tipo de entidad
# ──────────────────────────────────────────────────────────────

def query_equipo(club_uri: str) -> str:
    return f"""
PREFIX dbo:  <http://dbpedia.org/ontology/>
PREFIX dbp:  <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT DISTINCT ?club ?labelES ?labelEN ?stadium ?manager ?chairman
       ?capacity ?formationDate ?thumbnail ?nick WHERE {{
  BIND(<{club_uri}> AS ?club)
  OPTIONAL {{ ?club rdfs:label ?labelES . FILTER(lang(?labelES) = "es") }}
  OPTIONAL {{ ?club rdfs:label ?labelEN . FILTER(lang(?labelEN) = "en") }}
  OPTIONAL {{ ?club dbo:ground ?stadium . }}
  OPTIONAL {{ ?club dbo:manager ?manager . }}
  OPTIONAL {{ ?club dbo:chairman ?chairman . }}
  OPTIONAL {{ ?club dbo:capacity ?capacity . }}
  OPTIONAL {{ ?club dbo:formationDate ?formationDate . }}
  OPTIONAL {{ ?club dbo:thumbnail ?thumbnail . }}
  OPTIONAL {{ ?club foaf:nick ?nick . }}
}}
LIMIT 1
"""

def query_jugadores_de_equipo(club_uri: str) -> str:
    return f"""
PREFIX dbo:  <http://dbpedia.org/ontology/>
PREFIX dbp:  <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?player ?labelES ?labelEN ?birthDate ?birthPlace
       ?position ?positionLabelES ?positionLabelEN
       ?number ?height ?thumbnail ?nationality ?natLabelES
       ?currentClub WHERE {{
  ?player a dbo:SoccerPlayer .
  ?player dbo:team <{club_uri}> .
  OPTIONAL {{ ?player rdfs:label ?labelES . FILTER(lang(?labelES) = "es") }}
  OPTIONAL {{ ?player rdfs:label ?labelEN . FILTER(lang(?labelEN) = "en") }}
  OPTIONAL {{ ?player dbo:birthDate ?birthDate . }}
  OPTIONAL {{ ?player dbp:birthPlace ?birthPlace . FILTER(lang(?birthPlace) = "en") }}
  OPTIONAL {{
    ?player dbo:position ?position .
    OPTIONAL {{ ?position rdfs:label ?positionLabelES . FILTER(lang(?positionLabelES) = "es") }}
    OPTIONAL {{ ?position rdfs:label ?positionLabelEN . FILTER(lang(?positionLabelEN) = "en") }}
  }}
  OPTIONAL {{ ?player dbo:number ?number . }}
  OPTIONAL {{ ?player dbo:height ?height . }}
  OPTIONAL {{ ?player dbo:thumbnail ?thumbnail . }}
  OPTIONAL {{ ?player dbo:nationality ?natRes .
    ?natRes rdfs:label ?natLabelES . FILTER(lang(?natLabelES) = "es") }}
  OPTIONAL {{ ?player dbp:currentclub ?currentClub . }}
}}
LIMIT 5
"""

def query_estadio(stadium_uri: str) -> str:
    return f"""
PREFIX dbo:  <http://dbpedia.org/ontology/>
PREFIX dbp:  <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?labelES ?labelEN ?capacity ?seatingCap
       ?openingDate ?thumbnail ?location ?locationLabelES WHERE {{
  BIND(<{stadium_uri}> AS ?stadium)
  OPTIONAL {{ ?stadium rdfs:label ?labelES . FILTER(lang(?labelES) = "es") }}
  OPTIONAL {{ ?stadium rdfs:label ?labelEN . FILTER(lang(?labelEN) = "en") }}
  OPTIONAL {{ ?stadium dbp:capacity ?capacity . FILTER(REGEX(STR(?capacity), "^[0-9]+$")) }}
  OPTIONAL {{ ?stadium dbp:seatingCapacity ?seatingCap . FILTER(REGEX(STR(?seatingCap), "^[0-9]+$")) }}
  OPTIONAL {{ ?stadium dbo:openingDate ?openingDate . }}
  OPTIONAL {{ ?stadium dbo:thumbnail ?thumbnail . }}
  OPTIONAL {{
    ?stadium dbo:location ?location .
    OPTIONAL {{ ?location rdfs:label ?locationLabelES . FILTER(lang(?locationLabelES) = "es") }}
  }}
}}
LIMIT 1
"""

# ──────────────────────────────────────────────────────────────
# Generadores de triples Turtle
# ──────────────────────────────────────────────────────────────

def triples_equipo(club_uri: str, row: dict, stadium_uri: str | None) -> str:
    lines = [f"\n# ── EQUIPO: {club_uri} ──"]
    subject = uri_to_ttl(club_uri)
    lines.append(f"{subject}")
    lines.append(f"    a dbo:SoccerClub ;")
    if row.get("labelES"):
        lines.append(f'    rdfs:label "{escape_ttl(row["labelES"])}"@es ;')
    if row.get("labelEN"):
        lines.append(f'    rdfs:label "{escape_ttl(row["labelEN"])}"@en ;')
    if stadium_uri:
        lines.append(f"    dbo:ground {uri_to_ttl(stadium_uri)} ;")
    if row.get("manager"):
        lines.append(f"    dbo:manager {uri_to_ttl(row['manager'])} ;")
    if row.get("chairman"):
        lines.append(f"    dbo:chairman {uri_to_ttl(row['chairman'])} ;")
    if row.get("capacity"):
        lines.append(f'    dbo:capacity "{escape_ttl(row["capacity"])}"^^xsd:integer ;')
    if row.get("formationDate"):
        lines.append(f'    dbo:formationDate "{escape_ttl(row["formationDate"])}"^^xsd:date ;')
    if row.get("thumbnail"):
        lines.append(f"    dbo:thumbnail <{row['thumbnail']}> ;")
    if row.get("nick"):
        lines.append(f'    foaf:nick "{escape_ttl(row["nick"])}" ;')
    # Reemplazar el último ";" por "."
    lines[-1] = lines[-1].rstrip(" ;") + " ."
    return "\n".join(lines) + "\n"


def triples_estadio(stadium_uri: str, row: dict, club_uri: str) -> str:
    lines = [f"\n# ── ESTADIO: {stadium_uri} ──"]
    subject = uri_to_ttl(stadium_uri)
    lines.append(f"{subject}")
    lines.append(f"    a dbo:Stadium ;")
    if row.get("labelES"):
        lines.append(f'    rdfs:label "{escape_ttl(row["labelES"])}"@es ;')
    if row.get("labelEN"):
        lines.append(f'    rdfs:label "{escape_ttl(row["labelEN"])}"@en ;')
    if row.get("capacity"):
        lines.append(f'    dbp:capacity {row["capacity"]} ;')
    elif row.get("seatingCap"):
        lines.append(f'    dbp:seatingCapacity {row["seatingCap"]} ;')
    if row.get("openingDate"):
        lines.append(f'    dbo:openingDate "{escape_ttl(row["openingDate"])}"^^xsd:date ;')
    if row.get("thumbnail"):
        lines.append(f"    dbo:thumbnail <{row['thumbnail']}> ;")
    if row.get("location"):
        lines.append(f"    dbo:location {uri_to_ttl(row['location'])} ;")
    # Triple inverso: el equipo juega acá
    lines[-1] = lines[-1].rstrip(" ;") + " ."
    return "\n".join(lines) + "\n"


def triples_jugador(player_uri: str, row: dict, club_uri: str) -> str:
    lines = [f"\n# ── JUGADOR: {player_uri} ──"]
    subject = uri_to_ttl(player_uri)
    lines.append(f"{subject}")
    lines.append(f"    a dbo:SoccerPlayer ;")
    if row.get("labelES"):
        lines.append(f'    rdfs:label "{escape_ttl(row["labelES"])}"@es ;')
    if row.get("labelEN"):
        lines.append(f'    rdfs:label "{escape_ttl(row["labelEN"])}"@en ;')
    lines.append(f"    dbo:team {uri_to_ttl(club_uri)} ;")
    if row.get("birthDate"):
        lines.append(f'    dbo:birthDate "{escape_ttl(row["birthDate"])}"^^xsd:date ;')
    if row.get("birthPlace"):
        lines.append(f'    dbp:birthPlace "{escape_ttl(row["birthPlace"])}"@en ;')
    if row.get("position"):
        lines.append(f"    dbo:position {uri_to_ttl(row['position'])} ;")
    if row.get("number"):
        lines.append(f'    dbo:number "{escape_ttl(row["number"])}" ;')
    if row.get("height"):
        lines.append(f'    dbo:height "{escape_ttl(row["height"])}"^^xsd:double ;')
    if row.get("thumbnail"):
        lines.append(f"    dbo:thumbnail <{row['thumbnail']}> ;")
    if row.get("natLabelES"):
        lines.append(f'    # nacionalidad: "{escape_ttl(row["natLabelES"])}"@es ;')
    if row.get("currentClub"):
        lines.append(f"    dbp:currentclub {uri_to_ttl(row['currentClub'])} ;")
    lines[-1] = lines[-1].rstrip(" ;") + " ."
    return "\n".join(lines) + "\n"


def triples_posicion(position_uri: str, row: dict) -> str:
    if not row.get("positionLabelES") and not row.get("positionLabelEN"):
        return ""
    subject = uri_to_ttl(position_uri)
    lines = [f"{subject}"]
    if row.get("positionLabelES"):
        lines.append(f'    rdfs:label "{escape_ttl(row["positionLabelES"])}"@es ;')
    if row.get("positionLabelEN"):
        lines.append(f'    rdfs:label "{escape_ttl(row["positionLabelEN"])}"@en ;')
    lines[-1] = lines[-1].rstrip(" ;") + " ."
    return "\n".join(lines) + "\n"


# ──────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────

def main():
    total_equipos = 0
    total_jugadores = 0
    total_estadios = 0

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(TTL_PREFIXES)
        f.write("# Datos de fútbol descargados de DBpedia para modo offline\n")
        f.write("# Generado por descargar_dbpedia_futbol.py\n\n")

        positions_written = set()

        for club_uri in CLUB_URIS:
            club_name = club_uri.split("/")[-1].replace("_", " ")
            print(f"\n[{total_equipos+1}/{len(CLUB_URIS)}] Procesando: {club_name}")

            # 1. Datos del equipo
            eq_rows = sparql_query(query_equipo(club_uri))
            if not eq_rows:
                print(f"  ⚠ Sin datos para {club_name}, saltando...")
                continue

            eq_row = eq_rows[0]
            stadium_uri = eq_row.get("stadium")

            f.write(triples_equipo(club_uri, eq_row, stadium_uri))
            total_equipos += 1

            # 2. Datos del estadio
            if stadium_uri:
                print(f"  → Estadio: {stadium_uri.split('/')[-1]}")
                est_rows = sparql_query(query_estadio(stadium_uri))
                if est_rows:
                    f.write(triples_estadio(stadium_uri, est_rows[0], club_uri))
                    total_estadios += 1
                time.sleep(0.5)  # Respetar rate limit de DBpedia

            # 3. Jugadores
            print(f"  → Descargando jugadores...")
            jug_rows = sparql_query(query_jugadores_de_equipo(club_uri))
            print(f"  → {len(jug_rows)} jugadores encontrados")

            for jug in jug_rows:
                player_uri = jug.get("player")
                if not player_uri:
                    continue
                f.write(triples_jugador(player_uri, jug, club_uri))
                total_jugadores += 1

                # Posición (escribir solo una vez por URI)
                pos_uri = jug.get("position")
                if pos_uri and pos_uri not in positions_written:
                    triple = triples_posicion(pos_uri, jug)
                    if triple:
                        f.write(triple)
                    positions_written.add(pos_uri)

            time.sleep(1)  # Pausa entre equipos para no saturar DBpedia

    print(f"\n{'='*50}")
    print(f"✅ Archivo generado: {OUTPUT_FILE}")
    print(f"   Equipos:   {total_equipos}")
    print(f"   Estadios:  {total_estadios}")
    print(f"   Jugadores: {total_jugadores}")
    print(f"   Tamaño:    {os.path.getsize(OUTPUT_FILE) / 1024:.1f} KB")
    print(f"\nPróximo paso: cargar en Fuseki con:")
    print(f"  curl -X POST http://localhost:3030/futbol/data \\")
    print(f"    -H 'Content-Type: text/turtle' \\")
    print(f"    --data-binary @{OUTPUT_FILE}")


if __name__ == "__main__":
    main()