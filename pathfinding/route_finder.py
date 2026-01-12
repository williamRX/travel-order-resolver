#!/usr/bin/env python3
"""
Classe principale pour trouver des itinéraires entre villes/gares.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from pathfinding.data_loader import StationDataLoader
from pathfinding.graph_builder import GraphBuilder
from pathfinding.dijkstra import dijkstra, dijkstra_with_stats
from pathfinding.astar import astar, astar_with_stats
from pathfinding.utils import find_matching_stations, select_best_station, estimate_travel_time


@dataclass
class RouteResult:
    """Résultat d'une recherche d'itinéraire."""
    
    success: bool
    route: List[str] = field(default_factory=list)
    total_distance: float = 0.0
    estimated_time: float = 0.0
    message: Optional[str] = None
    algorithm: str = "unknown"  # "dijkstra" ou "astar"
    stats: dict = field(default_factory=dict)  # Statistiques (nodes_explored, etc.)
    
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


class RouteFinder:
    """Module de recherche d'itinéraires ferroviaires."""
    
    def __init__(
        self,
        data_path: Optional[str] = None,
        max_distance_km: float = 200.0,
        connect_hubs: bool = True
    ):
        """
        Initialise le route finder.
        
        Args:
            data_path: Chemin vers gares-francaises.json (optionnel)
            max_distance_km: Distance maximale pour connecter deux gares (défaut: 200 km)
            connect_hubs: Si True, connecte tous les hubs entre eux (défaut: True)
        """
        # Charger les données
        self.data_loader = StationDataLoader(data_path)
        
        # Construire le graphe
        self.graph_builder = GraphBuilder(self.data_loader)
        self.graph = self.graph_builder.build_graph(
            max_distance_km=max_distance_km,
            connect_hubs=connect_hubs
        )
        
        # Créer un index des stations pour l'heuristique A*
        self.stations_data = {
            station['nom']: station
            for station in self.data_loader.get_all_stations()
        }
    
    def find_route(
        self,
        departure: str,
        destination: str,
        algorithm: str = "dijkstra",
        return_stats: bool = False
    ) -> RouteResult:
        """
        Trouve un itinéraire entre deux villes.
        
        Args:
            departure: Ville/gare de départ
            destination: Ville/gare d'arrivée
            algorithm: Algorithme à utiliser ("dijkstra" ou "astar", défaut: "dijkstra")
            return_stats: Si True, retourne des statistiques (défaut: False)
        
        Returns:
            RouteResult avec le chemin trouvé ou message d'erreur
        """
        # Normaliser les noms de villes
        departure_station = self._normalize_station_name(departure)
        destination_station = self._normalize_station_name(destination)
        
        if not departure_station:
            return RouteResult(
                success=False,
                message=f"Gare de départ non trouvée : {departure}",
                algorithm=algorithm
            )
        
        if not destination_station:
            return RouteResult(
                success=False,
                message=f"Gare d'arrivée non trouvée : {destination}",
                algorithm=algorithm
            )
        
        departure_name = departure_station['nom']
        destination_name = destination_station['nom']
        
        # Exécuter l'algorithme choisi
        if algorithm.lower() == "astar":
            if return_stats:
                path, distance, stats = astar_with_stats(
                    self.graph,
                    departure_name,
                    destination_name,
                    self.stations_data
                )
            else:
                path, distance = astar(
                    self.graph,
                    departure_name,
                    destination_name,
                    self.stations_data
                )
                stats = {}
        else:  # dijkstra par défaut
            if return_stats:
                path, distance, stats = dijkstra_with_stats(
                    self.graph,
                    departure_name,
                    destination_name
                )
            else:
                path, distance = dijkstra(
                    self.graph,
                    departure_name,
                    destination_name
                )
                stats = {}
        
        # Vérifier le résultat
        if path is None or distance == float('inf'):
            return RouteResult(
                success=False,
                message="Aucun itinéraire trouvé entre ces deux gares",
                algorithm=algorithm,
                stats=stats
            )
        
        # Calculer le temps estimé
        estimated_time = estimate_travel_time(distance)
        
        return RouteResult(
            success=True,
            route=path,
            total_distance=distance,
            estimated_time=estimated_time,
            algorithm=algorithm,
            stats=stats
        )
    
    def _normalize_station_name(self, city_name: str) -> Optional[dict]:
        """
        Normalise un nom de ville et trouve la gare correspondante.
        
        Args:
            city_name: Nom de ville recherché
        
        Returns:
            Dictionnaire de la gare trouvée ou None
        """
        # Chercher les gares correspondantes
        matches = find_matching_stations(city_name, self.data_loader.get_all_stations())
        
        if not matches:
            return None
        
        # Sélectionner la meilleure gare
        return select_best_station(matches, city_name)
