# Classifieur de Validité des Phrases

Ce dossier contient tout ce qui est lié au **classifieur de validité** des phrases de trajet.

## 📁 Structure

```
classifier/
├── models/          # Modèles entraînés (vectorizer, classifier, metadata)
├── results/         # Résultats d'évaluation (métriques, graphiques, analyses d'erreurs)
├── notebooks/       # Notebooks Jupyter pour l'entraînement et l'évaluation
├── checkpoints/     # Checkpoints intermédiaires pendant l'entraînement
└── logs/            # Logs d'entraînement
    └── training/
```

## 🎯 Objectif

Le classifieur détermine si une phrase contient une **intention de trajet valide** ou non. Il filtre les phrases avant le traitement NLP pour ne traiter que les phrases pertinentes.

## 📊 Modèles Disponibles

- `validity_classifier_20260104_181633_v1` - Premier modèle entraîné
- `validity_classifier_20260104_184906_v1` - Modèle avec dataset amélioré

## 🔄 Workflow

1. **Entraînement** : Exécuter `notebooks/02_validity_classifier.ipynb`
2. **Évaluation** : Les résultats sont sauvegardés dans `results/`
3. **Analyse** : Consulter `results/*/MODEL_ERRORS_ANALYSIS.md` pour les erreurs
4. **Déploiement** : Utiliser les modèles dans `models/`

## 📝 Notes

- Les modèles sont sauvegardés avec timestamp pour traçabilité
- Chaque expérience génère un dossier dans `results/` avec toutes les métriques
- Les checkpoints permettent de reprendre l'entraînement ou d'analyser l'évolution

## 📓 Journal de Bord

Consultez [`JOURNAL.md`](JOURNAL.md) pour un suivi des problèmes rencontrés et des solutions apportées au classifieur.

