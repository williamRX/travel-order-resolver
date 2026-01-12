# Architecture du Module Pathfinding

## 🎯 Objectif

Le module Pathfinding a pour but de trouver un itinéraire optimal entre deux villes/gares françaises, en utilisant les données SNCF disponibles.

**Format d'entrée** : `sentenceID,Departure,Destination` (ex: `1,Paris,Lyon`)
**Format de sortie** : `sentenceID,Departure,Step1,Step2,...,Destination` (ex: `1,Paris,Dijon,Lyon`)

---

## 📊 Données Disponibles

### Fichier `gares-francaises.json`

Le fichier contient ~3000 gares avec :
- **Nom** : Nom complet de la gare (ex: "Paris Gare de Lyon")
- **Coordonnées GPS** : `lat` et `lon` pour chaque gare
- **Code UIC** : Identifiant unique de la gare
- **Segment DRG** : Catégorie de la gare (A, B, C)

**⚠️ Limitation importante** : Ce fichier ne contient **PAS** d'informations sur :
- Les connexions directes entre gares
- Les horaires de train
- Les temps de trajet
- Les lignes ferroviaires

---

## 🏗️ Architecture Proposée

### Option 1 : Graphe Basé sur la Distance Géographique (Recommandé pour MVP)

**Principe** : Construire un graphe où deux gares sont connectées si elles sont proches géographiquement.

#### Avantages :
- ✅ Simple à implémenter
- ✅ Pas besoin de données d'horaires réelles
- ✅ Fonctionne immédiatement
- ✅ Donne des résultats réalistes pour les grandes villes

#### Inconvénients :
- ⚠️ Ne reflète pas les vraies connexions ferroviaires
- ⚠️ Peut suggérer des trajets impossibles (ex: connexion directe entre deux petites gares éloignées)

#### Implémentation :

```
1. Charger toutes les gares depuis gares-francaises.json
2. Pour chaque gare, calculer la distance avec toutes les autres
3. Créer une arête si :
   - Distance < seuil (ex: 200 km)
   - OU si les deux gares sont des "hubs" majeurs (segment_drg = "A")
4. Poids de l'arête = distance géographique (ou temps estimé basé sur distance)
5. Utiliser Dijkstra pour trouver le chemin le plus court
```

### Option 2 : Graphe Basé sur les Données SNCF Réelles (Idéal mais complexe)

**Principe** : Utiliser les données Open Data SNCF pour construire un graphe réel des connexions.

#### Sources de données possibles :
- **SNCF Open Data** : https://ressources.data.sncf.com/
- **Horaires réels** : Fichiers GTFS (General Transit Feed Specification)
- **Lignes ferroviaires** : Données des lignes TGV, TER, etc.

#### Avantages :
- ✅ Reflète la réalité des trajets
- ✅ Peut inclure les temps de trajet réels
- ✅ Plus précis et utile

#### Inconvénients :
- ⚠️ Nécessite de télécharger/parser des données SNCF
- ⚠️ Plus complexe à implémenter
- ⚠️ Données peuvent être volumineuses

---

## 🔧 Structure du Module

```
pathfinding/
├── __init__.py              # Interface principale
├── graph_builder.py          # Construction du graphe
├── route_finder.py           # Algorithmes de recherche (Dijkstra, A*)
├── data_loader.py            # Chargement des données gares-francaises.json
└── utils.py                 # Utilitaires (distance, normalisation noms)
```

---

## 📐 Algorithme de Recherche

### Dijkstra (Recommandé pour débuter)

**Principe** : Trouve le chemin le plus court dans un graphe pondéré.

**Complexité** : O((V + E) log V) où V = nombre de sommets, E = nombre d'arêtes

**Pseudo-code** :
```
1. Initialiser : distance[départ] = 0, distance[tous les autres] = ∞
2. Créer une file de priorité avec (distance, gare)
3. Tant que la file n'est pas vide :
   a. Extraire la gare avec la plus petite distance
   b. Si c'est la destination, retourner le chemin
   c. Pour chaque voisin :
      - Calculer nouvelle_distance = distance[actuelle] + poids(arête)
      - Si nouvelle_distance < distance[voisin] :
        * Mettre à jour distance[voisin]
        * Ajouter voisin à la file
        * Enregistrer le prédécesseur pour reconstruire le chemin
4. Retourner le chemin reconstruit
```

### A* (Optimisation possible)

**Principe** : Amélioration de Dijkstra avec une heuristique (distance à vol d'oiseau jusqu'à la destination).

**Avantage** : Plus rapide que Dijkstra car explore moins de nœuds.

**Heuristique** : Distance géographique (haversine) entre la gare actuelle et la destination.

---

## 🗺️ Construction du Graphe

### Étape 1 : Normalisation des Noms de Villes

**Problème** : Le NLP peut retourner "Paris" mais la gare s'appelle "Paris Gare de Lyon" ou "Paris Nord".

**Solution** :
- Créer un mapping ville → liste de gares possibles
- Exemple : "Paris" → ["Paris Gare de Lyon", "Paris Nord", "Paris Montparnasse", ...]
- Pour le départ/arrivée, choisir la gare la plus appropriée (ex: la plus grande, la plus centrale)

### Étape 2 : Création des Arêtes

#### Stratégie 1 : Distance Seule
```python
for gare1 in gares:
    for gare2 in gares:
        distance = haversine(gare1, gare2)
        if distance < SEUIL_MAX (ex: 200 km):
            graph.add_edge(gare1, gare2, weight=distance)
```

