@echo off
echo Starting Database (PostgreSQL + pgvector)...
docker-compose -f docker-compose-db.yml up -d
echo.
echo Database is running on localhost:5432
echo.
pause
