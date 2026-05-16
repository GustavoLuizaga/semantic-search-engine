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

## 📝 Variables de Entorno

Crea un archivo `.env` en la carpeta `backend/` con las siguientes variables (según necesites):

```env
DATABASE_URL=your_database_url
DEBUG=True
```

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

## 🔗 Conexión Frontend-Backend

Para conectar el frontend con el backend, asegúrate de:

1. El backend esté ejecutándose en `http://localhost:8000`
2. Configurar CORS en FastAPI si es necesario
3. Usar la URL correcta en las peticiones fetch/axios desde React

Ejemplo en React:
```javascript
fetch('http://localhost:8000/api/endpoint')
  .then(response => response.json())
  .then(data => console.log(data))
```

## 🐛 Troubleshooting

### Backend
- **Puerto 8000 en uso:** Cambia el puerto con `uvicorn main:app --reload --port 8001`
- **ModuleNotFoundError:** Asegúrate de que el venv está activado

### Frontend
- **Puerto 5173 en uso:** Vite usará el siguiente puerto disponible automáticamente
- **node_modules corrupto:** Elimina `node_modules` y `package-lock.json`, luego ejecuta `npm install` nuevamente

## ❓ Preguntas que puede responder la API

La API está diseñada para consultar la ontología y puede responder preguntas en lenguaje natural sobre jugadores, equipos, partidos, estadios, árbitros y eventos. Ejemplos de consultas soportadas:

- Jugador(es):
   - Información general: "¿Quién es [Nombre del Jugador]?" / "Información de [Jugador]"
   - Posición o rol: "¿De qué juega [Jugador]?" / "¿En qué posición juega [Jugador]?"
   - Nacionalidad: "¿De dónde es [Jugador]?" / "Nacionalidad de [Jugador]"
   - Jugadores por país: "¿Cuáles son los jugadores de nacionalidad [Nacionalidad]?" / "Jugadores de [País]"
   - Jugador por dorsal: "¿Quién lleva el número [Dorsal] en el [Equipo]?" / "Dorsal [Dorsal] del [Equipo]"
   - Listar a todos: "¿Cuáles son todos los jugadores?"

- Equipos y Personal:
   - Información general: "[Equipo]" / "Datos del [Equipo]"
   - Entrenador: "¿Quién entrena al [Equipo]?" / "Entrenador del [Equipo]"
   - Capitán: "¿Quién es el capitán del [Equipo]?" / "Capitán de [Equipo]"
   - Estadio local: "Estadio del [Equipo]?"
   - Listar a todos: "¿Qué equipos hay?" / "Todos los equipos registrados"

- Partidos, Goles y Resultados:
   - Resultado de un enfrentamiento: "Resultado del [Equipo A] vs [Equipo B]" / "¿Quién ganó el partido de [Equipo A] contra [Equipo B]?"
   - Goles de un jugador en total: "¿Cuántos goles marcó [Nombre jugador]?"
   - Ranking de goleadores: "¿Quién es el máximo goleador?" / "Top goleadores" / "¿Quién marcó más?"
   - Partidos de una liga/competición: "Partidos de [Competición]" / "Partidos jugados en la [Liga]"
   - Listar a todos: "Todos los partidos" / "Lista de partidos jugados"

- Estadios:
   - Información general/Capacidad: "¿Qué capacidad tiene el [Estadio]?" / "Aforo del [Estadio]"
   - Búsqueda por país/ciudad: "Estadios en [País/Ciudad]" / "¿Qué estadios hay en [Lugar]?"

- Eventos (Tarjetas, Sustituciones) y Árbitros:
   - Árbitros registrados: "¿Cuáles son los árbitros?" / "Lista de árbitros"
   - Tarjetas mostradas: "Muestra las tarjetas" / "Amonestados" / "Expulsados"
   - Sustituciones (Cambios): "Sustituciones realizadas" / "Cambios en los partidos"

Algunos ejemplos de preguntas que puedes hacer a la API:

- "¿Cuál es el resultado entre Real Madrid y FC Barcelona?"
- "resultado Real Madrid vs Barça"
- "¿Quién ganó el partido de Bayern vs PSG?"
- "¿Quiénes son los jugadores del Real Madrid?"
- "Dime la plantilla del FC Barcelona"
- "¿Cuántos goles marcó Vinícius Júnior?"
- "¿Quién es Kylian Mbappé?"
- "Dame información del estadio Santiago Bernabéu"
- "¿Qué árbitros hay en la ontología?"
- "¿Quién recibió tarjeta roja?"
- "¿Hubo sustituciones?"
- "¿Quién es el máximo goleador?"
- "¿En qué competición jugó Real Madrid vs Barcelona?"
- "resultado PSG vs Real Madrid"
- "¿Qué equipos hay en la ontología?"
- "¿Cuánta capacidad tiene el Camp Nou?"
- "¿Quién entrena al Liverpool?"
- "Lista todos los partidos"

