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
- ✅ Post-processing (nettoyage caractères spéciaux, séparation Ville-Ville)

### 2. Infrastructure
- ✅ API FastAPI
- ✅ Frontend chatbot
- ✅ Docker et docker-compose
- ✅ Documentation partielle (Markdown)
- ✅ Journaux de bord (classifier et NLP)

---

## ❌ Ce qui MANQUE selon le sujet

### 🔴 PRIORITÉ 1 : Format d'entrée/sortie spécifique

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
- Le chatbot web a maintenant **aussi** une fonctionnalité CSV intégrée (upload de fichier)
- Les deux systèmes utilisent le même pipeline NLP et respectent le format du sujet
- Voir `docs/CHATBOT_VS_CLI.md` pour la différence entre chatbot et CLI
- Voir `docs/CSV_CHATBOT_INTEGRATION.md` pour l'utilisation CSV dans le chatbot

---

### 🔴 PRIORITÉ 1 : Module Pathfinding (Graph)

**Exigence du sujet :**
- Trouver un itinéraire optimal entre deux villes/gares
- Format de sortie : `sentenceID,Departure,Step1,Step2,...,Destination`
- Utiliser les données SNCF (gares-francaises.json)
- Trouver le chemin le plus court ou le plus rapide

**Ce qui manque :**
- ❌ Module de pathfinding
- ❌ Construction d'un graphe depuis les données de gares
- ❌ Algorithmes de recherche de chemin (Dijkstra, A*, etc.)
- ❌ Intégration avec les données SNCF
- ❌ Script pour générer la sortie finale avec étapes intermédiaires

**Action requise :**
Créer un module `pathfinding/` avec :
- `pathfinding/graph_builder.py` : Construire le graphe depuis gares-francaises.json
- `pathfinding/route_finder.py` : Trouver les itinéraires (Dijkstra ou similaire)
- `pathfinding/__init__.py` : Interface simple
- Script principal : `scripts/find_routes.py` qui prend `sentenceID,Departure,Destination` en entrée

**Note :** Le sujet dit que c'est "not the core" mais c'est quand même requis pour la livraison finale.

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

### Phase 1 : Format d'entrée/sortie (URGENT)
1. Créer `scripts/process_input.py` avec format spécifique
2. Tester avec fichiers d'exemple
3. Documenter l'utilisation

### Phase 2 : Pathfinding (URGENT)
1. Créer module `pathfinding/`
2. Implémenter construction du graphe
3. Implémenter algorithme de recherche (Dijkstra)
4. Intégrer avec données SNCF
5. Tester avec exemples réels
6. Créer script final : `sentenceID,Departure,Destination` → `sentenceID,Departure,Step1,...,Destination`

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
| NLP (Classification + NER) | ✅ 90% | - | - |
| Format I/O spécifique | ✅ 100% | ✅ Complété | ✅ 2-4h |
| Pathfinding | ❌ 0% | 🔴 Haute | 8-16h |
| Documentation PDF | ❌ 20% | 🟡 Moyenne | 8-12h |
| Métriques documentées | ❌ 40% | 🟡 Moyenne | 4-6h |
| Isolation NLP | ⚠️ 70% | 🟢 Basse | 2-3h |
| Bonuses | ❌ 0% | 🟢 Optionnel | Variable |

---

## 🎯 Résumé

**Points forts :**
- ✅ Module NLP robuste et fonctionnel
- ✅ Pipeline complet intégré
- ✅ Modèles entraînés et performants
- ✅ Infrastructure (API, Docker) en place

**Points à compléter :**
- ❌ Format d'entrée/sortie selon spécification
- ❌ Module pathfinding (graph)
- ❌ Documentation PDF complète
- ❌ Métriques documentées

**Recommandation :**
1. **Prioriser** le format I/O et le pathfinding (requis pour livraison)
2. **Ensuite** compléter la documentation PDF
3. **Enfin** améliorer isolation et ajouter bonuses si temps
