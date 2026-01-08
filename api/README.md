# API - Extraction d'Intentions de Voyage

API FastAPI pour extraire les destinations de départ et d'arrivée depuis des phrases.

## Structure

- `pipeline.py` : Pipeline complet qui charge les modèles et effectue les prédictions
- `main.py` : API FastAPI qui expose le service

## Utilisation

### Avec Docker

```bash
docker compose up api
```

L'API sera accessible sur `http://localhost:8000`

### Sans Docker

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer l'API
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

## Endpoints

### GET `/`
Page d'accueil avec la documentation

### GET `/health`
Vérifie l'état de l'API

### POST `/predict`
Analyse une phrase et extrait les destinations

**Requête:**
```json
{
  "sentence": "Je vais de Paris à Lyon"
}
```

**Réponse (phrase valide):**
```json
{
  "valid": true,
  "message": null,
  "departure": "Paris",
  "arrival": "Lyon"
}
```

**Réponse (phrase invalide):**
```json
{
  "valid": false,
  "message": "Merci de rentrer une phrase valide",
  "departure": null,
  "arrival": null
}
```

## Documentation interactive

Une fois l'API lancée, accédez à :
- Swagger UI : `http://localhost:8000/docs`
- ReDoc : `http://localhost:8000/redoc`

## Test

```bash
python scripts/test_pipeline.py
```

