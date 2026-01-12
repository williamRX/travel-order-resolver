#!/bin/bash
# Script d'aide pour l'installation de Conda sur macOS
# Ce script ouvre les liens de téléchargement et affiche les instructions

echo "🚀 Guide d'Installation de Conda pour macOS"
echo "=========================================="
echo ""

# Détecter l'architecture
ARCH=$(uname -m)
echo "🖥️  Architecture détectée: $ARCH"

if [ "$ARCH" = "arm64" ]; then
    echo "✅ Mac Apple Silicon détecté (M1/M2/M3/M4)"
    MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.pkg"
    ANACONDA_URL="https://www.anaconda.com/products/distribution#macos"
else
    echo "⚠️  Mac Intel détecté"
    MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.pkg"
    ANACONDA_URL="https://www.anaconda.com/products/distribution#macos"
fi

echo ""
echo "📦 Options d'installation :"
echo ""
echo "1. Miniconda (Recommandé - ~50 MB, léger)"
echo "   URL: $MINICONDA_URL"
echo ""
echo "2. Anaconda (Complet - ~500 MB, inclut beaucoup de packages)"
echo "   URL: $ANACONDA_URL"
echo ""

# Demander à l'utilisateur
read -p "Voulez-vous ouvrir la page de téléchargement Miniconda dans votre navigateur? (o/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[OoYy]$ ]]; then
    if command -v open &> /dev/null; then
        open "$MINICONDA_URL"
        echo "✅ Page de téléchargement ouverte dans votre navigateur"
    else
        echo "❌ Impossible d'ouvrir le navigateur automatiquement"
        echo "   Veuillez copier ce lien : $MINICONDA_URL"
    fi
fi

echo ""
echo "📋 Instructions d'installation :"
echo "================================"
echo ""
echo "1. Téléchargez le fichier .pkg"
echo "2. Double-cliquez sur le fichier téléchargé"
echo "3. Suivez l'assistant d'installation"
echo "4. Fermez et rouvrez votre terminal"
echo "5. Vérifiez avec: conda --version"
echo ""
echo "💡 Si conda n'est pas reconnu après l'installation :"
echo "   conda init zsh"
echo "   (Puis fermez et rouvrez le terminal)"
echo ""
echo "📚 Guide détaillé complet : docs/INSTALL_CONDA.md"
echo ""

