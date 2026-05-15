from rdflib import Graph

class SPARQLExecutor:
    def __init__(self, owx_path: str):
        self.g = Graph()
        try:
            self.g.parse(owx_path, format="xml")
        except Exception as e:
            print(f"Warning: rdflib parse error: {e}")

    def query(self, sparql_str: str) -> list[dict]:
        try:
            results = self.g.query(sparql_str)
            res_list = []
            for row in results:
                # User specifically requested dict(row) but we need str for JSON
                row_dict = {str(k): str(v) for k, v in dict(row).items() if v is not None}
                res_list.append(row_dict)
            return res_list
        except Exception as e:
            print(f"Warning: SPARQL query error: {e}")
            return []
