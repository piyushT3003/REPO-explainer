@echo off
echo Starting FastAPI backend...
uvicorn backend.main:app --reload
pause
