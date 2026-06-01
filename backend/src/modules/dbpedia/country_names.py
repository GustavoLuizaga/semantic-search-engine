# country_names.py
# Mapea nombre de país en cualquier idioma → nombre en español (usado en SPARQL)
COUNTRY_NAMES: dict[str, str] = {
    # Inglés → Español
    "germany":      "alemania",
    "spain":        "españa",
    "france":       "francia",
    "england":      "inglaterra",
    "italy":        "italia",
    "portugal":     "portugal",
    "netherlands":  "países bajos",
    "holland":      "países bajos",
    "brazil":       "brasil",
    "argentina":    "argentina",
    "mexico":       "méxico",
    "united states":"estados unidos",
    "usa":          "estados unidos",
    # Francés → Español
    "allemagne":    "alemania",
    "espagne":      "españa",
    "angleterre":   "inglaterra",
    "italie":       "italia",
    "pays-bas":     "países bajos",
    "brésil":       "brasil",
    "mexique":      "méxico",
    "états-unis":   "estados unidos",
    # Alemán → Español (bonus)
    "deutschland":  "alemania",
    "spanien":      "españa",
    "frankreich":   "francia",
    "england":      "inglaterra",
    "italien":      "italia",
    "brasilien":    "brasil",
}

def normalize_country(name: str) -> str:
    """Devuelve el nombre en español. Si no está en el dict, devuelve el original."""
    return COUNTRY_NAMES.get(name.lower().strip(), name.lower().strip())