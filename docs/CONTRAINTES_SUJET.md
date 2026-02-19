# Analyse des Contraintes du Sujet - État d'Avancement

Ce document liste ce qui doit être ajouté selon le sujet du projet et l'état actuel du développement.

---

## ✅ Ce qui est DÉJÀ FAIT

### 1. Module NLP
- ✅ Classification validité des phrases (VALID/INVALID)
- ✅ Extraction départ/arrivée avec NER (CamemBERT et SpaCy)
- ✅ Dataset de training généré
- ✅ Modèles entraînés et sauvegardés
- ✅ Pipeline de prédiction fonctionnel
- ✅ Post-processing avancé :
  - Nettoyage caractères spéciaux (`/`, `"`, `?`, `(`, `)`)
  - Séparation Ville-Ville (ex: "Marseille-Lyon" → "Marseille", "Lyon")
  - Extraction de villes depuis phrases (ex: "la gare de Lille" → "Lille")
  - Capitalisation intelligente des noms de villes

### 2. Infrastructure
- ✅ API FastAPI avec endpoints `/predict` et `/process_csv`
- ✅ Frontend chatbot interactif (page séparée)
- ✅ Frontend CSV upload (page séparée `csv_upload.html`)
- ✅ Docker et docker-compose
- ✅ Documentation complète (Markdown)
- ✅ Journaux de bord (classifier et NLP)

### 3. Module Pathfinding
- ✅ Module `pathfinding/` complet avec :
  - `data_loader.py` : Chargement des gares depuis `gares-francaises.json`
  - `graph_builder.py` : Construction du graphe de connexions
  - `dijkstra.py` : Implémentation de l'algorithme Dijkstra
  - `astar.py` : Implémentation de l'algorithme A* avec heuristique
  - `route_finder.py` : Classe principale pour trouver les itinéraires
  - `utils.py` : Utilitaires (distance haversine, normalisation)
- ✅ Intégration dans le pipeline NLP (`api/pipeline.py`)
- ✅ Format de sortie avec étapes : `sentenceID,Departure,Step1,Step2,...,Destination`
- ✅ Script de test/comparaison : `scripts/test_pathfinding.py`
- ✅ Documentation : `docs/PATHFINDING_ARCHITECTURE.md` et `docs/PATHFINDING_INTERFACE.md`

---

## 🆕 Améliorations Récentes

### Post-processing NLP Avancé
- ✅ Extraction intelligente de villes depuis phrases complexes :
  - "la gare de Lille" → "Lille"
  - "l'aéroport de Lyon" → "Lyon"
  - "station de Paris" → "Paris"
- ✅ Capitalisation automatique des noms de villes :
  - "nantes" → "Nantes"
  - "rennes" → "Rennes"
  - Utilise la capitalisation exacte depuis `gares-francaises.json`

### Module Pathfinding Complet
- ✅ Implémentation de **Dijkstra** et **A*** pour comparaison
- ✅ Construction automatique du graphe depuis `gares-francaises.json`
- ✅ Intégration transparente dans le pipeline NLP
- ✅ Format de sortie avec étapes intermédiaires automatique
- ✅ Script de test/comparaison des algorithmes

### Interface Utilisateur
- ✅ **Séparation des pages** : Chatbot et CSV upload sur des pages distinctes
- ✅ Affichage du trajet complet dans le chatbot (avec étapes intermédiaires)
- ✅ Page CSV dédiée avec instructions et interface spacieuse
- ✅ Navigation fluide entre les deux pages

### Intégration Pipeline
- ✅ Le pathfinding s'exécute automatiquement après l'extraction NLP
- ✅ Format de sortie adaptatif :
  - Avec pathfinding : `sentenceID,Departure,Step1,Step2,...,Destination`
  - Sans pathfinding : `sentenceID,Departure,Destination`
- ✅ Gestion d'erreurs robuste (gares non trouvées, trajets impossibles)

---

## ❌ Ce qui MANQUE selon le sujet

### ✅ PRIORITÉ 1 : Format d'entrée/sortie spécifique - COMPLÉTÉ

