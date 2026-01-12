# Module Pathfinding

Module de recherche d'itinéraires ferroviaires entre villes/gares françaises.

## 🎯 Fonctionnalités

- **Dijkstra** : Algorithme classique pour trouver le chemin le plus court
- **A*** : Algorithme optimisé avec heuristique pour une recherche plus rapide
- **Construction automatique du graphe** depuis `gares-francaises.json`
- **Normalisation intelligente** des noms de villes/gares

## 📁 Structure

```
pathfinding/
├── __init__.py          # Interface principale
├── data_loader.py       # Chargement des données gares-francaises.json
├── graph_builder.py     # Construction du graphe de connexions
├── dijkstra.py          # Implémentation de l'algorithme Dijkstra
├── astar.py             # Implémentation de l'algorithme A*
├── route_finder.py      # Classe principale RouteFinder
└── utils.py             # Utilitaires (distance, normalisation)
```

## 🚀 Utilisation

### Exemple basique

```python
from pathfinding import RouteFinder

# Initialiser (charge les données et construit le graphe)
route_finder = RouteFinder()

# Trouver un itinéraire avec Dijkstra
result = route_finder.find_route("Paris", "Lyon", algorithm="dijkstra")

if result.success:
    print(f"Route: {' → '.join(result.route)}")
    print(f"Distance: {result.total_distance:.1f} km")
    print(f"Temps estimé: {result.estimated_time:.2f} h")
else:
    print(f"Erreur: {result.message}")
```

### Comparer Dijkstra et A*

```python
# Dijkstra
result_dijkstra = route_finder.find_route("Paris", "Lyon", algorithm="dijkstra", return_stats=True)

# A*
result_astar = route_finder.find_route("Paris", "Lyon", algorithm="astar", return_stats=True)

# Comparer les statistiques
print(f"Dijkstra - Nœuds explorés: {result_dijkstra.stats['nodes_explored']}")
print(f"A* - Nœuds explorés: {result_astar.stats['nodes_explored']}")
```

### Script de test

```bash
python scripts/test_pathfinding.py
```

Ce script compare les performances de Dijkstra et A* sur plusieurs trajets.

## 📊 Format de sortie

Le module retourne un `RouteResult` qui peut être converti en format CSV :

```python
result = route_finder.find_route("Paris", "Lyon")
csv_output = result.to_csv_format("1")
# → "1,Paris,Dijon,Lyon"
```

## 🔧 Configuration

### Paramètres du graphe

```python
route_finder = RouteFinder(
    max_distance_km=200.0,    # Distance max pour connecter deux gares
    connect_hubs=True         # Connecter tous les hubs entre eux
)
```

### Algorithmes disponibles

- **`dijkstra`** : Algorithme classique, garanti optimal
- **`astar`** : Algorithme optimisé avec heuristique, généralement plus rapide

## 📈 Complexité

- **Dijkstra** : O((V + E) log V) où V = nombre de sommets, E = nombre d'arêtes
- **A*** : O((V + E) log V) dans le pire cas, mais généralement plus rapide grâce à l'heuristique

## 🧪 Tests

Voir `scripts/test_pathfinding.py` pour des exemples de tests et comparaisons.
