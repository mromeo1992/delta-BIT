@echo off
REM Imposta variabili UID e GID (non usate su Windows, ma definite per compatibilità)
set HOST_UID=1000
set HOST_GID=1000

REM Controlla se nvidia-smi è disponibile
where nvidia-smi >nul 2>nul
if %ERRORLEVEL%==0 (
    echo GPU detected → running GPU mode
    docker compose -f docker-compose.yml -f docker-compose.gpu.yml up --remove-orphans
) else (
    echo No GPU → running CPU mode
    docker compose up --remove-orphans
)