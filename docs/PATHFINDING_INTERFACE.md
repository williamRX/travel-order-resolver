# Interface du Module Pathfinding

## 📥 Entrée du Module Pathfinding

### Format d'entrée (selon le sujet)

Le module pathfinding reçoit en entrée le résultat du module NLP :

**Format** : `sentenceID,Departure,Destination`

**Exemples** :
```
1,Paris,Lyon
2,Bordeaux,Toulouse
3,Marseille,Nice
4,Brest,Rennes
```

### Interface Python (dans le code)

```python
from pathfinding import RouteFinder

# Initialisation (une seule fois)
route_finder = RouteFinder()

# Pour chaque trajet
result = route_finder.find_route(
    departure="Paris",
    destination="Lyon"
)
```

**Paramètres d'entrée** :
- `departure` : str - Nom de la ville/gare de départ (ex: "Paris")
- `destination` : str - Nom de la ville/gare d'arrivée (ex: "Lyon")

**Optionnel** :
- `max_stops` : int - Nombre maximum d'étapes intermédiaires (défaut: 10)
- `prefer_direct` : bool - Préférer les trajets directs (défaut: True)

---

## 📤 Sortie du Module Pathfinding

### Format de sortie (selon le sujet)

**Format** : `sentenceID,Departure,Step1,Step2,...,Destination`

**Exemples** :

#### Cas 1 : Trajet Direct (pas d'étapes intermédiaires)
```
Entrée  : 1,Paris,Lyon
Sortie  : 1,Paris,Lyon
```

#### Cas 2 : Trajet avec Étapes Intermédiaires
```
Entrée  : 2,Brest,Marseille
Sortie  : 2,Brest,Rennes,Paris,Lyon,Marseille
```

#### Cas 3 : Trajet Impossible
```
Entrée  : 3,Paris,New York
Sortie  : 3,NO_ROUTE
```
ou
```
Sortie  : 3,INVALID
```

### Interface Python (dans le code)

```python
# Retourne un objet RouteResult
result = route_finder.find_route("Paris", "Lyon")

# Structure de RouteResult
class RouteResult:
    success: bool              # True si route trouvée
    route: List[str]          # ["Paris", "Dijon", "Lyon"]
    total_distance: float      # Distance totale en km
    estimated_time: float     # Temps estimé en heures
    message: Optional[str]    # Message d'erreur si échec
```

**Exemple d'utilisation** :
```python
result = route_finder.find_route("Paris", "Lyon")

if result.success:
    print(f"Route trouvée : {' → '.join(result.route)}")
    print(f"Distance : {result.total_distance} km")
    print(f"Temps estimé : {result.estimated_time} heures")
    # Format pour sortie CSV : ",".join(result.route)
    # → "Paris,Dijon,Lyon"
else:
    print(f"Erreur : {result.message}")
    # Format pour sortie CSV : "NO_ROUTE"
```

---

## 🔄 Flux Complet : NLP → Pathfinding → Sortie

```
┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 1 : NLP (déjà fait)                                  │
│  ─────────────────────────────────────────────────────────  │
│  Entrée  : "1,Je vais de Paris à Lyon"                     │
│  Sortie  : "1,Paris,Lyon"                                  │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 2 : Pathfinding (à implémenter)                     │
│  ─────────────────────────────────────────────────────────  │
│  Entrée  : "1,Paris,Lyon"                                  │
│  Traitement :                                               │
│    - Normaliser "Paris" → "Paris Gare de Lyon"            │
│    - Normaliser "Lyon" → "Lyon Part-Dieu"                 │
│    - Exécuter Dijkstra sur le graphe                      │
│    - Trouver chemin : [Paris, Dijon, Lyon]               │
│  Sortie  : "1,Paris,Dijon,Lyon"                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Détails de l'Implémentation Dijkstra

### Entrée de l'algorithme Dijkstra

```python
def dijkstra(graph, start_node, end_node):
    """
    Trouve le chemin le plus court entre deux nœuds.
    
    Args:
        graph: NetworkX Graph ou dict représentant le graphe
               {
                   "Paris": {"Dijon": 315, "Lyon": 463},
                   "Dijon": {"Paris": 315, "Lyon": 192},
                   "Lyon": {"Paris": 463, "Dijon": 192}
               }
        start_node: str - Nom de la gare de départ (ex: "Paris")
        end_node: str - Nom de la gare d'arrivée (ex: "Lyon")
    
    Returns:
        List[str] - Chemin trouvé (ex: ["Paris", "Dijon", "Lyon"])
                   ou [] si aucun chemin trouvé
    """
```

### Sortie de l'algorithme Dijkstra

```python
# Succès
path = ["Paris", "Dijon", "Lyon"]
distance = 507  # km (315 + 192)

