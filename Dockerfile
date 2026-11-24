FROM python:3.11-slim

WORKDIR /app

# Se copian primero las dependencias para aprovechar la caché de Docker.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# El código cambia más seguido que las dependencias.
COPY . .

CMD ["python", "train.py", "--help"]
