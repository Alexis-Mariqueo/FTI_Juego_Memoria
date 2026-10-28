@echo off
title Juego de la Memoria - FTI Grupo N2
echo ========================================================
echo  Juego de la Memoria (Memotest) con Automatas Finitos
echo  Fundamentos Teoricos de Informatica - UNPSJB - Grupo N2
echo ========================================================
echo.
echo Iniciando juego con Python y Pygame...
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Ocurrio un error al ejecutar el juego.
    echo Asegurate de tener instalados los requisitos ejecutando:
    echo pip install pygame-ce automata-lib
    pause
)

