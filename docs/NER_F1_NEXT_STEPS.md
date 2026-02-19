# Prochaines Étapes pour Améliorer le F1-Score NER

**Date** : 2025-01-15  
**Modèle actuel** : `ner_camembert_20260115_111644_v1`  
**F1-Score actuel** : **85.71%** (amélioration de +2.63 points depuis le modèle précédent)

---

## 📊 État Actuel

### Métriques du Modèle Actuel

| Métrique | Valeur | Évolution |
|----------|--------|-----------|
| **F1-Score** | **85.71%** | +3.17% ✅ |
| **Precision** | 79.40% | +4.88% ✅ |
| **Recall** | 93.12% | +1.16% ✅ |
| **Accuracy** | 98.57% | +0.16% ✅ |

### Analyse

**Points forts** :
- ✅ **Recall excellent** (93.12%) : Le modèle détecte très bien les vraies entités
- ✅ **Amélioration significative de la précision** (+4.88%) grâce aux corrections des tirets et au post-processing
- ✅ **F1-Score en progression constante** : 83.08% → 85.71%

**Points à améliorer** :
- 🔴 **Precision encore limitée** (79.40%) : Encore ~20% de faux positifs
- 🟡 **Gap Precision/Recall** : 79.40% vs 93.12% (écart de 13.72 points)

---

## 🎯 Objectifs pour la Prochaine Itération

### Objectif Réaliste : F1-Score **87-89%**

**Cible** :
- Precision : 79.40% → **82-84%** (+2.6-4.6 points)
- Recall : 93.12% → **92-93%** (maintenir)
- **F1-Score : 85.71% → 87-89%** (+1.3-3.3 points)

---

## 🚀 Axes d'Amélioration Prioritaires

### 1. **Enrichir le Dataset avec Exemples Négatifs** 🔴 **PRIORITÉ 1**

**Problème** : Le modèle génère encore ~20% de faux positifs (noms propres, villes inconnues, etc.)

**Solution** : Ajouter des exemples où des mots similaires à des villes ne sont PAS des entités.

#### A. Patterns avec Noms Propres (Prénoms)

**Exemples à ajouter** :
```python
# Patterns négatifs (pas d'annotation)
"Mon ami Pierre veut partir" → aucune entité
"Je vais voir Victor demain" → aucune entité
"Marie et Paul sont là" → aucune entité
"Mon copain Thomas arrive" → aucune entité
```

**Impact estimé** : Réduction de ~10-15% des faux positifs sur noms propres

#### B. Patterns avec Pays

**Exemples à ajouter** :
```python
# Patterns négatifs
"Je vais en Tunisie" → aucune entité
"Je pars pour la Turquie" → aucune entité
"Voyage en Inde" → aucune entité
```

**Impact estimé** : Réduction de ~2-3% des faux positifs

#### C. Patterns avec Villes Hors Contexte

**Exemples à ajouter** :
```python
# Patterns négatifs
"Paris est une belle ville" → aucune entité
"J'aime beaucoup Lyon" → aucune entité
"Marseille est au sud" → aucune entité
"Le restaurant Le Paris est bon" → aucune entité
```

**Impact estimé** : Réduction de ~5-8% des faux positifs

#### D. Patterns avec Noms Composés Non-Gares

**Exemples à ajouter** :
```python
# Patterns négatifs
"Je vais au restaurant Le Paris" → aucune entité
"Le monument de Lyon est beau" → aucune entité
"La gare de Paris est grande" → "Paris" est une entité, mais "gare de Paris" ne doit pas être annoté comme entité complète
```

**Impact estimé** : Réduction de ~3-5% des faux positifs

**Total estimé** : Réduction de ~20-31% des faux positifs → **+3-5% de précision**

---

### 2. **Optimiser les Hyperparamètres** 🟡 **PRIORITÉ 2**

**Hyperparamètres actuels** :
- `learning_rate`: 2e-05
- `batch_size`: 16
- `num_epochs`: 3
- `max_length`: 128
- Pas de `weight_decay` visible

#### A. Ajuster le Learning Rate

**Recommandation** :
- **Réduire légèrement** : `2e-05` → `1.5e-05` ou `1e-05`
- **Raison** : Un learning rate plus bas peut améliorer la précision (moins de sur-apprentissage)

**Impact estimé** : +0.5-1% de précision

#### B. Ajouter Weight Decay (Régularisation L2)

**Recommandation** :
- **Ajouter** : `weight_decay=0.01` ou `0.001`
- **Raison** : Réduit le sur-apprentissage et peut améliorer la généralisation

**Impact estimé** : +0.5-1% de précision

#### C. Augmenter le Nombre d'Époques avec Early Stopping

**Recommandation** :
- **Augmenter** : `num_epochs`: 3 → `5-7`
- **Ajouter Early Stopping** : Arrêter si la précision sur validation ne s'améliore plus pendant 2-3 époques
- **Raison** : Plus d'époques peuvent améliorer les performances, mais avec early stopping pour éviter le sur-apprentissage

**Impact estimé** : +0.5-1.5% de F1

#### D. Ajuster le Batch Size

**Recommandation** :
- **Tester** : `batch_size`: 16 → `8` ou `32`
- **Raison** : Des batchs plus petits peuvent améliorer la généralisation

**Impact estimé** : +0.3-0.7% de F1

**Total estimé** : **+1.8-4.2% de F1-Score**

---

### 3. **Améliorer le Post-Processing** 🟡 **PRIORITÉ 3**

**Post-processing actuel** :
- ✅ Filtrage des lettres isolées (1-2 caractères)
- ✅ Filtrage des pays
- ✅ Validation par liste de gares

#### A. Améliorer la Validation par Liste de Gares

