# JUAN-APP (Mediciones + Puntos) — Electron + FastAPI + SQLite

TFG App con **Mediciones** y **Puntos** (CRUD, búsqueda, paginación, exportación CSV).

## Requisitos
- Python 3.9+
- Node.js 18+

## Instalación
```bash
# Backend (Python)
cd pybackend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# Frontend (Electron)
cd ..
npm install
```

## Ejecución
```bash
npm start
```
Levanta FastAPI en `http://127.0.0.1:8000` y abre la app Electron.

## Endpoints principales
- `GET /health`
- `POST/GET/PUT/DELETE /measurements` (+ listado `GET /measurements?page&limit&q`)
- `POST/GET/PUT/DELETE /points` (+ listado `GET /points?page&limit&q&measurement_id`)
- `GET /export.csv?q&measurement_id`