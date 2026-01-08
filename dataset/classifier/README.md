# Datasets - Classifieur de Validité

Ce dossier contient les datasets utilisés pour entraîner et évaluer le **classifieur de validité**.

## 📊 Datasets Disponibles

### 1. `dataset.jsonl` (Principal)
- **Taille** : 10 000 phrases
- **Distribution** : 70% valides, 30% invalides
- **Format** : JSONL (une ligne par phrase)
- **Structure** :
  ```json
  {
    "sentence": "Je vais de Paris à Lyon",
    "departure": "Paris",
    "arrival": "Lyon",
    "is_valid": 1
  }
  ```

### 2. `travel_dataset_50k.json` (Étendu)
- **Taille** : 50 000 phrases
- **Format** : JSON
- **Usage** : Pour des expériences plus larges

## 🔧 Génération

```bash
# Depuis la racine du projet
python dataset/generators/classifier/dataset_generator.py
```

Le dataset sera généré dans `dataset/classifier/json/dataset.jsonl`.

## 📝 Format des Données

Chaque ligne du JSONL contient :
- `sentence` : La phrase à classifier
- `departure` : Ville de départ (ou `null` si absente)
- `arrival` : Ville d'arrivée (ou `null` si absente)
- `is_valid` : Label binaire (1 = valide, 0 = invalide)

## 🎯 Utilisation

Le dataset est utilisé par le notebook `classifier/notebooks/02_validity_classifier.ipynb`.

