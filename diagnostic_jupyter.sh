#!/bin/bash

echo "🔍 Diagnostic Jupyter - Recherche du problème"
echo "=============================================="

# Vérifier si l'environnement virtuel existe
echo "1. Vérification de l'environnement virtuel..."
if [ -d "$HOME/ml_env" ]; then
    echo "   ✅ Environnement virtuel trouvé: $HOME/ml_env"
else
    echo "   ❌ Environnement virtuel non trouvé"
    echo "   💡 Lancez d'abord: ./setup_mac_ml.sh"
    exit 1
fi

# Activer l'environnement virtuel
echo "2. Activation de l'environnement virtuel..."
source $HOME/ml_env/bin/activate

# Vérifier si on est dans le bon environnement
echo "3. Vérification de l'environnement actif..."
which python3
python3 --version

# Vérifier si Jupyter est installé
echo "4. Vérification de Jupyter..."
if command -v jupyter &> /dev/null; then
    echo "   ✅ Jupyter installé"
    jupyter --version
else
    echo "   ❌ Jupyter non installé"
    echo "   Installation..."
    pip install jupyter ipykernel
fi

# Vérifier PyTorch
echo "5. Vérification de PyTorch..."
python3 -c "
try:
    import torch
    print(f'   ✅ PyTorch: {torch.__version__}')
    print(f'   MPS disponible: {torch.backends.mps.is_available()}')
    if torch.backends.mps.is_available():
        device = torch.device('mps')
        x = torch.randn(3, 3).to(device)
        print('   ✅ MPS fonctionne!')
    else:
        print('   ❌ MPS non disponible')
except Exception as e:
    print(f'   ❌ Erreur PyTorch: {e}')
"

# Vérifier si le port 8888 est libre
echo "6. Vérification du port 8888..."
if lsof -i :8888 &> /dev/null; then
    echo "   ❌ Port 8888 déjà utilisé"
    lsof -i :8888
else
    echo "   ✅ Port 8888 libre"
fi

# Essayer de lancer Jupyter avec un port différent
echo "7. Test de lancement Jupyter..."
echo "   Tentative avec le port 8889..."
timeout 10 jupyter notebook --notebook-dir=/Users/williamroux/Documents/Projets/T-AIA-911-LIL_3 --port=8889 --no-browser &
JUPYTER_PID=$!

# Attendre un peu
sleep 3

# Vérifier si Jupyter tourne
if kill -0 $JUPYTER_PID 2>/dev/null; then
    echo "   ✅ Jupyter lancé avec succès sur le port 8889"
    echo "   📱 Ouvrez: http://localhost:8889"
    echo "   🛑 Pour arrêter: kill $JUPYTER_PID"
else
    echo "   ❌ Jupyter n'a pas pu démarrer"
    # Montrer les logs d'erreur
    echo "   Logs d'erreur:"
    jupyter notebook --notebook-dir=/Users/williamroux/Documents/Projets/T-AIA-911-LIL_3 --port=8889 --help 2>&1 | head -20
fi

echo ""
echo "📋 Résumé des commandes pour lancer Jupyter:"
echo "   cd /Users/williamroux/Documents/Projets/T-AIA-911-LIL_3"
echo "   source ~/ml_env/bin/activate"
echo "   jupyter notebook --notebook-dir=/Users/williamroux/Documents/Projets/T-AIA-911-LIL_3 --port=8888"
