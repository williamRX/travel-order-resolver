#!/bin/bash

echo "🚀 Lancement de Jupyter avec environnement virtuel"
echo "=================================================="

# Activer l'environnement virtuel
source ~/ml_env/bin/activate

# Masquer les avertissements
export PYTHONWARNINGS="ignore"

# Trouver un port libre
find_free_port() {
    local port=8888
    while lsof -i :$port &>/dev/null; do
        port=$((port + 1))
    done
    echo $port
}

PORT=$(find_free_port)
TOKEN="mlgpu2024"

echo "🔧 Environnement virtuel activé"
echo "🔐 Token: $TOKEN"
echo "🌐 URL: http://localhost:$PORT/?token=$TOKEN"
echo ""

# Lancer Jupyter directement avec Python de l'environnement virtuel
~/ml_env/bin/python3 -m jupyter notebook \
    --notebook-dir=/Users/williamroux/Documents/Projets/T-AIA-911-LIL_3 \
    --port=$PORT \
    --no-browser \
    --NotebookApp.token="$TOKEN" \
    --NotebookApp.password=""
