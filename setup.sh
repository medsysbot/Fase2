#!/bin/bash

# Actualiza pip y luego instala las dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Opcional: alias para ejecutar el diagnostico rapidamente
echo 'alias medsys_diag="python diagnostico_medsys.py"' >> ~/.bashrc
