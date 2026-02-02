FROM python:3.11-slim

# Définit le dossier de travail
WORKDIR /app

# Copie d'abord uniquement les dépendances (optimise le cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie le reste du code et les CSV
COPY . .

CMD ["python3", "app.py"]
