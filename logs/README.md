# Logs Directory

Ce dossier contient tous les logs d'entraînement et d'évaluation.

## Structure

- **`training/`** : Logs d'entraînement
  - Historique des epochs
  - Loss curves
  - Temps d'entraînement
  - Utilisation des ressources

- **`evaluation/`** : Logs d'évaluation
  - Résultats de tests
  - Métriques détaillées
  - Erreurs et warnings

## Format

- Logs texte : `.log` ou `.txt`
- Logs structurés : JSON
- TensorBoard logs : événements TensorBoard

## Outils recommandés

- TensorBoard pour visualisation
- Weights & Biases (wandb) pour tracking
- MLflow pour expérimentation

