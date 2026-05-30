# Buscador Semántico
## 📋 Requisitos Previos

- **Python 3.8+** (para el backend)
- **Node.js 16+** y **npm** (para el frontend)
- **Git** (para control de versiones)

## 📁 Estructura del Proyecto

```
Buscador Semantico/
├── backend/               # API FastAPI
│   ├── main.py           # Punto de entrada
│   ├── requirements.txt   # Dependencias Python
│   ├── test_main.http    # Pruebas HTTP
│   └── src/
│       ├── config/       # Configuración
│       ├── modules/      # Módulos de negocio
│       └── ontology/     # Ontología
│
├── frontend/             # Aplicación React + Vite
│   ├── package.json      # Dependencias Node
│   ├── vite.config.js    # Configuración Vite
│   ├── index.html        # HTML principal
│   └── src/
│       ├── App.jsx       # Componente principal
│       ├── main.jsx      # Entrada de React
│       └── assets/       # Recursos estáticos
│
└── README.md             # Este archivo
```
## 🔍 Flujo Metabuscador
<img width="1440" height="1920" alt="image" src="https://github.com/user-attachments/assets/69d2943d-45dd-4ce9-ab09-649cebef889c" />

## 🚀 Instalación y Ejecución

### Backend (FastAPI)

1. **Navega a la carpeta backend:**
   ```bash
   cd backend
   ```

2. **Crea un entorno virtual:**
   ```bash
   python -m venv venv
   ```

3. **Activa el entorno virtual:**
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Ejecuta el servidor:**
   ```bash
   python main.py
   ```
   
   O con uvicorn directamente:
   ```bash
   uvicorn main:app --reload
   ```

   El servidor estará disponible en: `http://localhost:8000`

   - Documentación interactiva Swagger: `http://localhost:8000/docs`
   - Documentación ReDoc: `http://localhost:8000/redoc`

### Frontend (React + Vite)

1. **Abre otra terminal y navega a la carpeta frontend:**
   ```bash
   cd frontend
   ```

2. **Instala las dependencias:**
   ```bash
   npm install
   ```

3. **Ejecuta el servidor de desarrollo:**
   ```bash
   npm run dev
   ```

   El servidor estará disponible en: `http://localhost:5173`

## 🔧 Scripts Disponibles

### Backend
- `python main.py` - Inicia el servidor
- `pip install -r requirements.txt` - Instala dependencias

### Frontend
- `npm run dev` - Inicia el servidor de desarrollo
- `npm run build` - Crea build de producción
- `npm run preview` - Vista previa del build
- `npm run lint` - Ejecuta linter

## 🧪 Pruebas

### Backend
Para probar los endpoints, puedes usar:
- La documentación interactiva Swagger en `http://localhost:8000/docs`
- El archivo `backend/test_main.http` (si usas REST Client en VS Code)
- Herramientas como Postman o Insomnia

## 📦 Dependencias Principales

### Backend
- FastAPI - Framework web
- Uvicorn - Servidor ASGI
- Ver `backend/requirements.txt` para la lista completa

### Frontend
- React - Librería UI
- Vite - Build tool
- Ver `frontend/package.json` para la lista completa

## 🐛 Troubleshooting

### Backend
- **Puerto 8000 en uso:** Cambia el puerto con `uvicorn main:app --reload --port 8001`
- **ModuleNotFoundError:** Asegúrate de que el venv está activado

### Frontend
- **Puerto 5173 en uso:** Vite usará el siguiente puerto disponible automáticamente
- **node_modules corrupto:** Elimina `node_modules` y `package-lock.json`, luego ejecuta `npm install` nuevamente

## ❓ Preguntas que puede responder la API

La API está diseñada para consultar la ontología y puede responder preguntas en lenguaje natural sobre jugadores, equipos, partidos, estadios, árbitros y eventos.

# 👤 Jugador(es) y Personal

