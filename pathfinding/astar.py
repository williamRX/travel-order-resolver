#!/usr/bin/env python3
"""
Implémentation de l'algorithme A* pour trouver le chemin le plus court.
"""

import heapq
from typing import Dict, List, Optional, Tuple
from pathfinding.utils import haversine_distance


def astar(
    graph: Dict[str, Dict[str, float]],
    start: str,
    end: str,
    stations_data: Optional[Dict[str, Dict]] = None
) -> Tuple[Optional[List[str]], float]:
    """
    Trouve le chemin le plus court entre deux nœuds en utilisant l'algorithme A*.
    
    A* est une amélioration de Dijkstra qui utilise une heuristique pour
    explorer moins de nœuds. L'heuristique utilisée est la distance à vol d'oiseau
    jusqu'à la destination.
    
    Complexité : O((V + E) log V) dans le pire cas, mais généralement plus rapide que Dijkstra
    
    Args:
        graph: Graphe sous forme de dictionnaire {nœud: {voisin: poids, ...}, ...}
        start: Nœud de départ
        end: Nœud d'arrivée
        stations_data: Dictionnaire {nom_gare: {position_geographique: {lat, lon}, ...}}
                      pour calculer l'heuristique (optionnel)
    
    Returns:
        Tuple (chemin, distance) où :
        - chemin: Liste des nœuds du chemin [start, ..., end] ou None si pas de chemin
        - distance: Distance totale du chemin ou float('inf') si pas de chemin
    """
    # Vérifier que les nœuds existent
    if start not in graph:
        return None, float('inf')
    if end not in graph:
        return None, float('inf')
    
    # Si départ = arrivée
    if start == end:
        return [start], 0.0
    
    # Initialisation
    # g_score[n] = coût réel du chemin depuis start jusqu'à n
    g_score: Dict[str, float] = {node: float('inf') for node in graph}
    g_score[start] = 0.0
    
    # f_score[n] = g_score[n] + heuristique(n, end)
    # File de priorité : (f_score, nœud)
    f_start = _heuristic(start, end, stations_data)
    priority_queue = [(f_start, start)]
    
    # Pour reconstruire le chemin
    previous: Dict[str, Optional[str]] = {node: None for node in graph}
    
    # Ensemble des nœuds visités
    visited: set = set()
    
    while priority_queue:
        # Extraire le nœud avec le plus petit f_score
        current_f_score, current_node = heapq.heappop(priority_queue)
        
        # Si on a déjà visité ce nœud, ignorer
        if current_node in visited:
            continue
        
        # Marquer comme visité
        visited.add(current_node)
        
        # Si on a atteint la destination, reconstruire le chemin
        if current_node == end:
            path = []
            node = end
            while node is not None:
                path.append(node)
                node = previous[node]
            path.reverse()
            return path, g_score[end]
        
        # Explorer les voisins
        neighbors = graph.get(current_node, {})
        for neighbor, weight in neighbors.items():
            if neighbor in visited:
                continue
            
            # Calculer le nouveau g_score
            tentative_g_score = g_score[current_node] + weight
            
            # Si on a trouvé un meilleur chemin vers ce voisin
            if tentative_g_score < g_score[neighbor]:
                # Enregistrer ce meilleur chemin
                previous[neighbor] = current_node
                g_score[neighbor] = tentative_g_score
                
                # Calculer f_score = g_score + heuristique
                f_score = tentative_g_score + _heuristic(neighbor, end, stations_data)
                
                heapq.heappush(priority_queue, (f_score, neighbor))
    
    # Pas de chemin trouvé
    return None, float('inf')


def _heuristic(
    node: str,
    goal: str,
    stations_data: Optional[Dict[str, Dict]] = None
) -> float:
    """
    Heuristique pour A* : distance à vol d'oiseau jusqu'à la destination.
    
    Cette heuristique est admissible (ne surestime jamais le coût réel)
    car la distance à vol d'oiseau est toujours <= distance réelle.
    
    Args:
        node: Nœud actuel
        goal: Nœud destination
        stations_data: Données des stations pour calculer la distance
    
    Returns:
        Distance heuristique (en kilomètres)
    """
    if not stations_data:
        # Si pas de données, retourner 0 (A* devient équivalent à Dijkstra)
        return 0.0
    
    node_data = stations_data.get(node)
    goal_data = stations_data.get(goal)
    
    if not node_data or not goal_data:
        return 0.0
    
    node_pos = node_data.get('position_geographique', {})
    goal_pos = goal_data.get('position_geographique', {})
    
    if not node_pos or not goal_pos:
        return 0.0
    
    lat1 = node_pos.get('lat', 0)
    lon1 = node_pos.get('lon', 0)
    lat2 = goal_pos.get('lat', 0)
    lon2 = goal_pos.get('lon', 0)
    
    if lat1 == 0 or lon1 == 0 or lat2 == 0 or lon2 == 0:
        return 0.0
    
    return haversine_distance(lat1, lon1, lat2, lon2)


def astar_with_stats(
    graph: Dict[str, Dict[str, float]],
    start: str,
    end: str,
    stations_data: Optional[Dict[str, Dict]] = None
) -> Tuple[Optional[List[str]], float, Dict]:
    """
    Version de A* qui retourne aussi des statistiques.
    
    Args:
        graph: Graphe
        start: Nœud de départ
        end: Nœud d'arrivée
        stations_data: Données des stations pour l'heuristique
    
    Returns:
        Tuple (chemin, distance, stats) où stats contient :
        - nodes_explored: Nombre de nœuds explorés
        - edges_explored: Nombre d'arêtes explorées
    """
    if start not in graph or end not in graph:
        return None, float('inf'), {'nodes_explored': 0, 'edges_explored': 0}
    
    if start == end:
        return [start], 0.0, {'nodes_explored': 1, 'edges_explored': 0}
    
    g_score: Dict[str, float] = {node: float('inf') for node in graph}
    g_score[start] = 0.0
    
    f_start = _heuristic(start, end, stations_data)
    priority_queue = [(f_start, start)]
    previous: Dict[str, Optional[str]] = {node: None for node in graph}
    visited: set = set()
    
    nodes_explored = 0
    edges_explored = 0
    
    while priority_queue:
        current_f_score, current_node = heapq.heappop(priority_queue)
        
        if current_node in visited:
            continue
        
        visited.add(current_node)
        nodes_explored += 1
        
        if current_node == end:
            path = []
            node = end
            while node is not None:
                path.append(node)
                node = previous[node]
            path.reverse()
            return path, g_score[end], {
                'nodes_explored': nodes_explored,
                'edges_explored': edges_explored
            }
        
        neighbors = graph.get(current_node, {})
        for neighbor, weight in neighbors.items():
            edges_explored += 1
            if neighbor in visited:
                continue
            
            tentative_g_score = g_score[current_node] + weight
            if tentative_g_score < g_score[neighbor]:
                previous[neighbor] = current_node
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + _heuristic(neighbor, end, stations_data)
                heapq.heappush(priority_queue, (f_score, neighbor))
    
    return None, float('inf'), {
        'nodes_explored': nodes_explored,
        'edges_explored': edges_explored
    }
