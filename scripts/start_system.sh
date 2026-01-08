#!/bin/bash
# Script pour démarrer le système complet

echo "🚀 Démarrage du système d'extraction d'intentions de voyage"
echo ""

# Vérifier si Docker est disponible
if command -v docker &> /dev/null && docker ps &> /dev/null; then
    echo "✅ Docker détecté"
    echo ""
    echo "Options disponibles :"
    echo "  1. Tous les services (Jupyter + API + Front-end)"
    echo "  2. API + Front-end uniquement"
    echo "  3. API uniquement"
    echo ""
    read -p "Choisissez une option (1-3) : " choice
    
    case $choice in
        1)
            echo "🚀 Démarrage de tous les services..."
            docker compose up
            ;;
        2)
            echo "🚀 Démarrage de l'API et du Front-end..."
            docker compose up api frontend
            ;;
        3)
            echo "🚀 Démarrage de l'API..."
            docker compose up api
            ;;
        *)
            echo "❌ Option invalide"
            exit 1
            ;;
    esac
else
    echo "⚠️  Docker non disponible, démarrage manuel..."
    echo ""
    echo "Pour démarrer l'API :"
    echo "  uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload"
    echo ""
    echo "Pour démarrer le front-end :"
    echo "  python -m http.server 8080 --directory frontend"
    echo ""
    echo "Ou ouvrez simplement frontend/index.html dans votre navigateur"
fi

