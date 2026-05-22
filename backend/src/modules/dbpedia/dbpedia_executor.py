import urllib.request
import urllib.parse
import json

class DBpediaExecutor:
    ENDPOINT = "https://dbpedia.org/sparql"

    @staticmethod
    def query(sparql_str: str) -> list[dict]:
        """
        Envía una consulta SPARQL al endpoint de DBpedia y retorna los resultados como una lista de diccionarios.
        Cada diccionario mapea el nombre de la variable de SPARQL a su valor de cadena (string).
        """
        try:
            print(f"[DBpediaExecutor] Querying DBpedia:\n{sparql_str}")
            params = {
                "query": sparql_str,
                "format": "application/sparql-results+json"
            }
            # Codificamos los parámetros de la URL
            query_string = urllib.parse.urlencode(params)
            full_url = f"{DBpediaExecutor.ENDPOINT}?{query_string}"
            
            req = urllib.request.Request(
                full_url, 
                headers={
                    "User-Agent": "SemanticSearchEngine/1.0 (Python urllib)",
                    "Accept": "application/sparql-results+json"
                }
            )
            
            # Realizamos la petición con un timeout de 15 segundos
            with urllib.request.urlopen(req, timeout=15) as response:
                resp_data = json.loads(response.read().decode("utf-8"))
                
            # Formateamos los resultados al estilo del SPARQLExecutor local
            bindings = resp_data.get("results", {}).get("bindings", [])
            res_list = []
            for row in bindings:
                row_dict = {}
                for k, v in row.items():
                    row_dict[k] = v.get("value")
                res_list.append(row_dict)
                
            print(f"[DBpediaExecutor] Returned {len(res_list)} rows.")
            return res_list
            
        except Exception as e:
            print(f"[DBpediaExecutor ERROR] Error ejecutando SPARQL en DBpedia: {e}")
            import traceback
            traceback.print_exc()
            return []
