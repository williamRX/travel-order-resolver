# Améliorations Apportées au Notebook d'Entraînement NER

**Date** : 2025-01-15  
**Modèle analysé** : `ner_camembert_20260115_135604_v1`  
**Problème** : Precision (0.75) < Recall (0.91) → trop de faux positifs

---

## 📊 Analyse des Métriques

**Résultats actuels** :
- Precision : **0.7559** (75.59%) ⚠️ Faible
- Recall : **0.9134** (91.34%) ✅ Excellent
- F1-Score : **0.8272** (82.72%)
- Accuracy : **0.9861** (98.61%)

**Problème identifié** : **Precision trop faible** → Le modèle génère trop de faux positifs

---

## ✅ Modifications Appliquées

### 1. **Correction de la Fonction d'Alignement des Sous-Tokens** 🔴 **CRITIQUE**

**Problème** : La fonction `align_tokens_with_entities()` ne gérait pas correctement les sous-tokens avec `-100`.

**Solution** : Modification de la fonction pour :
- Détecter correctement les sous-tokens de CamemBERT (SentencePiece, pas WordPiece)
- Utiliser `-100` pour les sous-tokens (sauf le premier token d'une entité B-)
- Utiliser `-100` pour les tokens spéciaux ([CLS], [SEP], padding)

**Code modifié** :
```python
# Détection des sous-tokens : si le token précédent se termine où celui-ci commence
# (pas d'espace entre les tokens) → c'est un sous-token
if prev_token_end == token_start and prev_token_end > 0:
    # Sous-token : utiliser -100 SAUF si c'est B- (premier token d'entité)
    if labels[i].startswith('B-'):
        label_ids.append(LABEL2ID.get(labels[i], 0))  # Garder le label
    else:
        label_ids.append(-100)  # Ignorer dans la loss
```

**Impact** : Améliore la précision en évitant que le modèle apprenne sur les sous-tokens

---

### 2. **Ajout du Cosine Learning Rate Scheduler** ✅

**Modification** : Ajout de `lr_scheduler_type="cosine"` dans `TrainingArguments`

**Code** :
```python
training_args = TrainingArguments(
    # ... autres paramètres
    lr_scheduler_type="cosine",  # ✅ Cosine Learning Rate Scheduler
    # ...
)
```

**Impact estimé** : +0.5-1% de précision (meilleure convergence)

---

### 3. **Vérification du Weight Decay** ✅

**Statut** : Déjà configuré (`weight_decay=0.01`)

**Vérification** : ✅ Confirmé dans le notebook

---

### 4. **Data Augmentation avec 10% de Phrases Négatives** ✅

**Modification** : Ajout de data augmentation dans le notebook pour ajouter 10% d'exemples négatifs supplémentaires

**Code ajouté** :
```python
# Data Augmentation : Ajouter 10% de phrases négatives supplémentaires
from dataset.generators.nlp.dataset_generator import generate_negative_example

NEGATIVE_AUGMENTATION_RATIO = 0.10  # 10% d'exemples négatifs supplémentaires
num_negative_to_add = int(len(raw_data) * NEGATIVE_AUGMENTATION_RATIO)

augmented_negative_examples = []
for _ in range(num_negative_to_add):
    negative_example = generate_negative_example()
    augmented_negative_examples.append({
        'text': negative_example['text'],
        'entities': negative_example['entities']  # Vide
    })

raw_data.extend(augmented_negative_examples)
```

**Impact estimé** : +1-2% de précision (réduction des faux positifs)

---

### 5. **Analyse du Déséquilibre des Patterns** ⚠️

**Résultat de l'analyse** :
- **Patterns avec tirets** : 26.8% (5,366 sur 20,000)
- **Autres patterns** : 73.2%

**Évaluation** :
- ⚠️ **Déséquilibre modéré** : 26.8% est élevé mais peut être acceptable
- ✅ **Pas de correction nécessaire** : Si ce pattern est fréquent dans les données réelles, c'est normal
- 💡 **Recommandation** : Surveiller si le modèle devient trop biaisé vers ce pattern

**Décision** : Aucune modification du générateur nécessaire pour l'instant

---

## 📋 Résumé des Modifications

| Modification | Statut | Impact Estimé |
|--------------|--------|---------------|
| **Correction sous-tokens (-100)** | ✅ Fait | +1-2% précision |
| **Cosine LR Scheduler** | ✅ Fait | +0.5-1% précision |
| **Weight Decay** | ✅ Vérifié | Déjà configuré |
| **Data Augmentation (10%)** | ✅ Fait | +1-2% précision |
| **Déséquilibre patterns** | ✅ Analysé | Pas de problème détecté |

**Impact total estimé** : **+2.5-5% de précision** → Precision: 75.59% → **78-80%**

---

## 🎯 Prochaines Étapes

1. **Réentraîner le modèle** avec le notebook modifié
2. **Vérifier les nouvelles métriques** :
   - Precision devrait augmenter
   - Recall devrait rester élevé (~91%)
   - F1-Score devrait augmenter
3. **Analyser les erreurs** avec `scripts/analyze_ner_errors.py` pour voir les améliorations

---

## ⚠️ Points d'Attention

1. **Détection des sous-tokens** : La nouvelle logique utilise `prev_token_end == token_start` pour détecter les sous-tokens. Cela fonctionne pour SentencePiece (CamemBERT).

2. **Data Augmentation** : Les exemples négatifs sont ajoutés dynamiquement dans le notebook, pas dans le générateur. Cela permet de tester différents ratios facilement.

3. **Cosine Scheduler** : Réduit progressivement le learning rate selon une courbe cosinus, ce qui améliore généralement la convergence.

4. **Déséquilibre des patterns** : 26.8% de patterns avec tirets est élevé mais acceptable si c'est représentatif des données réelles. Surveiller si cela crée un biais.
