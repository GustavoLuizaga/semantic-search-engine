from rdflib import Graph

class SPARQLExecutor:
    def __init__(self, owx_path: str):
        self.g = Graph()
        try:
            # Auto-detectar formato según extensión
            if owx_path.endswith(".owl"):
                fmt = "xml"
            elif owx_path.endswith(".ttl"):
                fmt = "turtle"
            else:
                fmt = None  # rdflib intenta detectarlo solo

            self.g.parse(owx_path, format=fmt)
            print(f"[SPARQLExecutor] Cargado OK: {len(self.g)} triples desde {owx_path!r} (formato={fmt})")
        except Exception as e:
            print(f"[SPARQLExecutor] Warning: rdflib parse error: {e}")

    def query(self, sparql_str: str) -> list[dict]:
        try:
            results = self.g.query(sparql_str)
            res_list = []
            for row in results:
                row_dict = {str(k): str(v) for k, v in row.asdict().items() if v is not None}
                res_list.append(row_dict)
            return res_list
        except Exception as e:
            print(f"[SPARQLExecutor] Warning: SPARQL query error: {e}")
            return []