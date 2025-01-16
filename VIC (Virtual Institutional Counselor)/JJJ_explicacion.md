## Project Structure and Overview: `rumad-v2-app-no-pensamos-repetir-npr`

### 1. **Configuración de Entorno: `.env.development` y `.env.production`**

Estos archivos de configuración contienen las variables de entorno necesarias para la conexión a la base de datos y otras configuraciones específicas para cada entorno (desarrollo y producción).

- **DATABASE_URL**: URL de conexión de la base de datos en el entorno adecuado (por ejemplo, una URL de base de datos local en `.env.development` y la URL de Heroku en `.env.production`).
- **FLASK_ENV**: Especifica el entorno de Flask (`development` o `production`).
- **SECRET_KEY**: Llave secreta para operaciones de seguridad en Flask.

### 2. **Configuración de Flask: `app.py`**

Este archivo configura la aplicación Flask, establece la conexión a la base de datos y registra los blueprints para cada entidad. **app.py** toma su configuración inicial de los archivos `.env`, seleccionando entre `development` o `production` según la elección del usuario.

#### Funcionamiento de `app.py`:

- **Selección de base de datos**: Pregunta al usuario si desea conectar a la base de datos local o de Heroku.
- **Inicialización de la aplicación**: Configura la conexión y registra los blueprints necesarios para el proyecto:
  - `class_blueprint`: Define las operaciones CRUD específicas para la entidad `Class`.
  - `statistics_bp`: Define las rutas de estadísticas locales.

#### Blueprints en `app.py`:

- **`class_blueprint`**: Gestiona las operaciones CRUD para la entidad `Class`.
- **`statistics_bp`**: Define las rutas para estadísticas específicas, como capacidad de aula y clases más enseñadas.

#### Ejecución de la aplicación:

Para ejecutar la aplicación, utiliza el siguiente comando en la terminal:

```sh
python -m myApp.app
```

### Ruta de prueba básica:

- **GET** `/`: Verifica si la aplicación está en funcionamiento.
  - **Postman**:
    - **Método**: GET
    - **URL**: `http://localhost:5000/`
    - **Respuesta esperada (JSON)**:
      ```json
      {
          "message": "Welcome to the App API!",
          "environment": "development"
      }
      ```
---

### 3. **Controladores: `/controllers/`**

La carpeta `controllers` contiene archivos que definen la lógica de control para cada entidad. Estos archivos son responsables de recibir las solicitudes HTTP, interactuar con el modelo y retornar las respuestas formateadas usando las vistas.

#### Archivos en `controllers/`:

- **`class_controller.py`**: Controlador para la entidad `Class`.
  - Define las rutas CRUD para crear, leer, actualizar y eliminar clases.
  - Ejemplo de rutas:
    - **POST** `/class`: Crear una nueva clase.
      - **Postman**:
        - Método: POST
        - URL: `http://localhost:5000/class`
        - Body (JSON):
          ```json
          {
              "ccode": "4151",
              "cdesc": "Software Engineering Project I",
              "cname": "TEST",
              "cred": 3,
              "csyllabus": "https://www.uprm.edu/cse/wp-content/uploads/sites/153/2020/03/INSO-4151-Software-Engineering-Project-I.pdf",
              "term": "First Semester"
          }
          ```

    - **GET** `/api/class`: Obtener todas las clases.
      - **Postman**:
        - Método: GET
        - URL: `http://localhost:5000/class`
    - **GET** `/api/class/<id>`: Obtener una clase específica por ID.
      - **Postman**:
        - Método: GET
        - URL: `http://localhost:5000/class/1` (Reemplaza `1` con el ID de la clase que deseas obtener)
    - **PUT** `/api/class/<id>`: Actualizar una clase específica por ID.
      - **Postman**:
        - Método: PUT
        - URL: `http://localhost:5000/class/1` (Reemplaza `1` con el ID de la clase que deseas actualizar)
        - Body (JSON):
          ```json
          {
              "ccode": "4151",
              "cdesc": "Software Engineering Project I",
              "cname": "Test1",
              "cred": 10,
              "csyllabus": "https://www.uprm.edu/cse/wp-content/uploads/sites/153/2020/03/INSO-4151-Software-Engineering-Project-I.pdf",
              "term": "First Semester"
          }
          ```
    - **DELETE** `/api/class/<id>`: Eliminar una clase específica por ID.
      - **Postman**:
        - Método: DELETE
        - URL: `http://localhost:5000/class/1` (Reemplaza `1` con el ID de la clase que deseas eliminar)
  - **Funciones**:
    - `add_class()`: Crea una nueva clase.
    - `list_classes()`: Obtiene todas las clases.
    - `get_class(id)`: Obtiene una clase específica por ID.
    - `modify_class(id)`: Actualiza una clase específica por ID.
    - `remove_class(id)`: Elimina una clase específica por ID.

