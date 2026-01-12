#!/bin/bash
set -e

echo "🚀 Démarrage du conteneur..."

# Détecter le service (jupyter, api, ou frontend)
SERVICE="${1:-jupyter}"

# Vérifier si le dataset existe
if [ ! -f "/workspace/dataset/classifier/json/dataset.jsonl" ]; then
    echo "⚠️  Dataset non trouvé. Génération du dataset..."
    python /workspace/dataset/generators/classifier/dataset_generator.py
    echo "✅ Dataset généré avec succès !"
else
    echo "✅ Dataset trouvé."
fi

# Créer les dossiers nécessaires s'ils n'existent pas
mkdir -p /workspace/classifier/{models,checkpoints,results,logs/training}
mkdir -p /workspace/nlp/{models,checkpoints,results,logs/training}
mkdir -p /workspace/{models,results,checkpoints,logs/training}

# Lancer le service approprié
case "$SERVICE" in
    jupyter)
        echo "📓 Démarrage de Jupyter Lab..."
        exec jupyter lab \
            --ip=0.0.0.0 \
            --port=8888 \
            --no-browser \
            --allow-root \
            --NotebookApp.token='' \
            --NotebookApp.password='' \
            --NotebookApp.notebook_dir=/workspace
        ;;
    api)
        echo "🚀 Démarrage de l'API..."
        exec uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
        ;;
    frontend)
        echo "🌐 Démarrage du serveur frontend..."
        exec python -m http.server 8080 --directory /workspace/frontend
        ;;
    *)
        echo "⚠️  Service inconnu: $SERVICE"
        echo "   Services disponibles: jupyter, api, frontend"
        exec "$@"
        ;;
esac

