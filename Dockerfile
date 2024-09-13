FROM python:3.8.10-slim

# Instalamos git y las dependencias necesarias para OpenCV y el proyecto
RUN apt-get update && apt-get install -y \
    git \
    libgl1 \
    libglib2.0-0

WORKDIR /app

# Copiar los archivos del proyecto al contenedor
COPY . /app

# Copiar el archivo de dependencias e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto 5000 para Flask
EXPOSE 5000

# Configurar el entorno de Flask
ENV FLASK_APP=api/app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Comando para iniciar Flask
CMD ["flask", "run"]
