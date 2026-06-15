import urllib.request
import urllib.parse
import json
import os
import urllib.error
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

# ── 1. Creamos nuestra Excepción Personalizada ─────────────────────────────
class FusekiNoAvailableError(Exception):
    """Excepción lanzada cuando el servidor Fuseki está apagado o inaccesible."""
    pass


# ── Configuración ──────────────────────────────────────────────────────────
_DBPEDIA_ONLINE_ENDPOINT  = "https://dbpedia.org/sparql"

_FUSEKI_OFFLINE_ENDPOINT  = os.getenv(
    "FUSEKI_ENDPOINT", "http://localhost:3030/futbol/sparql"
)

_DEFAULT_MODE = os.getenv("DBPEDIA_MODE", "online").lower().strip()


class DBpediaExecutor:
    """
    Ejecuta consultas SPARQL contra DBpedia (online) o Fuseki (offline).
    """

    ENDPOINT_ONLINE  = _DBPEDIA_ONLINE_ENDPOINT
    ENDPOINT_OFFLINE = _FUSEKI_OFFLINE_ENDPOINT

    @staticmethod
    def _get_endpoint(mode: str) -> str:
        if mode == "offline":
            return DBpediaExecutor.ENDPOINT_OFFLINE
        return DBpediaExecutor.ENDPOINT_ONLINE

    @staticmethod
    def _adapt_query_for_fuseki(sparql_str: str) -> str:
        return sparql_str

    @staticmethod
    def query(sparql_str: str, mode: str | None = None) -> list[dict]:
        effective_mode = (mode or _DEFAULT_MODE).lower().strip()
        endpoint = DBpediaExecutor._get_endpoint(effective_mode)

        if effective_mode == "offline":
            sparql_str = DBpediaExecutor._adapt_query_for_fuseki(sparql_str)

        try:
            print(f"[DBpediaExecutor] mode={effective_mode} → {endpoint}")
            
            params = {
                "query": sparql_str,
                "format": "application/sparql-results+json"
            }
            query_string = urllib.parse.urlencode(params)
            full_url = f"{endpoint}?{query_string}"

            req = urllib.request.Request(
                full_url,
                headers={
                    "User-Agent": "SemanticSearchEngine/1.0 (Python urllib)",
                    "Accept": "application/sparql-results+json"
                }
            )

            timeout = 10 if effective_mode == "offline" else 15
            with urllib.request.urlopen(req, timeout=timeout) as response:
                resp_data = json.loads(response.read().decode("utf-8"))

            bindings = resp_data.get("results", {}).get("bindings", [])
            res_list = []
            for row in bindings:
                row_dict = {}
                for k, v in row.items():
                    row_dict[k] = v.get("value")
                res_list.append(row_dict)

            return res_list

        except urllib.error.URLError as e:
            if effective_mode == "offline":
                raise FusekiNoAvailableError("Tu servidor Fuseki está apagado o no es accesible. enciéndelo o revisa la documentacion del modo offline") from e
            else:
                # Si falla DBpedia online, imprimimos y retornamos vacío (como tenías antes)
                print(f"[DBpediaExecutor ERROR] mode={effective_mode}: {e}")
                return []
                
        except Exception as e:
             # Cualquier otro error (timeout, json mal formado, etc.)
             print(f"[DBpediaExecutor ERROR] mode={effective_mode}: {e}")
             if effective_mode == "offline":
                 raise FusekiNoAvailableError(f"Error al conectar con Fuseki: {str(e)}") from e
             return []

    @staticmethod
    def is_offline_available() -> bool:
        try:
            parsed_url = urlparse(DBpediaExecutor.ENDPOINT_OFFLINE)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            url = f"{base_url}/$/ping"
        
            req = urllib.request.Request(
                url,
                headers={"Accept": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                return resp.status == 200
        except Exception:
               return False