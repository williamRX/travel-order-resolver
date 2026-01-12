#!/usr/bin/env python3
"""
Utilitaires pour le module pathfinding.
"""

import math
from typing import Dict, List, Optional, Tuple


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcule la distance entre deux points géographiques en kilomètres
    en utilisant la formule de Haversine.
    
    Args:
        lat1: Latitude du premier point
        lon1: Longitude du premier point
        lat2: Latitude du deuxième point
        lon2: Longitude du deuxième point
    
    Returns:
        Distance en kilomètres
    """
    # Rayon de la Terre en kilomètres
    R = 6371.0
    
    # Convertir en radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Différences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Formule de Haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    distance = R * c
    return distance


def normalize_city_name(city_name: str) -> str:
    """
    Normalise un nom de ville pour la recherche.
    
    Args:
        city_name: Nom de ville à normaliser
    
    Returns:
        Nom normalisé (minuscules, sans accents, sans espaces multiples)
    """
    if not city_name:
        return ""
    
    # Convertir en minuscules
    normalized = city_name.lower().strip()
    
    # Supprimer les espaces multiples
    normalized = ' '.join(normalized.split())
    
    return normalized


def find_matching_stations(city_name: str, stations: List[Dict]) -> List[Dict]:
    """
    Trouve les gares qui correspondent à un nom de ville.
    
    Args:
        city_name: Nom de ville recherché
        stations: Liste de toutes les gares
    
    Returns:
        Liste des gares correspondantes
    """
    normalized_city = normalize_city_name(city_name)
    matches = []
    
    for station in stations:
        station_name = normalize_city_name(station.get('nom', ''))
        
        # Correspondance exacte
        if station_name == normalized_city:
            matches.append(station)
            continue
        
        # Correspondance si le nom de la ville est au début du nom de la gare
        # Ex: "Paris" correspond à "Paris Gare de Lyon", "Paris Nord", etc.
        if station_name.startswith(normalized_city + ' '):
            matches.append(station)
            continue
        
        # Correspondance si le nom de la ville est dans le nom de la gare
        # Ex: "Lyon" correspond à "Lyon Part-Dieu", "Lyon Perrache", etc.
        if normalized_city in station_name.split():
            matches.append(station)
    
    return matches


def select_best_station(matches: List[Dict], city_name: str) -> Optional[Dict]:
    """
    Sélectionne la meilleure gare parmi plusieurs correspondances.
    
    Priorité :
    1. Gares de catégorie A (hubs majeurs)
    2. Gares de catégorie B
    3. Gares de catégorie C
    
    Args:
        matches: Liste des gares correspondantes
        city_name: Nom de ville recherché
    
    Returns:
        Meilleure gare ou None
    """
    if not matches:
        return None
    
    # Trier par priorité de segment (A > B > C)
    def get_priority(station: Dict) -> int:
        segment = station.get('segment_drg', 'C')
        if 'A' in segment:
            return 1  # Priorité la plus haute
        elif 'B' in segment:
            return 2
        else:
            return 3
    
    # Trier par priorité
    sorted_matches = sorted(matches, key=get_priority)
    
    # Si plusieurs gares de même priorité, prendre la première
    return sorted_matches[0]


def estimate_travel_time(distance_km: float) -> float:
    """
    Estime le temps de trajet en heures basé sur la distance.
    
    Args:
        distance_km: Distance en kilomètres
    
    Returns:
        Temps estimé en heures
    """
    if distance_km <= 0:
        return 0.0
    
    # Vitesse moyenne selon la distance
    if distance_km > 300:
        # TGV pour longues distances
        avg_speed = 280  # km/h
    elif distance_km > 100:
        # Intercités pour distances moyennes
        avg_speed = 200  # km/h
    else:
        # TER pour courtes distances
        avg_speed = 120  # km/h
    
    # Temps = distance / vitesse
    time_hours = distance_km / avg_speed
    
    # Ajouter 10% pour les arrêts et changements
    time_hours *= 1.1
    
    return time_hours