| Categoría                             | Patrones de Pregunta (ES)                                                            | Ejemplo (ES)                                                                   | Patterns (EN)                                                              | Example (EN)                                                                            | Modèles (FR)                                                                  | Exemple (FR)                                                                      |
| ------------------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------ | -------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| **Información general de un jugador** | "¿Quién es [Nombre del Jugador]?" / "Información de [Jugador]"                       | "¿Quién es Vinícius Júnior?" / "Información de Kylian Mbappé"                  | "Who is [Player Name]?" / "Information about [Player]"                     | "Who is Vinícius Júnior?" / "Information about Kylian Mbappé"                           | "Qui est [Nom du Joueur] ?" / "Informations sur [Joueur]"                     | "Qui est Vinícius Júnior ?" / "Informations sur Kylian Mbappé"                    |
| **Posición o rol**                    | "¿De qué juega [Jugador]?" / "¿En qué posición juega [Jugador]?"                     | "¿De qué juega Luka Modric?" / "¿En qué posición juega Robert Lewandowski?"    | "What position does [Player] play?" / "Which position does [Player] play?" | "What position does Luka Modric play?" / "Which position does Robert Lewandowski play?" | "À quel poste joue [Joueur] ?" / "Quelle position occupe [Joueur] ?"          | "À quel poste joue Luka Modric ?" / "Quelle position occupe Robert Lewandowski ?" |
| **Nacionalidad de un jugador**        | "¿De dónde es [Jugador]?" / "Nacionalidad de [Jugador]"                              | "¿De dónde es Harry Kane?" / "Nacionalidad de Gavi"                            | "Where is [Player] from?" / "Nationality of [Player]"                      | "Where is Harry Kane from?" / "Nationality of Gavi"                                     | "D'où vient [Joueur] ?" / "Nationalité de [Joueur]"                           | "D'où vient Harry Kane ?" / "Nationalité de Gavi"                                 |
| **Jugadores por país**                | "¿Cuáles son los jugadores de nacionalidad [Nacionalidad]?" / "Jugadores de [País]"  | "¿Cuáles son los jugadores de nacionalidad Brasileña?" / "Jugadores de España" | "Which players are [Nationality]?" / "Players from [Country]"              | "Which players are Brazilian?" / "Players from Spain"                                   | "Quels joueurs sont [Nationalité] ?" / "Joueurs de [Pays]"                    | "Quels joueurs sont brésiliens ?" / "Joueurs d’Espagne"                           |
| **Jugador por dorsal**                | "¿Quién lleva el número [Dorsal] en el [Equipo]?" / "Dorsal [Dorsal] del [Equipo]"   | "¿Quién lleva el número 7 en el Real Madrid?" / "Dorsal 10 del Barcelona"      | "Who wears number [Number] for [Team]?" / "[Team]'s number [Number]"       | "Who wears number 7 for Real Madrid?" / "Barcelona's number 10"                         | "Qui porte le numéro [Numéro] au [Équipe] ?" / "Numéro [Numéro] du [Équipe]"  | "Qui porte le numéro 7 au Real Madrid ?" / "Numéro 10 du Barcelone"               |
| **Listar a todos (Jugadores)**        | "¿Cuáles son todos los jugadores?"                                                   | "¿Cuáles son todos los jugadores?"                                             | "Who are all the players?"                                                 | "Who are all the players?"                                                              | "Quels sont tous les joueurs ?"                                               | "Quels sont tous les joueurs ?"                                                   |
| **✨ NUEVO - Fecha de nacimiento**     | "¿Cuándo nació el [Jugador/Entrenador/Árbitro]?" / "Fecha de nacimiento de [Nombre]" | "¿Cuándo nació Jude Bellingham?" / "Fecha de nacimiento de Carlo Ancelotti"    | "When was [Player/Coach/Referee] born?" / "Birth date of [Name]"           | "When was Jude Bellingham born?" / "Birth date of Carlo Ancelotti"                      | "Quand est né [Joueur/Entraîneur/Arbitre] ?" / "Date de naissance de [Nom]"   | "Quand est né Jude Bellingham ?" / "Date de naissance de Carlo Ancelotti"         |
| **✨ NUEVO - Titularidad**             | "¿Es titular [Jugador]?" / "¿Es [Jugador] un jugador titular?"                       | "¿Es titular Mbappé?" / "¿Es Pedri un jugador titular?"                        | "Is [Player] a starter?" / "Is [Player] in the starting lineup?"           | "Is Mbappé a starter?" / "Is Pedri in the starting lineup?"                             | "[Joueur] est-il titulaire ?" / "[Joueur] fait-il partie du onze de départ ?" | "Mbappé est-il titulaire ?" / "Pedri fait-il partie du onze de départ ?"          |

# 🛡 Equipos

