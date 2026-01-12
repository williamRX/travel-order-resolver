#!/usr/bin/env python3
"""
Chargement des données de gares depuis gares-francaises.json
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class StationDataLoader:
    """Charge et gère les données des gares françaises."""
    
    def __init__(self, data_path: Optional[Path] = None):
        """
        Initialise le chargeur de données.
        
        Args:
            data_path: Chemin vers gares-francaises.json
                      (défaut: dataset/shared/gares-francaises.json)
        """
        if data_path is None:
            # Chemin par défaut depuis la racine du projet
            project_root = Path(__file__).resolve().parent.parent
            data_path = project_root / "dataset" / "shared" / "gares-francaises.json"
        
        self.data_path = Path(data_path)
        self.stations: List[Dict] = []
        self.station_by_name: Dict[str, Dict] = {}
        self.station_by_uic: Dict[str, Dict] = {}
        
        self._load_data()
    
    def _load_data(self) -> None:
        """Charge les données depuis le fichier JSON."""
        if not self.data_path.exists():
            raise FileNotFoundError(
                f"Fichier de données non trouvé : {self.data_path}"
            )
        
        print(f"📖 Chargement des gares depuis {self.data_path}...")
        
        with open(self.data_path, 'r', encoding='utf-8') as f:
            self.stations = json.load(f)
        
        # Créer des index pour recherche rapide
        for station in self.stations:
            name = station.get('nom', '')
            if name:
                self.station_by_name[name] = station
            
            # Indexer par code UIC aussi
            codes_uic = station.get('codes_uic', '')
            if codes_uic:
                # codes_uic peut être "87313759" ou "87001479;87271494"
                for code in codes_uic.split(';'):
                    self.station_by_uic[code.strip()] = station
        
        print(f"✅ {len(self.stations)} gares chargées")
    
    def get_station_by_name(self, name: str) -> Optional[Dict]:
        """
        Récupère une gare par son nom exact.
        
        Args:
            name: Nom de la gare
        
        Returns:
            Dictionnaire de la gare ou None
        """
        return self.station_by_name.get(name)
    
    def get_all_stations(self) -> List[Dict]:
        """
        Récupère toutes les gares.
        
        Returns:
            Liste de toutes les gares
        """
        return self.stations
    
    def get_stations_by_segment(self, segment: str) -> List[Dict]:
        """
        Récupère les gares d'un segment donné (A, B, ou C).
        
        Args:
            segment: Segment DRG ('A', 'B', ou 'C')
        
        Returns:
            Liste des gares du segment
        """
        return [
            station for station in self.stations
            if segment in station.get('segment_drg', '')
        ]
    
    def get_hub_stations(self) -> List[Dict]:
        """
        Récupère les gares hubs (catégorie A).
        
        Returns:
            Liste des gares hubs
        """
        return self.get_stations_by_segment('A')
