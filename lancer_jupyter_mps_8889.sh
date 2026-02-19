#!/bin/bash

echo "🚀 Lancement de Jupyter avec GPU MPS sur le port 8889"
echo "====================================================="

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "❌ Environnement virtuel 'venv' non trouvé dans le répertoire actuel"
    echo "💡 Assurez-vous d'être dans le répertoire du projet"
    exit 1
fi

# Masquer les avertissements
export PYTHONWARNINGS="ignore"

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel venv..."
source venv/bin/activate

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
    sys.exit(0)
else:
    print('❌ MPS non disponible')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Erreur: PyTorch MPS n'est pas disponible"
    exit 1
fi

# Vérifier si le port 8889 est libre
if lsof -i :8889 &>/dev/null; then
    echo "⚠️  Le port 8889 est déjà utilisé"
    echo "💡 Voulez-vous continuer quand même ? (y/n)"
    read -r response
    if [ "$response" != "y" ]; then
        echo "❌ Annulé"
        exit 1
    fi
fi

# Générer un token simple pour le développement
JUPYTER_TOKEN="mlgpu2024"

echo ""
echo "🌟 Lancement de Jupyter sur le port 8889..."
echo "📁 Ouvrez cette URL dans votre navigateur:"
echo "   http://localhost:8889/?token=$JUPYTER_TOKEN"
echo ""
echo "🔐 Token Jupyter: $JUPYTER_TOKEN"
echo ""
echo "📝 Instructions:"
echo "1. Ouvrez l'URL ci-dessus dans Chrome/Safari"
echo "2. Naviguez vers:"
echo "   - NLP NER: nlp/notebooks/02_ner_training_camembert.ipynb"
echo "   - Classifier: classifier/notebooks/03_validity_classifier_camembert.ipynb"
echo "3. Le notebook utilisera automatiquement votre GPU MPS!"
echo ""
echo "⚠️  Pour arrêter Jupyter, appuyez sur Ctrl+C dans ce terminal"
echo ""

# Lancer Jupyter avec le port 8889
jupyter notebook \
    --notebook-dir=/Users/williamroux/Documents/Projets/T-AIA-911-LIL_3 \
    --port=8889 \
    --no-browser \
    --NotebookApp.token="$JUPYTER_TOKEN" \
    --NotebookApp.password=""
