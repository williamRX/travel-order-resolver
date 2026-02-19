# Stratégie d'Amélioration du F1-Score NER - Approche Avancée

**Date** : 2025-01-15  
**Situation** : Les exemples négatifs n'ont pas amélioré les performances (F1: 85.71% → 85.10%)  
**Objectif** : Atteindre 87-90% de F1-Score

---

## 🔍 Analyse de la Situation

### Résultats du Dernier Modèle

**Modèle avec exemples négatifs** (`ner_camembert_20260115_133236_v1`) :
- F1-Score : **85.10%** (-0.61% vs modèle précédent)
- Precision : 78.98% (-0.42%)
- Recall : 92.26% (-0.86%)

**Problème identifié** :
- Les exemples négatifs (20% du dataset) n'ont pas amélioré la précision
- Légère régression sur tous les métriques
- Le modèle semble avoir du mal à généraliser avec plus d'exemples négatifs

**Hypothèses** :
1. **Ratio d'exemples négatifs trop élevé** (20% vs 10-15% recommandé)
2. **Hyperparamètres non optimisés** (learning_rate, weight_decay, epochs)
3. **Loss function non adaptée** (Cross-Entropy standard ne pénalise pas assez les faux positifs)
4. **Pas de class weights** (toutes les classes ont le même poids)

---

## 🎯 Stratégies d'Amélioration Prioritaires

### 1. **Optimisation des Hyperparamètres** 🔴 **PRIORITÉ 1**

**Problème actuel** : Hyperparamètres par défaut non optimisés

**Solutions** :

#### A. Ajuster le Learning Rate

**Actuel** : `2e-05` (par défaut)  
**Recommandation** : `1e-05` ou `1.5e-05`

**Raison** : Un learning rate plus bas permet un apprentissage plus stable et peut améliorer la précision

**Code** :
```python
learning_rate = 1e-05  # Au lieu de 2e-05
```

#### B. Ajouter Weight Decay (Régularisation L2)

**Actuel** : Pas de weight_decay  
**Recommandation** : `weight_decay=0.01`

**Raison** : Réduit le sur-apprentissage et améliore la généralisation

**Code** :
```python
optimizer = AdamW(
    model.parameters(),
    lr=learning_rate,
    weight_decay=0.01  # Ajouter cette ligne
)
```

#### C. Augmenter le Nombre d'Époques avec Early Stopping

**Actuel** : `num_epochs=3`  
**Recommandation** : `num_epochs=5-7` avec early stopping

**Raison** : Plus d'époques peuvent améliorer les performances, mais avec early stopping pour éviter le sur-apprentissage

**Code** :
```python
from transformers import EarlyStoppingCallback

training_args = TrainingArguments(
    num_train_epochs=7,  # Augmenter
    # ... autres paramètres
)

trainer = Trainer(
    # ...
    callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]  # Arrêter si pas d'amélioration pendant 2 époques
)
```

**Impact estimé** : **+1-2% de F1-Score**

---

### 2. **Utiliser Focal Loss** 🔴 **PRIORITÉ 2**

**Problème** : Cross-Entropy Loss standard ne pénalise pas assez les faux positifs

**Solution** : Implémenter Focal Loss qui pénalise plus les erreurs difficiles

**Code** :
```python
import torch.nn.functional as F

class FocalLoss(nn.Module):
    def __init__(self, alpha=1, gamma=2, reduction='mean'):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction

    def forward(self, inputs, targets):
        ce_loss = F.cross_entropy(inputs, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss
        
        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        return focal_loss

# Dans le Trainer, utiliser compute_loss personnalisé
def compute_loss(self, model, inputs, return_outputs=False):
    labels = inputs.get("labels")
    outputs = model(**inputs)
    logits = outputs.get("logits")
    
    loss_fct = FocalLoss(alpha=1, gamma=2)
    loss = loss_fct(logits.view(-1, self.model.config.num_labels), labels.view(-1))
    
    return (loss, outputs) if return_outputs else loss
```

**Impact estimé** : **+1-2% de précision** → **+0.8-1.5% de F1**

---

### 3. **Ajuster les Class Weights** 🟡 **PRIORITÉ 3**

**Problème** : Toutes les classes ont le même poids, le modèle n'est pas pénalisé pour les faux positifs

**Solution** : Augmenter le poids de la classe "O" (Outside) pour pénaliser plus les faux positifs

**Code** :
```python
from torch import nn

# Calculer les poids des classes
# Plus de poids pour "O" (Outside) pour réduire les faux positifs
class_weights = torch.tensor([
    1.5,  # O (Outside) - pénaliser plus les faux positifs
    1.0,  # B-DEPARTURE
    1.0,  # I-DEPARTURE
    1.0,  # B-ARRIVAL
    1.0,  # I-ARRIVAL
]).to(device)

# Utiliser dans la loss
loss_fct = nn.CrossEntropyLoss(weight=class_weights)
```

**Impact estimé** : **+0.5-1% de précision** → **+0.4-0.8% de F1**

---

### 4. **Réduire le Ratio d'Exemples Négatifs** 🟡 **PRIORITÉ 4**

**Problème** : 20% d'exemples négatifs peut être trop élevé

**Solution** : Réduire à 10-12% d'exemples négatifs

**Code** :
```python
# Dans dataset_generator.py
generate_dataset(
    total=20000,
    negative_ratio=0.10  # Réduire de 0.12 à 0.10
)
```

**Impact estimé** : **+0.3-0.5% de F1**

---

### 5. **Améliorer le Post-Processing** 🟡 **PRIORITÉ 5**

**Problème** : Le post-processing actuel peut être amélioré

**Solutions** :

