import unicodedata

def _normalize(s: str) -> str:
    """Elimina acentos y pasa a minúsculas para comparación."""
    return unicodedata.normalize('NFKD', s.lower()).encode('ascii', 'ignore').decode('ascii')

class OntologyIndexer:
    def __init__(self, loader):
        self.loader = loader
        self.nombre_idx: dict[str, str] = {}   # nombre.lower() → ind_id
        self.clase_idx: dict[str, list] = {}   # clase → [ind_ids]
        self.prop_idx: dict[str, list] = {}    # prop → [(subj, obj)]
        self._build_indexes()

    def _build_indexes(self):
        # clase_idx
        for ind_id, cls in self.loader.classes.items():
            if cls not in self.clase_idx:
                self.clase_idx[cls] = []
            self.clase_idx[cls].append(ind_id)

        # nombre_idx: solo indexar la propiedad tieneNombre para evitar colisiones
        for ind_id, props in self.loader.data_props.items():
            if "tieneNombre" in props:
                nombre_val = props["tieneNombre"]
                if isinstance(nombre_val, str):
                    self.nombre_idx[nombre_val.lower()] = ind_id
                    # También indexar versión sin acentos
                    norm = _normalize(nombre_val)
                    if norm != nombre_val.lower():
                        self.nombre_idx[norm] = ind_id

        # prop_idx
        for subj, props in self.loader.obj_props.items():
            for prop, obj in props:
                if prop not in self.prop_idx:
                    self.prop_idx[prop] = []
                self.prop_idx[prop].append((subj, obj))

    def nombre(self, ind_id: str) -> str:
        """Retorna el nombre (tieneNombre) de un individuo."""
        if not ind_id:
            return "?"
        props = self.loader.data_props.get(ind_id, {})
        return props.get("tieneNombre", ind_id)

    def get_obj(self, subj: str, prop: str):
        """Retorna el primer objeto para (subj, prop)."""
        objs = self.get_objs(subj, prop)
        return objs[0] if objs else None

    def get_objs(self, subj: str, prop: str) -> list:
        """Retorna todos los objetos para (subj, prop)."""
        if subj not in self.loader.obj_props:
            return []
        return [o for p, o in self.loader.obj_props[subj] if p == prop]

    def find_by_name(self, name: str):
        """Busca un individuo por nombre exacto (case-insensitive), luego fuzzy."""
        if not name:
            return None
        name_low = name.lower().strip()
        if name_low in self.nombre_idx:
            return self.nombre_idx[name_low]
        return self.find_fuzzy(name_low)

    def find_fuzzy(self, name: str):
        """Búsqueda aproximada con normalización de acentos."""
        if not name:
            return None
        name_low  = name.lower().strip()
        name_norm = _normalize(name_low)

        # 1. Substring directo (con y sin acentos)
        for k, v in self.nombre_idx.items():
            k_norm = _normalize(k)
            if name_low in k or k in name_low:
                return v
            if name_norm in k_norm or k_norm in name_norm:
                return v

        # 2. Tokens (todos deben estar en el nombre normalizado)
        tokens = [_normalize(t) for t in name_low.split() if len(t) > 2]
        if tokens:
            for k, v in self.nombre_idx.items():
                k_norm = _normalize(k)
                if all(t in k_norm for t in tokens):
                    return v

        return None

    def get_resultado_de_partido(self, partido_id: str):
        """Retorna el resultado_id asociado a un partido."""
        # resultado → resultadoDe → partido (dirección inversa)
        for subj, obj_list in self.loader.obj_props.items():
            for prop, obj in obj_list:
                if prop == "resultadoDe" and obj == partido_id:
                    return subj
        return None
