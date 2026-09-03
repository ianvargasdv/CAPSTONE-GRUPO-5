# CAPSTONE-GRUPO-5

Estructura inicial del proyecto.

## Estructura

- `backend/`: API en FastAPI con endpoint `/health`.
- `frontend/`: Aplicación en React + Vite.

## Cómo ejecutar

### Backend
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```