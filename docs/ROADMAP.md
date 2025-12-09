# Roadmap - Dataset Optimization & NLP Model Training

## 🎯 Objectif Global

Créer un dataset optimisé pour l'entraînement de modèles NLP de classification (VALID/INVALID/AMBIGU), en commençant par une régression logistique comme baseline, puis en évoluant vers des modèles plus avancés.

---

## 📋 Phase 1: Exploration & Analyse du Dataset

### 1.1 Chargement et Inspection Initiale
- [ ] Charger les datasets existants (travel_dataset.csv, extended_travel_dataset.csv, travel_dataset_50k.csv)
- [ ] Analyser la structure des données (colonnes, types, valeurs manquantes)
- [ ] Vérifier la distribution des classes (VALID/INVALID/AMBIGU)
- [ ] Identifier les doublons et les incohérences

### 1.2 Analyse Statistique
- [ ] Distribution des longueurs de phrases
- [ ] Analyse de la fréquence des mots
- [ ] Identification des patterns récurrents
- [ ] Analyse des fautes d'orthographe et variations
- [ ] Statistiques par classe (moyenne de mots, complexité)

### 1.3 Visualisations
- [ ] Graphiques de distribution des classes
- [ ] Histogrammes de longueurs de phrases
- [ ] Nuages de mots (word clouds) par classe
- [ ] Analyse des villes les plus fréquentes

---

## 📋 Phase 2: Nettoyage & Préparation des Données

### 2.1 Consolidation des Datasets
- [ ] Fusionner les différents fichiers CSV
- [ ] Supprimer les doublons exacts
- [ ] Uniformiser le format (colonnes, encodage)
- [ ] Vérifier et corriger les labels (VALID/INVALID/AMBIGU)

### 2.2 Nettoyage du Texte
- [ ] Normalisation des espaces multiples
- [ ] Gestion des caractères spéciaux
- [ ] Normalisation des accents (optionnel selon stratégie)
- [ ] Suppression des emojis (ou conversion en texte)
- [ ] Gestion de la casse (lowercase vs. préservation)

### 2.3 Détection et Gestion des Doublons Approximatifs
- [ ] Utiliser des techniques de similarité (fuzzy matching)
- [ ] Identifier les phrases quasi-identiques
- [ ] Décision : supprimer ou conserver avec variation

### 2.4 Équilibrage des Classes
- [ ] Analyser la distribution actuelle
- [ ] Appliquer la distribution cible (70% INVALID, 25% VALID, 5% AMBIGU)
- [ ] Techniques : undersampling, oversampling, ou génération de nouvelles données
- [ ] Créer train/validation/test splits équilibrés

---

## 📋 Phase 3: Feature Engineering

### 3.1 Extraction de Features Basiques
- [ ] Longueur de la phrase (nombre de caractères, mots)
- [ ] Nombre de villes mentionnées
- [ ] Présence de mots-clés (trajet, aller, depuis, vers, etc.)
- [ ] Présence de prépositions de mouvement
- [ ] Nombre de verbes d'action

### 3.2 Features Linguistiques
- [ ] POS tagging (Part-of-Speech)
- [ ] Détection d'entités nommées (NER) - villes
- [ ] Analyse de dépendances syntaxiques
- [ ] Détection de patterns (regex pour structures communes)

### 3.3 Features Statistiques
- [ ] TF-IDF sur les mots
- [ ] N-grams (bigrams, trigrams)
- [ ] Caractéristiques de caractères (n-grams de caractères)
- [ ] Features de similarité (cosine similarity avec phrases de référence)

---

## 📋 Phase 4: Baseline Model - Régression Logistique

### 4.1 Préparation pour ML
- [ ] Vectorisation du texte (CountVectorizer, TfidfVectorizer)
- [ ] Sélection des features les plus importantes
- [ ] Normalisation/standardisation si nécessaire
- [ ] Création des splits train/validation/test (70/15/15 ou 80/10/10)

### 4.2 Entraînement du Modèle
- [ ] Initialisation du modèle de régression logistique
- [ ] Grid search ou random search pour hyperparamètres
  - Régularisation (L1, L2, C)
  - Solver (liblinear, lbfgs, saga)
  - max_iter
- [ ] Entraînement sur le dataset d'entraînement
- [ ] Validation croisée (cross-validation)

