# Checkpoints Directory

Ce dossier contient les checkpoints sauvegardés pendant l'entraînement.

## Usage

Les checkpoints permettent de :
- Reprendre l'entraînement après interruption
- Sauvegarder l'état à intervalles réguliers
- Implémenter early stopping

## Format

- Modèles scikit-learn : `.joblib` ou `.pkl`
- Modèles PyTorch : `.pt` ou `.pth`
- Modèles TensorFlow/Keras : `.h5` ou `.ckpt`
- Modèles HuggingFace : format standard HF

## Convention

`checkpoint_epoch_{epoch}_loss_{loss}.{ext}`

