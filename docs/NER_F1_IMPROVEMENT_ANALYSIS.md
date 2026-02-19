# Analyse des Résultats NER - Axes d'Amélioration du F1-Score

**Date** : 2025-01-15  
**Modèle analysé** : `ner_camembert_20260115_100039_v1`  
**F1-Score actuel** : 83.08%

**Analyse d'erreurs** : `nlp/results/error_analysis_ner_camembert_20260115_100039_v1.json`

---

## 📊 Résultats Actuels

### Métriques Globales

| Métrique | Valeur | Comparaison avec meilleur précédent |
|----------|--------|-------------------------------------|
| **Precision** | 75.70% | +0.55% ✅ |
| **Recall** | 92.06% | +0.28% ✅ |
| **F1-Score** | **83.08%** | +0.45% ✅ |
| **Accuracy** | 98.41% | +0.05% ✅ |

### Métriques par Type d'Entité

#### DEPARTURE
- **Precision** : 75.88% → ~878 faux positifs estimés
- **Recall** : 92.90% → ~210 faux négatifs estimés
- **F1** : 83.53%

#### ARRIVAL
- **Precision** : 75.50% → ~761 faux positifs estimés
- **Recall** : 91.08% → ~229 faux négatifs estimés
- **F1** : 82.56%

---

## 🔍 Diagnostic Principal

### Problème Identifié

**Precision < Recall** (75.70% vs 92.06%)

Le modèle génère **trop de faux positifs** :
- **159 faux positifs** sur 500 exemples testés (31.8%)
- **48 faux négatifs** sur 500 exemples testés (9.6%)
- Le modèle détecte des entités qui n'en sont pas
- Il est trop "généreux" dans ses prédictions
- Le recall est excellent (92%), donc le modèle détecte bien les vraies entités

### Patterns de Faux Positifs Identifiés

D'après l'analyse d'erreurs (`error_analysis_ner_camembert_20260115_100039_v1.json`) :

1. **Tirets avec espaces** : **16 cas (16%)** 🔴
   - Exemples : "Bretenoux - birs", "Saint-Amand-Montrond - orrval", "Fontaines - Mercureyy"
   - Le modèle détecte "Ville - Ville" comme une seule entité au lieu de deux entités séparées

2. **Lettres isolées / mots très courts** : **6 cas (6%)** 🟡
   - Exemples : "l" (3 fois), "la", "Ma", "champ"
   - Le modèle détecte des lettres ou mots isolés comme des entités

3. **Préfixes inclus** : **4 cas (4%)** 🟡
   - Exemples : "l'aéroport d fretin", "la garre de capdennac", "l'aéropport de lisson"
   - Le modèle inclut encore parfois les préfixes dans les annotations (malgré les corrections)

4. **Pays** : **2 cas (2%)** 🟡
   - Exemples : "Tunisie", "turquie"
   - Le modèle détecte des pays comme des entités ARRIVAL

5. **Noms propres (probablement prénoms ou villes inconnues)** : **~28 cas (28%)** 🔴
   - Exemples : "Villars-les-Dombes", "Houdann", "bellvue", "guilléval", "victor"
   - Le modèle détecte des noms propres qui ne sont pas des gares/villes valides

6. **Autres** : **~103 cas (65%)**
   - Divers cas : villes avec fautes de frappe, noms composés, etc.

### Impact sur le F1-Score

Le F1-Score est limité par la précision faible. Pour améliorer le F1 :
- **Option 1** : Augmenter la précision (réduire les faux positifs) → **RECOMMANDÉ**
- **Option 2** : Augmenter le recall (mais déjà à 92%, peu de marge)
- **Option 3** : Équilibrer les deux (meilleur compromis)

---

## 🎯 Axes d'Amélioration Prioritaires

### 1. **Réduction des Faux Positifs** (PRIORITÉ ABSOLUE) 🔴

**Objectif** : Passer de 75.70% à 80-85% de précision

#### A. Enrichir le Dataset avec des Exemples Négatifs

**Problème** : Le modèle n'a pas assez d'exemples où des noms propres similaires à des villes ne sont PAS des entités.

**Solutions prioritaires** (basées sur l'analyse d'erreurs) :

1. **Gérer les tirets avec espaces** (16% des FP) 🔴 **PRIORITÉ 1** :
   - Ajouter des patterns explicites : "VilleA - VilleB" où chaque ville est annotée séparément
   - Le tiret " - " doit être O (Outside), pas I-DEPARTURE/I-ARRIVAL
   - Exemples à ajouter :
     ```
     "Je vais de Paris - Lyon à Marseille"
     → "Paris" (DEPARTURE), "Lyon" (DEPARTURE), "Marseille" (ARRIVAL)
     → Le tiret " - " est O
     ```

