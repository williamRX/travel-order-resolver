#!/bin/bash
# Script pour lancer le chatbot avec Docker

set -e

echo "🚀 Lancement du chatbot avec Docker"
echo "===================================="
echo ""

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé"
    echo "   Installez Docker Desktop depuis: https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose n'est pas installé"
    echo "   Installez Docker Compose"
    exit 1
fi

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Erreur: Ce script doit être exécuté depuis la racine du projet"
    exit 1
fi

# Option pour reconstruire
if [ "$1" == "--build" ] || [ "$1" == "-b" ]; then
    echo "🔨 Construction des images Docker..."
    docker-compose build
    echo ""
fi

# Vérifier si les images existent
if ! docker images | grep -q "t-aia-911-lil3"; then
    echo "⚠️  Les images Docker n'existent pas"
    echo "🔨 Construction des images..."
    docker-compose build
    echo ""
fi

echo "📡 Démarrage des services (API + Frontend)..."
echo ""
echo "   Services lancés:"
echo "   - API: http://localhost:8000"
echo "   - Frontend (Chatbot): http://localhost:3000"
echo "   - Documentation API: http://localhost:8000/docs"
echo ""
echo "   Pour arrêter: Ctrl+C ou 'docker-compose down'"
echo ""

# Lancer les services
docker-compose up api frontend