- **`localStatistics_controller.py`**: Controlador para estadísticas locales.
  - Define las rutas para obtener estadísticas como capacidad de aulas, ratios de capacidad de estudiantes y clases más enseñadas.
  - Ejemplo de rutas:
    - **GET** `/api/room/<id>/capacity`: Obtener las 3 aulas con mayor capacidad.
      - **Postman**:
        - Método: GET
        - URL: `http://localhost:5000/room/1/capacity` (Reemplaza `1` con el ID del edificio)
    - **GET** `/api/room/<id>/ratio`: Obtener las 3 secciones con el mayor ratio estudiantes/capacidad.
      - **Postman**:
        - Método: GET
        - URL: `http://localhost:5000/room/1/ratio` (Reemplaza `1` con el ID del aula)
    - **GET** `/api/room/<id>/classes`: Obtener las 3 clases más enseñadas en el aula específica.
      - **Postman**:
        - Método: GET
        - URL: `http://localhost:5000/room/1/classes` (Reemplaza `1` con el ID del aula)
    - **GET** `/api/classes/<year>/<semester>`: Obtener las 3 clases más enseñadas por semestre y año.
      - **Postman**:
        - Método: GET
        - URL: `http://localhost:5000/classes/2023/Fall` (Reemplaza `2023` y `Fall` con el año y semestre deseados)
  - **Funciones**:
    - `room_capacity(id)`: Obtiene las 3 aulas con mayor capacidad para un edificio dado.
    - `room_ratio(id)`: Obtiene las 3 secciones con el mayor ratio estudiantes/capacidad para un aula dada.
    - `room_classes(id)`: Obtiene las 3 clases más enseñadas para un edificio y aula dados.
    - `classes_by_semester(year, semester)`: Obtiene las 3 clases más enseñadas para un semestre y año dados.
---

### 4. **Modelos: `/models/`**

La carpeta `models` contiene los archivos que interactúan con la base de datos. Cada archivo en esta carpeta representa una entidad y contiene funciones para ejecutar las consultas necesarias en la base de datos.

#### Archivos en `models/`:

- **`class_model.py`**: Modelo para la entidad `Class`.
  - Proporciona funciones para crear, leer, actualizar y eliminar clases.
  - **Funciones**:
    - `create_class(data)`: Inserta una nueva clase en la base de datos.
    - `get_all_classes()`: Obtiene todas las clases de la base de datos.
    - `get_class_by_id(class_id)`: Obtiene una clase específica usando su ID.
    - `update_class(class_id, data)`: Actualiza una clase específica usando su ID.
    - `delete_class(class_id)`: Elimina una clase específica usando su ID.

- **`localStatistics_model.py`**: Modelo para estadísticas locales.
  - Define funciones para realizar consultas sobre estadísticas, como capacidad de aulas y clases enseñadas.
  - **Funciones**:
    - `get_top_rooms_by_capacity(building_id)`: Obtiene las aulas con mayor capacidad en un edificio específico.
    - `get_top_sections_by_ratio(building_id)`: Obtiene las secciones con el mayor ratio estudiantes/capacidad en un edificio específico.
    - `get_top_classes_per_room(building_id)`: Obtiene las clases más enseñadas en cada aula de un edificio.
    - `get_top_classes_per_semester(year, semester)`: Obtiene las clases más enseñadas por semestre y año.

- **`error_handler.py`**: Contiene un decorador `handle_errors` que maneja y reporta errores en las funciones del modelo.
  - **Funciones**:
    - `handle_errors(f)`: Decorador para manejar errores de manera consistente en las rutas de Flask.
    - `decorated_function(*args, **kwargs)`: Función decorada que maneja los errores y retorna una respuesta JSON apropiada.

---

### 5. **Vistas: `/views/`**

La carpeta `views` contiene archivos que formatean las respuestas JSON y errores para cada controlador. Las funciones en esta carpeta devuelven las respuestas en un formato JSON uniforme.

#### Archivos en `views/`:

- **`class_view.py`**: Vista para la entidad `Class`.
  - Proporciona funciones de respuesta que formatean el resultado de las operaciones CRUD para `Class`.
  - **Funciones**:
    - `format_class_response(data)`: Devuelve una respuesta JSON exitosa con los datos de `Class`.
    - `format_class_error(message, status_code)`: Devuelve una respuesta JSON con un mensaje de error y código de estado.

---

### 6. **Configuración de Base de Datos: `/config/`**

La carpeta `config` define la configuración de la base de datos y selecciona el entorno correcto en base al archivo `.env` especificado.

#### Archivos en `config/`:

