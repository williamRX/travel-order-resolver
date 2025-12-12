# Scripts Directory

Ce dossier contient tous les scripts Python réutilisables.

## Structure

- **`utils/`** : Fonctions utilitaires
  - Preprocessing
  - Feature engineering
  - Evaluation helpers
  - Visualization helpers

## Scripts principaux

- `prepare_spacy_dataset.py` : Conversion de dataset.jsonl en format spaCy pour l'extraction de villes
- `train_baseline.py` : Entraînement du modèle baseline
- `train_transformer.py` : Entraînement des modèles transformers
- `evaluate_model.py` : Évaluation d'un modèle
- `predict.py` : Script de prédiction
- `preprocess_data.py` : Preprocessing des données

### prepare_spacy_dataset.py

Convertit le fichier `dataset.jsonl` en format spaCy pour l'entraînement d'un modèle NER (Named Entity Recognition) pour l'extraction de villes de départ et d'arrivée.

**Usage:**
```bash
python scripts/prepare_spacy_dataset.py
```

**Entrée:** `dataset/json/dataset.jsonl`
**Sortie:** `dataset/json/jsonl_extracteur/spacy_training_data.jsonl`

**Format de sortie:**
```json
{"text": "Je vais de Paris à Lyon", "entities": [[10, 15, "DEPARTURE"], [18, 22, "ARRIVAL"]]}
```

Le script :
- Filtre uniquement les phrases valides (is_valid=1)
- Extrait les positions des villes de départ et d'arrivée dans le texte
- Gère les variations (typos, casse, accents)
- Crée les annotations au format spaCy NER

## Utils

Fonctions communes réutilisables dans les notebooks et scripts.

