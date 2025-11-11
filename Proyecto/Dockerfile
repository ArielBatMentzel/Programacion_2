# Imagen base de Python
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
# ENV PYTHONUNBUFFERED=1 # Evita prompts interactivos 
WORKDIR /app

# Copiamos solo lo necesario primero (cache de pip)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiamos los archivos del proyecto
COPY . /app

# Exponer no es obligatorio en Render, pero ayuda para lectura
EXPOSE 8000

# Usamos sh -c para que expanda la variable PORT en Render
CMD ["sh", "-c", "uvicorn main:cotizar --host 0.0.0.0 --port ${PORT:-8000}"]