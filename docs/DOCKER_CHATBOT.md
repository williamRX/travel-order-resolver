# Lancer le Chatbot avec Docker

Ce guide vous explique comment lancer le chatbot avec Docker, en utilisant le classifieur CamemBERT.

## 🎯 Vue d'ensemble

Le système Docker se compose de 3 services :
1. **jupyter** : Jupyter Lab pour l'entraînement (port 8888)
2. **api** : API FastAPI avec le pipeline CamemBERT (port 8000)
3. **frontend** : Interface chatbot (port 3000)

---

## 🚀 Lancement rapide

### Option 1 : Lancer tous les services

```bash
# Construire les images (première fois ou après modification)
docker-compose build

# Lancer tous les services
docker-compose up
```

### Option 2 : Lancer uniquement le chatbot (API + Frontend)

```bash
# Construire les images
docker-compose build

# Lancer uniquement l'API et le frontend
docker-compose up api frontend
```

### Option 3 : Lancer en arrière-plan

```bash
# Lancer en mode détaché
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter
docker-compose down
```

---

## 📋 Accès aux services

Une fois lancés, les services sont accessibles sur :

- **Chatbot (Frontend)** : http://localhost:3000
- **API** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs
- **Health Check** : http://localhost:8000/health
- **Jupyter Lab** : http://localhost:8888 (si lancé)

---

## 🔧 Commandes utiles

### Voir les logs

```bash
# Tous les services
docker-compose logs -f

# Un service spécifique
docker-compose logs -f api
docker-compose logs -f frontend
```

### Redémarrer un service

```bash
# Redémarrer l'API
docker-compose restart api

# Redémarrer le frontend
docker-compose restart frontend
```

### Arrêter les services

```bash
# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v
```

### Reconstruire après modification

```bash
# Reconstruire les images
docker-compose build --no-cache

# Relancer
docker-compose up
```

---

## ✅ Vérification

### Vérifier que l'API fonctionne

```bash
# Health check
curl http://localhost:8000/health

# Test de prédiction
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"sentence": "Je vais de Paris à Lyon"}'
```

### Vérifier les conteneurs

```bash
# Voir les conteneurs en cours d'exécution
docker-compose ps

# Voir les logs d'un conteneur
docker logs t-aia-911-lil3-api
docker logs t-aia-911-lil3-frontend
```

---

## 🔍 Dépannage

### Erreur : "Aucun modèle CamemBERT trouvé"

**Solution :**
1. Vérifiez que vous avez entraîné un modèle CamemBERT :
   ```bash
   ls classifier/models/validity_classifier_camembert_*/
   ```

2. Si aucun modèle n'existe, entraînez-en un :
   - Lancez Jupyter : `docker-compose up jupyter`
   - Ouvrez http://localhost:8888
   - Exécutez le notebook : `classifier/notebooks/03_validity_classifier_camembert_gpu.ipynb`

3. Les modèles sont montés en volume, donc ils sont disponibles dans le conteneur

### Erreur : "Aucun modèle NLP trouvé"

**Solution :**
1. Vérifiez que vous avez entraîné un modèle NLP :
   ```bash
   ls nlp/models/spacy_ner_*/
   ```

2. Si aucun modèle n'existe, entraînez-en un avec Jupyter

### L'API ne répond pas

**Vérifications :**
1. Le conteneur est-il en cours d'exécution ?
   ```bash
   docker-compose ps
   ```

2. Voir les logs pour les erreurs :
   ```bash
   docker-compose logs api
   ```

3. Vérifier que le port 8000 n'est pas déjà utilisé :
   ```bash
   lsof -i :8000
   ```

### Le frontend ne se connecte pas à l'API

**Solution :**
1. Vérifiez que l'API est lancée et accessible :
   ```bash
   curl http://localhost:8000/health
   ```

2. Ouvrez la console du navigateur (F12) pour voir les erreurs

3. Le frontend détecte automatiquement l'URL de l'API :
   - Si accès via `localhost:3000` → utilise `http://localhost:8000`
   - Si dans Docker → utilise `http://api:8000`

---

## 📦 Structure des volumes

Les modèles sont montés en volumes pour persister entre les redémarrages :

```
./classifier/models → /workspace/classifier/models
./nlp/models → /workspace/nlp/models
```

Cela signifie que :
- ✅ Les modèles entraînés sont conservés
- ✅ Les modifications du code sont visibles (hot-reload)
- ✅ Pas besoin de reconstruire l'image après entraînement

---

## 🎨 Personnalisation

### Changer les ports

Dans `docker-compose.yml` :

```yaml
api:
  ports:
    - "8001:8000"  # Changer 8000 en 8001

frontend:
  ports:
    - "3001:3000"  # Changer 3000 en 3001
```

### Modifier les variables d'environnement

Dans `docker-compose.yml` :

```yaml
api:
  environment:
    - LOG_LEVEL=debug
    - MODEL_PATH=/workspace/classifier/models
```

---

## 🚀 Script de lancement rapide

Créez un script `lancer_chatbot_docker.sh` :

```bash
#!/bin/bash
echo "🚀 Lancement du chatbot avec Docker..."

# Construire si nécessaire
if [ "$1" == "--build" ]; then
    echo "🔨 Construction des images..."
    docker-compose build
fi

# Lancer les services
echo "📡 Démarrage des services..."
docker-compose up api frontend

echo "✅ Chatbot accessible sur http://localhost:3000"
```

Rendez-le exécutable :
```bash
chmod +x lancer_chatbot_docker.sh
./lancer_chatbot_docker.sh
```

---

## 📚 Ressources

- **Docker Compose** : https://docs.docker.com/compose/
- **FastAPI** : https://fastapi.tiangolo.com/
- **Documentation API** : http://localhost:8000/docs (quand l'API est lancée)

---

**Besoin d'aide ?** Consultez les logs avec `docker-compose logs -f`

