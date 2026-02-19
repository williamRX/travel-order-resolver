# Corrections Rapides pour Améliorer le F1-Score NER

**Date** : 2025-01-15  
**Situation** : F1-Score stagne à ~85% malgré les améliorations  
**Objectif** : Atteindre 87-90% de F1-Score

---

## 🔍 Analyse du Problème

**Résultats actuels** :
- F1-Score : **85.10%** (légère régression après exemples négatifs)
- Precision : 78.98% (toujours faible)
- Recall : 92.26% (excellent)

**Problème principal** : **Precision trop faible** (78.98%) → trop de faux positifs

**Causes probables** :
1. ✅ `weight_decay=0.01` déjà configuré
2. ❌ `learning_rate=2e-5` peut être trop élevé
3. ❌ `num_epochs=3` peut être insuffisant
4. ❌ Pas de class weights pour pénaliser les faux positifs
5. ❌ Ratio d'exemples négatifs trop élevé (20% vs 10-12% recommandé)

---

## 🚀 Corrections Immédiates (30 minutes)

### 1. **Réduire le Learning Rate** 🔴 **PRIORITÉ 1**

**Dans le notebook, ligne ~99, modifier** :
```python
# AVANT
LEARNING_RATE = 2e-5  # Taux d'apprentissage (standard pour fine-tuning)

# APRÈS
LEARNING_RATE = 1e-5  # Taux d'apprentissage réduit pour meilleure précision
```

**Impact estimé** : +0.5-1% de précision

---

### 2. **Augmenter le Nombre d'Époques avec Early Stopping** 🔴 **PRIORITÉ 2**

**Dans le notebook, ligne ~100, modifier** :
```python
# AVANT
NUM_EPOCHS = 3  # Nombre d'époques d'entraînement

# APRÈS
NUM_EPOCHS = 7  # Nombre d'époques d'entraînement (avec early stopping)
```

**Dans le notebook, ligne ~886, vérifier que EarlyStoppingCallback est utilisé** :
```python
training_args = TrainingArguments(
    num_train_epochs=NUM_EPOCHS,
    # ... autres paramètres
    load_best_model_at_end=True,  # Charger le meilleur modèle à la fin
    metric_for_best_model="eval_f1",  # Utiliser F1 comme métrique
    greater_is_better=True,
)

# Dans le Trainer, ligne ~939
trainer = Trainer(
    # ... autres paramètres
    callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]  # Arrêter si pas d'amélioration pendant 2 époques
)
```

**Impact estimé** : +0.5-1% de F1

---

### 3. **Ajouter Class Weights** 🔴 **PRIORITÉ 3**

**Dans le notebook, après la création du modèle, ajouter** :

```python
# Calculer les poids des classes pour pénaliser plus les faux positifs
# Plus de poids pour "O" (Outside) pour réduire les faux positifs
class_weights = torch.tensor([
    1.5,  # O (Outside) - pénaliser plus les faux positifs
    1.0,  # B-DEPARTURE
    1.0,  # I-DEPARTURE
    1.0,  # B-ARRIVAL
    1.0,  # I-ARRIVAL
]).to(device)

# Créer une fonction de loss personnalisée
from torch import nn

class WeightedCrossEntropyLoss(nn.Module):
    def __init__(self, weights):
        super().__init__()
        self.weights = weights
        self.loss_fct = nn.CrossEntropyLoss(weight=weights, ignore_index=-100)
    
    def forward(self, logits, labels):
        return self.loss_fct(logits.view(-1, logits.size(-1)), labels.view(-1))

# Dans le Trainer, utiliser compute_loss personnalisé
def compute_loss(self, model, inputs, return_outputs=False):
    labels = inputs.get("labels")
    outputs = model(**inputs)
    logits = outputs.get("logits")
    
    loss_fct = WeightedCrossEntropyLoss(class_weights)
    loss = loss_fct(logits, labels)
    
    return (loss, outputs) if return_outputs else loss

# Modifier le Trainer pour utiliser cette fonction
trainer = Trainer(
    # ... autres paramètres
    compute_loss=compute_loss  # Utiliser la loss personnalisée
)
```

**Impact estimé** : +0.5-1% de précision → +0.4-0.8% de F1

---

### 4. **Réduire le Ratio d'Exemples Négatifs** 🟡 **PRIORITÉ 4**

