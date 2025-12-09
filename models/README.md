# Models Directory

Ce dossier contient tous les modèles entraînés sauvegardés.

## Structure

- **`baseline/`** : Modèles baseline (régression logistique, SVM, etc.)
- **`transformers/`** : Modèles basés sur des transformers (CamemBERT, FlauBERT, etc.)

## Format de sauvegarde

Les modèles sont sauvegardés avec :
- Le modèle lui-même (`.pkl`, `.joblib`, ou format HuggingFace)
- Le vectorizer/preprocessor associé
- Un fichier de métadonnées (version, date, métriques)

## Convention de nommage

`{model_type}_{date}_{version}.{ext}`

Exemple : `logistic_regression_2024-01-15_v1.pkl`