**Exigence du sujet :**
- Format d'entrée : `sentenceID,sentence` (une ligne par phrase)
- Format de sortie pour phrases VALIDES : `sentenceID,Departure,Destination`
- Format de sortie pour phrases INVALIDES : `sentenceID,Code` (ex: `sentenceID,INVALID`)

**Ce qui était manquant :**
- ❌ Script/commande pour lire depuis fichier/URL/stdin au format spécifié
- ❌ Script qui traite ligne par ligne et génère le format de sortie attendu
- ❌ Support pour lire depuis URL (optionnel mais mentionné)

**✅ IMPLÉMENTÉ :**
- ✅ Script `scripts/process_input.py` créé
- ✅ Lecture depuis fichier : `--file input.csv`
- ✅ Lecture depuis stdin : pipe automatique
- ✅ Lecture depuis URL : `--url http://example.com/sentences.csv`
- ✅ Format d'entrée : `sentenceID,sentence`
- ✅ Format de sortie VALIDE : `sentenceID,Departure,Destination`
- ✅ Format de sortie INVALIDE : `sentenceID,INVALID`
- ✅ Documentation complète dans `docs/PROCESS_INPUT_USAGE.md`

**Usage :**
```bash
# Lecture depuis fichier
python scripts/process_input.py --file input.csv > output.csv

# Lecture depuis stdin
cat input.csv | python scripts/process_input.py

# Lecture depuis URL
python scripts/process_input.py --url http://example.com/sentences.csv > output.csv
```

**Note importante :** 
- Le script CLI (`process_input.py`) est un outil ligne de commande pour le format CSV
- Le chatbot web a maintenant **aussi** une fonctionnalité CSV intégrée :
  - **Page séparée** : `frontend/csv_upload.html` pour éviter la surcharge de l'interface
  - Upload de fichier CSV avec traitement automatique
  - Affichage des résultats et téléchargement
- Les deux systèmes utilisent le même pipeline NLP + Pathfinding et respectent le format du sujet
- **Format de sortie amélioré** : Si le pathfinding est activé, le format inclut les étapes intermédiaires :
  - `sentenceID,Departure,Step1,Step2,...,Destination` (avec pathfinding)
  - `sentenceID,Departure,Destination` (sans pathfinding ou trajet direct)
- Voir `docs/CHATBOT_VS_CLI.md` pour la différence entre chatbot et CLI
- Voir `docs/CSV_CHATBOT_INTEGRATION.md` pour l'utilisation CSV dans le chatbot

---

### ✅ PRIORITÉ 1 : Module Pathfinding (Graph) - COMPLÉTÉ

**Exigence du sujet :**
- Trouver un itinéraire optimal entre deux villes/gares
- Format de sortie : `sentenceID,Departure,Step1,Step2,...,Destination`
- Utiliser les données SNCF (gares-francaises.json)
- Trouver le chemin le plus court ou le plus rapide

**✅ IMPLÉMENTÉ :**
- ✅ Module `pathfinding/` complet créé avec toute la structure
- ✅ Construction du graphe depuis `gares-francaises.json` :
  - Connexion des hubs majeurs (catégorie A) entre eux
  - Connexion des autres gares selon distance géographique (seuil configurable)
  - Calcul des distances avec formule de Haversine
