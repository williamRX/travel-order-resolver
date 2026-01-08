# Dataset - Organisation par Modèle

Ce dossier contient tous les datasets organisés par domaine (classifieur et NLP).

## 📁 Structure

```
dataset/
├── classifier/          # 🎯 Datasets pour le Classifieur de Validité
│   ├── json/            # Datasets JSON/JSONL
│   │   ├── dataset.jsonl              # Dataset principal (10k phrases)
│   │   └── travel_dataset_50k.json    # Dataset étendu (50k phrases)
│   └── csv/             # Datasets CSV (conversions)
│
├── nlp/                 # 🔍 Datasets pour le Modèle NLP
│   ├── json/            # Datasets JSON/JSONL annotés
│   ├── csv/             # Datasets CSV annotés
│   └── annotations/     # Données d'entraînement annotées
│       └── jsonl_extracteur/
│           └── spacy_training_data.jsonl
│
├── shared/              # 📚 Données partagées
│   └── gares-francaises.json  # Liste des gares françaises (référence)
│
└── generators/          # 🔧 Générateurs de datasets
    ├── classifier/      # Générateurs pour le classifieur
    │   ├── dataset_generator.py
    │   ├── generate_50k_dataset.py
    │   └── generate_dataset.py
    └── nlp/             # Générateurs pour le NLP (à venir)
```

## 🎯 Classifieur

### Dataset Principal
- **Fichier** : `classifier/json/dataset.jsonl`
- **Format** : JSONL (une ligne par phrase)
- **Contenu** : 10 000 phrases (70% valides, 30% invalides)
- **Structure** :
  ```json
  {"sentence": "...", "departure": "... or null", "arrival": "... or null", "is_valid": 0/1}
  ```

### Génération
```bash
python dataset/generators/classifier/dataset_generator.py
```

## 🔍 NLP

### Dataset d'Entraînement
- **Fichier** : `nlp/annotations/jsonl_extracteur/spacy_training_data.jsonl`
- **Format** : JSONL annoté pour Spacy
- **Contenu** : Phrases valides annotées avec départ/arrivée

### Génération
Les datasets NLP seront générés à partir des phrases validées par le classifieur.

## 📚 Données Partagées

- **gares-francaises.json** : Liste complète des gares françaises utilisée comme référence pour la génération de datasets

## 🔄 Workflow

1. **Générer le dataset du classifieur** :
   ```bash
   python dataset/generators/classifier/dataset_generator.py
   ```

2. **Entraîner le classifieur** avec `classifier/json/dataset.jsonl`

3. **Filtrer les phrases valides** pour créer le dataset NLP

4. **Annoter les phrases valides** pour l'entraînement du modèle NLP

5. **Entraîner le modèle NLP** avec les données annotées

## 📝 Notes

- Les datasets sont versionnés par timestamp dans les noms de fichiers
- Les CSV sont des conversions des JSON pour faciliter l'analyse
- Les données partagées sont utilisées par tous les générateurs

