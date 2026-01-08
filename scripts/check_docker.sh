#!/bin/bash
# Script de diagnostic pour Docker

echo "🔍 Diagnostic Docker - Système d'Extraction d'Intentions de Voyage"
echo "=================================================================="
echo ""

# Vérifier Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé ou n'est pas dans le PATH"
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo "❌ Docker n'est pas en cours d'exécution ou vous n'avez pas les permissions"
    echo "   Essayez: sudo docker ps ou démarrez Docker Desktop"
    exit 1
fi

echo "✅ Docker est installé et fonctionne"
echo ""

# Vérifier docker-compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ docker-compose n'est pas installé"
    exit 1
fi

echo "✅ docker-compose est disponible"
echo ""

# Vérifier les conteneurs
echo "📦 Conteneurs en cours d'exécution:"
docker ps --filter "name=t-aia-911-lil3" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# Vérifier les ports
echo "🔌 Ports utilisés:"
echo "   Jupyter:  http://localhost:8888"
echo "   API:      http://localhost:8000"
echo "   Frontend: http://localhost:8080"
echo ""

# Vérifier les logs
echo "📋 Derniers logs des services:"
echo ""
echo "--- API ---"
docker compose logs api --tail=10 2>/dev/null || echo "   Service API non démarré"
echo ""
echo "--- Frontend ---"
docker compose logs frontend --tail=10 2>/dev/null || echo "   Service Frontend non démarré"
echo ""
echo "--- Jupyter ---"
docker compose logs jupyter --tail=10 2>/dev/null || echo "   Service Jupyter non démarré"
echo ""

# Vérifier les fichiers nécessaires
echo "📁 Fichiers nécessaires:"
if [ -f "api/pipeline.py" ]; then
    echo "   ✅ api/pipeline.py"
else
    echo "   ❌ api/pipeline.py manquant"
fi

if [ -f "api/main.py" ]; then
    echo "   ✅ api/main.py"
else
    echo "   ❌ api/main.py manquant"
fi

if [ -f "frontend/index.html" ]; then
    echo "   ✅ frontend/index.html"
else
    echo "   ❌ frontend/index.html manquant"
fi

if [ -d "classifier/models" ] && [ "$(ls -A classifier/models/*.joblib 2>/dev/null)" ]; then
    echo "   ✅ Modèles de classifieur trouvés"
else
    echo "   ⚠️  Aucun modèle de classifieur trouvé"
fi

if [ -d "nlp/models" ] && [ "$(ls -A nlp/models/spacy_ner_* 2>/dev/null)" ]; then
    echo "   ✅ Modèles NLP trouvés"
else
    echo "   ⚠️  Aucun modèle NLP trouvé"
fi

echo ""
echo "💡 Commandes utiles:"
echo "   docker compose up api frontend    # Démarrer API et Frontend"
echo "   docker compose logs -f api        # Voir les logs de l'API"
echo "   docker compose restart api        # Redémarrer l'API"
echo "   docker compose down               # Arrêter tous les services"

