# Datasets - Modèle NLP

Ce dossier contient les datasets utilisés pour entraîner et évaluer le **modèle NLP** d'extraction des destinations.

## 📊 Datasets Disponibles

### 1. `annotations/jsonl_extracteur/spacy_training_data.jsonl`
- **Format** : JSONL annoté pour Spacy
- **Contenu** : Phrases valides annotées avec les entités (départ/arrivée)
- **Usage** : Entraînement du modèle Spacy

## 🔧 Génération

Les datasets NLP seront générés à partir des phrases validées par le classifieur.

### Workflow
1. Filtrer les phrases valides du dataset du classifieur
2. Annoter ces phrases avec les destinations de départ et d'arrivée
3. Convertir au format d'entraînement Spacy (JSONL)

## 📝 Format des Données

Format Spacy JSONL :
```json
{
  "text": "Je vais de Paris à Lyon",
  "entities": [
    {"start": 12, "end": 17, "label": "DEPARTURE"},
    {"start": 20, "end": 24, "label": "ARRIVAL"}
  ]
}
```

## 🎯 Utilisation

Les datasets seront utilisés par les notebooks dans `nlp/notebooks/` (à venir).

