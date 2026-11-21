#!/bin/bash
# ==============================================================================
# Script de Compilación para Linux - Genera el ejecutable nativo (ELF)
# ==============================================================================

set -e
cd "$(dirname "$0")"

echo "=== Compilando ejecutable nativo de Linux (PyInstaller) ==="

# Verificar Python y pip
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 no está instalado."
    exit 1
fi

echo "Instalando paquetes requeridos..."
python3 -m pip install -q --user pyinstaller pygame-ce automata-lib numpy pillow

echo "Generando ejecutable autónomo con PyInstaller..."
python3 -m PyInstaller \
    --noconfirm \
    --onefile \
    --windowed \
    --name "Memotest_FTI_linux" \
    --add-data "assets:assets" \
    --collect-all automata \
    main.py

echo "=== ¡Compilación exitosa! ==="
echo "El ejecutable se encuentra en: dist/Memotest_FTI_linux"
echo "Puedes ejecutarlo con: ./dist/Memotest_FTI_linux"
