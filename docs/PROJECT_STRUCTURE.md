# Structure du Projet

## 📁 Organisation des Dossiers

```
T-AIA-911-LIL_3/
│
├── dataset/                    # Datasets bruts et scripts de génération
│   ├── travel_dataset.csv
│   ├── extended_travel_dataset.csv
│   ├── travel_dataset_50k.csv
│   └── generate_*.py
│
├── notebooks/                  # Notebooks Jupyter pour exploration et expérimentation
│   └── 01_dataset_exploration_and_baseline.ipynb
│
├── models/                     # Modèles entraînés sauvegardés
│   ├── baseline/              # Modèles baseline (régression logistique, etc.)
│   └── transformers/          # Modèles transformers (CamemBERT, FlauBERT, etc.)
│
├── results/                    # Résultats d'évaluation et analyses
│   ├── metrics/               # Métriques (CSV, JSON)
│   ├── visualizations/        # Graphiques et visualisations
│   └── confusion_matrices/    # Matrices de confusion
│
├── logs/                       # Logs d'entraînement et d'évaluation
│   ├── training/             # Logs d'entraînement
│   └── evaluation/           # Logs d'évaluation
│
├── scripts/                    # Scripts Python réutilisables
│   └── utils/                 # Fonctions utilitaires
│
├── configs/                    # Fichiers de configuration (YAML, JSON)
│
├── checkpoints/                # Checkpoints pendant l'entraînement
│
├── evaluations/                # Analyses détaillées des performances
│   └── error_analysis/        # Analyses d'erreurs
│
├── exports/                    # Modèles et artefacts prêts pour production
│   └── production/            # Modèles optimisés pour déploiement
│
├── dataset_overview.md         # Documentation du dataset
├── ROADMAP.md                  # Roadmap du projet
└── PROJECT_STRUCTURE.md        # Ce fichier
```

## 🎯 Usage des Dossiers

### `dataset/`
- Contient tous les datasets CSV/JSON
- Scripts de génération de données
- **Ne pas modifier directement** - utiliser les scripts

### `notebooks/`
- Exploration et expérimentation
- Analyse des données
- Développement itératif
- **Versionner les notebooks** pour garder une trace

### `models/`
- Sauvegarder les modèles entraînés
- Inclure le vectorizer/preprocessor associé
- Métadonnées (version, date, métriques)
- **Format** : `.pkl`, `.joblib`, ou format HuggingFace

### `results/`
- Tous les résultats d'évaluation
- Métriques comparatives
- Visualisations pour rapports
- **Organiser par date/expérience**

### `logs/`
- Logs d'entraînement (loss, accuracy, etc.)
- Logs d'évaluation
- Tracking avec TensorBoard, wandb, MLflow
- **Ne pas versionner les logs volumineux**

### `scripts/`
- Code réutilisable
- Fonctions utilitaires
- Scripts d'entraînement automatisés
- **Bien documenter les fonctions**

### `configs/`
- Hyperparamètres des modèles
- Configuration du preprocessing
- Paramètres d'expérimentation
- **Versionner les configs** pour reproductibilité

### `checkpoints/`
- Sauvegardes intermédiaires
- Reprise d'entraînement
- Early stopping
- **Nettoyer régulièrement** (garder seulement les meilleurs)

### `evaluations/`
- Analyses détaillées
- Rapports d'erreurs
- Comparaisons de modèles
- **Documenter les insights**

### `exports/`
- Modèles finaux validés
- Pipelines de production
- APIs et endpoints
- **Versionner les exports** pour déploiement

## 📝 Conventions

### Nommage des Fichiers

- **Modèles** : `{model_type}_{date}_{version}.{ext}`
  - Exemple : `logistic_regression_2024-01-15_v1.pkl`

- **Résultats** : `{model_type}_{metric}_{date}.{ext}`
  - Exemple : `logistic_regression_metrics_2024-01-15.csv`

- **Configs** : `{model_type}_config.yaml`
  - Exemple : `baseline_config.yaml`

- **Notebooks** : `{number}_{description}.ipynb`
  - Exemple : `01_dataset_exploration_and_baseline.ipynb`

### Git

- **Versionner** : code, configs, notebooks, documentation
- **Ignorer** : logs volumineux, checkpoints intermédiaires, modèles lourds
- Utiliser `.gitkeep` pour tracker les dossiers vides

### Documentation

- Chaque dossier a un `README.md` expliquant son usage
- Documenter les décisions importantes
- Garder la roadmap à jour

## 🚀 Workflow Typique

1. **Exploration** : `notebooks/` → Analyser les données
2. **Preprocessing** : `scripts/utils/` → Créer les fonctions
3. **Configuration** : `configs/` → Définir les hyperparamètres
4. **Entraînement** : `scripts/` → Exécuter les scripts
5. **Sauvegarde** : `models/` → Sauvegarder les modèles
6. **Évaluation** : `results/` → Analyser les performances
7. **Analyse** : `evaluations/` → Comprendre les erreurs
8. **Export** : `exports/` → Préparer pour production

## 📊 Tracking des Expériences

Pour chaque expérience, créer un dossier avec :
- Configuration utilisée
- Résultats obtenus
- Modèle sauvegardé
- Notes et observations

Exemple : `experiments/exp_001_baseline_lr/`

---

**Note** : Cette structure est évolutive et peut être adaptée selon les besoins du projet.

