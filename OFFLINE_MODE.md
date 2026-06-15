## Modo Offline (Base de Datos Local con Apache Fuseki)

Este modo permite ejecutar la aplicación utilizando un servidor de base de datos de grafos local (Apache Jena Fuseki) en lugar de consultar directamente a DBpedia en la web. Es ideal para entornos de desarrollo, demostraciones sin conexión a internet o para utilizar un dataset especializado.

### Paso 1: Generar la Ontología (Dataset)

Antes de levantar la base de datos, necesitamos generar el archivo de datos con la información de fútbol.

1. Abre tu terminal en la src/utils del proyecto.
2. Ejecuta el script generador:

```bash
python generator.py
```

Verifica que se haya creado el archivo `dbpedia_futbol_offline.ttl` en tu directorio.

---

### Paso 2: Descargar e Instalar Apache Fuseki

1. Ve a la página oficial de descargas de Apache Jena:

   https://jena.apache.org/download/index.cgi

2. Descarga la versión de Apache Jena Fuseki (generalmente un archivo `.zip` o `.tar.gz`).

3. Descomprime el archivo en la carpeta de tu preferencia.

---

### Paso 3: Iniciar el Servidor Fuseki con el Dataset

Debemos iniciar el servidor creando automáticamente el dataset llamado `/futbol`.

1. Abre una terminal dentro de la carpeta donde descomprimiste Fuseki.

2. Ejecuta el siguiente comando según tu sistema operativo:

#### Windows

```bash
./fuseki-server --update --mem /futbol
```

#### Linux / macOS

```bash
./fuseki-server --update --mem /futbol
```

Una vez iniciado correctamente, Fuseki estará disponible en:

```
http://localhost:3030
```

---

### Paso 4: Cargar los Datos en Fuseki

1. Abre tu navegador y accede a:

```
http://localhost:3030
```

2. Ve a la pestaña **Manage datasets**.
3. Verás que el dataset `/futbol` ya existe.
4. Haz clic en **Add Data**.
5. Selecciona el archivo `dbpedia_futbol_offline.ttl` generado en el Paso 1.
6. Haz clic en **Upload Now**.

Cuando finalice la carga, Fuseki estará listo para responder consultas SPARQL.

---

### Paso 5: Configurar el Entorno del Backend

Asegúrate de indicar al backend que debe utilizar el modo offline.

1. En la carpeta del backend, abre o crea el archivo `.env`.
2. Configura las siguientes variables:

```env
FUSEKI_ENDPOINT="http://localhost:3030/futbol/sparql"
DBPEDIA_MODE="offline"
```

---

### Paso 6: Iniciar la Aplicación

Con la base de datos local funcionando y configurada, ya puedes iniciar el sistema normalmente.

#### Backend (FastAPI)

Sigue las instrucciones principales del proyecto para activar tu entorno virtual y ejecutar:

```bash
uvicorn main:app --reload
```

#### Frontend (React)

Asegúrate de que el frontend apunte a tu backend local y ejecuta:

```bash
npm install
npm run dev
```

---

### Verificación Rápida

Si todo está configurado correctamente:

- Apache Fuseki estará ejecutándose en `http://localhost:3030`
- El dataset `/futbol` contendrá los datos cargados desde `dbpedia_futbol_offline.ttl`
- El backend utilizará Fuseki mediante la variable `DBPEDIA_MODE="offline"`
- Las consultas SPARQL se resolverán localmente sin depender de DBpedia en Internet