| Categoría                      | Patrones de Pregunta (ES)                                    | Ejemplo (ES)                                                         | Patterns (EN)                                              | Example (EN)                                                      | Modèles (FR)                                                     | Exemple (FR)                                                           |
| ------------------------------ | ------------------------------------------------------------ | -------------------------------------------------------------------- | ---------------------------------------------------------- | ----------------------------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------- |
| **Información general**        | "[Equipo]" / "Datos del [Equipo]"                            | "Real Madrid" / "Datos del Bayern Munich"                            | "[Team]" / "Information about [Team]"                      | "Real Madrid" / "Information about Bayern Munich"                 | "[Équipe]" / "Informations sur [Équipe]"                         | "Real Madrid" / "Informations sur le Bayern Munich"                    |
| **Entrenador**                 | "¿Quién entrena al [Equipo]?" / "Entrenador del [Equipo]"    | "¿Quién entrena al Liverpool?" / "Entrenador del FC Barcelona"       | "Who coaches [Team]?" / "Coach of [Team]"                  | "Who coaches Liverpool?" / "Coach of FC Barcelona"                | "Qui entraîne [Équipe] ?" / "Entraîneur de [Équipe]"             | "Qui entraîne Liverpool ?" / "Entraîneur du FC Barcelone"              |
| **Capitán**                    | "¿Quién es el capitán del [Equipo]?" / "Capitán de [Equipo]" | "¿Quién es el capitán del Real Madrid?" / "Capitán de Bayern Munich" | "Who is the captain of [Team]?" / "Captain of [Team]"      | "Who is the captain of Real Madrid?" / "Captain of Bayern Munich" | "Qui est le capitaine du [Équipe] ?" / "Capitaine de [Équipe]"   | "Qui est le capitaine du Real Madrid ?" / "Capitaine du Bayern Munich" |
| **Estadio local**              | "Estadio del [Equipo]?"                                      | "Estadio del FC Barcelona?"                                          | "What is [Team]'s stadium?"                                | "What is FC Barcelona's stadium?"                                 | "Quel est le stade du [Équipe] ?"                                | "Quel est le stade du FC Barcelone ?"                                  |
| **Listar a todos (Equipos)**   | "¿Qué equipos hay?" / "Todos los equipos registrados"        | "¿Qué equipos hay?" / "Todos los equipos registrados"                | "Which teams are registered?" / "All registered teams"     | "Which teams are registered?" / "All registered teams"            | "Quelles équipes existent ?" / "Toutes les équipes enregistrées" | "Quelles équipes existent ?" / "Toutes les équipes enregistrées"       |
| **✨ NUEVO - Equipos por país** | "¿Cuáles son los equipos de [País]?" / "Equipos de [País]"   | "¿Cuáles son los equipos de Alemania?" / "Equipos de Francia"        | "Which teams are from [Country]?" / "Teams from [Country]" | "Which teams are from Germany?" / "Teams from France"             | "Quelles équipes viennent de [Pays] ?" / "Équipes de [Pays]"     | "Quelles équipes viennent d'Allemagne ?" / "Équipes de France"         |

# ⚽ Partidos, Goles y Resultados

