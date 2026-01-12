# Guide d'utilisation Docker

## Services disponibles

- **Jupyter Lab** : Port 8888
- **API** : Port 8000
- **Frontend** : Port 3000

## Commandes utiles

### Lancer uniquement Jupyter

```bash
docker compose up jupyter
```

Ou en arrière-plan :
```bash
docker compose up -d jupyter
```

### Lancer uniquement l'API

```bash
docker compose up api
```

Ou en arrière-plan :
```bash
docker compose up -d api
```

### Lancer uniquement le Frontend

```bash
docker compose up frontend
```

Ou en arrière-plan :
```bash
docker compose up -d frontend
```

### Lancer plusieurs services

```bash
# Jupyter + API
docker compose up jupyter api

# Tous les services
docker compose up
```

### Arrêter un service spécifique

```bash
docker compose stop jupyter
docker compose stop api
docker compose stop frontend
```

### Arrêter tous les services

```bash
# Arrêter et supprimer les conteneurs (recommandé)
docker compose down

# Arrêter sans supprimer les conteneurs
docker compose stop

# Arrêter et supprimer les conteneurs + volumes (⚠️ supprime les données)
docker compose down -v

# Arrêter et supprimer les conteneurs + volumes + images (⚠️ supprime tout)
docker compose down --rmi all
```

### Voir les logs

```bash
# Logs de Jupyter
docker compose logs -f jupyter

# Logs de l'API
docker compose logs -f api

# Logs de tous les services
docker compose logs -f
```

### Redémarrer un service

```bash
docker compose restart jupyter
docker compose restart api
```

## Accès aux services

Une fois lancés :
- **Jupyter Lab** : http://localhost:8888
- **API** : http://localhost:8000
- **Frontend** : http://localhost:3000

## Notes importantes

- Les services sont indépendants : vous pouvez lancer uniquement celui dont vous avez besoin
- Les volumes sont partagés : les modifications dans le workspace sont visibles dans tous les conteneurs
- Les modèles et résultats sont persistés dans `./models`, `./results`, `./checkpoints`

