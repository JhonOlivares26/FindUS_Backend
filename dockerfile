# Usa una imagen oficial de Python
FROM python:3.11

# Configura el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de requerimientos y lo instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código del proyecto
COPY . .

# Expone el puerto 8000 (para Django)
EXPOSE 8000

# Comando de inicio del contenedor
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