### 4.3 Évaluation
- [ ] Métriques sur validation set :
  - Accuracy
  - Precision, Recall, F1-score (par classe et macro/micro)
  - Matrice de confusion
  - Classification report
- [ ] Métriques sur test set (évaluation finale)
- [ ] Analyse des erreurs (confusion matrix, exemples mal classés)

### 4.4 Analyse des Features
- [ ] Importance des features (coefficients du modèle)
- [ ] Identification des mots/features les plus discriminants
- [ ] Visualisation des poids des features

---

## 📋 Phase 5: Optimisation & Amélioration

### 5.1 Analyse des Erreurs
- [ ] Identifier les patterns d'erreurs récurrents
- [ ] Analyser les cas ambigus mal classés
- [ ] Examiner les faux positifs et faux négatifs
- [ ] Créer une liste de cas edge à améliorer

### 5.2 Amélioration du Dataset
- [ ] Générer des exemples pour les cas problématiques
- [ ] Augmentation de données (data augmentation)
- [ ] Rééquilibrage ciblé des classes difficiles
- [ ] Ajout de features supplémentaires si nécessaire

### 5.3 Réentraînement
- [ ] Réentraîner avec le dataset amélioré
- [ ] Comparer les performances avant/après
- [ ] Itérer jusqu'à satisfaction des métriques

---

## 📋 Phase 6: Modèles Avancés (Futur)

### 6.1 Word Embeddings
- [ ] Utilisation de word2vec, GloVe, ou FastText
- [ ] Embeddings pré-entraînés en français
- [ ] Features moyennes ou concaténées des embeddings

### 6.2 Modèles Transformer
- [ ] Fine-tuning de CamemBERT ou FlauBERT
- [ ] Utilisation de modèles pré-entraînés
- [ ] Comparaison avec le baseline

### 6.3 Optimisation Avancée
- [ ] Hyperparameter tuning avec Optuna ou Ray Tune
- [ ] Ensemble methods
- [ ] Optimisation pour production (quantization, pruning)

---

## 📋 Phase 7: Production & Déploiement

### 7.1 Pipeline de Prédiction
- [ ] Créer un pipeline de preprocessing
- [ ] Sauvegarder le modèle et le vectorizer
- [ ] Créer une API ou fonction de prédiction
- [ ] Gestion des cas edge (phrases vides, très longues, etc.)

### 7.2 Monitoring
- [ ] Logging des prédictions
- [ ] Métriques de performance en production
- [ ] Détection de drift (changement de distribution)
- [ ] Système de feedback pour amélioration continue

---

## 📊 Métriques de Succès

### Baseline (Régression Logistique)
- **Objectif:** F1-score macro > 0.85
- **Précision VALID:** > 0.90 (critique pour éviter faux positifs)
- **Recall VALID:** > 0.80
- **Temps de prédiction:** < 10ms par phrase

### Modèles Avancés
- **Objectif:** F1-score macro > 0.92
- **Amélioration:** +5-10% par rapport au baseline

---

## 🛠️ Outils & Technologies

- **Notebooks:** Jupyter Notebook / JupyterLab
- **Data Processing:** pandas, numpy
- **NLP:** scikit-learn, nltk, spacy (optionnel)
- **ML:** scikit-learn (LogisticRegression)
- **Visualisation:** matplotlib, seaborn, plotly
- **Version Control:** Git (déjà en place)
- **Documentation:** Markdown

---

## 📝 Structure du Notebook

Le notebook sera organisé en sections correspondant aux phases :

1. **Setup & Imports**
2. **Phase 1: Exploration**
3. **Phase 2: Nettoyage**
4. **Phase 3: Feature Engineering**
5. **Phase 4: Baseline Model**
6. **Phase 5: Optimisation**
7. **Phase 6: Modèles Avancés** (futur)
8. **Phase 7: Production** (futur)

---

## 🎯 Prochaines Étapes Immédiates

1. Créer le notebook Jupyter de base avec la structure
2. Commencer par la Phase 1 (Exploration)
3. Documenter les découvertes au fur et à mesure
4. Itérer rapidement sur les premières phases

---

**Note:** Cette roadmap est évolutive et sera mise à jour au fur et à mesure des découvertes et des besoins du projet.

