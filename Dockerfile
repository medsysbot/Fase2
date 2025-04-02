FROM python:3.10-slim

# Instalar dependencias del sistema, incluyendo ffmpeg
RUN apt-get update && apt-get install -y ffmpeg git && apt-get clean

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos
COPY . /app

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto para Uvicorn
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]