2. **Ajouter des phrases avec noms propres non-annotés** (28% des FP) 🔴 **PRIORITÉ 2** :
   ```
   "Je vais voir mon ami Pierre à Paris"
   → "Pierre" ne doit PAS être annoté (c'est un prénom)
   → "Paris" doit être annoté comme ARRIVAL
   
   "Mon copain Victor habite à Lyon"
   → "Victor" ne doit PAS être annoté
   → "Lyon" doit être annoté comme ARRIVAL
   ```

3. **Ajouter des phrases avec pays/continents** (2% des FP) :
   ```
   "Je vais en Tunisie depuis l'aéroport de Paris"
   → "Tunisie" ne doit PAS être annoté (c'est un pays)
   → "Paris" doit être annoté comme DEPARTURE
   ```

4. **Filtrer les lettres isolées** (6% des FP) :
   - Ajouter une règle de post-processing : rejeter les entités de 1-2 caractères
   - Ou enrichir le dataset avec des exemples où "l", "la", "le" apparaissent mais ne sont pas annotés

5. **Ajouter des phrases avec villes mentionnées hors contexte de trajet** :
   ```
   "Paris est une belle ville"
   → "Paris" ne doit PAS être annoté (pas un trajet)
   ```

**Impact estimé** : +5-8% de précision (en ciblant les 16% de tirets + 28% de noms propres)

#### B. Post-Processing Intelligent

**Solution** : Filtrer les prédictions avec une liste de validation

1. **Validation par liste de gares valides** :
   - Charger `dataset/shared/gares-francaises.json`
   - Filtrer les entités prédites qui ne sont pas dans la liste
   - Garder uniquement les entités validées
   - **Impact** : Éliminer ~28% des FP (noms propres qui ne sont pas des gares)

2. **Filtrage des lettres isolées** :
   - Rejeter automatiquement les entités de 1-2 caractères
   - **Impact** : Éliminer ~6% des FP

3. **Filtrage des pays** :
   - Liste de pays à exclure : Tunisie, Turquie, Inde, etc.
   - **Impact** : Éliminer ~2% des FP

4. **Validation contextuelle** :
   - Vérifier que l'entité est dans un contexte de trajet
   - Exemples de contextes valides : "de X à Y", "depuis X", "vers Y"
   - Rejeter les entités isolées sans contexte

**Impact estimé total** : +4-6% de précision

#### C. Ajustement des Hyperparamètres

**Solutions** :

