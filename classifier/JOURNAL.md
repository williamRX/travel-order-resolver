# Journal de Bord - Classifieur de Validité

Ce journal documente les problèmes rencontrés, les solutions apportées et les améliorations effectuées sur le classifieur de validité des phrases de trajet.

---

## 📝 Format des entrées

Chaque entrée du journal doit suivre ce format :

### 📅 Date - Titre court

#### 🐛 Problème rencontré

**Contexte :** Description de la situation

**Problème :** Description claire du problème

**Cause :** Analyse de la cause racine (si identifiée)

#### ✅ Solution appliquée

**Fichier(s) modifié(s) :** Liste des fichiers

**Changement :** Description des modifications

**Code modifié :** Exemples de code avant/après si pertinent

#### 📊 Résultat

- Liste des résultats obtenus
- Métriques de performance si applicable

#### 🔍 Points d'attention pour l'avenir

- Leçons apprises
- Bonnes pratiques à retenir

---

## 📚 Notes générales

### Modèles disponibles

- **CamemBERT** : Modèles de classifieurs basés sur CamemBERT pour la classification de séquences
  - Format : `validity_classifier_camembert_YYYYMMDD_HHMMSS_v1/`
  - Localisation : `classifier/models/`

- **Baseline (TF-IDF + Logistic Regression)** : Modèles classiques
  - Format : `logistic_regression_*.joblib` + `vectorizer_*.joblib`
  - Localisation : `classifier/models/`

### Bonnes pratiques

- Toujours vérifier que les modèles sont correctement chargés avant de les utiliser en production
- Tester sur des phrases variées après chaque modification
- Documenter les métriques de performance après entraînement

---
