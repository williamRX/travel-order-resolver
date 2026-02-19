#!/bin/bash

echo "🚀 Lancement de Jupyter avec GPU MPS (version simplifiée)"
echo "=========================================================="

# Vérifier si l'environnement virtuel existe
if [ ! -d "$HOME/ml_env" ]; then
    echo "❌ Environnement virtuel non trouvé dans $HOME/ml_env"
    echo "💡 Lancez d'abord : ./setup_mac_ml.sh"
    exit 1
fi

# Masquer les avertissements
export PYTHONWARNINGS="ignore"

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source $HOME/ml_env/bin/activate

# Vérifier que PyTorch fonctionne
echo "🔍 Test de PyTorch MPS..."
python3 -c "
import torch
import sys
print(f'PyTorch: {torch.__version__}')
print(f'MPS disponible: {torch.backends.mps.is_available()}')
if torch.backends.mps.is_available():
    device = torch.device('mps')
    x = torch.randn(3, 3).to(device)
    print('✅ MPS fonctionne!')
else:
    print('❌ MPS non disponible')
    exit(1)
"

# Fonction pour trouver un port libre
find_free_port() {
    local port=8888
    while lsof -i :$port &>/dev/null; do
        port=$((port + 1))
    done
    echo $port
}

# Trouver un port libre
PORT=$(find_free_port)

echo ""
echo "🌟 Lancement de Jupyter..."
echo "📁 Ouvrez cette URL dans votre navigateur:"
echo "   http://localhost:$PORT"
echo ""
echo "📝 Instructions:"
echo "1. Ouvrez l'URL ci-dessus dans Chrome/Safari"
echo "2. Naviguez vers:"
echo "   - NLP: nlp/notebooks/02_ner_training_camembert.ipynb"
echo "   - Classifier: classifier/notebooks/03_validity_classifier_camembert.ipynb"
echo "3. Le notebook utilisera automatiquement votre GPU MPS!"
echo ""

# Générer un token simple pour le développement
JUPYTER_TOKEN="mlgpu2024"

echo "🔐 Token Jupyter: $JUPYTER_TOKEN"
echo "   (Utilisez ce token si demandé)"
echo ""

# Lancer Jupyter avec le token
echo "🔧 Jupyter utilisera automatiquement l'environnement virtuel"
echo "   (PyTorch et MPS seront disponibles dans tous les notebooks)"
echo ""

jupyter notebook --notebook-dir=/Users/williamroux/Documents/Projets/T-AIA-911-LIL_3 --port=$PORT --no-browser --NotebookApp.token="$JUPYTER_TOKEN" --NotebookApp.password=""
