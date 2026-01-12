# Configuration GPU MPS pour Mac Apple Silicon

Ce guide vous explique comment configurer PyTorch pour utiliser le GPU de votre Mac M4 Max (ou autre Mac Apple Silicon) pour l'entraînement du classifieur CamemBERT.

## 🎯 Vue d'ensemble

Sur Mac Apple Silicon, PyTorch utilise **MPS (Metal Performance Shaders)** au lieu de CUDA (réservé à NVIDIA). MPS permet d'utiliser le GPU intégré pour accélérer l'entraînement.

## 📋 Prérequis

1. **Mac avec Apple Silicon** (M1, M2, M3, M4, etc.)
2. **macOS à jour** (recommandé: macOS 12.3 ou plus récent)
3. **Outils de ligne de commande Apple** installés

## 🚀 Installation

### Option 1 : Script automatique (Recommandé)

```bash
# Depuis la racine du projet
./scripts/install_pytorch_mps.sh
```

Le script va :
- Vérifier les prérequis
- Installer PyTorch avec support MPS
- Tester que MPS fonctionne correctement

### Option 2 : Installation manuelle

#### Étape 1 : Installer les outils de ligne de commande Apple

```bash
xcode-select --install
```

Si déjà installé, cette commande vous le dira.

#### Étape 2 : Créer un environnement virtuel (recommandé)

**Avec Conda :**
```bash
conda create -n machine_learning python=3.11 -y
conda activate machine_learning
```

**Avec venv :**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Étape 3 : Installer PyTorch avec support MPS

```bash
pip install torch torchvision torchaudio
```

Cette commande installe automatiquement la version de PyTorch avec support MPS pour macOS.

## ✅ Vérification

Pour vérifier que MPS est disponible, exécutez ce code Python :

```python
import torch

print(f"PyTorch version: {torch.__version__}")

if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
    mps_device = torch.device("mps")
    x = torch.ones(1, device=mps_device)
    print("✅ Succès ! Le tenseur est sur le GPU :", x)
    print("✅ MPS est disponible et fonctionne correctement")
else:
    print("❌ Erreur : MPS n'est pas détecté.")
    print("   Vérifiez que vous êtes sur un Mac Apple Silicon")
```

## 📓 Utilisation dans le Notebook

Le notebook `03_validity_classifier_camembert.ipynb` détecte automatiquement MPS et l'utilise si disponible.

### Cellule de vérification

Le notebook contient une cellule qui :
1. Vérifie si MPS est disponible
2. Configure automatiquement le device (`mps` ou `cpu`)
3. Teste que MPS fonctionne correctement

### Configuration automatique

Une fois MPS détecté, le notebook :
- Utilise automatiquement le GPU pour l'entraînement
- Désactive fp16 (MPS ne supporte pas fp16, contrairement à CUDA)
- Optimise les paramètres pour Apple Silicon

## 🔧 Dépannage

### MPS n'est pas détecté

1. **Vérifiez votre Mac** : Assurez-vous d'être sur un Mac Apple Silicon
   ```bash
   uname -m
   # Devrait afficher "arm64"
   ```

2. **Vérifiez la version de PyTorch** : Assurez-vous d'avoir PyTorch 2.0+
   ```python
   import torch
   print(torch.__version__)
   ```

3. **Réinstallez PyTorch** :
   ```bash
   pip uninstall torch torchvision torchaudio
   pip install torch torchvision torchaudio
   ```

### Erreurs pendant l'entraînement

Si vous rencontrez des erreurs avec MPS :

1. **Désactivez temporairement MPS** : Le notebook basculera automatiquement sur CPU
2. **Vérifiez les logs** : Les erreurs MPS sont généralement liées à des opérations non supportées
3. **Mettez à jour macOS** : Les versions récentes de macOS améliorent le support MPS

### Performance

- **MPS vs CPU** : MPS peut être 2-5x plus rapide que CPU pour l'entraînement
- **MPS vs CUDA** : MPS est généralement plus lent que CUDA, mais c'est la seule option sur Mac
- **Optimisation** : Utilisez des batch sizes adaptés (16-32 fonctionnent généralement bien)

## 📚 Ressources

- [Documentation PyTorch MPS](https://pytorch.org/docs/stable/notes/mps.html)
- [Guide Apple Metal](https://developer.apple.com/metal/)

## 💡 Notes importantes

1. **fp16 non supporté** : MPS ne supporte pas la précision mixte (fp16). Le notebook désactive automatiquement fp16 sur MPS.

2. **Compatibilité** : Toutes les opérations PyTorch ne sont pas encore supportées par MPS. Si une opération n'est pas supportée, PyTorch basculera automatiquement sur CPU pour cette opération.

3. **Jupyter** : Assurez-vous de lancer Jupyter depuis l'environnement où PyTorch est installé :
   ```bash
   conda activate machine_learning  # ou votre environnement
   jupyter notebook
   ```

## ✅ Checklist

- [ ] Outils de ligne de commande Apple installés
- [ ] Environnement virtuel créé et activé
- [ ] PyTorch installé avec `pip install torch torchvision torchaudio`
- [ ] MPS détecté avec le code de vérification
- [ ] Notebook exécuté avec succès

---

**Besoin d'aide ?** Consultez les logs d'erreur ou ouvrez une issue sur le dépôt du projet.

