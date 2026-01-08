# Optimisations du Dataset du Classifieur

## Modifications apportées (2026-01-06)

### 0. Augmentation de la taille du dataset

**Problème identifié** : Avec 199 patterns valides et 226 patterns invalides (total 425 patterns) pour seulement 10 000 phrases, certains patterns risquaient d'être sous-représentés ou même absents du dataset.

**Solution** : Augmentation de `TOTAL_SENTENCES` de **10 000 à 30 000 phrases**

**Impact** :
- **21 000 phrases valides** (70%) = ~105 occurrences par pattern valide en moyenne
- **9 000 phrases invalides** (30%) = ~40 occurrences par pattern invalide en moyenne
- Garantit que même les patterns avec poids faible (1.0) auront plusieurs occurrences
- Meilleure représentation de tous les patterns pour un apprentissage plus robuste

**Recommandation** : Pour un bon apprentissage, il faut au moins **10 occurrences par pattern**. Avec 30k phrases, cette condition est largement remplie même pour les patterns avec poids faible.

### 1. Ajout de 5 nouveaux patterns valides (195-199)

Ces patterns ont été identifiés comme non reconnus par le modèle actuel :

1. **"Je vais de X à Y"** (sans point final)
   - Pattern simple et courant qui n'était pas bien reconnu
   - Poids: 2.5 (très élevé pour améliorer la reconnaissance)

2. **"X -> Y"** (avec flèche et espaces)
   - Variante du pattern existant avec flèche Unicode
   - Poids: 2.5 (très élevé)

3. **"Je veux me rendre à Y et partir depuis X"** (ordre inversé)
   - Pattern avec ordre inversé des destinations
   - Poids: 2.0

4. **"Trajet X - Y"** (avec tiret)
   - Pattern court avec tiret comme séparateur
   - Poids: 2.0

5. **"Donne moi le trajet SNCF suivant : X - Y"** (avec préfixe SNCF)
   - Pattern avec préfixe explicite SNCF et tiret
   - Poids: 2.0

### 2. Optimisation des poids des patterns

#### Patterns de base (1-10)
- **Pattern 1** ("Je vais de X à Y") : Poids augmenté à **2.5** (au lieu de 1.0)
  - C'est le pattern le plus courant et le plus simple
  - Doit être bien représenté dans le dataset

- **Patterns 2-10** : Poids augmentés à **2.0** ou **1.5**
  - Patterns standards qui doivent être fréquents

#### Patterns abrégés (71-80)
- Poids augmentés à **1.5** (au lieu de 1.0)
  - Ces patterns sont souvent utilisés dans les messages courts/SMS
  - Incluent les patterns avec flèches, tirets, abréviations

#### Nouveaux patterns (195-199)
- Poids très élevés (**2.5** pour les 2 premiers, **2.0** pour les autres)
  - Ces patterns ont été identifiés comme problématiques
  - Poids élevé pour s'assurer qu'ils sont bien représentés dans le dataset

### 3. Analyse du dataset actuel

#### Distribution actuelle
- **70% de phrases valides** (7000 phrases)
- **30% de phrases invalides** (3000 phrases)
- Distribution équilibrée pour un problème de classification binaire

#### Patterns les plus fréquents
1. Patterns standards avec "Je vais de X à Y" (maintenant avec poids 2.5)
2. Patterns avec transports et dates
3. Patterns abrégés/SMS
4. Patterns avec questions

#### Points d'attention
- Les patterns avec beaucoup de typos sont bien représentés (poids 1.2)
- Les patterns "mais je vais à X" sont bien représentés (poids 1.5)
- Les patterns invalides avec emojis seuls sont bien représentés (poids 1.8-2.0)

### 4. Recommandations pour améliorer encore

#### Patterns à surveiller
1. **Patterns avec tirets** : Maintenant bien représentés avec les nouveaux patterns
2. **Patterns avec flèches** : Deux variantes maintenant (Unicode → et ASCII ->)
3. **Patterns avec préfixes** : Ajout du pattern SNCF, pourrait ajouter d'autres variantes

#### Optimisations futures possibles
1. **Augmenter la diversité des patterns invalides**
   - Ajouter plus de patterns avec contextes non-voyage
   - Ajouter des patterns avec lieux fictifs mais formulés comme des voyages

2. **Variations de casse et ponctuation**
   - Le générateur applique déjà des variations, mais on pourrait augmenter leur fréquence

3. **Patterns avec nombres et dates**
   - S'assurer que les patterns avec dates/heures sont bien représentés

4. **Patterns avec lieux composés**
   - "la gare de X", "l'aéroport de Y", etc. sont bien représentés

## Impact attendu

Avec ces optimisations, on s'attend à :
- ✅ Meilleure reconnaissance des patterns simples ("Je vais de X à Y")
- ✅ Meilleure reconnaissance des patterns avec flèches et tirets
- ✅ Meilleure reconnaissance des patterns avec ordre inversé
- ✅ Meilleure reconnaissance des patterns avec préfixes (SNCF, etc.)
- ✅ Distribution plus équilibrée des patterns les plus courants

## Prochaines étapes

1. **Régénérer le dataset** avec les nouveaux patterns
2. **Réentraîner le modèle** avec le nouveau dataset
3. **Évaluer les performances** et comparer avec le modèle précédent
4. **Analyser les nouvelles erreurs** pour identifier d'autres patterns problématiques