# Échec (pas de chemin possible)
path = []
distance = float('inf')
```

---

## 📋 Exemples Concrets

### Exemple 1 : Trajet Simple

**Entrée NLP** : `1,Je vais de Paris à Lyon`
```
↓
NLP extrait : departure="Paris", arrival="Lyon"
↓
Pathfinding reçoit : find_route("Paris", "Lyon")
↓
Dijkstra trouve : ["Paris", "Dijon", "Lyon"]
↓
Sortie finale : 1,Paris,Dijon,Lyon
```

### Exemple 2 : Trajet Direct Possible

**Entrée NLP** : `2,Bordeaux,Toulouse`
```
↓
NLP extrait : departure="Bordeaux", arrival="Toulouse"
↓
Pathfinding reçoit : find_route("Bordeaux", "Toulouse")
↓
Dijkstra trouve : ["Bordeaux", "Toulouse"]  (connexion directe)
↓
Sortie finale : 2,Bordeaux,Toulouse
```

### Exemple 3 : Trajet Long avec Plusieurs Étapes

**Entrée NLP** : `3,Brest,Marseille`
```
↓
NLP extrait : departure="Brest", arrival="Marseille"
↓
Pathfinding reçoit : find_route("Brest", "Marseille")
↓
Dijkstra trouve : ["Brest", "Rennes", "Paris", "Lyon", "Marseille"]
↓
Sortie finale : 3,Brest,Rennes,Paris,Lyon,Marseille
```

### Exemple 4 : Trajet Impossible

**Entrée NLP** : `4,Paris,New York`
```
↓
NLP extrait : departure="Paris", arrival="New York"
↓
Pathfinding reçoit : find_route("Paris", "New York")
↓
Normalisation : "New York" n'est pas dans gares-francaises.json
↓
Sortie finale : 4,NO_ROUTE
```

---

## 🔧 Interface Complète du Module

### Classe RouteFinder

```python
class RouteFinder:
    """Module de recherche d'itinéraires ferroviaires."""
    
    def __init__(self, graph_data_path: Optional[Path] = None):
        """
        Initialise le route finder.
        
        Args:
            graph_data_path: Chemin vers gares-francaises.json
                            (défaut: dataset/shared/gares-francaises.json)
        """
        # Charge les gares
        # Construit le graphe
        # Prépare les normalisateurs de noms
    
    def find_route(
        self,
        departure: str,
        destination: str,
        max_stops: int = 10
    ) -> RouteResult:
        """
        Trouve un itinéraire entre deux villes.
        
        Args:
            departure: Ville/gare de départ
            destination: Ville/gare d'arrivée
            max_stops: Nombre maximum d'étapes (défaut: 10)
        
        Returns:
            RouteResult avec le chemin trouvé ou message d'erreur
        """
        # 1. Normaliser les noms (départ et arrivée)
        # 2. Vérifier que les gares existent
        # 3. Exécuter Dijkstra
        # 4. Retourner le résultat
```

### Classe RouteResult

```python
@dataclass
class RouteResult:
    """Résultat d'une recherche d'itinéraire."""
    
    success: bool
    route: List[str] = field(default_factory=list)
    total_distance: float = 0.0
    estimated_time: float = 0.0
    message: Optional[str] = None
    
    def to_csv_format(self, sentence_id: str) -> str:
        """
        Convertit en format CSV selon le sujet.
        
        Args:
            sentence_id: ID de la phrase originale
        
        Returns:
            Format: "sentenceID,Departure,Step1,...,Destination"
                   ou "sentenceID,NO_ROUTE"
        """
        if not self.success:
            return f"{sentence_id},NO_ROUTE"
        
        if len(self.route) <= 2:
            # Trajet direct
            return f"{sentence_id},{','.join(self.route)}"
        else:
            # Trajet avec étapes
            return f"{sentence_id},{','.join(self.route)}"
```

---

## 📝 Script CLI d'Utilisation

### Script : `scripts/find_routes.py`

```bash
# Utilisation
python scripts/find_routes.py input.csv output.csv

# Format input.csv : sentenceID,Departure,Destination
# Format output.csv : sentenceID,Departure,Step1,...,Destination
```

**Exemple** :
```bash
# input.csv
1,Paris,Lyon
2,Bordeaux,Toulouse
3,Brest,Marseille

# output.csv (après traitement)
1,Paris,Dijon,Lyon
2,Bordeaux,Toulouse
3,Brest,Rennes,Paris,Lyon,Marseille
```

---

## 🎯 Résumé : Entrée/Sortie

| Composant | Entrée | Sortie |
|-----------|--------|--------|
| **Module Pathfinding** | `departure: str`<br>`destination: str` | `RouteResult`<br>(route, distance, temps) |
| **Algorithme Dijkstra** | `graph`<br>`start_node: str`<br>`end_node: str` | `List[str]`<br>(chemin trouvé) |
| **Format CSV Final** | `sentenceID,Departure,Destination` | `sentenceID,Departure,Step1,...,Destination`<br>ou `sentenceID,NO_ROUTE` |

---

## 💡 Points Importants

1. **Normalisation** : "Paris" peut correspondre à plusieurs gares → choisir la plus appropriée
2. **Gestion d'erreurs** : Si gare non trouvée → retourner `NO_ROUTE`
3. **Trajets directs** : Si connexion directe existe → pas d'étapes intermédiaires
4. **Performance** : Dijkstra est efficace pour des graphes de ~3000 nœuds
