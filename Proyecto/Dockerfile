# Imagen base de Python
FROM python:3.11-slim

# Evita prompts de salida estándar o de errores interactivos 
ENV PYTHONUNBUFFERED=1 
# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalamos herramientas básicas de compilación
RUN apt-get update && apt-get install -y build-essential

# Copiamos solo lo necesario primero (cache de pip)
COPY requirements.txt /app/requirements.txt

# Instalamos pip, setuptools y wheel antes de las dependencias
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiamos los archivos del proyecto
COPY . /app

# Exponer no es obligatorio en Render, pero ayuda para lectura
EXPOSE 8000

# Usamos sh -c para que expanda la variable PORT en Render
CMD ["sh", "-c", "uvicorn main:cotizar --host 0.0.0.0 --port ${PORT:-8000}"]