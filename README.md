# T-AIA-911-LIL_3 - Système de Traitement NLP pour Phrases de Trajet

Projet en deux parties :
1. **Classifieur de Validité** : Détecte si une phrase contient une intention de trajet valide
2. **Modèle NLP** : Extrait les destinations de départ et d'arrivée des phrases valides

## 🚀 Démarrage Rapide

### Option 1 : Avec Conda (Recommandé pour ML)

```bash
# 1. Installer Conda si ce n'est pas déjà fait
# Télécharger depuis https://www.anaconda.com/products/distribution

# 2. Créer l'environnement
conda env create -f environment.yml

# 3. Activer l'environnement
conda activate t-aia-911-lil3

# 4. Lancer Jupyter
jupyter notebook
# ou
jupyter lab
```

### Option 2 : Avec pip et venv (Standard Python)

```bash
# 1. Créer un environnement virtuel
python3 -m venv venv

# 2. Activer l'environnement
# Sur macOS/Linux:
source venv/bin/activate
# Sur Windows:
# venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer Jupyter
jupyter notebook
# ou
jupyter lab
```

### Option 3 : Avec Docker (Isolation complète)

```bash
# 1. Construire l'image Docker
docker-compose build

# 2. Lancer le conteneur avec Jupyter
docker-compose up

# 3. Accéder à Jupyter sur http://localhost:8888
# Le dataset sera généré automatiquement s'il n'existe pas
# Pas de token/password requis (à sécuriser en production)
```

**Note** : Le conteneur génère automatiquement le dataset au démarrage s'il n'existe pas encore.

## 📋 Prérequis

- **Python 3.8+** (recommandé: Python 3.10)
- **Jupyter Notebook** ou **Jupyter Lab**
- Optionnel: **Conda** ou **Docker**

### 🚀 Pour Mac Apple Silicon (M1/M2/M3/M4) - Utilisation du GPU

Si vous êtes sur un Mac Apple Silicon et souhaitez utiliser le GPU pour accélérer l'entraînement :

1. **Installez PyTorch avec support MPS** :
   ```bash
   ./scripts/install_pytorch_mps.sh
   # ou manuellement:
   pip install torch torchvision torchaudio
   ```

2. **Vérifiez la configuration** :
   ```bash
   python scripts/verify_mps.py
   ```

3. **Consultez le guide complet** : [`docs/MPS_GPU_SETUP.md`](docs/MPS_GPU_SETUP.md)

Le notebook détectera automatiquement MPS et utilisera le GPU si disponible.

## 📦 Structure du Projet

Le projet est organisé par **domaine** pour faciliter la navigation :

```
T-AIA-911-LIL_3/
├── classifier/          # 🎯 Classifieur de Validité
│   ├── models/         # Modèles entraînés
│   ├── results/        # Résultats d'évaluation
│   ├── notebooks/      # Notebooks d'entraînement
│   ├── checkpoints/    # Checkpoints d'entraînement
│   └── logs/           # Logs d'entraînement
│
├── nlp/                # 🔍 Modèle NLP (Extraction des destinations)
│   ├── models/         # Modèles NLP entraînés
│   ├── results/        # Résultats d'évaluation
│   ├── notebooks/      # Notebooks d'entraînement
│   ├── checkpoints/    # Checkpoints d'entraînement
│   └── logs/           # Logs d'entraînement
│
├── dataset/            # 📊 Datasets et générateurs
│   ├── json/           # Datasets JSON/JSONL
│   ├── csv/            # Datasets CSV
│   └── generators/     # Scripts de génération
│
├── api/                # 🌐 API FastAPI
│   ├── pipeline.py     # Pipeline complet (Classifieur + NLP)
│   └── main.py         # API FastAPI
│
├── frontend/           # 💻 Interface Web
│   └── index.html      # Chatbot interactif
│
├── scripts/            # 🔧 Scripts utilitaires
│   └── test_pipeline.py # Test du pipeline complet
│
├── docs/               # 📚 Documentation
└── notebooks/          # 📓 Notebooks généraux (exploration, etc.)
```

**Avantages de cette structure** :
- ✅ Séparation claire entre les deux modèles
- ✅ Facilite la navigation et la maintenance
- ✅ Chaque domaine a ses propres modèles, résultats, notebooks

## 🎯 Utilisation

### 🚀 Système Complet (API + Front-end)

Le projet inclut maintenant un système complet avec API et interface web :

#### Avec Docker (Recommandé)

```bash
# Lancer tous les services (Jupyter, API, Front-end)
docker compose up

# Ou lancer uniquement l'API et le front-end
docker compose up api frontend
```

**Services disponibles :**
- **Jupyter Lab** : `http://localhost:8888`
- **API** : `http://localhost:8000`
- **Front-end (Chatbot)** : `http://localhost:8080`

