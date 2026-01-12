# Scripts Directory

Ce dossier contient tous les scripts Python réutilisables.

## Structure

- **`utils/`** : Fonctions utilitaires
  - Preprocessing
  - Feature engineering
  - Evaluation helpers
  - Visualization helpers

## Scripts principaux

- `process_input.py` : **Script principal de traitement** - Lit des phrases au format `sentenceID,sentence` et génère le format de sortie spécifié
- `prepare_spacy_dataset.py` : Conversion de dataset.jsonl en format spaCy pour l'extraction de villes
- `test_pipeline.py` : Test du pipeline complet
- `test_ner_camembert.py` : Test spécifique du modèle NER CamemBERT
- `train_baseline.py` : Entraînement du modèle baseline
- `train_transformer.py` : Entraînement des modèles transformers
- `evaluate_model.py` : Évaluation d'un modèle
- `predict.py` : Script de prédiction
- `preprocess_data.py` : Preprocessing des données

### process_input.py

Script principal de traitement selon le format spécifié du sujet. Lit des phrases et génère les résultats au format attendu.

**Usage:**
```bash
# Depuis un fichier
python scripts/process_input.py --file input.csv > output.csv

# Depuis stdin
cat input.csv | python scripts/process_input.py

# Depuis URL
python scripts/process_input.py --url http://example.com/sentences.csv

# Spécifier fichier de sortie
python scripts/process_input.py --file input.csv --output output.csv
```

**Format d'entrée:** `sentenceID,sentence` (une ligne par phrase)
```
1,Je vais de Paris à Lyon
2,Billet Marseille Nice demain
3,Bonjour comment allez-vous?
```

**Format de sortie:**
- Phrases **valides** : `sentenceID,Departure,Destination`
- Phrases **invalides** : `sentenceID,INVALID`

```
1,Paris,Lyon
2,Marseille,Nice
3,INVALID
```

**Fonctionnalités:**
- Lit depuis fichier, stdin, ou URL
- Utilise le pipeline NLP complet (classification + NER)
- Gère les erreurs et lignes invalides
- Affiche des statistiques (valides/invalides)
- Support UTF-8

**Exemple:**
```bash
# Créer un fichier d'exemple
echo -e "1,Je vais de Paris à Lyon\n2,Bonjour" > test.csv

# Traiter
python scripts/process_input.py --file test.csv
# Output:
# 1,Paris,Lyon
# 2,INVALID
```

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

