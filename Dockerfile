# Image de base Python
FROM python:3.10-slim

# Métadonnées
LABEL maintainer="Travel Order Resolver Team"
LABEL description="Environnement Jupyter pour le projet de classification NLP"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Créer le répertoire de travail
WORKDIR /workspace

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    python -m spacy download fr_core_news_sm

# Copier le projet
COPY . .

# Créer les dossiers nécessaires
RUN mkdir -p \
    classifier/models classifier/checkpoints classifier/results classifier/logs/training \
    nlp/models nlp/checkpoints nlp/results nlp/logs/training \
    dataset/classifier/json dataset/classifier/csv \
    dataset/nlp/json dataset/nlp/csv dataset/nlp/annotations \
    dataset/shared

# Copier et rendre exécutable le script d'entrée
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Exposer les ports
EXPOSE 8888 8000 3000

# Utiliser le script d'entrée qui vérifie et génère le dataset si nécessaire
ENTRYPOINT ["docker-entrypoint.sh"]

