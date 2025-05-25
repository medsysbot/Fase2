#!/bin/bash
# ╔══════════════════════════════════════════════╗
# ║      Script de Setup para MedSys - Codex     ║
# ╚══════════════════════════════════════════════╝

echo "📦 Instalando dependencias del proyecto..."
pip install -r requirements.txt

echo "📁 Creando carpetas necesarias (si no existen)..."
mkdir -p static/pdf
mkdir -p static/icons/alerta
mkdir -p static/icons/firmas
mkdir -p static/uploads
mkdir -p static/firmas_y_sellos

echo "🔍 Verificando errores de sintaxis en los scripts Python..."
python -m compileall -q .

echo "✅ Setup completo. El entorno de MedSys está listo para usar."
