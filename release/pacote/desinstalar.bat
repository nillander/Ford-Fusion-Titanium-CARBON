@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
echo Restaura o Ford Mustang GT original a partir de CARS\MUSTANGGT_original.
echo.
set "JOGO="
for %%K in ("HKLM\SOFTWARE\WOW6432Node\Electronic Arts\Need for Speed Carbon" "HKLM\SOFTWARE\Electronic Arts\Need for Speed Carbon") do (
    for /f "tokens=2,*" %%A in ('reg query %%K /v "Install Dir" 2^>nul') do if /i "%%A"=="REG_SZ" if not defined JOGO set "JOGO=%%B"
)
if defined JOGO if "!JOGO:~-1!"=="\" set "JOGO=!JOGO:~0,-1!"
if defined JOGO if not exist "!JOGO!\CARS\MUSTANGGT_original\GEOMETRY.BIN" set "JOGO="
if not defined JOGO set /p JOGO=Digite a pasta do jogo ^(onde esta NFSC.exe^): 
if not exist "!JOGO!\CARS\MUSTANGGT_original\GEOMETRY.BIN" (
    echo Nao encontrei CARS\MUSTANGGT_original em:
    echo !JOGO!
    pause
    exit /b 1
)
tasklist /FI "IMAGENAME eq NFSC.exe" 2>nul | find /I "NFSC.exe" >nul
if not errorlevel 1 (
    echo O jogo esta aberto. Feche o Need for Speed Carbon e execute o script de novo.
    pause
    exit /b 1
)
robocopy "!JOGO!\CARS\MUSTANGGT_original" "!JOGO!\CARS\MUSTANGGT" /E /R:1 /W:1 >nul
if errorlevel 8 (
    echo A copia falhou.
    pause
    exit /b 1
)
echo Mustang GT original restaurado. A pasta MUSTANGGT_original foi mantida.
pause
exit /b 0
