# Capstone - Grupo 5

Estructura inicial base para el proyecto Capstone.

## 📁 Estructura del Proyecto

```text
CAPSTONE-GRUPO-5/
├── backend/
│   ├── main.py            # API FastAPI mínima con endpoint /health
│   ├── requirements.txt   # Dependencias de Python (FastAPI, Uvicorn)
│   └── .env.example       # Variables de entorno del backend
├── frontend/
│   ├── src/               # Código fuente React (App.jsx, main.jsx, index.css)
│   ├── index.html         # Documento HTML principal
│   ├── package.json       # Dependencias y scripts de Node.js
│   ├── vite.config.js     # Configuración de Vite
│   └── .env.example       # Variables de entorno del frontend
├── .gitignore             # Ignora venv, node_modules, .env, etc.
├── .env.example           # Variables de entorno globales
└── README.md              # Documentación del proyecto
```

---

## 🚀 Cómo Probar el Backend

1. Abre una terminal y navega a la carpeta `backend`:
   ```bash
   cd backend
   ```

2. Crea y activa el entorno virtual de Python:
   * **Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   * **Linux/macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Inicia el servidor FastAPI:
   ```bash
   uvicorn main:app --reload
   ```

5. Verifica el funcionamiento abriendo en tu navegador o haciendo petición a:
   * Endpoint de salud: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
   * Documentación interactiva Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 💻 Cómo Probar el Frontend

1. Abre una terminal y navega a la carpeta `frontend`:
   ```bash
   cd frontend
   ```

2. Instala las dependencias de Node:
   ```bash
   npm install
   ```

3. Inicia el servidor de desarrollo Vite:
   ```bash
   npm run dev
   ```

4. Abre en tu navegador la URL que muestra la consola (por defecto: [http://localhost:3000](http://localhost:3000)).