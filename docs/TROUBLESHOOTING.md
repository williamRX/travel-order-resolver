# Guide de Dépannage

## Problèmes Docker

### Les services ne démarrent pas

1. **Vérifier que Docker est en cours d'exécution**
   ```bash
   docker ps
   ```

2. **Vérifier les logs**
   ```bash
   docker compose logs api
   docker compose logs frontend
   ```

3. **Reconstruire les images**
   ```bash
   docker compose down
   docker compose build --no-cache
   docker compose up
   ```

### L'API ne répond pas

1. **Vérifier que le service est démarré**
   ```bash
   docker compose ps
   ```

2. **Vérifier les logs pour les erreurs**
   ```bash
   docker compose logs -f api
   ```

3. **Tester l'API directement**
   ```bash
   curl http://localhost:8000/health
   ```

4. **Vérifier que les modèles existent**
   - Les modèles doivent être dans `classifier/models/` et `nlp/models/`
   - Si les modèles n'existent pas, entraînez-les d'abord avec les notebooks

### Le frontend ne s'affiche pas

1. **Vérifier que le service frontend est démarré**
   ```bash
   docker compose ps
   ```

2. **Vérifier les logs**
   ```bash
   docker compose logs frontend
   ```

3. **Accéder directement au fichier**
   - Ouvrir `http://localhost:8080` dans le navigateur
   - Vérifier la console du navigateur (F12) pour les erreurs

4. **Vérifier la connexion à l'API**
   - Le frontend pointe vers `http://localhost:8000`
   - Vérifier que l'API est accessible depuis le navigateur

### Erreur "Pipeline non initialisé"

Cette erreur signifie que les modèles n'ont pas pu être chargés.

1. **Vérifier que les modèles existent**
   ```bash
   ls classifier/models/*.joblib
   ls nlp/models/spacy_ner_*/
   ```

2. **Vérifier les chemins dans le conteneur**
   ```bash
   docker compose exec api ls -la /workspace/classifier/models/
   docker compose exec api ls -la /workspace/nlp/models/
   ```

3. **Vérifier les logs au démarrage de l'API**
   - L'API devrait afficher "✅ Classifieur chargé" et "✅ Modèle NLP chargé"
   - Si ces messages n'apparaissent pas, il y a un problème de chargement

### Erreur "Module not found"

1. **Reconstruire l'image Docker**
   ```bash
   docker compose build --no-cache
   ```

2. **Vérifier que requirements.txt contient toutes les dépendances**

### Les ports sont déjà utilisés

Si vous obtenez une erreur "port already in use" :

1. **Vérifier ce qui utilise les ports**
   ```bash
   # macOS/Linux
   lsof -i :8000
   lsof -i :8080
   lsof -i :8888
   ```

2. **Changer les ports dans docker-compose.yml**
   ```yaml
   ports:
     - "8001:8000"  # Au lieu de 8000:8000
   ```

3. **Mettre à jour l'URL dans le frontend**
   - Modifier `API_URL` dans `frontend/index.html`

## Problèmes de Modèles

### Modèles non trouvés

1. **Entraîner les modèles d'abord**
   - Ouvrir `classifier/notebooks/02_validity_classifier.ipynb`
   - Exécuter toutes les cellules pour entraîner le classifieur
   - Ouvrir `nlp/notebooks/01_ner_training.ipynb`
   - Exécuter toutes les cellules pour entraîner le modèle NLP

2. **Vérifier les chemins**
   - Les modèles doivent être dans `classifier/models/` et `nlp/models/`
   - Le pipeline cherche automatiquement les modèles les plus récents

## Commandes Utiles

```bash
# Voir tous les conteneurs
docker compose ps

# Voir les logs en temps réel
docker compose logs -f

# Redémarrer un service
docker compose restart api

# Arrêter tous les services
docker compose down

# Nettoyer complètement
docker compose down -v
docker system prune -a

# Exécuter une commande dans un conteneur
docker compose exec api python scripts/test_pipeline.py
```

## Diagnostic Complet

Utilisez le script de diagnostic :
```bash
./scripts/check_docker.sh
```

