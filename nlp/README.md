# Modèle NLP - Extraction des Destinations

Ce dossier contient tout ce qui est lié au **modèle NLP** pour l'extraction des destinations de départ et d'arrivée.

## 📁 Structure

```
nlp/
├── models/          # Modèles NLP entraînés (Spacy, transformers, etc.)
├── results/         # Résultats d'évaluation (métriques, graphiques)
├── notebooks/       # Notebooks Jupyter pour l'entraînement et l'évaluation
├── checkpoints/     # Checkpoints intermédiaires pendant l'entraînement
└── logs/            # Logs d'entraînement
    └── training/
```

## 🎯 Objectif

Le modèle NLP extrait les **destinations de départ** et les **destinations d'arrivée** à partir de phrases de trajet valides.

## 🔄 Workflow

1. **Préparation des données** : Utiliser les phrases validées par le classifieur
2. **Entraînement** : Exécuter les notebooks dans `notebooks/`
3. **Évaluation** : Les résultats sont sauvegardés dans `results/`
4. **Déploiement** : Utiliser les modèles dans `models/`

## 📝 Notes

- Ce modèle sera entraîné après le classifieur
- Il utilise uniquement les phrases validées comme valides
- Les modèles sont sauvegardés avec timestamp pour traçabilité

## 📓 Journal de Bord

Consultez [`JOURNAL.md`](JOURNAL.md) pour un suivi des problèmes rencontrés et des solutions apportées au modèle NLP.

