# TODO - Liste des Tâches

## Phase 1: Exploration & Analyse
- [ ] Charger et inspecter les datasets existants
- [ ] Analyser la distribution des classes (VALID/INVALID)
- [ ] Analyser les longueurs de phrases par classe
- [ ] Détecter et supprimer les doublons
- [ ] Visualiser les distributions (graphiques, word clouds)
- [ ] Identifier les patterns récurrents

## Phase 2: Nettoyage & Préparation
- [ ] Fusionner les datasets (travel_dataset, extended, 50k)
- [ ] Uniformiser les noms de colonnes
- [ ] Nettoyage minimal du texte (espaces, lowercase)
- [ ] Filtrer les phrases vides ou invalides
- [ ] Équilibrer les classes (70% INVALID, 30% VALID)
- [ ] Créer les splits train/validation/test (stratifiés)

## Phase 3: Feature Engineering
- [ ] Extraire features basiques (longueur, nombre de villes)
- [ ] Détecter les mots-clés de trajet
- [ ] Compter les prépositions de mouvement
- [ ] Vectorisation TF-IDF (ngrams 1-2, max_features=50k)
- [ ] Sauvegarder le vectorizer

## Phase 4: Baseline Model - Binaire
- [ ] Entraîner Logistic Regression
- [ ] Entraîner Linear SVM
- [ ] Entraîner Naive Bayes
- [ ] Comparer les performances (Accuracy, F1, Recall INVALID)
- [ ] Analyser les matrices de confusion
- [ ] Identifier les features les plus importantes
- [ ] Analyser les erreurs (faux positifs, faux négatifs)

## Phase 5: Optimisation Baseline
- [ ] Grid search pour hyperparamètres (C, solver, class_weight)
- [ ] Optimiser le vectorizer (max_features, ngram_range)
- [ ] Réentraîner avec meilleurs paramètres
- [ ] Valider performance > 85% F1-score
- [ ] Documenter les résultats

## Phase 6: Détection Ambiguïté
- [ ] Utiliser probabilités Logistic Regression (zone 0.40-0.60)
- [ ] Identifier phrases ambigues automatiquement
- [ ] Valider manuellement un échantillon
- [ ] Labeler les phrases AMBIGU confirmées
- [ ] Ajouter au dataset (distribution: 60% INVALID, 30% VALID, 10% AMBIGU)

## Phase 7: Modèle 3 Classes
- [ ] Réentraîner TF-IDF sur dataset 3 classes
- [ ] Entraîner Logistic Regression multi-class
- [ ] Évaluer performance par classe (VALID, INVALID, AMBIGU)
- [ ] Analyser matrice de confusion 3x3
- [ ] Optimiser pour classe AMBIGU (recall, precision)
- [ ] Valider performance globale

## Phase 8: Export & Documentation
- [ ] Sauvegarder modèle final + vectorizer
- [ ] Créer métadonnées (version, date, métriques)
- [ ] Documenter les performances finales
- [ ] Créer script de prédiction
- [ ] Tester le pipeline de prédiction

## Phase 9: Améliorations Futures
- [ ] Expérimenter avec CamemBERT/FlauBERT
- [ ] Fine-tuning de transformers
- [ ] Comparer avec baseline
- [ ] Augmenter le dataset (100k+ phrases)
- [ ] Ajouter exemples de production
- [ ] Optimiser pour production (quantization, latence)

## Scripts & Utilitaires
- [ ] Créer script de preprocessing réutilisable
- [ ] Créer script d'entraînement automatisé
- [ ] Créer script d'évaluation standardisé
- [ ] Créer fonctions utilitaires (features, visualisation)
- [ ] Créer pipeline de prédiction

## Documentation
- [ ] Mettre à jour ROADMAP avec résultats
- [ ] Documenter les décisions importantes
- [ ] Créer guide d'utilisation du modèle
- [ ] Documenter les cas edge et limitations