| Categoría                            | Patrones de Pregunta (ES)                                                                            | Ejemplo (ES)                                                                                             | Patterns (EN)                                                                         | Example (EN)                                                              | Modèles (FR)                                                                                         | Exemple (FR)                                                                         |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| **Resultado de un enfrentamiento**   | "Resultado del [Equipo A] vs [Equipo B]" / "¿Quién ganó el partido de [Equipo A] contra [Equipo B]?" | "¿Cuál es el resultado entre Real Madrid y FC Barcelona?" / "¿Quién ganó el partido de Bayern vs PSG?"   | "Result of [Team A] vs [Team B]" / "Who won the match between [Team A] and [Team B]?" | "Result of Real Madrid vs FC Barcelona" / "Who won Bayern vs PSG?"        | "Résultat du [Équipe A] contre [Équipe B]" / "Qui a gagné le match entre [Équipe A] et [Équipe B] ?" | "Résultat du Real Madrid contre le FC Barcelone" / "Qui a gagné Bayern contre PSG ?" |
| **Goles de un jugador en total**     | "¿Cuántos goles marcó [Nombre jugador]?"                                                             | "¿Cuántos goles marcó Vinícius Júnior?"                                                                  | "How many goals did [Player] score?"                                                  | "How many goals did Vinícius Júnior score?"                               | "Combien de buts [Joueur] a-t-il marqués ?"                                                          | "Combien de buts Vinícius Júnior a-t-il marqués ?"                                   |
| **Ranking de goleadores**            | "¿Quién es el máximo goleador?" / "Top goleadores" / "¿Quién marcó más?"                             | "¿Quién es el máximo goleador?" / "Top goleadores"                                                       | "Who is the top scorer?" / "Top scorers" / "Who scored the most?"                     | "Who is the top scorer?" / "Top scorers"                                  | "Qui est le meilleur buteur ?" / "Meilleurs buteurs" / "Qui a marqué le plus ?"                      | "Qui est le meilleur buteur ?" / "Meilleurs buteurs"                                 |
| **Partidos de una liga/competición** | "Partidos de [Competición]" / "Partidos jugados en la [Liga]"                                        | "Partidos jugados en la UEFA Champions League" / "Partidos jugados en La Liga"                           | "Matches in [Competition]" / "Matches played in [League]"                             | "Matches in the UEFA Champions League" / "Matches played in La Liga"      | "Matchs de [Compétition]" / "Matchs joués en [Ligue]"                                                | "Matchs de l’UEFA Champions League" / "Matchs joués en Liga"                         |
| **Listar a todos (Partidos)**        | "Todos los partidos" / "Lista de partidos jugados"                                                   | "Todos los partidos" / "Lista de partidos jugados"                                                       | "All matches" / "List of played matches"                                              | "All matches" / "List of played matches"                                  | "Tous les matchs" / "Liste des matchs joués"                                                         | "Tous les matchs" / "Liste des matchs joués"                                         |
| **✨ NUEVO - Asistencias de gol**     | "¿Quién le dio la asistencia de gol a [Jugador]?" / "Asistencias de [Jugador]"                       | "¿Quién le dio la asistencia de gol a Mbappé?" / "¿Quién le dio la asistencia de gol a Vinícius Júnior?" | "Who assisted [Player]'s goal?" / "Assists for [Player]"                              | "Who assisted Mbappé's goal?" / "Assists for Vinícius Júnior"             | "Qui a fait la passe décisive pour [Joueur] ?" / "Passes décisives de [Joueur]"                      | "Qui a fait la passe décisive pour Mbappé ?" / "Passes décisives de Vinícius Júnior" |
| **✨ NUEVO - Tipos de competiciones** | "¿Cuáles son los torneos internacionales?" / "Competiciones internacionales"                         | "¿Cuáles son los torneos internacionales?" / "Competiciones internacionales"                             | "Which are the international tournaments?" / "International competitions"             | "Which are the international tournaments?" / "International competitions" | "Quels sont les tournois internationaux ?" / "Compétitions internationales"                          | "Quels sont les tournois internationaux ?" / "Compétitions internationales"          |

# 🏟 Estadios

| Categoría                         | Patrones de Pregunta (ES)                                     | Ejemplo (ES)                                                           | Patterns (EN)                                                   | Example (EN)                                                          | Modèles (FR)                                                  | Exemple (FR)                                                             |
| --------------------------------- | ------------------------------------------------------------- | ---------------------------------------------------------------------- | --------------------------------------------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------ |
| **Información general/Capacidad** | "¿Qué capacidad tiene el [Estadio]?" / "Aforo del [Estadio]"  | "¿Cuánta capacidad tiene el Santiago Bernabéu?" / "Aforo del Camp Nou" | "What is the capacity of [Stadium]?" / "Capacity of [Stadium]"  | "What is the capacity of Santiago Bernabéu?" / "Capacity of Camp Nou" | "Quelle est la capacité du [Stade] ?" / "Capacité du [Stade]" | "Quelle est la capacité du Santiago Bernabéu ?" / "Capacité du Camp Nou" |
| **Búsqueda por país/ciudad**      | "Estadios en [País/Ciudad]" / "¿Qué estadios hay en [Lugar]?" | "Estadios en España" / "¿Qué estadios hay en Barcelona?"               | "Stadiums in [Country/City]" / "Which stadiums are in [Place]?" | "Stadiums in Spain" / "Which stadiums are in Barcelona?"              | "Stades en [Pays/Ville]" / "Quels stades y a-t-il à [Lieu] ?" | "Stades en Espagne" / "Quels stades y a-t-il à Barcelone ?"              |

