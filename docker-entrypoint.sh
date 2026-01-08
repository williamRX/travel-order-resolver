#!/bin/bash
set -e

echo "🚀 Démarrage du conteneur Jupyter..."

# Vérifier si le dataset existe
if [ ! -f "/workspace/dataset/classifier/json/dataset.jsonl" ]; then
    echo "⚠️  Dataset non trouvé. Génération du dataset..."
    python /workspace/dataset/generators/classifier/dataset_generator.py
    echo "✅ Dataset généré avec succès !"
else
    echo "✅ Dataset trouvé."
fi

# Lancer Jupyter Lab
echo "📓 Démarrage de Jupyter Lab..."
exec jupyter lab \
    --ip=0.0.0.0 \
    --port=8888 \
    --no-browser \
    --allow-root \
    --NotebookApp.token='' \
    --NotebookApp.password='' \
    --NotebookApp.notebook_dir=/workspace