**Dans `dataset/generators/nlp/dataset_generator.py`, ligne ~729, modifier** :
```python
# AVANT
def generate_dataset(
    total: int = TOTAL_SENTENCES,
    seed: Optional[int] = 42,
    output_file: Path = OUTPUT_FILE,
    negative_ratio: float = 0.12,  # 12% d'exemples négatifs par défaut
) -> None:

# APRÈS
def generate_dataset(
    total: int = TOTAL_SENTENCES,
    seed: Optional[int] = 42,
    output_file: Path = OUTPUT_FILE,
    negative_ratio: float = 0.10,  # 10% d'exemples négatifs (réduit de 12%)
) -> None:
```

**Puis régénérer le dataset** :
```bash
python dataset/generators/nlp/dataset_generator.py
```

**Impact estimé** : +0.3-0.5% de F1

---

## 📋 Ordre d'Implémentation Recommandé

### Étape 1 : Modifications du Notebook (15 minutes)

1. **Réduire learning_rate** : `2e-5` → `1e-5`
2. **Augmenter num_epochs** : `3` → `7` (avec early stopping)
3. **Ajouter class weights** : Poids 1.5 pour "O"

**Impact estimé** : **+1-2% de F1-Score** → F1: 85.10% → **86-87%**

### Étape 2 : Régénérer le Dataset (5 minutes)

1. **Réduire negative_ratio** : `0.12` → `0.10`
2. **Régénérer le dataset**

**Impact estimé** : **+0.3-0.5% de F1-Score** → F1: 86-87% → **86.5-87.5%**

### Étape 3 : Réentraîner (30-60 minutes)

1. **Exécuter le notebook modifié**
2. **Vérifier les métriques**

**Objectif** : F1-Score **87-88%**

---

## 🎯 Résultat Attendu

**Après toutes les modifications** :
- F1-Score : 85.10% → **87-88%** (+1.9-2.9 points)
- Precision : 78.98% → **81-83%** (+2-4 points)
- Recall : 92.26% → **91-92%** (maintenir)

---

## ⚠️ Points d'Attention

1. **Early Stopping essentiel** : Avec 7 époques, l'early stopping est crucial pour éviter le sur-apprentissage
2. **Tester une modification à la fois** : Si possible, tester learning_rate et epochs d'abord, puis class weights
3. **Valider sur test set** : Toujours vérifier les métriques sur le test set, pas seulement sur validation

---

## 📝 Code Complet pour Class Weights

Si vous voulez implémenter les class weights, voici le code complet à ajouter dans le notebook :

```python
# Après la création du modèle (ligne ~800)
# Calculer les poids des classes
class_weights = torch.tensor([
    1.5,  # O (Outside) - pénaliser plus les faux positifs
    1.0,  # B-DEPARTURE
    1.0,  # I-DEPARTURE
    1.0,  # B-ARRIVAL
    1.0,  # I-ARRIVAL
]).to(device)

# Fonction de loss personnalisée
from torch import nn

class WeightedCrossEntropyLoss(nn.Module):
    def __init__(self, weights):
        super().__init__()
        self.weights = weights
        self.loss_fct = nn.CrossEntropyLoss(weight=weights, ignore_index=-100)
    
    def forward(self, logits, labels):
        return self.loss_fct(logits.view(-1, logits.size(-1)), labels.view(-1))

# Fonction compute_loss pour le Trainer
def compute_loss(model, inputs, return_outputs=False):
    labels = inputs.get("labels")
    outputs = model(**inputs)
    logits = outputs.get("logits")
    
    loss_fct = WeightedCrossEntropyLoss(class_weights)
    loss = loss_fct(logits, labels)
    
    return (loss, outputs) if return_outputs else loss

# Modifier le Trainer (ligne ~939)
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
    compute_loss=compute_loss  # Ajouter cette ligne
)
```

---

## 🚀 Action Immédiate

**Commencez par** :
1. Modifier `LEARNING_RATE = 1e-5`
2. Modifier `NUM_EPOCHS = 7`
3. Vérifier que `EarlyStoppingCallback` est utilisé
4. Réentraîner

**Si F1 < 87% après ces modifications** :
- Ajouter les class weights
- Réduire le ratio d'exemples négatifs et régénérer le dataset
