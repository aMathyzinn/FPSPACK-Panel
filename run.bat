@echo off
title FPSPACK PANEL - Iniciando...

echo.
echo  ███████╗██████╗ ███████╗██████╗  █████╗  ██████╗██╗  ██╗
echo  ██╔════╝██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝
echo  █████╗  ██████╔╝███████╗██████╔╝███████║██║     █████╔╝ 
echo  ██╔══╝  ██╔═══╝ ╚════██║██╔═══╝ ██╔══██║██║     ██╔═██╗ 
echo  ██║     ██║     ███████║██║     ██║  ██║╚██████╗██║  ██╗
echo  ╚═╝     ╚═╝     ╚══════╝╚═╝     ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
echo.
echo                    PANEL v1.0.0
echo              Sistema de Otimizacao Avancado
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Por favor, instale Python 3.8+ de https://python.org
    pause
    exit /b 1
)

REM Verifica se está executando como administrador
net session >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Nao esta executando como Administrador
    echo Para melhor funcionamento, execute como Administrador
    echo.
    timeout /t 3 >nul
)

REM Verifica se as dependências estão instaladas
echo [INFO] Verificando dependencias...
python -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando dependencias necessarias...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERRO] Falha ao instalar dependencias!
        pause
        exit /b 1
    )
)

REM Cria diretórios necessários
if not exist "logs" mkdir logs
if not exist "config" mkdir config
if not exist "backups" mkdir backups

echo [INFO] Iniciando FPSPACK PANEL...
echo.

REM Executa o aplicativo
python main.py

REM Se chegou aqui, o aplicativo foi fechado
echo.
echo [INFO] FPSPACK PANEL encerrado.
pause