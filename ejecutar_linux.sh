#!/bin/bash
# ==============================================================================
# Script de Lanzamiento para Linux - Memotest FTI (Grupo N°2 - UNPSJB)
# ==============================================================================

set -e
cd "$(dirname "$0")"

echo "=== Iniciando Juego de la Memoria (Memotest FTI) ==="

# Verificar Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 no está instalado. Instálalo con: sudo apt install python3 python3-pip"
    exit 1
fi

# Instalar dependencias necesarias si faltan
echo "Comprobando dependencias..."
python3 -m pip install -q --user pygame-ce automata-lib numpy pillow || true

# Ejecutar el juego
echo "Lanzando el juego..."
python3 main.py
