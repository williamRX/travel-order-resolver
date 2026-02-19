# Checklist & Roadmap (référence descriptif Gemini)

Ce document croise le descriptif projet (style Gemini) avec l’état actuel du repo : ce qui est fait, ce qui est partiel, et ce qui reste à faire.

---

## 1. Stratégie de Données (Data-Centric AI)

| Point Gemini | Fait ? | Détail |
|--------------|--------|--------|
| **Génération synthétique avancée** | Partiel | Templates complexes et nombreux patterns dans `dataset/generators/nlp/dataset_generator.py` (valides, semi-valides, négatifs). **Pas d’usage de LLM/API** pour variations linguistiques (argot, structures inversées). |
| **Data augmentation** | Oui | `nlp/data_augmentation.py` : typos (inversion/suppression/remplacement lettres), casse et ponctuation (lower/upper, suppression ponctuation), mots parasites (euh, du coup…). Appliquée dans le notebook NER. |
| **Suppression d’accents / bruit** | Oui | Typos et variantes de casse dans l’augmentation ; similarité caractères dans le générateur pour tolérance. |
| **Dataset étiqueté format BIO** | Oui | Labels `O`, `B-DEPARTURE`, `I-DEPARTURE`, `B-ARRIVAL`, `I-ARRIVAL` dans le notebook NER et le pipeline. Format cohérent avec NER BIO. |

**À faire (roadmap)**  
- Optionnel : utiliser un LLM (API) pour générer des variations linguistiques (argot, formulations inversées) et enrichir le dataset.  
- Enrichir encore les patterns “casse” et “villes à tirets” si besoin après éval.

---

## 2. Architecture NLP (Du simple au complexe)

| Point Gemini | Fait ? | Détail |
|--------------|--------|--------|
| **Baseline heuristiques / Regex** | Oui | Pré-traitement dans `api/pipeline.py` : extraction directe du pattern "Ville - Ville" par regex avant l’IA. Liste de gares (`gares-francaises.json`) utilisée partout (génération, matching). |
| **Spacy / CamemBERT** | Oui | CamemBERT pour la classification de validité et pour le NER (fine-tuning). SpaCy mentionné/utile pour préparation données ; le flux principal est CamemBERT. |
| **Fine-tuning NER** | Oui | Notebook `nlp/notebooks/02_ner_training_camembert.ipynb` : fine-tuning CamemBERT pour NER avec distinction **Origine (DEPARTURE) / Destination (ARRIVAL)**. |
| **Gestion des ambiguïtés (Paris nom vs ville)** | Partiel | Contexte pris en compte dans le générateur (mots-clés départ/arrivée, patterns “avec/chez” vs “à/de”). Pas de couche dédiée “ambiguïté nom propre vs ville” dans le pipeline de prédiction. |

**À faire (roadmap)**  
- Documenter ou renforcer la logique “préposition de lieu” (à, de, vers) vs “avec/chez” pour réduire confusions type “Paris” nom de famille.  
- Optionnel : baseline regex pure (sans modèle) sur un sous-ensemble de test pour chiffrer le gain du NER.

---

## 3. Moteur de Graphes (Pathfinding)

| Point Gemini | Fait ? | Détail |
|--------------|--------|--------|
| **Modélisation type “graphe”** | Oui (in-memory) | Gares = nœuds, trajets = arêtes dans `pathfinding/graph_builder.py` (dict de dict). **Pas de Neo4j** : graphe en mémoire. |
| **Propriétés sur les relations (durée, prix)** | Partiel | Distance (km) sur les arêtes. **Durée et prix** pas dans le graphe local ; l’API SNCF renvoie durée (et infos trajet), pas stockées dans le graphe. |
| **Dijkstra** | Oui | `pathfinding/dijkstra.py` : plus court chemin en distance. |
| **A\*** | Oui | `pathfinding/astar.py` : A* avec heuristique (distance géo). |
| **Multi-critères (rapide vs moins de changements)** | Non | Un seul critère (distance) pour le graphe local. Pas d’option “le plus rapide” vs “moins de changements”. |

**À faire (roadmap)**  
- Optionnel : ajouter durée estimée sur les arêtes (ex. dérivée de la distance) et critère “temps” en plus de la distance.  
- Optionnel : Neo4j si besoin de persistance / requêtes graphe avancées.  
- Bonus : proposer 2 modes (ex. “le plus court” vs “le moins de changements”) si le graphe a des métriques adaptées.

