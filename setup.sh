#!/bin/bash
set -e

# ╔═════════════════════════════════════════════════════╗
# ║      INSTALACIÓN DE DEPENDENCIAS PARA MEDSYS       ║
# ╚═════════════════════════════════════════════════════╝

echo "📦 Instalando dependencias desde requirements.txt..."
pip install -r requirements.txt
echo "✅ Dependencias instaladas correctamente"
