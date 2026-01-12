# Guide d'Installation Détaillé

Ce guide vous accompagne étape par étape pour configurer le projet.

## 🎯 Choisir sa Méthode d'Installation

### Pour les Débutants
👉 **Recommandation : Conda** (Option 1)
- Installation simple
- Gère automatiquement les dépendances
- Très populaire en Machine Learning

### Pour les Utilisateurs Python Expérimentés
👉 **Recommandation : pip + venv** (Option 2)
- Standard Python
- Plus léger
- Contrôle total

### Pour l'Isolation Complète
👉 **Recommandation : Docker** (Option 3)
- Environnement identique pour tous
- Pas besoin d'installer Python localement
- Idéal pour le déploiement

---

## 📦 Option 1 : Installation avec Conda

### Étape 1 : Installer Conda

**Si vous n'avez pas Conda :**

👉 **Guide détaillé complet** : Voir [`docs/INSTALL_CONDA.md`](docs/INSTALL_CONDA.md) pour les instructions pas à pas.

**Résumé rapide :**

1. **Télécharger Miniconda** (recommandé, plus léger) :
   - https://docs.conda.io/en/latest/miniconda.html
   - Choisir "Miniconda3 macOS Apple Silicon 64-bit pkg" pour Mac M4 Max
   - Ou Anaconda (plus complet) : https://www.anaconda.com/products/distribution

2. **Installer** : Double-cliquer sur le fichier `.pkg` et suivre l'assistant

3. **Fermer et rouvrir le terminal**

4. **Vérifier l'installation** :
   ```bash
   conda --version
   ```

**Si `conda` n'est pas reconnu**, initialiser Conda :
```bash
conda init zsh  # Pour zsh (terminal par défaut macOS)
# Puis fermer et rouvrir le terminal
```

### Étape 2 : Créer l'Environnement

```bash
# Se placer dans le dossier du projet
cd T-AIA-911-LIL_3

# Créer l'environnement depuis le fichier environment.yml
conda env create -f environment.yml
```

Cela va créer un environnement nommé `t-aia-911-lil3` avec toutes les dépendances.

### Étape 3 : Activer l'Environnement

```bash
# Activer l'environnement
conda activate t-aia-911-lil3

# Vérifier que Python est bien celui de l'environnement
which python  # macOS/Linux
# ou
where python  # Windows
```

### Étape 4 : Lancer Jupyter

```bash
# Lancer Jupyter Notebook
jupyter notebook

# OU lancer Jupyter Lab (interface plus moderne)
jupyter lab
```

Un navigateur s'ouvrira automatiquement. Si ce n'est pas le cas, copiez l'URL affichée dans le terminal.

### Étape 5 : Ouvrir le Notebook

Dans Jupyter, naviguez vers `notebooks/02_validity_classifier.ipynb` et exécutez les cellules.

---

## 🐍 Option 2 : Installation avec pip et venv

### Étape 1 : Vérifier Python

```bash
# Vérifier la version de Python (doit être 3.8+)
python3 --version
```

Si Python n'est pas installé, téléchargez-le depuis https://www.python.org/downloads/

### Étape 2 : Créer un Environnement Virtuel

```bash
# Se placer dans le dossier du projet
cd T-AIA-911-LIL_3

# Créer l'environnement virtuel
python3 -m venv venv
```

### Étape 3 : Activer l'Environnement

**Sur macOS/Linux :**
```bash
source venv/bin/activate
```

**Sur Windows (PowerShell) :**
```powershell
venv\Scripts\Activate.ps1
```

**Sur Windows (CMD) :**
```cmd
venv\Scripts\activate.bat
```

Vous devriez voir `(venv)` au début de votre ligne de commande.

### Étape 4 : Installer les Dépendances

```bash
# Mettre à jour pip
pip install --upgrade pip

# Installer toutes les dépendances
pip install -r requirements.txt
```

### Étape 5 : Configurer Jupyter Kernel (Important)

