#!/usr/bin/env python3
"""
Construction du graphe de connexions entre gares.
"""

from typing import Dict, List, Set, Tuple
from pathfinding.data_loader import StationDataLoader
from pathfinding.utils import haversine_distance, normalize_city_name


class GraphBuilder:
    """Construit un graphe de connexions entre gares."""
    
    def __init__(self, data_loader: StationDataLoader):
        """
        Initialise le constructeur de graphe.
        
        Args:
            data_loader: Chargeur de données des gares
        """
        self.data_loader = data_loader
        self.graph: Dict[str, Dict[str, float]] = {}
        self.stations: List[Dict] = data_loader.get_all_stations()
    
    def build_graph(
        self,
        max_distance_km: float = 200.0,
        connect_hubs: bool = True,
        hub_max_distance_km: float = 500.0
    ) -> Dict[str, Dict[str, float]]:
        """
        Construit le graphe de connexions.
        
        Stratégie :
        1. Connecter toutes les gares hubs (catégorie A) entre elles
        2. Connecter les autres gares aux gares proches (distance < max_distance_km)
        
        Args:
            max_distance_km: Distance maximale pour connecter deux gares (défaut: 200 km)
            connect_hubs: Si True, connecte tous les hubs entre eux (défaut: True)
            hub_max_distance_km: Distance maximale entre hubs (défaut: 500 km)
        
        Returns:
            Graphe sous forme de dictionnaire {gare1: {gare2: distance, ...}, ...}
        """
        print("🔨 Construction du graphe...")
        
        # Initialiser le graphe
        self.graph = {station['nom']: {} for station in self.stations}
        
        # Étape 1 : Connecter les hubs majeurs entre eux
        if connect_hubs:
            hubs = self.data_loader.get_hub_stations()
            print(f"   📍 Connexion de {len(hubs)} hubs majeurs...")
            
            for i, hub1 in enumerate(hubs):
                for hub2 in hubs[i+1:]:
                    distance = self._calculate_distance(hub1, hub2)
                    if distance <= hub_max_distance_km:
                        self._add_edge(hub1['nom'], hub2['nom'], distance)
        
        # Étape 2 : Connecter les autres gares aux gares proches
        print(f"   🔗 Connexion des gares (distance < {max_distance_km} km)...")
        connections_count = 0
        
        for i, station1 in enumerate(self.stations):
            # Pour les hubs, on les a déjà connectés entre eux
            if 'A' in station1.get('segment_drg', ''):
                continue
            
            for station2 in self.stations[i+1:]:
                distance = self._calculate_distance(station1, station2)
                
                if distance <= max_distance_km:
                    self._add_edge(station1['nom'], station2['nom'], distance)
                    connections_count += 1
        
        total_edges = sum(len(neighbors) for neighbors in self.graph.values()) // 2
        print(f"✅ Graphe construit : {len(self.graph)} nœuds, {total_edges} arêtes")
        
        return self.graph
    
    def _calculate_distance(self, station1: Dict, station2: Dict) -> float:
        """
        Calcule la distance entre deux gares.
        
        Args:
            station1: Première gare
            station2: Deuxième gare
        
        Returns:
            Distance en kilomètres
        """
        pos1 = station1.get('position_geographique', {})
        pos2 = station2.get('position_geographique', {})
        
        if not pos1 or not pos2:
            return float('inf')
        
        lat1 = pos1.get('lat', 0)
        lon1 = pos1.get('lon', 0)
        lat2 = pos2.get('lat', 0)
        lon2 = pos2.get('lon', 0)
        
        if lat1 == 0 or lon1 == 0 or lat2 == 0 or lon2 == 0:
            return float('inf')
        
        return haversine_distance(lat1, lon1, lat2, lon2)
    
    def _add_edge(self, station1_name: str, station2_name: str, distance: float) -> None:
        """
        Ajoute une arête au graphe (bidirectionnelle).
        
        Args:
            station1_name: Nom de la première gare
            station2_name: Nom de la deuxième gare
            distance: Distance en kilomètres
        """
        if station1_name not in self.graph:
            self.graph[station1_name] = {}
        if station2_name not in self.graph:
            self.graph[station2_name] = {}
        
        self.graph[station1_name][station2_name] = distance
        self.graph[station2_name][station1_name] = distance
    
    def get_graph(self) -> Dict[str, Dict[str, float]]:
        """
        Récupère le graphe construit.
        
        Returns:
            Graphe sous forme de dictionnaire
        """
        return self.graph
    
    def get_neighbors(self, station_name: str) -> Dict[str, float]:
        """
        Récupère les voisins d'une gare.
        
        Args:
            station_name: Nom de la gare
        
        Returns:
            Dictionnaire {nom_voisin: distance, ...}
        """
        return self.graph.get(station_name, {})
