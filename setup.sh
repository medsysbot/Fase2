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
# ║       MENSAJE FINAL DE INSTALACIÓN COMPLETADA      ║
# ╚═════════════════════════════════════════════════════╝

echo "✅ Setup completo. Ya podés iniciar tu backend en Codex sin problemas."