#### Stratégie 2 : Hubs Majeurs
```python
# Connecter toutes les gares de catégorie A entre elles
hubs = [gare for gare in gares if gare.segment_drg == "A"]
for hub1 in hubs:
    for hub2 in hubs:
        if hub1 != hub2:
            distance = haversine(hub1, hub2)
            graph.add_edge(hub1, hub2, weight=distance)

# Connecter les petites gares aux hubs proches
for gare in gares:
    if gare.segment_drg != "A":
        nearest_hub = trouver_hub_le_plus_proche(gare, hubs)
        graph.add_edge(gare, nearest_hub, weight=haversine(gare, nearest_hub))
```

#### Stratégie 3 : Réseau Hiérarchique
```
Niveau 1 : Hubs majeurs (Paris, Lyon, Marseille, etc.) - tous connectés entre eux
Niveau 2 : Gares régionales - connectées aux hubs de leur région
Niveau 3 : Petites gares - connectées aux gares régionales proches
```

### Étape 3 : Calcul des Poids

**Option 1 : Distance géographique**
```python
weight = haversine(gare1, gare2)  # en kilomètres
```

**Option 2 : Temps estimé**
```python
distance = haversine(gare1, gare2)
# Vitesse moyenne train : 150 km/h (TER) à 300 km/h (TGV)
if distance > 300:
    vitesse = 280  # TGV
elif distance > 100:
    vitesse = 200  # Intercités
else:
    vitesse = 120  # TER
weight = distance / vitesse  # en heures
```

---

## 🔍 Exemple Concret

### Entrée : `1,Paris,Lyon`

#### Étape 1 : Normalisation
- "Paris" → Choisir "Paris Gare de Lyon" (hub majeur)
- "Lyon" → Choisir "Lyon Part-Dieu" (hub majeur)

#### Étape 2 : Recherche du Chemin
```
Paris Gare de Lyon → [Dijon Ville] → Lyon Part-Dieu
```

#### Étape 3 : Sortie
```
1,Paris,Dijon,Lyon
```

**Note** : Si connexion directe possible, la sortie serait `1,Paris,Lyon` (sans étapes intermédiaires).

---

## 🚀 Implémentation Progressive

### Phase 1 : MVP Simple
1. ✅ Charger `gares-francaises.json`
2. ✅ Construire graphe basé sur distance (seuil 200 km)
3. ✅ Implémenter Dijkstra
4. ✅ Normalisation basique des noms
5. ✅ Script CLI : `sentenceID,Departure,Destination` → `sentenceID,Departure,Step1,...,Destination`

### Phase 2 : Amélioration
1. ✅ Graphe hiérarchique (hubs majeurs)
2. ✅ Heuristique A* pour performance
3. ✅ Meilleure normalisation (fuzzy matching)
4. ✅ Gestion des cas edge (gares non trouvées, trajets impossibles)

### Phase 3 : Données Réelles (Optionnel)
1. ⚠️ Télécharger données SNCF Open Data
2. ⚠️ Parser horaires GTFS
3. ⚠️ Construire graphe avec connexions réelles
4. ⚠️ Intégrer temps de trajet réels

---

## 📦 Bibliothèques Utiles

### Pour le Graphe
- **NetworkX** : Bibliothèque Python pour graphes (recommandé)
  ```python
  import networkx as nx
  G = nx.Graph()
  G.add_edge('Paris', 'Lyon', weight=463)
  path = nx.shortest_path(G, 'Paris', 'Lyon', weight='weight')
  ```

### Pour les Distances
- **geopy** : Calcul de distances géographiques (haversine)
  ```python
  from geopy.distance import geodesic
  distance = geodesic((lat1, lon1), (lat2, lon2)).kilometers
  ```

### Alternative : Implémentation Manuelle
- Dijkstra peut être implémenté avec `heapq` (file de priorité)
- Haversine peut être implémenté manuellement (formule mathématique)

---

## 🎯 Format de Sortie Final

### Cas 1 : Trajet Direct
**Entrée** : `1,Paris,Lyon`
**Sortie** : `1,Paris,Lyon` (pas d'étapes intermédiaires si connexion directe)

### Cas 2 : Trajet avec Étapes
**Entrée** : `2,Brest,Marseille`
**Sortie** : `2,Brest,Rennes,Paris,Lyon,Marseille`

### Cas 3 : Trajet Impossible
**Entrée** : `3,Paris,New York` (ville non française)
**Sortie** : `3,NO_ROUTE` ou `3,INVALID`

---

## 🔄 Intégration avec le Pipeline

```
1. NLP extrait : Departure="Paris", Destination="Lyon"
2. Pathfinding reçoit : ("Paris", "Lyon")
3. Pathfinding trouve : ["Paris", "Dijon", "Lyon"]
4. Format final : "1,Paris,Dijon,Lyon"
```

---

## 📝 Prochaines Étapes

1. **Créer le module `pathfinding/`**
2. **Implémenter `graph_builder.py`** (construction du graphe)
3. **Implémenter `route_finder.py`** (Dijkstra)
4. **Créer script `scripts/find_routes.py`** (CLI pour pathfinding)
5. **Tester avec exemples réels**
6. **Intégrer avec le pipeline NLP**

---

## 💡 Notes Importantes

- Le pathfinding n'est **pas le cœur du projet** (le NLP l'est)
- Une solution simple mais fonctionnelle est préférable à une solution complexe
- On peut commencer avec un graphe basé sur distance, puis améliorer avec données réelles si temps
- La complexité algorithmique doit être documentée (comme demandé dans le sujet)
