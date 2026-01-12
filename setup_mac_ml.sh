#!/bin/bash

# Script d'installation automatique pour PyTorch avec MPS sur Mac M4
echo "🚀 Installation de PyTorch avec MPS pour Mac M4 Pro"
echo "=================================================="

# Vérifier si Homebrew est installé
if ! command -v brew &> /dev/null; then
    echo "📦 Installation de Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"
else
    echo "✅ Homebrew déjà installé"
fi

# Vérifier si Python est installé via Homebrew
if ! command -v python3 &> /dev/null || [[ $(python3 --version) == *"Library/Developer"* ]]; then
    echo "🐍 Installation de Python via Homebrew..."
    brew install python
else
    echo "✅ Python déjà installé"
fi

# Créer l'environnement virtuel
echo "🔧 Création de l'environnement virtuel..."
python3 -m venv ~/ml_env

# Activer l'environnement
echo "⚡ Activation de l'environnement..."
source ~/ml_env/bin/activate

# Installer PyTorch avec MPS
echo "🧠 Installation de PyTorch avec MPS..."
pip install --upgrade pip
pip install torch torchvision torchaudio

# Installer les autres dépendances
echo "📚 Installation des dépendances ML..."
pip install transformers accelerate scikit-learn pandas numpy tqdm jupyter ipykernel

# Vérifier l'installation
echo "🔍 Vérification de l'installation..."
python3 -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'MPS disponible: {torch.backends.mps.is_available()}')
if torch.backends.mps.is_available():
    device = torch.device('mps')
    print(f'✅ MPS device: {device}')
    # Test rapide
    x = torch.randn(3, 3).to(device)
    y = x * x
    print('✅ Test MPS réussi!')
else:
    print('❌ MPS non disponible')
"

echo ""
echo "🎉 Installation terminée!"
echo "=========================="
echo "Pour utiliser Jupyter avec GPU:"
echo "1. Activez l'environnement: source ~/ml_env/bin/activate"
echo "2. Lancez Jupyter: jupyter notebook --notebook-dir=/Users/williamroux/Documents/Projets/T-AIA-911-LIL_3"
echo ""
echo "Le notebook 03_validity_classifier_camembert.ipynb détectera automatiquement le GPU MPS!"
