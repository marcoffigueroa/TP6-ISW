# Usa una imagen base de Python ligera
FROM python:3.10-slim

# Establece variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de requerimientos y los instala
# Hacemos esto en pasos separados para aprovechar el caché de Docker
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copia todo el código de tu proyecto al directorio de trabajo
COPY . .

# Expone el puerto en el que correrá Gunicorn
EXPOSE 8000

# Comando para iniciar la aplicación
# IMPORTANTE: Cambia 'myproject.wsgi:application'
# 'myproject' debe ser el nombre de la carpeta que contiene tu archivo wsgi.py
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "project.wsgi:application"]