@echo off
setlocal EnableExtensions
cd /d "%~dp0"
echo Restaura todos os arquivos anteriores a instalacao da v1.2.
set "JOGO="
set /p JOGO=Digite a pasta do jogo (onde esta NFSC.exe):
if not defined JOGO exit /b 1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar.ps1" -GamePath "%JOGO%" -Action Restore
if errorlevel 1 (
    echo Restauracao interrompida. Confira o erro acima.
    pause
    exit /b 1
)
echo Arquivos restaurados. Backup mantido.
pause
