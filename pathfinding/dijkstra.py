#!/usr/bin/env python3
"""
Implémentation de l'algorithme de Dijkstra pour trouver le chemin le plus court.
"""

import heapq
from typing import Dict, List, Optional, Tuple


def dijkstra(
    graph: Dict[str, Dict[str, float]],
    start: str,
    end: str
) -> Tuple[Optional[List[str]], float]:
    """
    Trouve le chemin le plus court entre deux nœuds en utilisant l'algorithme de Dijkstra.
    
    Complexité : O((V + E) log V) où V = nombre de sommets, E = nombre d'arêtes
    
    Args:
        graph: Graphe sous forme de dictionnaire {nœud: {voisin: poids, ...}, ...}
        start: Nœud de départ
        end: Nœud d'arrivée
    
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
    distances: Dict[str, float] = {node: float('inf') for node in graph}
    distances[start] = 0.0
    
    # File de priorité : (distance, nœud)
    priority_queue = [(0.0, start)]
    
    # Pour reconstruire le chemin
    previous: Dict[str, Optional[str]] = {node: None for node in graph}
    
    # Ensemble des nœuds visités
    visited: set = set()
    
    while priority_queue:
        # Extraire le nœud avec la plus petite distance
        current_distance, current_node = heapq.heappop(priority_queue)
        
        # Si on a déjà visité ce nœud avec une distance plus petite, ignorer
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
            return path, distances[end]
        
        # Explorer les voisins
        neighbors = graph.get(current_node, {})
        for neighbor, weight in neighbors.items():
            if neighbor in visited:
                continue
            
            # Calculer la nouvelle distance
            new_distance = current_distance + weight
            
            # Si on a trouvé un chemin plus court
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current_node
                heapq.heappush(priority_queue, (new_distance, neighbor))
    
    # Pas de chemin trouvé
    return None, float('inf')


def dijkstra_with_stats(
    graph: Dict[str, Dict[str, float]],
    start: str,
    end: str
) -> Tuple[Optional[List[str]], float, Dict]:
    """
    Version de Dijkstra qui retourne aussi des statistiques.
    
    Args:
        graph: Graphe
        start: Nœud de départ
        end: Nœud d'arrivée
    
    Returns:
        Tuple (chemin, distance, stats) où stats contient :
        - nodes_explored: Nombre de nœuds explorés
        - edges_explored: Nombre d'arêtes explorées
    """
    if start not in graph or end not in graph:
        return None, float('inf'), {'nodes_explored': 0, 'edges_explored': 0}
    
    if start == end:
        return [start], 0.0, {'nodes_explored': 1, 'edges_explored': 0}
    
    distances: Dict[str, float] = {node: float('inf') for node in graph}
    distances[start] = 0.0
    
    priority_queue = [(0.0, start)]
    previous: Dict[str, Optional[str]] = {node: None for node in graph}
    visited: set = set()
    
    nodes_explored = 0
    edges_explored = 0
    
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        
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
            return path, distances[end], {
                'nodes_explored': nodes_explored,
                'edges_explored': edges_explored
            }
        
        neighbors = graph.get(current_node, {})
        for neighbor, weight in neighbors.items():
            edges_explored += 1
            if neighbor in visited:
                continue
            
            new_distance = current_distance + weight
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current_node
                heapq.heappush(priority_queue, (new_distance, neighbor))
    
    return None, float('inf'), {
        'nodes_explored': nodes_explored,
        'edges_explored': edges_explored
    }