#### Sans Docker

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Lancer l'API (dans un terminal)
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# 3. Ouvrir le front-end (dans un autre terminal)
# Option A: Ouvrir directement index.html dans le navigateur
# Option B: Servir avec un serveur HTTP
python -m http.server 8080 --directory frontend
```

**Utilisation :**
1. Ouvrez `http://localhost:8080` dans votre navigateur
2. Entrez une phrase dans le chatbot
3. Le système vérifie d'abord si la phrase est valide avec le classifieur
4. Si valide, extrait les destinations avec le modèle NLP
5. Affiche les résultats : `{départ: "Ville1", arrivée: "Ville2"}`

**Test du pipeline :**
```bash
python scripts/test_pipeline.py
```

Pour plus de détails, voir :
- [Documentation API](api/README.md)
- [Documentation Front-end](frontend/README.md)

---

### 1. Générer le Dataset

```bash
python dataset/generators/dataset_generator.py
```

Génère `dataset/json/dataset.jsonl` avec 10 000 phrases (70% valides, 30% invalides).

### 2. Entraîner le Classifieur

Ouvrir le notebook `classifier/notebooks/02_validity_classifier.ipynb` dans Jupyter et exécuter toutes les cellules.

Le notebook :
- Charge le dataset
- Prépare les données (TF-IDF)
- Entraîne un modèle de classification binaire
- Sauvegarde des checkpoints pendant l'entraînement
- Évalue les performances
- Sauvegarde le modèle final

### 3. Utiliser le Modèle Entraîné

```python
import joblib

# Charger le modèle
model = joblib.load('classifier/models/logistic_regression_XXX_v1.joblib')
vectorizer = joblib.load('classifier/models/vectorizer_XXX_v1.joblib')

# Prédire sur une nouvelle phrase
sentence = "Je vais de Paris à Lyon"
sentence_tfidf = vectorizer.transform([sentence])
prediction = model.predict(sentence_tfidf)[0]
probability = model.predict_proba(sentence_tfidf)[0]

print(f"Valide: {prediction == 1}, Confiance: {probability[1]:.2%}")
```

## 🔧 Configuration

Les paramètres sont centralisés dans le notebook `classifier/notebooks/02_validity_classifier.ipynb` :

- **MODEL_TYPE** : Type de modèle (`logistic_regression`, `svm`, `random_forest`, `gradient_boosting`)
- **SAVE_CHECKPOINTS** : Activer/désactiver les checkpoints
- **TEST_SIZE** : Proportion pour le test set (défaut: 0.2)
- **MAX_FEATURES** : Nombre de features TF-IDF (défaut: 10000)

## 📊 Résultats

Les résultats sont sauvegardés dans :
- **Classifieur** :
  - `classifier/models/` : Modèles entraînés
  - `classifier/results/{experiment_name}/` : Métriques et visualisations
  - `classifier/checkpoints/{experiment_name}/` : Checkpoints d'entraînement
- **NLP** (à venir) :
  - `nlp/models/` : Modèles NLP entraînés
  - `nlp/results/{experiment_name}/` : Métriques et visualisations
  - `nlp/checkpoints/{experiment_name}/` : Checkpoints d'entraînement

## ✅ Vérifier l'Installation

Après l'installation, vérifiez que tout fonctionne :

```bash
python scripts/check_installation.py
```

Ce script vérifie :
- ✅ Toutes les dépendances sont installées
- ✅ Les fichiers du projet sont présents
- ✅ Les dossiers nécessaires existent

## 🐛 Dépannage

### Problème : ModuleNotFoundError

Assurez-vous d'avoir activé l'environnement virtuel :
```bash
# Conda
conda activate t-aia-911-lil3

# venv
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate  # Windows
```

### Problème : Jupyter ne trouve pas les modules

Installez ipykernel dans votre environnement :
```bash
pip install ipykernel
python -m ipykernel install --user --name=t-aia-911-lil3
```

Puis sélectionnez ce kernel dans Jupyter.

### Problème : Chemin du dataset incorrect

Le notebook détecte automatiquement le chemin. Si problème, modifiez `PROJECT_ROOT` dans la cellule de configuration.

## 📚 Documentation

- [Structure du Projet](docs/PROJECT_STRUCTURE.md)
- [Vue d'ensemble du Dataset](docs/dataset_overview.md)
- [Roadmap](docs/ROADMAP.md)
- [Pipeline du Dataset](docs/DATASET_PIPELINE.md)

## 🤝 Contribution

1. Créer une branche pour votre feature
2. Faire vos modifications
3. Tester avec le notebook
4. Créer une pull request

## 📝 Licence

[À compléter selon votre licence]

## 👥 Auteurs

[À compléter]

---

**Note** : Pour toute question, consulter la documentation dans `docs/` ou ouvrir une issue.