```bash
# Installer ipykernel
pip install ipykernel

# Créer un kernel Jupyter pour cet environnement
python -m ipykernel install --user --name=t-aia-911-lil3
```

### Étape 6 : Lancer Jupyter

```bash
jupyter notebook
# ou
jupyter lab
```

**Important :** Dans Jupyter, sélectionnez le kernel `t-aia-911-lil3` (menu Kernel > Change Kernel).

---

## 🐳 Option 3 : Installation avec Docker

### Étape 1 : Installer Docker

1. Télécharger Docker Desktop : https://www.docker.com/products/docker-desktop
2. Installer selon votre système
3. Lancer Docker Desktop
4. Vérifier l'installation :
```bash
docker --version
docker-compose --version
```

### Étape 2 : Construire l'Image

```bash
# Se placer dans le dossier du projet
cd T-AIA-911-LIL_3

# Construire l'image Docker
docker-compose build
```

Cela peut prendre quelques minutes la première fois.

### Étape 3 : Lancer le Conteneur

```bash
# Démarrer Jupyter
docker-compose up

# Pour lancer en arrière-plan :
docker-compose up -d
```

### Étape 4 : Accéder à Jupyter

1. Ouvrir un navigateur
2. Aller sur http://localhost:8888
3. Le token est affiché dans les logs du conteneur

Pour voir les logs :
```bash
docker-compose logs jupyter
```

### Étape 5 : Arrêter le Conteneur

```bash
# Arrêter le conteneur
docker-compose down

# Arrêter et supprimer les volumes (attention : supprime les données)
docker-compose down -v
```

---

## ✅ Vérification de l'Installation

Après l'installation, testez que tout fonctionne :

```python
# Dans un terminal Python ou dans Jupyter
import pandas as pd
import numpy as np
import sklearn
import matplotlib
import seaborn
import joblib

print("✅ Toutes les dépendances sont installées !")
```

---

## 🐛 Problèmes Courants

### "ModuleNotFoundError: No module named 'X'"

**Solution :**
- Vérifiez que l'environnement est activé (vous devriez voir `(venv)` ou `(t-aia-911-lil3)`)
- Réinstallez les dépendances : `pip install -r requirements.txt`

### "Jupyter ne trouve pas les modules"

**Solution :**
- Assurez-vous d'avoir créé le kernel : `python -m ipykernel install --user --name=t-aia-911-lil3`
- Dans Jupyter, changez le kernel (Kernel > Change Kernel > t-aia-911-lil3)

### "Permission denied" avec Docker

**Solution :**
- Sur Linux, vous pourriez avoir besoin de `sudo`
- Vérifiez que Docker Desktop est lancé

### "Port 8888 already in use"

**Solution :**
- Arrêtez l'autre instance de Jupyter
- Ou changez le port dans `docker-compose.yml` :
```yaml
ports:
  - "8889:8888"  # Utiliser le port 8889 au lieu de 8888
```

---

## 📚 Prochaines Étapes

Une fois l'installation terminée :

1. **Générer le dataset** :
   ```bash
   python dataset/generators/dataset_generator.py
   ```

2. **Ouvrir le notebook** :
   - Ouvrir `notebooks/02_validity_classifier.ipynb` dans Jupyter
   - Exécuter toutes les cellules

3. **Consulter la documentation** :
   - Lire `README.md` pour l'utilisation
   - Consulter `docs/` pour plus de détails

---

## 💡 Astuces

- **Conda** : Pour mettre à jour l'environnement après modification de `environment.yml` :
  ```bash
  conda env update -f environment.yml --prune
  ```

- **venv** : Pour désactiver l'environnement :
  ```bash
  deactivate
  ```

- **Docker** : Pour voir les logs en temps réel :
  ```bash
  docker-compose logs -f jupyter
  ```

---

Besoin d'aide ? Consultez la documentation dans `docs/` ou ouvrez une issue.

