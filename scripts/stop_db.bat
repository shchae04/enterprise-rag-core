@echo off
echo Stopping Database...
docker-compose -f docker-compose-db.yml down
echo.
echo Database stopped.
pause
