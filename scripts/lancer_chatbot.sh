#!/bin/bash
# Script pour lancer le chatbot avec le classifieur CamemBERT

set -e

echo "🚀 Lancement du chatbot avec classifieur CamemBERT"
echo "=================================================="
echo ""

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "api/main.py" ]; then
    echo "❌ Erreur: Ce script doit être exécuté depuis la racine du projet"
    echo "   Répertoire actuel: $(pwd)"
    exit 1
fi

# Activer l'environnement virtuel si disponible
if [ -d "venv" ]; then
    echo "📦 Activation de l'environnement virtuel..."
    source venv/bin/activate
elif [ -n "$CONDA_DEFAULT_ENV" ]; then
    echo "📦 Environnement Conda actif: $CONDA_DEFAULT_ENV"
else
    echo "⚠️  Aucun environnement virtuel détecté"
    echo "   Assurez-vous d'avoir activé votre environnement (venv ou conda)"
    read -p "Continuer quand même? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Vérifier les dépendances
echo ""
echo "🔍 Vérification des dépendances..."
python3 -c "import fastapi, uvicorn, transformers, torch, spacy" 2>/dev/null || {
    echo "❌ Dépendances manquantes"
    echo "   Installez-les avec: pip install fastapi uvicorn transformers torch spacy"
    exit 1
}
echo "✅ Dépendances OK"

# Vérifier que les modèles existent
echo ""
echo "🔍 Vérification des modèles..."
if [ -d "classifier/models/validity_classifier_camembert_"* ] 2>/dev/null; then
    echo "✅ Modèle CamemBERT trouvé"
else
    echo "⚠️  Modèle CamemBERT non trouvé"
    echo "   Le pipeline utilisera l'ancien modèle si disponible"
fi

if [ -d "nlp/models/spacy_ner_"* ] 2>/dev/null; then
    echo "✅ Modèle NLP trouvé"
else
    echo "❌ Modèle NLP non trouvé"
    echo "   Entraînez d'abord un modèle avec: nlp/notebooks/01_ner_training.ipynb"
    exit 1
fi

# Lancer l'API
echo ""
echo "📡 Démarrage de l'API FastAPI..."
echo "   API sera accessible sur: http://localhost:8000"
echo "   Documentation: http://localhost:8000/docs"
echo ""
echo "   Pour arrêter l'API, appuyez sur Ctrl+C"
echo ""

# Lancer l'API en arrière-plan
python api/main.py &
API_PID=$!

# Attendre que l'API soit prête
echo "⏳ Attente du démarrage de l'API..."
sleep 3

# Vérifier que l'API répond
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API démarrée avec succès!"
else
    echo "⚠️  L'API semble ne pas répondre, mais elle peut être en cours de démarrage"
fi

# Ouvrir le chatbot dans le navigateur
echo ""
echo "🌐 Ouverture du chatbot dans le navigateur..."
if command -v open &> /dev/null; then
    open frontend/index.html
elif command -v xdg-open &> /dev/null; then
    xdg-open frontend/index.html
else
    echo "   Ouvrez manuellement: frontend/index.html"
fi

echo ""
echo "=" * 60
echo "✅ Chatbot lancé !"
echo ""
echo "📋 Informations:"
echo "   - API: http://localhost:8000"
echo "   - Documentation: http://localhost:8000/docs"
echo "   - Health check: http://localhost:8000/health"
echo ""
echo "🛑 Pour arrêter l'API:"
echo "   kill $API_PID"
echo "   ou appuyez sur Ctrl+C dans ce terminal"
echo "=" * 60

# Attendre que l'utilisateur arrête l'API
wait $API_PID