# 🟨 Eventos (Tarjetas, Sustituciones) y Árbitros

| Categoría                         | Patrones de Pregunta (ES)                                               | Ejemplo (ES)                                                                      | Patterns (EN)                                                     | Example (EN)                                                                    | Modèles (FR)                                                        | Exemple (FR)                                                                           |
| --------------------------------- | ----------------------------------------------------------------------- | --------------------------------------------------------------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| **Árbitros registrados**          | "¿Cuáles son los árbitros?" / "Lista de árbitros"                       | "¿Cuáles son los árbitros?" / "Lista de árbitros"                                 | "Who are the referees?" / "List of referees"                      | "Who are the referees?" / "List of referees"                                    | "Quels sont les arbitres ?" / "Liste des arbitres"                  | "Quels sont les arbitres ?" / "Liste des arbitres"                                     |
| **Tarjetas mostradas**            | "Muestra las tarjetas" / "Amonestados" / "Expulsados"                   | "Muestra las tarjetas" / "Amonestados" / "Expulsados"                             | "Show the cards" / "Booked players" / "Sent off players"          | "Show the cards" / "Booked players"                                             | "Montre les cartons" / "Joueurs avertis" / "Joueurs expulsés"       | "Montre les cartons" / "Joueurs avertis"                                               |
| **Sustituciones (Cambios)**       | "Sustituciones realizadas" / "Cambios en los partidos"                  | "Sustituciones realizadas" / "Cambios en los partidos"                            | "Substitutions made" / "Match substitutions"                      | "Substitutions made" / "Match substitutions"                                    | "Remplacements effectués" / "Changements pendant les matchs"        | "Remplacements effectués" / "Changements pendant les matchs"                           |
| **✨ NUEVO - Tarjetas por motivo** | "¿Qué jugador fue amonestado por [Motivo]?" / "Expulsados por [Motivo]" | "¿Qué jugador fue amonestado por Juego brusco?" / "Expulsados por Doble amarilla" | "Which player was booked for [Reason]?" / "Sent off for [Reason]" | "Which player was booked for rough play?" / "Sent off for a second yellow card" | "Quel joueur a été averti pour [Motif] ?" / "Expulsés pour [Motif]" | "Quel joueur a été averti pour jeu dangereux ?" / "Expulsés pour double avertissement" |

## 📚 Preguntas atendidas por DBpedia

| Categoría | Patrones de Pregunta | Ejemplo |
|-----------|---------------------|---------|
| **Jugadores** | "¿Quién es [Jugador]?" / "Información de [Jugador]" <br> "¿Cuándo nació [Jugador]?" / "Fecha de nacimiento de [Jugador]" <br> "¿En qué posición juega [Jugador]?" / "¿Qué dorsal usa [Jugador]?" | "¿Quién es Kylian Mbappé?" / "¿Cuándo nació Jude Bellingham?" |
| **Equipos** | "[Equipo]" / "Datos del [Equipo]" <br> "¿Quién entrena al [Equipo]?" / "¿Cuándo se fundó [Equipo]?" <br> "¿Cuál es el estadio del [Equipo]?" | "Real Madrid" / "¿Quién entrena al Liverpool?" |
| **Estadios** | "Información del [Estadio]" / "¿Qué capacidad tiene el [Estadio]?" <br> "Estadio del [Equipo]" / "¿Dónde juega el [Equipo]?" / "Estadios en [Ciudad/País]" | "Información del Camp Nou" / "Estadios en Barcelona" / "Estadio del Real Madrid" |
| **Equipos por ubicación** | "¿Qué equipos hay en [País]?" / "Equipos de [País]" | "¿Cuáles son los equipos de Brasil?" |
| **Consulta general (fallback)** | Búsqueda por etiqueta/abstract cuando no encaja en intents específicos — devuelve descripción/abstract de DBpedia | También soporta búsquedas de listados como  "Lista de estadios" |

Nota: DBpedia no es una fuente de resultados de partidos (goles, marcadores, listados exhaustivos de partidos ni estadísticas temporales). Para consultas sobre resultados de partidos, sustituciones, tarjetas o rankings por competencia, el sistema recomienda usar la ontología local incluida en el proyecto.