#### A. Fuzzy Matching pour Validation

**Code** :
```python
from difflib import SequenceMatcher

def fuzzy_match(text, known_cities, threshold=0.85):
    """Fuzzy matching pour trouver des villes similaires."""
    text_lower = text.lower().strip()
    best_match = None
    best_score = 0
    
    for city in known_cities:
        city_lower = city.lower()
        # Similarité de séquence
        score = SequenceMatcher(None, text_lower, city_lower).ratio()
        if score > best_score:
            best_score = score
            best_match = city
    
    return best_match if best_score >= threshold else None
```

#### B. Règles Contextuelles Plus Agressives

**Code** :
```python
def is_likely_false_positive(text, sentence):
    """Détecte les faux positifs probables."""
    sentence_lower = sentence.lower()
    text_lower = text.lower()
    
    # Contexte "mon ami", "mon copain" → probablement un prénom
    if any(phrase in sentence_lower for phrase in ["mon ami", "mon copain", "mon pote"]):
        if text_lower in sentence_lower:
            # Vérifier si c'est juste après ces phrases
            idx = sentence_lower.find(text_lower)
            before = sentence_lower[max(0, idx-20):idx]
            if any(phrase in before for phrase in ["mon ami", "mon copain", "mon pote"]):
                return True
    
    # Contexte "en [pays]", "pour la [pays]" → probablement un pays
    if any(phrase in sentence_lower for phrase in ["en ", "pour la ", "vers la "]):
        if text_lower in COUNTRIES:
            return True
    
    return False
```

**Impact estimé** : **+0.5-1% de précision** (uniquement en production, pas sur le dataset d'entraînement)

---

### 6. **Fine-tuning avec Données Ciblées** 🟢 **PRIORITÉ 6**

**Solution** : Réentraîner sur un dataset enrichi avec les cas problématiques identifiés dans l'analyse d'erreurs

**Étapes** :
1. Analyser les erreurs du dernier modèle
2. Créer des patterns spécifiques pour ces cas
3. Réentraîner avec ces patterns supplémentaires

**Impact estimé** : **+1-2% de F1**

---

## 📋 Plan d'Action Recommandé

### Phase 1 : Optimisation des Hyperparamètres (1 jour) 🔴 **PRIORITÉ ABSOLUE**

**Actions** :
1. Modifier le notebook d'entraînement :
   - Réduire `learning_rate` à `1e-05`
   - Ajouter `weight_decay=0.01`
   - Augmenter `num_epochs` à `7` avec early stopping
   - Ajouter class weights (poids 1.5 pour "O")

2. Réentraîner le modèle

**Impact estimé** : **+1.5-2.5% de F1-Score** → F1: 85.10% → **86.5-87.5%**

---

### Phase 2 : Implémenter Focal Loss (0.5 jour) 🔴 **PRIORITÉ 2**

**Actions** :
1. Implémenter Focal Loss dans le notebook
2. Réentraîner le modèle

**Impact estimé** : **+0.8-1.5% de F1-Score** → F1: 86.5-87.5% → **87.3-89%**

---

### Phase 3 : Ajuster le Ratio d'Exemples Négatifs (0.5 jour) 🟡

**Actions** :
1. Réduire `negative_ratio` à `0.10` (10%)
2. Régénérer le dataset
3. Réentraîner le modèle

**Impact estimé** : **+0.3-0.5% de F1-Score**

---

### Phase 4 : Améliorer le Post-Processing (0.5 jour) 🟡

**Actions** :
1. Ajouter fuzzy matching
2. Ajouter règles contextuelles plus agressives
3. Tester sur le pipeline

**Impact estimé** : **+0.5-1% de précision** (uniquement en production)

---

## 📈 Projection des Résultats

### Scénario Optimiste

**Actions** : Phase 1 + Phase 2 + Phase 3
- F1-Score : 85.10% → **88-89%** (+2.9-3.9 points)
- Precision : 78.98% → **82-84%** (+3-5 points)
- Recall : 92.26% → **91-92%** (maintenir)

### Scénario Réaliste

**Actions** : Phase 1 + Phase 2
- F1-Score : 85.10% → **87-88%** (+1.9-2.9 points)
- Precision : 78.98% → **81-83%** (+2-4 points)
- Recall : 92.26% → **91-92%** (maintenir)

---

## 🎯 Recommandation Finale

**Priorité immédiate** : **Phase 1 (Optimisation des Hyperparamètres)**

**Raison** :
- ✅ Impact le plus élevé (+1.5-2.5% de F1)
- ✅ Relativement rapide à implémenter (1 jour)
- ✅ Pas de risque de régression majeure
- ✅ Améliore directement le problème principal (précision faible)

**Après Phase 1** :
- Si F1 < 87% → Passer à Phase 2 (Focal Loss)
- Si F1 >= 87% → Évaluer si Phase 3/4 sont nécessaires

---

## ⚠️ Points d'Attention

1. **Ne pas sur-optimiser** : Tester une modification à la fois
2. **Early stopping essentiel** : Pour éviter le sur-apprentissage avec plus d'époques
3. **Valider sur test set** : Toujours vérifier les métriques sur le test set
4. **Post-processing** : Les améliorations du post-processing n'affectent que la production, pas les métriques d'entraînement

---

## 📝 Notes Techniques

- **Focal Loss** : Plus complexe à implémenter mais très efficace pour réduire les faux positifs
- **Class Weights** : Simple à implémenter, impact modéré mais sûr
- **Hyperparamètres** : Impact modéré mais cumulatif avec les autres techniques
- **Early Stopping** : Essentiel pour éviter le sur-apprentissage avec plus d'époques