---

## 4. Pipeline d’Évaluation

| Point Gemini | Fait ? | Détail |
|--------------|--------|--------|
| **Métriques classification (Précision, Rappel, F1)** | Oui | NER : `seqeval` dans le notebook (precision, recall, F1). Classifieur validité : accuracy, precision, recall, F1, ROC AUC dans les notebooks classifier. |
| **Métriques par entité (DEPARTURE vs ARRIVAL)** | Oui | Rapport seqeval par type d’entité ; métriques par label dans le notebook NER. |
| **Matrice de confusion** | Partiel | Matrice de confusion pour le **classifieur validité** (valid/invalid). **Pas de matrice de confusion dédiée NER** (confusion Départ vs Arrivée au niveau token ou phrase). |
| **Stress test / robustesse** | Partiel | CSV `evaluations/test_examples.csv` avec phrases variées (casse, typos, villes à tirets, etc.) et section 11 du notebook NER pour test sur ce CSV. Pas de “stress test” formalisé (ex. Port-Boulet, phrases non-trajets). |

**À faire (roadmap)**  
- Ajouter une **matrice de confusion NER** (DEPARTURE vs ARRIVAL vs O / autres) sur un split test et la documenter.  
- Créer un **jeu de stress test** : phrases avec noms difficiles (ex. Port-Boulet), phrases hors trajet, et rapport d’erreurs associé.

---

## 5. Industrialisation et Bonus

| Point Gemini | Fait ? | Détail |
|--------------|--------|--------|
| **API FastAPI** | Oui | `api/main.py` : `/predict`, `/process_csv`, `/health`. |
| **Documentation (Swagger)** | Oui | Lien `/docs` (Swagger) sur la page d’accueil de l’API. |
| **Post-processing / Fuzzy (ex. “St Lazare” → “Paris Saint-Lazare”)** | Partiel | `pathfinding/utils.py` : `find_matching_stations` (normalisation, préfixe, sous-chaîne). **Pas de Levenshtein** ni fuzzy dédié. Similarité “caractères communs” dans le générateur de dataset. |
| **RAG (trajet inexistant → explication / alternative)** | Non | Pas de module RAG. Si pas de trajet, le pipeline renvoie un message d’erreur / pas de route, sans explication par graphe ni proposition d’alternative. |

**À faire (roadmap)**  
- **Fuzzy matching** : intégrer une distance de Levenshtein (ou librairie type `rapidfuzz`) pour mapper “St Lazare” → “Paris Saint-Lazare” (ou liste de candidats).  
- **Bonus RAG** : en cas de “pas de trajet”, utiliser le graphe (ou l’API) pour expliquer pourquoi et/ou proposer une gare proche / un trajet alternatif.

---

## Résumé : roadmap priorisée

### Priorité haute (impact direct sur la note / livrable)
1. **Matrice de confusion NER** : DEPARTURE vs ARRIVAL (et O) sur le jeu de test NER.  
2. **Stress test** : jeu d’exemples “difficiles” + rapport (phrases non-trajets, noms de gares complexes).  
3. **Fuzzy matching** : Levenshtein (ou équivalent) pour normaliser noms de gares (ex. “St Lazare” → “Paris Saint-Lazare”).

### Priorité moyenne (renforce le discours “pro”)
4. **Documentation** de la gestion des ambiguïtés (contexte “à/de” vs “avec/chez”).  
5. **Multi-critères pathfinding** : au moins “distance” vs “temps” (ou “moins de changements”) si les données le permettent.  
6. **Durée (et optionnellement prix)** sur les arêtes du graphe si vous voulez aligner avec le descriptif “propriétés sur les relations”.

### Priorité basse / bonus
7. **LLM pour génération** de variations linguistiques (argot, structures inversées).  
8. **Neo4j** : uniquement si besoin de persistance ou requêtes graphe avancées.  
9. **RAG** : explication “pourquoi pas de trajet” + proposition d’alternative à partir du graphe ou de l’API.

---

## Légende checklist

- **Oui** : déjà en place et utilisé dans le flux principal.  
- **Partiel** : partiellement fait (ex. pas de LLM, pas de Neo4j, pas de matrice de confusion NER).  
- **Non** : pas implémenté.

Ce document peut être mis à jour au fil des implémentations (renommer les lignes en “Oui” et déplacer les tâches correspondantes dans “Fait” ou “Améliorations récentes”).
