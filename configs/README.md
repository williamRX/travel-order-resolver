# Configs Directory

Ce dossier contient les fichiers de configuration pour les différents modèles et expériences.

## Format

Fichiers YAML ou JSON avec les hyperparamètres et configurations.

## Exemples

- `baseline_config.yaml` : Configuration pour régression logistique
- `transformer_config.yaml` : Configuration pour modèles transformers
- `data_config.yaml` : Configuration du preprocessing

## Structure d'un config

```yaml
model:
  type: logistic_regression
  hyperparameters:
    C: 1.0
    solver: lbfgs
    max_iter: 1000

data:
  train_size: 0.8
  validation_size: 0.1
  test_size: 0.1

features:
  max_features: 5000
  ngram_range: [1, 2]
```

