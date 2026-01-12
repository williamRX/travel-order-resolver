#!/bin/bash

echo "🚀 Lancement de Jupyter avec GPU MPS"
echo "===================================="

# Vérifier si l'environnement virtuel existe
if [ ! -d "$HOME/ml_env" ]; then
    echo "❌ Environnement virtuel non trouvé dans $HOME/ml_env"
    echo "💡 Lancez d'abord : ./setup_mac_ml.sh"
    exit 1
fi

# Masquer l'avertissement urllib3
export PYTHONWARNINGS="ignore::urllib3.exceptions.InsecureRequestWarning"

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source $HOME/ml_env/bin/activate

# Vérifier PyTorch MPS
echo "🔍 Vérification de PyTorch MPS..."
python3 -c "
import warnings
warnings.filterwarnings('ignore')
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

# Lancer Jupyter
echo "🌟 Lancement de Jupyter sur le port $PORT..."
echo "📁 Ouvrez cette URL dans votre navigateur:"
echo "   http://localhost:$PORT"
echo ""
echo "📝 Dans Jupyter, allez dans votre projet:"
echo "   /Users/williamroux/Documents/Projets/T-AIA-911-LIL_3"
echo ""
echo "🎯 Ouvrez le notebook:"
echo "   classifier/notebooks/03_validity_classifier_camembert.ipynb"
echo ""

# Masquer les warnings dans Jupyter aussi
export PYTHONWARNINGS="ignore"
jupyter notebook --notebook-dir=/Users/williamroux/Documents/Projets/T-AIA-911-LIL_3 --port=$PORT