**Améliorations possibles** :
1. **Fuzzy matching** : Accepter des variations proches (ex: "Marseille" vs "Marseille Blancarde")
2. **Normalisation** : Gérer les accents, majuscules/minuscules, tirets
3. **Suffixes** : Gérer les suffixes comme "Blancarde" dans "Marseille Blancarde"

**Impact estimé** : +0.5-1% de précision

#### B. Ajouter des Règles Contextuelles

**Exemples** :
- Si une entité est détectée après "mon ami", "mon copain", etc. → probablement un prénom, pas une ville
- Si une entité est détectée après "en", "pour la", "vers la" et que c'est un pays → rejeter

**Impact estimé** : +0.3-0.7% de précision

**Total estimé** : **+0.8-1.7% de précision**

---

### 4. **Data Augmentation Ciblée** 🟢 **PRIORITÉ 4**

#### A. Augmenter la Diversité des Patterns avec Tirets

**Action** : S'assurer que tous les patterns avec tirets sont bien annotés
- Vérifier que "VilleA - VilleB" génère bien deux entités séparées
- Ajouter plus de variations : "VilleA-VilleB" (sans espaces), "VilleA – VilleB" (tiret long)

**Impact estimé** : +0.3-0.5% de précision

#### B. Augmenter la Diversité des Suffixes

**Action** : Ajouter plus de variations de suffixes après les villes
- "vers Paris rapidement", "vers Paris svp", "vers Paris merci", "vers Paris demain", etc.

**Impact estimé** : +0.2-0.4% de précision

**Total estimé** : **+0.5-0.9% de précision**

---

### 5. **Techniques Avancées** 🟢 **PRIORITÉ 5** (Si nécessaire)

#### A. Focal Loss

**Solution** : Utiliser Focal Loss au lieu de Cross-Entropy Loss
- Pénalise plus les faux positifs
- Impact estimé : +1-2% précision

#### B. Class Weights

**Solution** : Ajuster les poids des classes pour pénaliser plus les faux positifs
- Augmenter le poids de la classe "O" (Outside)
- Impact estimé : +0.5-1% précision

#### C. Fine-tuning avec Données Ciblées

**Solution** : Réentraîner sur un dataset enrichi avec les cas problématiques identifiés
- Impact estimé : +2-3% F1

---

## 📋 Plan d'Action Recommandé

### Phase 1 : Enrichissement du Dataset (1-2 jours) 🔴 **PRIORITÉ ABSOLUE**

1. **Ajouter des patterns négatifs** :
   - Noms propres (prénoms) : ~50-100 exemples
   - Pays : ~20-30 exemples
   - Villes hors contexte : ~50-100 exemples
   - Noms composés non-gares : ~30-50 exemples

2. **Modifier le générateur** :
   - Ajouter une fonction `generate_negative_examples()` dans `dataset/generators/nlp/dataset_generator.py`
   - Générer ~200-300 exemples négatifs par batch

3. **Régénérer le dataset** :
   ```bash
   python dataset/generators/nlp/dataset_generator.py
   ```

**Impact estimé** : **+3-5% de précision** → F1: 85.71% → **88-90%**

---

### Phase 2 : Optimisation des Hyperparamètres (1 jour)

1. **Modifier le notebook d'entraînement** :
   - Ajouter `weight_decay=0.01`
   - Réduire `learning_rate` à `1.5e-05`
   - Augmenter `num_epochs` à `5-7`
   - Ajouter early stopping

2. **Réentraîner le modèle**

**Impact estimé** : **+1.8-4.2% de F1**

---

### Phase 3 : Amélioration du Post-Processing (0.5 jour)

1. **Améliorer la validation par liste de gares** :
   - Ajouter fuzzy matching
   - Normalisation améliorée

2. **Ajouter des règles contextuelles** :
   - Détecter les contextes "mon ami", "mon copain", etc.
   - Filtrer les pays après "en", "pour la", etc.

**Impact estimé** : **+0.8-1.7% de précision**

---

## 📈 Projection des Résultats

### Scénario Optimiste

**Actions** : Phase 1 + Phase 2 + Phase 3
- Precision : 79.40% → **84-86%** (+4.6-6.6 points)
- Recall : 93.12% → **92-93%** (maintenir)
- **F1-Score : 85.71% → 88-90%** (+2.3-4.3 points)

### Scénario Réaliste

**Actions** : Phase 1 + Phase 2
- Precision : 79.40% → **82-84%** (+2.6-4.6 points)
- Recall : 93.12% → **92-93%** (maintenir)
- **F1-Score : 85.71% → 87-89%** (+1.3-3.3 points)

### Scénario Conservateur

**Actions** : Phase 1 uniquement
- Precision : 79.40% → **82-83%** (+2.6-3.6 points)
- Recall : 93.12% → **92-93%** (maintenir)
- **F1-Score : 85.71% → 87-88%** (+1.3-2.3 points)

---

## 🎯 Recommandation Finale

**Priorité immédiate** : **Phase 1 (Enrichissement du Dataset)**

**Raison** :
- ✅ Impact le plus élevé (+3-5% de précision)
- ✅ Relativement rapide à implémenter (1-2 jours)
- ✅ Pas de risque de régression
- ✅ Améliore directement le problème principal (faux positifs)

**Après Phase 1** :
- Si F1 < 88% → Passer à Phase 2 (Hyperparamètres)
- Si F1 >= 88% → Évaluer si Phase 3 est nécessaire

---

## 📝 Notes

- Le post-processing s'applique déjà automatiquement aux prédictions
- Les corrections des tirets sont déjà en place dans le générateur
- Le recall est excellent (93.12%), donc l'objectif principal est d'améliorer la précision
- Un F1-Score de 87-90% serait excellent pour un modèle NER en production
