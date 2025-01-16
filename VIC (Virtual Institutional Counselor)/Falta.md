
---

## **Estado del Proyecto Completo**

### **Backend**
Ya se han implementado.

- **Chatbot**:
  - **Modelo** (`myApp/models/chatbot_model.py`):
    - Consulta de embeddings relevantes desde la base de datos.
    - Registro de interacciones usuario-chatbot.
    - Generación de respuestas utilizando el modelo Ollama.
  - **Controlador** (`myApp/controllers/chatbot_controller.py`):
    - Conexión entre vistas y modelo.
    - Lógica para obtener respuestas del modelo Ollama.
  - **Vistas** (`myApp/views/chatbot_views.py`):
    - Endpoints REST para interactuar con el chatbot.
    - Endpoint principal: `POST /chatbot`.

- **Autenticación**:
  - **Modelo** (`myApp/models/auth_model.py`):
    - Registro de usuarios en la base de datos.
    - Verificación de credenciales de usuarios.
    - Validación de tokens JWT.
  - **Controlador** (`myApp/controllers/auth_controller.py`):
    - Hashing y verificación de contraseñas.
    - Generación y validación de tokens JWT.
  - **Vistas** (`myApp/views/auth_views.py`):
    - Registro de usuarios (`POST /auth/register`).
    - Autenticación y generación de tokens (`POST /auth/login`).
    - Validación de tokens para rutas protegidas (`GET /auth/protected`).

- **ETL**:
  - **Archivo**: `ETL/load.py`.
    - Creación de tablas para el chatbot y la autenticación:
      - `knowledge_base`, `chat_logs`, `questions`, `users`.
    - Manejo del esquema `pgvector` para trabajar con embeddings.
    - Funciones para cargar datos y resetear secuencias.

---

### **Lo que falta por hacer**

#### **Chatbot**
1. **Procesamiento de syllabuses**:
   - Leer los PDFs de `syllabuses/`.
   - Dividir los documentos en "chunks".
   - Generar embeddings y almacenarlos en las tablas `knowledge_base` y `syllabus`.

2. **Opcionales**:
   - Implementar memoria para que el chatbot utilice contextos previos en sus respuestas.

#### **Estadísticas**
1. **Proteger rutas**:
   - Validar JWT en todos los endpoints de estadísticas (`localStatistics` y `globalStatistics`).
   - Retornar `401 Unauthorized` si el token es inválido o ausente.
   - **Rutas existentes a ajustar**:
     - `myApp/views/globalStatistics_views.py`.
     - `myApp/views/localStatistics_views.py`.

2. **Pruebas**:
   - Validar endpoints de estadísticas protegidas con Postman:
     - Probar solicitudes con token válido e inválido.
     - Verificar el manejo de errores.

---

#### **Frontend**
1. **Streamlit App**:
   - Crear una interfaz de usuario para:
     - Login y autenticación con JWT.
     - Visualización de estadísticas.
     - Interacción con el chatbot.
   - **Gráficos**:
     - Usar **Plotly** o **Matplotlib** para mostrar estadísticas locales y globales.
   - **Chatbot**:
     - Crear un formulario para enviar preguntas y mostrar respuestas.

---

## **Estructura de Archivos**

### **Chatbot**

1. **`myApp/models/chatbot_model.py`**:
   - **Responsabilidad**:
     - Interactuar directamente con la base de datos para las operaciones relacionadas al chatbot.
   - **Funcionalidades principales**:
     - **`fetch_relevant_embeddings`**: Busca embeddings relevantes en la base de datos, ordenados por similitud.
     - **`log_chat_interaction`**: Registra las preguntas del usuario y las respuestas generadas en la tabla `chat_logs`.
     - **`query_ollama`**: Se comunica con la API de Ollama para generar respuestas basadas en un contexto.
     - **`get_answer_from_ollama`**: Orquesta todo el flujo: busca embeddings relevantes, consulta a Ollama y registra la interacción.

2. **`myApp/controllers/chatbot_controller.py`**:
   - **Responsabilidad**:
     - Actuar como intermediario entre el modelo y las vistas.
   - **Funcionalidades principales**:
     - **`process_question`**: Recibe una pregunta desde las vistas, llama al modelo para obtener una respuesta.

3. **`myApp/views/chatbot_views.py`**:
   - **Responsabilidad**:
     - Proveer endpoints REST para que el cliente interactúe con el chatbot.
   - **Endpoints principales**:
     - **`POST /chatbot`**: Recibe preguntas, valida la estructura y retorna respuestas.

### **Autenticación (Auth)**

1. **`myApp/models/auth_model.py`**:
   - **Responsabilidad**:
     - Manejar operaciones relacionadas con usuarios en la base de datos.
   - **Funcionalidades principales**:
     - **`register_user`**: Registra nuevos usuarios con contraseña hash.
     - **`get_user_by_username`**: Búsqueda por nombre de usuario.
     - **`get_user_by_id`**: Búsqueda por ID.

2. **`myApp/controllers/auth_controller.py`**:
   - **Responsabilidad**:
     - Implementar lógica de autenticación y manejo de tokens JWT.
   - **Funcionalidades principales**:
     - **`register_user`**: Valida entrada y registra usuarios.
     - **`authenticate_user`**: Verifica credenciales y genera tokens JWT.
     - **`validate_token`**: Valida tokens JWT.

3. **`myApp/views/auth_views.py`**:
   - **Responsabilidad**:
     - Proveer endpoints REST para autenticación.
   - **Endpoints principales**:
     - **`POST /auth/register`**: Registro de usuarios.
     - **`POST /auth/login`**: Autenticación y generación de tokens.
     - **`GET /auth/protected`**: Ejemplo de ruta protegida.

### **Relación entre los archivos**

1. **Chatbot**:
   - Las vistas reciben preguntas del cliente.
   - El controlador orquesta el flujo.
   - El modelo accede a la base de datos y API de Ollama.

2. **Autenticación**:
   - Las vistas manejan solicitudes de registro y login.
   - El controlador realiza hashing y manejo de tokens.
   - El modelo interactúa con la base de datos de usuarios.

