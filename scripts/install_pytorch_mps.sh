#!/bin/bash
# Script d'installation de PyTorch avec support MPS pour Mac Apple Silicon
# Usage: ./scripts/install_pytorch_mps.sh

set -e

echo "🚀 Installation de PyTorch avec support MPS pour Mac Apple Silicon"
echo "======================================================================"
echo ""

# Vérifier que nous sommes sur macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Ce script est conçu pour macOS uniquement"
    exit 1
fi

# Vérifier les outils de ligne de commande Apple
echo "📦 Vérification des outils de ligne de commande Apple..."
if ! command -v xcode-select &> /dev/null; then
    echo "⚠️  xcode-select non trouvé. Installation des outils de ligne de commande..."
    xcode-select --install
    echo "✅ Veuillez terminer l'installation des outils de ligne de commande, puis relancez ce script"
    exit 1
else
    echo "✅ Outils de ligne de commande Apple détectés"
fi

# Vérifier si nous sommes dans un environnement virtuel
if [[ -z "$VIRTUAL_ENV" ]] && [[ -z "$CONDA_DEFAULT_ENV" ]]; then
    echo ""
    echo "⚠️  Aucun environnement virtuel détecté"
    echo "💡 Recommandation: Créez et activez un environnement virtuel avant d'installer PyTorch"
    echo ""
    echo "   Avec Conda:"
    echo "   conda create -n machine_learning python=3.11 -y"
    echo "   conda activate machine_learning"
    echo ""
    echo "   Avec venv:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo ""
    read -p "Continuer quand même? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Installer PyTorch avec support MPS
echo ""
echo "📦 Installation de PyTorch avec support MPS..."
echo "   Cette installation peut prendre quelques minutes..."
echo ""

pip install torch torchvision torchaudio

# Vérifier l'installation
echo ""
echo "🔍 Vérification de l'installation..."
python3 << EOF
import torch
print(f"✅ PyTorch {torch.__version__} installé avec succès")

if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
    print("✅ MPS (Metal Performance Shaders) est disponible!")
    print("   🚀 Votre GPU Apple Silicon sera utilisé pour l'entraînement")
    
    # Test rapide
    try:
        device = torch.device("mps")
        test_tensor = torch.randn(1000, 1000).to(device)
        torch.mm(test_tensor, test_tensor)
        print("   ✅ Test MPS réussi - Prêt pour l'entraînement!")
    except Exception as e:
        print(f"   ⚠️  Test MPS échoué: {e}")
else:
    print("⚠️  MPS n'est pas disponible")
    print("   💡 Vérifiez que vous êtes sur un Mac avec Apple Silicon (M1/M2/M3/M4)")
    print("   💡 Vérifiez que macOS est à jour")
else:
    print("⚠️  MPS non disponible, utilisation du CPU")
EOF

echo ""
echo "✅ Installation terminée!"
echo ""
echo "📝 Prochaines étapes:"
echo "   1. Ouvrez votre notebook Jupyter"
echo "   2. Exécutez la cellule de vérification MPS"
echo "   3. Le GPU sera automatiquement utilisé si disponible"
echo ""