- **`heroku_config.py`**: Configuración de la base de datos para producción (Heroku).
  - **Funciones**:
    - `get_db_connection()`: Establece una conexión con la base de datos de Heroku utilizando las credenciales de las variables de entorno.
  - **Descripción**:
    - Carga las variables de entorno desde `.env.production` si el entorno es de producción, de lo contrario, carga desde `.env.development`.
    - Intenta conectar a la base de datos utilizando la URL proporcionada en las variables de entorno y maneja cualquier error de conexión.

- **`local_config.py`**: Configuración de la base de datos para desarrollo (local).
  - **Funciones**:
    - `get_db_connection()`: Establece una conexión con la base de datos local utilizando las credenciales de las variables de entorno.
  - **Descripción**:
    - Carga las variables de entorno desde `.env.development`.
    - Intenta conectar a la base de datos utilizando la URL proporcionada en las variables de entorno y maneja cualquier error de conexión.

Ambos archivos obtienen las credenciales de conexión desde las variables de entorno definidas en `.env.development` o `.env.production`.

### 7. **Extract, Transform, Load (ETL): `/ETL/`**

La carpeta `ETL` contiene scripts para el procesamiento de datos. Estos archivos realizan la extracción, transformación y carga de datos en la base de datos, de acuerdo con las especificaciones del proyecto.

#### Archivos en `ETL/`:

- **`createTables.sql`**: Script SQL para crear las tablas necesarias en la base de datos.
- **`etl_to_db.py`**: Script que automatiza la carga de datos en la base de datos.
  - **Funciones**:
    - `ask_database_choice()`: Pregunta al usuario qué base de datos desea usar (local o Heroku).
    - `ensure_directories_exist(*directories)`: Asegura que los directorios necesarios existan, y si no, los crea.
    - `main()`: Ejecuta el proceso ETL completo: extracción, transformación y carga de datos.
- **`extract.py`**: Extrae datos de archivos CSV, JSON, y XML.
  - **Funciones**:
    - `extract_csv(file_name)`: Extrae datos de un archivo CSV y elimina registros incompletos.
    - `extract_json(file_name)`: Extrae datos de un archivo JSON y aplana estructuras anidadas.
    - `extract_db(file_name)`: Extrae datos de una base de datos SQLite y elimina registros incompletos.
    - `extract_xml(file_name)`: Extrae datos de un archivo XML y elimina registros incompletos.
    - `extract_all()`: Extrae datos de todas las fuentes (CSV, JSON, SQLite, XML) y devuelve DataFrames.
- **`transform.py`**: Aplica transformaciones necesarias en los datos extraídos.
  - **Funciones**:
    - `clean_courses()`: Asegura que los IDs de los cursos comiencen desde 2 e incluye el registro dummy (cid=37).
    - `clean_requisites()`: Elimina referencias al curso dummy (cid=37) en los requisitos.
    - `resolve_section_conflicts()`: Resuelve conflictos donde las secciones se superponen en la misma sala o curso.
    - `filter_meetings()`: Filtra reuniones inválidas y ajusta aquellas que exceden los rangos de tiempo válidos.
    - `validate_meeting_durations()`: Asegura que las reuniones 'LMV' duren 50 minutos y las 'MJ' duren 75 minutos.
    - `check_overcapacity()`: Asegura que las secciones no excedan la capacidad de la sala.
    - `validate_sections()`: Valida las secciones basadas en datos de clase, reunión y sala.
    - `adjust_timestamps()`: Ajusta las marcas de tiempo para las reuniones basadas en el año y semestre.
    - `download_syllabus(course_info)`: Descarga un archivo de syllabus.
    - `parallel_download_syllabi()`: Descarga todos los syllabi en paralelo.
    - `transform_all()`: Ejecuta todas las transformaciones en los datos.
- **`load.py`**: Carga los datos transformados en la base de datos.
  - **Funciones**:
    - `create_tables()`: Crea las tablas necesarias para el proyecto con secuencias adecuadas.
    - `load_all(courses_df, meetings_df, requisites_df, rooms_df, sections_df)`: Carga datos desde DataFrames en las tablas de PostgreSQL con validación.
    - `_load_classes(courses_df, cur)`: Carga datos de clases con barra de progreso.
    - `_load_rooms(rooms_df, cur)`: Carga datos de salas con barra de progreso.
    - `_load_meetings(meetings_df, cur)`: Carga datos de reuniones y almacena el mapeo de IDs de reuniones.
    - `_load_requisites(requisites_df, cur)`: Carga datos de requisitos con barra de progreso.
    - `_load_sections(sections_df, cur)`: Carga secciones con IDs de reuniones mapeados.
    - `clean_duplicate_sections()`: Elimina secciones duplicadas basadas en especificaciones.
    - `reset_sequences()`: Restablece todas las secuencias a valores adecuados después de cargar los datos.
