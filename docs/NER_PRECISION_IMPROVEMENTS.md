# Axes d'Amélioration pour la Précision du Modèle NER

## 📊 État Actuel

**Modèle :** `ner_camembert_20260112_230754_v1`

### Métriques Globales
- **Precision :** 74.38% ⚠️ (Faible)
- **Recall :** 90.64% ✅ (Bon)
- **F1-Score :** 81.71%

### Métriques par Type

#### DEPARTURE
- **Precision :** 73.45% ⚠️
- **Recall :** 88.92% ✅
- **F1-Score :** 80.45%
- **Support :** 2871 exemples

#### ARRIVAL
- **Precision :** 75.40% ⚠️
- **Recall :** 92.52% ✅
- **F1-Score :** 83.09%
- **Support :** 2607 exemples

### Constat
- **Problème principal :** Precision < Recall → **Trop de faux positifs** (le modèle détecte des entités qui n'en sont pas)
- **Rappel :** Le recall est excellent (~90%), donc le modèle ne manque pas beaucoup d'entités
- **Conclusion :** Le modèle est trop "généreux" et annote trop de mots comme des villes

---

## 🔍 Analyse des Causes Probables

### 1. **Confusion Noms de Personnes / Noms de Villes**
- Le modèle confond probablement des prénoms avec des noms de villes
- Exemples : "Florence", "Paris", "Nancy", "Jean", "Laurent" peuvent être des prénoms OU des villes
- Le dataset a été enrichi avec des patterns ambigus, mais peut-être pas assez

### 2. **Contextes Ambigus**
- Le modèle peut annoter des villes mentionnées dans un contexte où elles ne sont PAS des entités de trajet
- Exemple : "Mon ami habite à Paris" → "Paris" est mentionné mais n'est pas une entité de trajet
- "Je vais voir Florence à Lyon" → "Florence" est un prénom, "Lyon" est une destination

### 3. **Sous-annotation des Exemples Négatifs**
- Le dataset contient principalement des exemples positifs (phrases avec villes de trajet)
- Pas assez d'exemples négatifs montrant des villes mentionnées MAIS qui ne sont PAS des entités de trajet
- Pas assez d'exemples avec des noms propres qui ne sont PAS des villes

---

## 💡 Axes d'Amélioration

### 🔴 **PRIORITÉ 1 : Enrichir le Dataset avec Plus d'Exemples Négatifs**

#### 1.1 Ajouter des Patterns avec Villes Mentionnées mais NON-Annotées

**Objectif :** Montrer au modèle que toutes les mentions de villes ne sont pas des entités de trajet.

**Patterns à ajouter :**
```python
# Villes dans un contexte descriptif (pas de trajet)
"Mon ami habite à {city} depuis 5 ans" → PAS d'annotation
"J'ai visité {city} l'été dernier" → PAS d'annotation
"La gare de {city} est très belle" → PAS d'annotation (juste une description)

# Villes comme noms de personnes (déjà fait mais à renforcer)
"Avec mes amis {friend1} et {friend2}, on va à {dep} depuis {arr}" → annoter seulement dep et arr
"Mon cousin {friend1} habite à {city}" → PAS d'annotation pour friend1, city mentionnée mais pas trajet

# Villes dans des phrases non-trajets
"J'aime bien {city}, c'est une jolie ville" → PAS d'annotation
"Combien coûte un billet pour {city} ?" → PAS d'annotation (pas de départ)
```

**Impact attendu :** Réduire les faux positifs de ~25% à ~15-20%

#### 1.2 Ajouter des Patterns avec Noms Propres Non-Villes

**Objectif :** Apprendre au modèle à distinguer les noms de personnes des noms de villes.

**Patterns à ajouter :**
```python
# Phrases avec des noms de personnes connus (non-villes)
"Je dois appeler {random_name} pour organiser mon voyage"
"Mon collègue {random_name} travaille à {city}"
"J'ai rendez-vous avec {random_name} demain"

# Mots qui ressemblent à des villes mais n'en sont pas
# (nécessite une liste de mots courants qui pourraient être confondus)
```

**Impact attendu :** Réduire les faux positifs sur les noms propres de ~10-15%

---

### 🟡 **PRIORITÉ 2 : Post-Processing Intelligent**

#### 2.1 Filtrage par Liste de Villes Valides

**Objectif :** Utiliser la liste des gares françaises pour filtrer les faux positifs.

**Implémentation :**
```python
# Dans api/pipeline.py, après l'extraction NER
def _filter_invalid_cities(self, entities):
    """Filtre les entités qui ne sont pas dans la liste des gares valides."""
    valid_entities = []
    for entity in entities:
        if self._is_valid_station(entity["text"]):
            valid_entities.append(entity)
    return valid_entities
```

**Avantages :**
- Élimine les faux positifs évidents (mots qui ne sont pas des villes)
- Conservé le comportement actuel du post-processing

**Limitations :**
- N'aide pas si la ville est valide mais n'est pas une entité de trajet
- Peut créer des faux négatifs si le nom de la ville est mal orthographié

**Impact attendu :** Réduire les faux positifs de ~5-10%

#### 2.2 Validation Contextuelle

**Objectif :** Vérifier que les entités détectées sont dans un contexte de trajet.

**Critères :**
- Présence de mots-clés de trajet ("aller", "voyage", "trajet", "depuis", "vers", etc.)
- Structure syntaxique typique d'une requête de trajet

**Impact attendu :** Réduire les faux positifs de ~3-5%

---

### 🟢 **PRIORITÉ 3 : Ajustement des Hyperparamètres**

#### 3.1 Augmenter la Régularisation

**Objectif :** Réduire la sur-annotation en pénalisant les prédictions trop confiantes.

**Modifications :**
```python
# Dans le notebook d'entraînement
training_args = TrainingArguments(
    ...
    weight_decay=0.01,  # Augmenter de 0.0 à 0.01
    ...
)
```

**Impact attendu :** Légère amélioration de la précision (+2-3%)

#### 3.2 Early Stopping basé sur la Précision

**Objectif :** Arrêter l'entraînement quand la précision commence à diminuer.

**Modifications :**
```python
# Utiliser une métrique personnalisée pour early stopping
# Stopper quand precision_val > precision_best après N époques
```

**Impact attendu :** Éviter la sur-optimisation sur le recall

#### 3.3 Réduire Légèrement le Learning Rate

**Objectif :** Apprendre plus lentement pour éviter la sur-annotation.

**Modifications :**
```python
learning_rate=1.5e-05  # Réduire de 2e-05 à 1.5e-05
```

**Impact attendu :** Légère amélioration (+1-2%)

---

### 🔵 **PRIORITÉ 4 : Techniques Avancées**

#### 4.1 Focal Loss

**Objectif :** Pénaliser plus les faux positifs que les faux négatifs.

**Complexité :** Moyenne (nécessite de modifier la fonction de perte)

**Impact attendu :** Amélioration significative de la précision (+5-8%)

#### 4.2 Ensemble de Modèles

**Objectif :** Combiner plusieurs modèles pour réduire les erreurs.

**Complexité :** Élevée

**Impact attendu :** Amélioration modérée (+3-5%)

#### 4.3 Ré-annotation du Dataset

**Objectif :** Vérifier manuellement un échantillon du dataset pour identifier les annotations incorrectes.

**Complexité :** Faible mais temps de travail manuel

**Impact attendu :** Variable (dépend de la qualité actuelle du dataset)

---

## 📋 Plan d'Action Recommandé

### Phase 1 : Diagnostic (FAIT ✅)
- ✅ Script d'analyse des erreurs créé : `scripts/analyze_ner_errors.py`
- ⏳ **À FAIRE :** Exécuter le script pour identifier les patterns d'erreurs précis

### Phase 2 : Enrichissement du Dataset (RECOMMANDÉ)
1. **Ajouter 20-30 nouveaux patterns** avec villes mentionnées mais non-annotées
2. **Ajouter 10-15 patterns** avec noms de personnes clairement identifiés
3. **Régénérer le dataset** (20k phrases)
4. **Réentraîner le modèle**

**Temps estimé :** 2-3 heures
**Impact attendu :** Precision ~78-80%

### Phase 3 : Post-Processing (FACULTATIF)
1. **Implémenter le filtrage par liste de villes valides**
2. **Tester sur un échantillon**

**Temps estimé :** 1 heure
**Impact attendu :** Precision ~80-82%

### Phase 4 : Hyperparamètres (FACULTATIF)
1. **Ajuster weight_decay et learning_rate**
2. **Réentraîner avec early stopping sur précision**

**Temps estimé :** 2-3 heures
**Impact attendu :** Precision ~82-85%

---

## 🎯 Objectifs Réalistes

### Court Terme (1-2 semaines)
- **Précision :** 78-82%
- **Recall :** Maintenir >88%
- **F1-Score :** 83-85%

### Moyen Terme (1 mois)
- **Précision :** 82-85%
- **Recall :** Maintenir >85%
- **F1-Score :** 83-85%

### Long Terme (si nécessaire)
- **Précision :** 85-90%
- **Recall :** 85-90%
- **F1-Score :** 85-90%

---

## 🔧 Utilisation du Script d'Analyse

```bash
# Analyser le dernier modèle entraîné
python scripts/analyze_ner_errors.py

# Analyser un modèle spécifique
python scripts/analyze_ner_errors.py ner_camembert_20260112_230754_v1
```

Le script va :
1. Charger le modèle et le dataset
2. Faire des prédictions sur 500 exemples
3. Identifier les faux positifs et faux négatifs
4. Analyser les patterns d'erreurs
5. Afficher des statistiques détaillées
6. Sauvegarder les résultats dans `nlp/results/error_analysis_*.json`

---

## 📝 Notes

- **Rappel :** Le recall est excellent (~90%), donc ne pas trop pénaliser le recall en améliorant la précision
- **Balance :** L'objectif est d'améliorer la précision sans trop réduire le recall
- **Dataset :** La qualité du dataset est cruciale - mieux vaut avoir moins d'exemples mais bien annotés
- **Itération :** Améliorer progressivement (dataset → hyperparamètres → post-processing)
