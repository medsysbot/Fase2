#!/bin/bash
set -e

# ╔═════════════════════════════════════════════════════╗
# ║       INSTALACIÓN DE DEPENDENCIAS REQUERIDAS       ║
# ╚═════════════════════════════════════════════════════╝

echo "Instalando dependencias de Python..."

pip install fastapi python-dotenv psycopg2-binary python-multipart jinja2 supabase

echo "✅ Librerías instaladas correctamente"

# ╔═════════════════════════════════════════════════════╗
# ║         VERIFICACIÓN DE ESTRUCTURA DE PROYECTO     ║
# ╚═════════════════════════════════════════════════════╝

mkdir -p static/js static/icons static/doc templates routes utils

echo "📁 Carpetas esenciales verificadas"

# ╔═════════════════════════════════════════════════════╗
# ║        LIMPIEZA DE ARCHIVOS Y CACHÉS VIEJOS        ║
# ╚═════════════════════════════════════════════════════╝

echo "🧹 Limpiando archivos temporales y caché..."

find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*~" -delete
find . -type f -name "*.bak" -delete
rm -rf tmp 2>/dev/null || true

echo "🧼 Limpieza completada"

# ╔═════════════════════════════════════════════════════╗
# ║       MENSAJE FINAL DE INSTALACIÓN COMPLETADA      ║
# ╚═════════════════════════════════════════════════════╝

echo "✅ Setup completo. Ya podés iniciar tu backend en Codex sin problemas."
