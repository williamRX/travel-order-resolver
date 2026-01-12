# Configuration Docker - Guide Complet

## ✅ État de la Dockerisation

### Services Dockerisés

Le projet est **entièrement dockerisé** avec 3 services :

1. **Jupyter Lab** (port 8888)
   - Environnement de développement pour les notebooks
   - Support pour tous les notebooks (classifier classique et CamemBERT)
   - Accès : http://localhost:8888

2. **API FastAPI** (port 8000)
   - API REST pour le pipeline NLP
   - Accès : http://localhost:8000
   - Documentation : http://localhost:8000/docs

3. **Frontend** (port 3000)
   - Interface web simple
   - Accès : http://localhost:3000

### Dépendances Installées dans Docker

Le Dockerfile installe automatiquement toutes les dépendances depuis `requirements.txt`, incluant :

- ✅ **Core** : pandas, numpy, scikit-learn
- ✅ **NLP** : spacy, transformers
- ✅ **Deep Learning** : torch (PyTorch), transformers, accelerate
- ✅ **API** : fastapi, uvicorn, pydantic
- ✅ **Jupyter** : jupyter, jupyterlab, ipykernel
- ✅ **Utilitaires** : joblib, tqdm, matplotlib, seaborn

### Volumes Persistants

Les volumes suivants sont montés pour persister les données :

**Modèles et résultats :**
- `./models` → `/workspace/models` (modèles baseline)
- `./classifier/models` → `/workspace/classifier/models` (modèles classifier)
- `./classifier/checkpoints` → `/workspace/classifier/checkpoints`
- `./classifier/results` → `/workspace/classifier/results`
- `./classifier/logs` → `/workspace/classifier/logs`
- `./nlp/models` → `/workspace/nlp/models` (modèles NLP)
- `./nlp/checkpoints` → `/workspace/nlp/checkpoints`
- `./nlp/results` → `/workspace/nlp/results`
- `./nlp/logs` → `/workspace/nlp/logs`

**Données :**
- Tout le projet est monté en volume (`.:/workspace`)
- Les modifications sont visibles immédiatement dans le conteneur

**Jupyter :**
- Volume nommé `jupyter-data` pour persister les configurations Jupyter

## 🚀 Utilisation

### Lancer les services

```bash
# Lancer uniquement Jupyter (recommandé pour le développement)
docker compose up jupyter

# Lancer tous les services
docker compose up

# Lancer en arrière-plan
docker compose up -d
```

### Reconstruire l'image (après modification de requirements.txt)

```bash
# Reconstruire et relancer
docker compose build --no-cache
docker compose up jupyter
```

### Accéder aux notebooks

1. Lancer Jupyter : `docker compose up jupyter`
2. Ouvrir http://localhost:8888 dans votre navigateur
3. Les notebooks sont dans `/workspace/classifier/notebooks/`

### Utiliser le notebook CamemBERT

Le notebook `03_validity_classifier_camembert.ipynb` fonctionne directement dans Docker car :
- ✅ `torch` et `transformers` sont installés dans l'image
- ✅ Toutes les dépendances sont disponibles
- ✅ Pas besoin d'installer manuellement les packages

## 📝 Notes Importantes

### Dataset automatique

Le `docker-entrypoint.sh` vérifie automatiquement si le dataset existe et le génère si nécessaire au démarrage de Jupyter.

### GPU Support (optionnel)

Pour utiliser un GPU avec PyTorch dans Docker, vous devez :

1. Installer [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
2. Modifier `docker-compose.yml` pour ajouter :
   ```yaml
   deploy:
     resources:
       reservations:
         devices:
           - driver: nvidia
             count: 1
             capabilities: [gpu]
   ```

### Rebuild après modification de requirements.txt

Si vous modifiez `requirements.txt`, vous devez reconstruire l'image :

```bash
docker compose build --no-cache jupyter
docker compose up jupyter
```

## 🔧 Dépannage

### Problème : "Module not found" dans le notebook

**Solution** : Reconstruire l'image Docker après avoir ajouté la dépendance dans `requirements.txt`

```bash
docker compose build --no-cache
docker compose up jupyter
```

### Problème : Port déjà utilisé

**Solution** : Modifier les ports dans `docker-compose.yml` ou arrêter le service qui utilise le port

```bash
# Voir les ports utilisés
docker compose ps

# Arrêter un service
docker compose stop jupyter
```

### Problème : Modèles non sauvegardés

**Solution** : Vérifier que les volumes sont bien montés dans `docker-compose.yml`

## ✅ Checklist de Dockerisation

- [x] Dockerfile configuré avec toutes les dépendances
- [x] docker-compose.yml avec 3 services (jupyter, api, frontend)
- [x] Volumes persistants pour modèles et résultats
- [x] docker-entrypoint.sh pour génération automatique du dataset
- [x] Support pour notebooks classiques (TF-IDF + scikit-learn)
- [x] Support pour notebooks CamemBERT (transformers + torch)
- [x] Documentation Docker complète

## 📚 Ressources

- [Guide d'utilisation Docker](DOCKER_USAGE.md) - Commandes utiles
- [Troubleshooting Docker](TROUBLESHOOTING.md) - Solutions aux problèmes courants