- ✅ Algorithmes implémentés :
  - **Dijkstra** : Algorithme classique pour chemin optimal
  - **A*** : Algorithme optimisé avec heuristique (distance à vol d'oiseau)
  - Les deux algorithmes retournent des statistiques (nœuds explorés, etc.)
- ✅ Intégration complète dans le pipeline NLP :
  - Le pathfinding s'exécute automatiquement après l'extraction NLP
  - Retourne le trajet complet avec étapes intermédiaires
  - Format de sortie : `sentenceID,Departure,Step1,Step2,...,Destination`
- ✅ Normalisation intelligente des noms de villes/gares
- ✅ Script de test/comparaison : `scripts/test_pathfinding.py`
- ✅ Documentation complète :
  - `docs/PATHFINDING_ARCHITECTURE.md` : Architecture détaillée
  - `docs/PATHFINDING_INTERFACE.md` : Interfaces d'entrée/sortie
  - `pathfinding/README.md` : Documentation du module

**Utilisation :**
```python
from pathfinding import RouteFinder

# Initialiser
route_finder = RouteFinder()

# Trouver un itinéraire
result = route_finder.find_route("Paris", "Lyon", algorithm="dijkstra")
# ou
result = route_finder.find_route("Paris", "Lyon", algorithm="astar")

if result.success:
    print(f"Route: {' → '.join(result.route)}")
    print(f"Distance: {result.total_distance} km")
```

**Intégration dans le pipeline :**
Le pathfinding est automatiquement activé dans `api/pipeline.py`. Quand le NLP extrait `departure` et `arrival`, le pathfinding trouve automatiquement l'itinéraire optimal et le retourne dans le champ `route`.

**Note :** Le sujet dit que c'est "not the core" mais c'est quand même requis pour la livraison finale. ✅ **Complété !**

---

### 🔴 PRIORITÉ 2 : Documentation PDF complète

**Exigence du sujet :**
> "We obviously also expect a strong documentation, specifically on the NLP part (please provide PDF files)"

**Contenu requis :**

1. **Architecture complète** ❌
   - Description de toutes les couches de l'application
   - Diagrammes d'architecture
   - Flux de données

2. **Processus d'entraînement** ❌
   - Description détaillée du processus
   - Description des datasets utilisés
   - Méthodologie de génération du dataset

3. **Paramètres finaux** ❌
   - Identification des paramètres après entraînement + fine-tuning
   - Hyperparamètres finaux
   - Configuration des modèles

4. **Exemple détaillé** ❌
   - Exemple complet de traitement d'un texte
   - Étape par étape : entrée → sortie
   - Ce qui se passe à chaque étape du pipeline

5. **Expériences et résultats** ❌
   - Description des différentes expériences menées
   - Résultats obtenus
   - Métriques de performance
   - Comparaison des modèles
   - Analyse des erreurs

**Action requise :**
Créer un document PDF (ou Markdown à convertir en PDF) : `docs/RAPPORT_NLP.md` ou `docs/RAPPORT_FINAL.md`

---

### 🟡 PRIORITÉ 2 : Métriques d'évaluation documentées

**Exigence du sujet :**
> "You must evaluate your NLP processing! And you must document the progress you've done on the NLP"

**Ce qui manque :**
- ❌ Document récapitulatif des métriques
- ❌ Comparaison des modèles (baseline vs CamemBERT)
- ❌ Métriques pour le classifieur (Accuracy, F1, Precision, Recall)
- ❌ Métriques pour le NER (F1 par entité, Precision, Recall)
- ❌ Analyse d'erreurs détaillée
- ❌ Évolution des métriques (avant/après fine-tuning)

**Action requise :**
Créer `docs/METRICS_EVALUATION.md` ou section dans le rapport principal

---

### 🟡 PRIORITÉ 3 : Isolabilité du module NLP

**Exigence du sujet :**
> "The NLP part MUST be isolated for testing and evaluation purpose."

**Ce qui existe :**
- ✅ Le module NLP est dans `api/pipeline.py` mais est lié à FastAPI
- ✅ Les modèles sont séparés mais pas vraiment "isolés"

**Ce qui manque :**
- ❌ Script CLI standalone pour le NLP
- ❌ Module NLP pouvant être utilisé indépendamment de l'API
- ⚠️ Actuellement, le NLP est intégré dans l'API mais pourrait être mieux isolé

**Action requise :**
Créer un script `scripts/nlp_standalone.py` qui peut être utilisé indépendamment :
```bash
python scripts/nlp_standalone.py "Je vais de Paris à Lyon"
# Output: VALID,Paris,Lyon
```

---

### 🟢 PRIORITÉ 4 : Bonuses (optionnels mais valorisés)

#### Bonus 1 : Arrêts intermédiaires
- ❌ Détection des arrêts intermédiaires ("en passant par Limoges")
- ❌ Format : `sentenceID,Departure,Step1,Step2,Destination`

#### Bonus 2 : Autres langues
- ❌ Support pour d'autres langues (anglais, etc.)

#### Bonus 3 : Reconnaissance vocale
- ❌ Module voice-to-text
- ❌ Intégration avec le pipeline NLP

#### Bonus 4 : Optimisations avancées
- ❌ Temps d'attente dans les gares intermédiaires
- ❌ Complexité computationnelle optimisée
- ❌ Monitoring CPU/RAM

---

## 📋 Plan d'Action Recommandé

### Phase 1 : Format d'entrée/sortie (URGENT) - ✅ COMPLÉTÉ
1. ✅ Créer `scripts/process_input.py` avec format spécifique
2. ✅ Tester avec fichiers d'exemple
3. ✅ Documenter l'utilisation
4. ✅ Intégration dans le chatbot web (page CSV séparée)
5. ✅ Support du format avec pathfinding (étapes intermédiaires)

### Phase 2 : Pathfinding (URGENT) - ✅ COMPLÉTÉ
1. ✅ Créer module `pathfinding/`
2. ✅ Implémenter construction du graphe
3. ✅ Implémenter algorithmes de recherche (Dijkstra + A*)
4. ✅ Intégrer avec données SNCF
5. ✅ Tester avec exemples réels
6. ✅ Intégration dans le pipeline : `sentenceID,Departure,Destination` → `sentenceID,Departure,Step1,...,Destination`
7. ✅ Script de test/comparaison des algorithmes

### Phase 3 : Documentation PDF (IMPORTANT)
1. Rédiger rapport complet en Markdown
2. Convertir en PDF
3. Inclure tous les éléments requis (architecture, entraînement, paramètres, exemples, résultats)

### Phase 4 : Métriques et évaluation (IMPORTANT)
1. Compiler toutes les métriques existantes
2. Créer document récapitulatif
3. Analyser les erreurs
4. Comparer les modèles

### Phase 5 : Isolation NLP (MOYEN)
1. Créer script standalone
2. Tester indépendamment
3. Documenter

### Phase 6 : Bonuses (SI TEMPS)
1. Prioriser selon intérêt/valeur
2. Arrêts intermédiaires si possible
3. Autres langues si temps
4. Voice-to-text si temps

---

## 📊 État d'Avancement Global

| Composant | État | Priorité | Est. Temps |
|-----------|------|----------|------------|
| NLP (Classification + NER) | ✅ 95% | - | - |
| Post-processing NLP | ✅ 100% | ✅ Complété | - |
| Format I/O spécifique | ✅ 100% | ✅ Complété | ✅ 2-4h |
| Pathfinding (Dijkstra + A*) | ✅ 100% | ✅ Complété | ✅ 8-16h |
| Intégration Pipeline | ✅ 100% | ✅ Complété | - |
| Frontend (Chatbot + CSV) | ✅ 100% | ✅ Complété | - |
| Documentation PDF | ❌ 20% | 🟡 Moyenne | 8-12h |
| Métriques documentées | ❌ 40% | 🟡 Moyenne | 4-6h |
| Isolation NLP | ⚠️ 70% | 🟢 Basse | 2-3h |
| Bonuses | ❌ 0% | 🟢 Optionnel | Variable |

---

## 🎯 Résumé

**Points forts :**
- ✅ Module NLP robuste et fonctionnel avec post-processing avancé
- ✅ Pipeline complet intégré (NLP + Pathfinding)
- ✅ Module Pathfinding complet (Dijkstra + A*)
- ✅ Modèles entraînés et performants
- ✅ Infrastructure complète (API FastAPI, Frontend séparé, Docker)
- ✅ Format I/O conforme au sujet avec support pathfinding
- ✅ Interface utilisateur moderne (chatbot + CSV upload séparés)

**Points à compléter :**
- ❌ Documentation PDF complète (rapport final)
- ❌ Métriques documentées (compilation et analyse)
- ⚠️ Isolation NLP (amélioration possible mais fonctionnel)

**Recommandation :**
1. ✅ **Complété** : Format I/O et pathfinding (requis pour livraison) ✅
2. **Prioriser maintenant** : Documentation PDF complète
3. **Ensuite** : Compiler et documenter les métriques
4. **Enfin** : Améliorer isolation et ajouter bonuses si temps

**État actuel :**
Le système est **fonctionnellement complet** pour la livraison. Les composants principaux (NLP, Pathfinding, API, Frontend) sont tous implémentés et intégrés. Il reste principalement la documentation finale à compléter.
