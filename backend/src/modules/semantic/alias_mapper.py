ALIASES = {
    "barça": "fc barcelona",
    "barca": "fc barcelona",
    "madrid": "real madrid",
    "merengues": "real madrid",
    "psg": "paris saint-germain",
    "bayern": "bayern munchen",
    "bayer": "bayern munchen",
    "liverpool": "liverpool fc",
    "champions": "uefa champions league",
    "clasico": "__real_madrid_vs_barcelona__",
}

class AliasMapper:
    @staticmethod
    def resolve(name: str) -> str:
        if not name:
            return ""
        name = name.lower().strip()
        return ALIASES.get(name, name)
