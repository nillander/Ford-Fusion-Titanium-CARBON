@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "CANDIDATOS=%TEMP%\fusion-carbon-pastas.txt"
if exist "%CANDIDATOS%" del /f /q "%CANDIDATOS%"

if not exist "%~dp0CARS\MUSTANGGT\GEOMETRY.BIN" (
    echo Nao encontrei CARS\MUSTANGGT\GEOMETRY.BIN nesta pasta:
    echo %~dp0
    pause
    exit /b 1
)

echo Ford Fusion Titanium 2018 - Need for Speed Carbon
echo Substitui o Ford Mustang GT ^(slot MUSTANGGT^).
echo.
echo Procurando Need for Speed Carbon...
echo.

call :DoRegistro "HKLM\SOFTWARE\WOW6432Node\Electronic Arts\Need for Speed Carbon"
call :DoRegistro "HKLM\SOFTWARE\Electronic Arts\Need for Speed Carbon"
call :DoRegistro "HKLM\SOFTWARE\WOW6432Node\EA Games\Need for Speed Carbon"
call :DoRegistro "HKLM\SOFTWARE\EA Games\Need for Speed Carbon"

call :Testar "C:\Program Files (x86)\Electronic Arts\Need for Speed Carbon"
call :Testar "C:\Program Files\Electronic Arts\Need for Speed Carbon"
call :Testar "D:\Program Files (x86)\Electronic Arts\Need for Speed Carbon"
call :Testar "C:\Program Files (x86)\EA Games\Need for Speed Carbon"
call :Testar "C:\Jogos\Need for Speed Carbon"
call :Testar "D:\Jogos\Need for Speed Carbon"
call :Testar "D:\Games\Need for Speed Carbon"

if exist "%CANDIDATOS%" (
    for /f "usebackq delims=" %%G in ("%CANDIDATOS%") do (
        call :Confirmar "%%G"
        if not errorlevel 1 exit /b 0
    )
)

:Manual
echo.
set "DIGITADA="
set /p DIGITADA=Digite a pasta do jogo ^(onde esta NFSC.exe^), ou Enter para cancelar: 
if not defined DIGITADA (
    echo Instalacao cancelada.
    pause
    exit /b 1
)
call :Confirmar "%DIGITADA%"
if errorlevel 1 goto Manual
exit /b 0

:DoRegistro
for /f "tokens=2,*" %%A in ('reg query "%~1" /v "Install Dir" 2^>nul') do (
    if /i "%%A"=="REG_SZ" call :Testar "%%B"
)
exit /b 0

:Testar
set "PASTA=%~1"
if not defined PASTA exit /b 0
if "!PASTA:~-1!"=="\" set "PASTA=!PASTA:~0,-1!"
if not exist "!PASTA!\NFSC.exe" exit /b 0
if not exist "!PASTA!\CARS\MUSTANGGT" exit /b 0
if exist "%CANDIDATOS%" (
    findstr /L /I /X /C:"!PASTA!" "%CANDIDATOS%" >nul
    if not errorlevel 1 exit /b 0
)
>>"%CANDIDATOS%" echo !PASTA!
exit /b 0

:Confirmar
set "JOGO=%~1"
if "!JOGO:~-1!"=="\" set "JOGO=!JOGO:~0,-1!"
if not exist "!JOGO!\NFSC.exe" (
    echo.
    echo Essa pasta nao tem NFSC.exe:
    echo !JOGO!
    exit /b 1
)
if not exist "!JOGO!\CARS\MUSTANGGT" (
    echo.
    echo Essa pasta nao tem CARS\MUSTANGGT:
    echo !JOGO!
    exit /b 1
)
echo.
echo Pasta encontrada:
echo !JOGO!
set "RESP="
set /p RESP=Esta pasta esta correta? (S/N) 
if /i "!RESP!"=="S" goto Instalar
if /i "!RESP!"=="SIM" goto Instalar
exit /b 1

:Instalar
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar.ps1" -GamePath "!JOGO!" -Action Install
if errorlevel 1 goto Falhou
echo Instalacao v1.2 concluida. Backup: Fusion2018_v1.2_backup.
pause
exit /b 0

:Falhou
echo Instalacao interrompida. Confira o erro acima.
pause
exit /b 1