1. **Augmenter la régularisation** :
   - `weight_decay` : 0.0 → 0.01 (réduit l'overfitting)
   - Impact : +1-2% précision

2. **Réduire légèrement le learning rate** :
   - `learning_rate` : 2e-05 → 1.5e-05
   - Impact : +0.5-1% précision

3. **Early stopping basé sur la précision** :
   - Arrêter l'entraînement quand la précision sur validation ne s'améliore plus
   - Impact : +0.5-1% précision

**Impact estimé** : +2-4% de précision

---

### 2. **Réduction des Faux Négatifs** (PRIORITÉ SECONDAIRE) 🟡

**Objectif** : Maintenir le recall à ~92% tout en améliorant la précision

#### A. Enrichir le Dataset avec des Variantes

**Solutions** :

1. **Ajouter des patterns avec fautes de frappe** :
   - "Pariss" au lieu de "Paris"
   - "Lyonn" au lieu de "Lyon"

2. **Ajouter des patterns avec abréviations** :
   - "Paris Gare du Nord" → "Paris GDN"
   - "Lyon Part-Dieu" → "Lyon PD"

3. **Ajouter des patterns avec variations de casse** :
   - "PARIS", "paris", "PaRiS"

**Impact estimé** : Maintien du recall à ~92%

---

### 3. **Techniques Avancées** (PRIORITÉ TERTIAIRE) 🟢

#### A. Focal Loss

**Solution** : Utiliser Focal Loss au lieu de Cross-Entropy Loss
- Pénalise plus les faux positifs
- Impact estimé : +2-3% précision

#### B. Model Ensembles

**Solution** : Combiner plusieurs modèles entraînés avec différentes initialisations
- Impact estimé : +1-2% F1

#### C. Fine-tuning avec Données Ciblées

**Solution** : Réentraîner sur un dataset enrichi avec les cas problématiques identifiés
- Impact estimé : +3-5% F1

---

## 📈 Objectifs Réalistes

### Court Terme (1-2 semaines)

**Objectifs** :
- Precision : 75.70% → **80-82%** (+4-6%)
- Recall : 92.06% → **91-92%** (maintenir)
- **F1-Score : 83.08% → 85-87%** (+2-4%)

**Actions** :
1. ✅ Enrichir le dataset avec exemples négatifs (noms propres, pays, etc.)
2. ✅ Implémenter post-processing avec validation par liste de gares
3. ✅ Ajuster les hyperparamètres (weight_decay, learning_rate)

### Moyen Terme (1 mois)

**Objectifs** :
- Precision : **82-85%**
- Recall : **91-92%**
- **F1-Score : 86-88%**

**Actions** :
1. ✅ Itérer sur le dataset basé sur l'analyse d'erreurs
2. ✅ Implémenter Focal Loss
3. ✅ Optimiser les hyperparamètres avec grid search

### Long Terme (si nécessaire)

**Objectifs** :
- Precision : **85-90%**
- Recall : **90-92%**
- **F1-Score : 87-91%**

**Actions** :
1. ✅ Model ensembles
2. ✅ Fine-tuning avancé
3. ✅ Techniques de data augmentation sophistiquées

---

## 🛠️ Plan d'Action Recommandé

### Phase 1 : Analyse des Erreurs ✅ **FAIT**

1. ✅ **Analyse d'erreurs exécutée** :
   - Fichier : `nlp/results/error_analysis_ner_camembert_20260115_100039_v1.json`
   - 159 faux positifs identifiés sur 500 exemples
   - 48 faux négatifs identifiés

2. ✅ **Patterns identifiés** :
   - **Tirets avec espaces** : 16 cas (16%) - PRIORITÉ 1
   - **Noms propres** : ~28 cas (28%) - PRIORITÉ 2
   - **Lettres isolées** : 6 cas (6%)
   - **Préfixes inclus** : 4 cas (4%)
   - **Pays** : 2 cas (2%)

### Phase 2 : Enrichissement du Dataset (1-2 jours) 🔴 **PRIORITÉ**

1. **Corriger les patterns avec tirets** (16% des FP) :
   - Modifier le générateur pour annoter correctement "VilleA - VilleB"
   - Chaque ville doit être annotée séparément
   - Le tiret " - " doit être O (Outside)
   - Exemple : "Paris - Lyon" → "Paris" (DEPARTURE), "Lyon" (ARRIVAL), "-" (O)

2. **Ajouter des exemples négatifs** :
   - **Noms propres (prénoms)** : "Mon ami Pierre", "Je vais voir Victor"
   - **Pays** : "Je vais en Tunisie", "Je pars pour la Turquie"
   - **Noms de lieux non-gares** : "restaurant Le Paris", "monument de Lyon"
   - **Villes mentionnées hors contexte** : "Paris est belle", "J'aime Lyon"

3. **Régénérer le dataset** :
   ```bash
   python dataset/generators/nlp/dataset_generator.py
   ```

### Phase 3 : Post-Processing (1 jour) 🔴 **PRIORITÉ**

1. **Implémenter la validation par liste de gares** :
   - Charger `dataset/shared/gares-francaises.json`
   - Filtrer les entités prédites qui ne sont pas dans la liste
   - **Impact** : Éliminer ~28% des FP (noms propres non-gares)

2. **Filtrage des lettres isolées** :
   - Rejeter les entités de 1-2 caractères
   - **Impact** : Éliminer ~6% des FP

3. **Filtrage des pays** :
   - Liste de pays à exclure
   - **Impact** : Éliminer ~2% des FP

4. **Implémenter la validation contextuelle** :
   - Vérifier que l'entité est dans un contexte de trajet
   - Rejeter les entités isolées sans contexte

5. **Tester sur le dataset de test**

### Phase 4 : Réentraînement (1 jour)

1. **Ajuster les hyperparamètres**
2. **Réentraîner le modèle**
3. **Comparer les résultats**

---

## 📝 Notes Importantes

- **Le recall est excellent (92%)** : Ne pas le sacrifier en améliorant la précision
- **L'objectif est d'équilibrer** : Precision ≈ Recall pour un F1 optimal
- **Itération continue** : Améliorer le dataset basé sur les erreurs identifiées
- **Qualité > Quantité** : Mieux vaut moins d'exemples mais bien annotés

---

## 🔗 Ressources

- Script d'analyse d'erreurs : `scripts/analyze_ner_errors.py`
- Générateur de dataset : `dataset/generators/nlp/dataset_generator.py`
- Liste des gares : `dataset/shared/gares-francaises.json`
- Journal du projet : `nlp/JOURNAL.md`
