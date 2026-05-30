@echo off
echo Starting ClauseGuard Local Stack...
start cmd /k "uvicorn backend.main:app --host 0.0.0.0 --port 8000"
start cmd /k "cd frontend && npm run dev"
echo Both servers successfully launched! 
echo FastAPI Backend running at http://localhost:8000
echo Vite React Frontend running at http://localhost:5173
pause
