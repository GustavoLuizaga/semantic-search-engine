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

### 👤 Jugador(es) y Personal

| Categoría | Patrones de Pregunta | Ejemplo |
|-----------|-------------------|---------|
| **Información general de un jugador** | "¿Quién es [Nombre del Jugador]?" / "Información de [Jugador]" | "¿Quién es Vinícius Júnior?" / "Información de Kylian Mbappé" |
| **Posición o rol** | "¿De qué juega [Jugador]?" / "¿En qué posición juega [Jugador]?" | "¿De qué juega Luka Modric?" / "¿En qué posición juega Robert Lewandowski?" |
| **Nacionalidad de un jugador** | "¿De dónde es [Jugador]?" / "Nacionalidad de [Jugador]" | "¿De dónde es Harry Kane?" / "Nacionalidad de Gavi" |
| **Jugadores por país** | "¿Cuáles son los jugadores de nacionalidad [Nacionalidad]?" / "Jugadores de [País]" | "¿Cuáles son los jugadores de nacionalidad Brasileña?" / "Jugadores de España" |
| **Jugador por dorsal** | "¿Quién lleva el número [Dorsal] en el [Equipo]?" / "Dorsal [Dorsal] del [Equipo]" | "¿Quién lleva el número 7 en el Real Madrid?" / "Dorsal 10 del Barcelona" |
| **Listar a todos (Jugadores)** | "¿Cuáles son todos los jugadores?" | "¿Cuáles son todos los jugadores?" |
| **✨ NUEVO - Fecha de nacimiento** | "¿Cuándo nació el [Jugador/Entrenador/Árbitro]?" / "Fecha de nacimiento de [Nombre]" | "¿Cuándo nació Jude Bellingham?" / "Fecha de nacimiento de Carlo Ancelotti" |
| **✨ NUEVO - Titularidad** | "¿Es titular [Jugador]?" / "¿Es [Jugador] un jugador titular?" | "¿Es titular Mbappé?" / "¿Es Pedri un jugador titular?" |

### 🛡 Equipos

| Categoría | Patrones de Pregunta | Ejemplo |
|-----------|-------------------|---------|
| **Información general** | "[Equipo]" / "Datos del [Equipo]" | "Real Madrid" / "Datos del Bayern Munich" |
| **Entrenador** | "¿Quién entrena al [Equipo]?" / "Entrenador del [Equipo]" | "¿Quién entrena al Liverpool?" / "Entrenador del FC Barcelona" |
| **Capitán** | "¿Quién es el capitán del [Equipo]?" / "Capitán de [Equipo]" | "¿Quién es el capitán del Real Madrid?" / "Capitán de Bayern Munich" |
| **Estadio local** | "Estadio del [Equipo]?" | "Estadio del FC Barcelona?" |
| **Listar a todos (Equipos)** | "¿Qué equipos hay?" / "Todos los equipos registrados" | "¿Qué equipos hay?" / "Todos los equipos registrados" |
| **✨ NUEVO - Equipos por país** | "¿Cuáles son los equipos de [País]?" / "Equipos de [País]" | "¿Cuáles son los equipos de Alemania?" / "Equipos de Francia" |

### ⚽ Partidos, Goles y Resultados

| Categoría | Patrones de Pregunta | Ejemplo |
|-----------|-------------------|---------|
| **Resultado de un enfrentamiento** | "Resultado del [Equipo A] vs [Equipo B]" / "¿Quién ganó el partido de [Equipo A] contra [Equipo B]?" | "¿Cuál es el resultado entre Real Madrid y FC Barcelona?" / "¿Quién ganó el partido de Bayern vs PSG?" |
| **Goles de un jugador en total** | "¿Cuántos goles marcó [Nombre jugador]?" | "¿Cuántos goles marcó Vinícius Júnior?" |
| **Ranking de goleadores** | "¿Quién es el máximo goleador?" / "Top goleadores" / "¿Quién marcó más?" | "¿Quién es el máximo goleador?" / "Top goleadores" / "¿Quién marcó más?" |
| **Partidos de una liga/competición** | "Partidos de [Competición]" / "Partidos jugados en la [Liga]" | "Partidos jugados en la UEFA Champions LEAGUE" / "Partidos jugados en La Liga" |
| **Listar a todos (Partidos)** | "Todos los partidos" / "Lista de partidos jugados" | "Todos los partidos" / "Lista de partidos jugados" |
| **✨ NUEVO - Asistencias de gol** | "¿Quién le dio la asistencia de gol a [Jugador]?" / "Asistencias de [Jugador]" | "¿Quién le dio la asistencia de gol a Mbappé?" / "¿Quién le dio la asistencia de gol a Vinícius Júnior?" |
| **✨ NUEVO - Tipos de competiciones** | "¿Cuáles son los torneos internacionales?" / "Competiciones internacionales" | "¿Cuáles son los torneos internacionales?" / "Competiciones internacionales" |

### 🏟 Estadios

| Categoría | Patrones de Pregunta | Ejemplo |
|-----------|-------------------|---------|
| **Información general/Capacidad** | "¿Qué capacidad tiene el [Estadio]?" / "Aforo del [Estadio]" | "¿Cuánta capacidad tiene el Santiago Bernabéu?" / "Aforo del Camp Nou" |
| **Búsqueda por país/ciudad** | "Estadios en [País/Ciudad]" / "¿Qué estadios hay en [Lugar]?" | "Estadios en España" / "¿Qué estadios hay en Barcelona?" |

### 🟨 Eventos (Tarjetas, Sustituciones) y Árbitros

| Categoría | Patrones de Pregunta | Ejemplo |
|-----------|-------------------|---------|
| **Árbitros registrados** | "¿Cuáles son los árbitros?" / "Lista de árbitros" | "¿Cuáles son los árbitros?" / "Lista de árbitros" |
| **Tarjetas mostradas** | "Muestra las tarjetas" / "Amonestados" / "Expulsados" | "Muestra las tarjetas" / "Amonestados" / "Expulsados" |
| **Sustituciones (Cambios)** | "Sustituciones realizadas" / "Cambios en los partidos" | "Sustituciones realizadas" / "Cambios en los partidos" |
| **✨ NUEVO - Tarjetas por motivo** | "¿Qué jugador fue amonestado por [Motivo]?" / "Expulsados por [Motivo]" | "¿Qué jugador fue amonestado por Juego brusco?" / "Expulsados por Doble amarilla" |

