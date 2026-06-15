import json
import os
import sys

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from src.modules.search.search_service import search_service

questions = [
    # Español
    {"query": "¿Quién es Vinícius Júnior?", "language": "es"},
    {"query": "¿De qué juega Luka Modric?", "language": "es"},
    {"query": "¿De dónde es Harry Kane?", "language": "es"},
    {"query": "¿Cuáles son los jugadores de nacionalidad Brasileña?", "language": "es"},
    {"query": "¿Quién lleva el número 7 en el Real Madrid?", "language": "es"},
    {"query": "¿Cuáles son todos los jugadores?", "language": "es"},
    {"query": "¿Cuándo nació Jude Bellingham?", "language": "es"},
    {"query": "¿Es titular Mbappé?", "language": "es"},
    {"query": "¿Quién entrena al Liverpool?", "language": "es"},
    {"query": "¿Quién es el capitán del Real Madrid?", "language": "es"},
    {"query": "Estadio del FC Barcelona?", "language": "es"},
    {"query": "¿Qué equipos hay?", "language": "es"},
    {"query": "¿Cuáles son los equipos de Alemania?", "language": "es"},
    {"query": "¿Cuál es el resultado entre Real Madrid y FC Barcelona?", "language": "es"},
    {"query": "¿Cuántos goles marcó Vinícius Júnior?", "language": "es"},
    {"query": "¿Quién es el máximo goleador?", "language": "es"},
    {"query": "Partidos jugados en la UEFA Champions League", "language": "es"},
    {"query": "Todos los partidos", "language": "es"},
    {"query": "¿Quién le dio la asistencia de gol a Mbappé?", "language": "es"},
    {"query": "¿Cuáles son los torneos internacionales?", "language": "es"},
    {"query": "¿Cuánta capacidad tiene el Santiago Bernabéu?", "language": "es"},
    {"query": "Estadios en España", "language": "es"},
    {"query": "¿Cuáles son los árbitros?", "language": "es"},
    {"query": "Muestra las tarjetas", "language": "es"},
    {"query": "Sustituciones realizadas", "language": "es"},
    {"query": "¿Qué jugador fue amonestado por Juego brusco?", "language": "es"},
    {"query": "¿Qué partidos se jugaron el 2024-11-25?", "language": "es"},

    # English
    {"query": "Who is Vinícius Júnior?", "language": "en"},
    {"query": "What position does Luka Modric play?", "language": "en"},
    {"query": "Where is Harry Kane from?", "language": "en"},
    {"query": "Which players are Brazilian?", "language": "en"},
    {"query": "Who wears number 7 for Real Madrid?", "language": "en"},
    {"query": "Who are all the players?", "language": "en"},
    {"query": "When was Jude Bellingham born?", "language": "en"},
    {"query": "Is Mbappé a starter?", "language": "en"},
    {"query": "Who coaches Liverpool?", "language": "en"},
    {"query": "Who is the captain of Real Madrid?", "language": "en"},
    {"query": "What is FC Barcelona's stadium?", "language": "en"},
    {"query": "Which teams are registered?", "language": "en"},
    {"query": "Which teams are from Germany?", "language": "en"},
    {"query": "Result of Real Madrid vs FC Barcelona", "language": "en"},
    {"query": "How many goals did Vinícius Júnior score?", "language": "en"},
    {"query": "Who is the top scorer?", "language": "en"},
    {"query": "Matches in the UEFA Champions League", "language": "en"},
    {"query": "All matches", "language": "en"},
    {"query": "Who assisted Mbappé's goal?", "language": "en"},
    {"query": "Which are the international tournaments?", "language": "en"},
    {"query": "What is the capacity of Santiago Bernabéu?", "language": "en"},
    {"query": "Stadiums in Spain", "language": "en"},
    {"query": "Who are the referees?", "language": "en"},
    {"query": "Show the cards", "language": "en"},
    {"query": "Substitutions made", "language": "en"},
    {"query": "Which player was booked for rough play?", "language": "en"},
    {"query": "What matches were played on 2024-11-25?", "language": "en"},

    # Francés
    {"query": "Qui est Vinícius Júnior ?", "language": "fr"},
    {"query": "À quel poste joue Luka Modric ?", "language": "fr"},
    {"query": "D'où vient Harry Kane ?", "language": "fr"},
    {"query": "Quels joueurs sont brésiliens ?", "language": "fr"},
    {"query": "Qui porte le numéro 7 au Real Madrid ?", "language": "fr"},
    {"query": "Quels sont tous les joueurs ?", "language": "fr"},
    {"query": "Quand est né Jude Bellingham ?", "language": "fr"},
    {"query": "Mbappé est-il titulaire ?", "language": "fr"},
    {"query": "Qui entraîne Liverpool ?", "language": "fr"},
    {"query": "Qui est le capitaine du Real Madrid ?", "language": "fr"},
    {"query": "Quel est le stade du FC Barcelone ?", "language": "fr"},
    {"query": "Quelles équipes existent ?", "language": "fr"},
    {"query": "Quelles équipes viennent d'Allemagne ?", "language": "fr"},
    {"query": "Résultat du Real Madrid contre le FC Barcelone", "language": "fr"},
    {"query": "Combien de buts Vinícius Júnior a-t-il marqués ?", "language": "fr"},
    {"query": "Qui est le meilleur buteur ?", "language": "fr"},
    {"query": "Matchs de l’UEFA Champions League", "language": "fr"},
    {"query": "Tous les matchs", "language": "fr"},
    {"query": "Qui a fait la passe décisive pour Mbappé ?", "language": "fr"},
    {"query": "Quels sont les tournois internationaux ?", "language": "fr"},
    {"query": "Quelle est la capacité du Santiago Bernabéu ?", "language": "fr"},
    {"query": "Stades en Espagne", "language": "fr"},
    {"query": "Quels sont les arbitres ?", "language": "fr"},
    {"query": "Montre les cartons", "language": "fr"},
    {"query": "Remplacements effectués", "language": "fr"},
    {"query": "Quel joueur a été averti pour jeu dangereux ?", "language": "fr"},
    {"query": "Quels matchs ont été joués le 2024-11-25 ?", "language": "fr"},

    # ES - posición + equipo
    {"query": "¿Cuáles son los delanteros del Real Madrid?", "language": "es"},
    {"query": "¿Cuáles son los mediocampistas del FC Barcelona?", "language": "es"},
    {"query": "¿Cuáles son los porteros del Bayern Munchen?", "language": "es"},
    {"query": "¿Cuáles son los defensas del Liverpool FC?", "language": "es"},
    # EN - position + team
    {"query": "Who are the forwards of Real Madrid?", "language": "en"},
    {"query": "Who are the midfielders of FC Barcelona?", "language": "en"},
    {"query": "Who are the goalkeepers of Bayern Munchen?", "language": "en"},
    {"query": "Who are the defenders of Liverpool FC?", "language": "en"},
    # FR - position + équipe
    {"query": "Quels sont les attaquants du Real Madrid?", "language": "fr"},
    {"query": "Quels sont les milieux du FC Barcelona?", "language": "fr"},
    {"query": "Quels sont les gardiens du Bayern Munchen?", "language": "fr"},
    {"query": "Quels sont les défenseurs du Liverpool FC?", "language": "fr"},
]

output_file = "resultados_locales.txt"

with open(output_file, "w", encoding="utf-8") as file:
    file.write("RESULTADOS DE PRUEBAS LOCALES\n")
    file.write("=" * 100 + "\n\n")

    for index, item in enumerate(questions, start=1):
        separator = "=" * 80
        file.write(separator + "\n")
        file.write(f"TEST #{index}\n")
        file.write(separator + "\n")
        file.write(f"Idioma: {item['language']}\n")
        file.write(f"Pregunta: {item['query']}\n\n")

        try:
            res = search_service.execute(item['query'], item['language'])
            # Mimic FastAPI serialization
            data_dict = {
                "query": res.query,
                "intent": res.intent,
                "answer": res.answer,
                "data": res.data,
                "found": res.found
            }
            file.write("Respuesta:\n")
            file.write(json.dumps(data_dict, indent=4, ensure_ascii=False))
            file.write("\n\n")
        except Exception as e:
            file.write(f"Error procesando query: {e}\n\n")

print("Finished running tests locally. Saved in resultados_locales.txt")
