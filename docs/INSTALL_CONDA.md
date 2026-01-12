# Guide d'Installation de Conda sur macOS

Ce guide vous explique comment installer Conda sur votre Mac Apple Silicon (M4 Max).

## 🎯 Choix entre Anaconda et Miniconda

### Anaconda (Recommandé pour débutants)
- **Taille** : ~500 MB
- **Avantages** : Inclut beaucoup de packages pré-installés (pandas, numpy, jupyter, etc.)
- **Inconvénients** : Plus lourd, installation plus longue

### Miniconda (Recommandé pour utilisateurs expérimentés)
- **Taille** : ~50 MB
- **Avantages** : Léger, installation rapide, vous installez seulement ce dont vous avez besoin
- **Inconvénients** : Vous devez installer les packages manuellement

**💡 Recommandation** : Miniconda est généralement préféré car plus léger et vous gardez le contrôle.

---

## 📦 Installation de Miniconda (Recommandé)

### Étape 1 : Télécharger Miniconda

1. **Ouvrez votre navigateur** et allez sur : https://docs.conda.io/en/latest/miniconda.html

2. **Téléchargez la version pour macOS Apple Silicon (arm64)** :
   - Cherchez "Miniconda3 macOS Apple M1 64-bit pkg" ou "Miniconda3 macOS Apple Silicon 64-bit pkg"
   - Le fichier se termine par `.pkg` et fait environ 50-60 MB

   **Lien direct** (peut changer selon la version) :
   ```
   https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.pkg
   ```

### Étape 2 : Installer Miniconda

1. **Double-cliquez sur le fichier `.pkg`** téléchargé
2. **Suivez l'assistant d'installation** :
   - Cliquez sur "Continuer"
   - Acceptez les conditions d'utilisation
   - Choisissez l'emplacement d'installation (par défaut : `/Users/votre_nom/miniconda3`)
   - Cliquez sur "Installer"
   - Entrez votre mot de passe administrateur si demandé

### Étape 3 : Vérifier l'installation

**Fermez et rouvrez votre terminal**, puis exécutez :

```bash
conda --version
```

Vous devriez voir quelque chose comme : `conda 23.x.x` ou similaire.

Si vous obtenez une erreur "command not found", continuez avec l'étape 4.

### Étape 4 : Initialiser Conda (si nécessaire)

Si `conda` n'est pas reconnu, initialisez-le :

```bash
# Pour zsh (terminal par défaut sur macOS récent)
conda init zsh

# Pour bash (si vous utilisez bash)
conda init bash
```

**Fermez et rouvrez votre terminal** après cette commande.

---

## 📦 Installation d'Anaconda (Alternative)

Si vous préférez Anaconda :

1. **Téléchargez Anaconda** : https://www.anaconda.com/products/distribution
   - Choisissez "macOS" et "64-Bit (M1) Graphical Installer" pour Apple Silicon
   - Le fichier fait environ 500 MB

2. **Double-cliquez sur le fichier `.pkg`** et suivez l'assistant d'installation

3. **Fermez et rouvrez votre terminal**

4. **Vérifiez l'installation** :
   ```bash
   conda --version
   ```

---

## ✅ Vérification finale

Après l'installation, testez Conda :

```bash
# Vérifier la version
conda --version

# Vérifier que Conda fonctionne
conda info

# Lister les environnements (devrait être vide au début)
conda env list
```

---

## 🚀 Prochaines étapes

Une fois Conda installé, vous pouvez :

1. **Créer l'environnement du projet** :
   ```bash
   cd /Users/williamroux/Documents/Projets/T-AIA-911-LIL_3
   conda env create -f environment.yml
   ```

2. **Activer l'environnement** :
   ```bash
   conda activate t-aia-911-lil3
   ```

3. **Installer PyTorch avec support MPS** :
   ```bash
   pip install torch torchvision torchaudio
   ```

4. **Vérifier MPS** :
   ```bash
   python scripts/verify_mps.py
   ```

5. **Lancer Jupyter** :
   ```bash
   jupyter notebook
   # ou
   jupyter lab
   ```

---

## 🔧 Dépannage

### Conda n'est pas reconnu après l'installation

1. **Vérifiez que Conda est dans votre PATH** :
   ```bash
   echo $PATH | grep conda
   ```

2. **Si rien n'apparaît, ajoutez Conda manuellement** :
   ```bash
   # Pour zsh
   echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   
   # Pour bash
   echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> ~/.bash_profile
   source ~/.bash_profile
   ```

3. **Ou réinitialisez Conda** :
   ```bash
   conda init zsh  # ou bash
   ```

### Erreur "zsh: command not found: conda"

- Fermez complètement votre terminal et rouvrez-le
- Ou exécutez : `source ~/.zshrc` (ou `source ~/.bash_profile` pour bash)

### Problèmes avec Apple Silicon

- Assurez-vous d'avoir téléchargé la version **arm64** (Apple Silicon), pas la version Intel
- Vérifiez votre architecture : `uname -m` (devrait afficher `arm64`)

---

## 📚 Ressources

- **Documentation Miniconda** : https://docs.conda.io/en/latest/miniconda.html
- **Documentation Anaconda** : https://docs.anaconda.com/anaconda/install/
- **Guide Conda** : https://docs.conda.io/projects/conda/en/latest/user-guide/

---

**Besoin d'aide ?** Consultez les logs d'erreur ou ouvrez une issue sur le dépôt du projet.

