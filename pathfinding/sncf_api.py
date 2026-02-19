#!/usr/bin/env python3
"""
Module pour interagir avec l'API SNCF (Navitia).

Utilise l'API officielle SNCF pour obtenir des itinéraires réels.
"""

import json
import requests
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class SNCFRouteResult:
    """Résultat d'une recherche d'itinéraire via l'API SNCF."""
    
    success: bool
    route: List[str] = field(default_factory=list)
    departure_time: Optional[str] = None  # Format: YYYYMMDDThhmmss
    arrival_time: Optional[str] = None  # Format: YYYYMMDDThhmmss
    departure_time_formatted: Optional[str] = None  # Format: HH:MM
    arrival_time_formatted: Optional[str] = None  # Format: HH:MM
    duration_seconds: Optional[int] = None
    transfers: int = 0
    message: Optional[str] = None
    raw_response: Optional[Dict] = None
    next_train_departure: Optional[str] = None  # Prochain train disponible (format: HH:MM)
    sections_details: List[Dict] = field(default_factory=list)  # Détails des sections (trains, correspondances)
    departure_uic: Optional[str] = None  # Code UIC de la gare de départ (8 chiffres)
    arrival_uic: Optional[str] = None  # Code UIC de la gare d'arrivée (8 chiffres)


class SNCFAPI:
    """Client pour l'API SNCF (Navitia)."""
    
    BASE_URL = "https://api.sncf.com/v1/coverage/sncf"
    JOURNEYS_ENDPOINT = f"{BASE_URL}/journeys"
    
    def __init__(self, api_key: Optional[str] = None, gares_file: Optional[Path] = None):
        """
        Initialise le client API SNCF.
        
        Args:
            api_key: Clé API SNCF (si None, les requêtes échoueront)
            gares_file: Chemin vers gares-francaises.json (pour conversion nom → UIC)
        """
        self.api_key = api_key
        self.gares_file = gares_file or Path("dataset/shared/gares-francaises.json")
        self._gares_map = None
        self._insee_map = None  # Mapping nom → code INSEE
        
        # Charger le mapping nom de gare → code UIC et INSEE
        if self.gares_file.exists():
            self._load_gares_map()
    
    def _load_gares_map(self):
        """Charge le mapping nom de gare → code UIC et code INSEE."""
        try:
            with open(self.gares_file, 'r', encoding='utf-8') as f:
                gares = json.load(f)
            
            self._gares_map = {}
            self._insee_map = {}  # Mapping nom → code INSEE
            
            for gare in gares:
                nom = gare.get('nom', '').lower()
                codes_uic = gare.get('codes_uic', '')
                code_insee = gare.get('codeinsee', '')
                
                # Mapping code UIC
                if codes_uic:
                    # Certaines gares ont plusieurs codes UIC séparés par ";"
                    first_code = codes_uic.split(';')[0].strip()
                    if first_code and len(first_code) == 8:  # Code UIC fait 8 chiffres
                        self._gares_map[nom] = first_code
                        
                        # Ajouter aussi les variations (sans accents, etc.)
                        nom_normalized = nom.replace('-', ' ').replace("'", ' ')
                        if nom_normalized != nom:
                            self._gares_map[nom_normalized] = first_code
                
                # Mapping code INSEE (pour fallback)
                if code_insee:
                    self._insee_map[nom] = code_insee
                    nom_normalized = nom.replace('-', ' ').replace("'", ' ')
                    if nom_normalized != nom:
                        self._insee_map[nom_normalized] = code_insee
        
        except Exception as e:
            print(f"⚠️  Erreur lors du chargement des gares: {e}")
            self._gares_map = {}
            self._insee_map = {}
    
    def _find_uic_code(self, gare_name: str) -> Optional[str]:
        """
        Trouve le code UIC d'une gare à partir de son nom.
        
        Args:
            gare_name: Nom de la gare
            
        Returns:
            Code UIC (8 chiffres) ou None si non trouvé
        """
        if not self._gares_map:
            return None
        
        # Recherche exacte
        gare_lower = gare_name.lower().strip()
        if gare_lower in self._gares_map:
            return self._gares_map[gare_lower]
        
        # Recherche partielle (pour gérer les variantes)
        for nom, code in self._gares_map.items():
            if gare_lower in nom or nom in gare_lower:
                return code
        
        return None
    
    def _find_stop_area_id_via_api(self, gare_name: str) -> Optional[str]:
        """
        Recherche l'identifiant stop_area via l'API SNCF en cherchant par nom.
        
        Args:
            gare_name: Nom de la gare
            
        Returns:
            Identifiant stop_area ou None si non trouvé
        """
        if not self.api_key:
            return None
        
        try:
            # Utiliser l'endpoint de recherche de places
            search_url = f"{self.BASE_URL}/places"
            params = {
                "q": gare_name,
                "type[]": "stop_area",  # Chercher uniquement des stop_areas
                "count": 5  # Limiter à 5 résultats
            }
            
            response = requests.get(
                search_url,
                params=params,
                auth=(self.api_key, ''),
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                places = data.get("places", [])
                
                # Chercher la meilleure correspondance
                gare_lower = gare_name.lower()
                for place in places:
                    place_name = place.get("name", "").lower()
                    place_id = place.get("id", "")
                    
                    # Si le nom correspond exactement ou partiellement
                    if place_id.startswith("stop_area:") and (
                        gare_lower in place_name or place_name in gare_lower
                    ):
                        return place_id
            
        except Exception as e:
            print(f"⚠️  Erreur lors de la recherche API pour '{gare_name}': {e}")
        
        return None
    
    def _build_navitia_id(self, gare_name: str) -> Optional[str]:
        """
        Construit l'identifiant Navitia depuis un nom de gare.
        
        Essaie plusieurs formats :
        1. Recherche via API SNCF (stop_area:SNCF:SA:XXXXX)
        2. Code INSEE (admin:fr:XXXXX) en fallback
        
        Args:
            gare_name: Nom de la gare
            
        Returns:
            Identifiant Navitia ou None si non trouvé
        """
        # 1. Essayer de trouver via l'API de recherche SNCF
        stop_area_id = self._find_stop_area_id_via_api(gare_name)
        if stop_area_id:
            return stop_area_id
        
        # 2. Fallback : utiliser le code INSEE (format admin:fr:XXXXX)
        if self._insee_map:
            gare_lower = gare_name.lower().strip()
            if gare_lower in self._insee_map:
                code_insee = self._insee_map[gare_lower]
                return f"admin:fr:{code_insee}"
            
            # Recherche partielle pour INSEE
            for nom, code_insee in self._insee_map.items():
                if gare_lower in nom or nom in gare_lower:
                    return f"admin:fr:{code_insee}"
        
        return None
    
    def find_route(
        self,
        departure: str,
        arrival: str,
        datetime_str: Optional[str] = None,
        datetime_represents: str = "departure",
        data_freshness: str = "realtime",
        max_transfers: Optional[int] = None
    ) -> SNCFRouteResult:
        """
        Trouve un itinéraire entre deux gares via l'API SNCF.
        
        Args:
            departure: Nom de la gare de départ
            arrival: Nom de la gare d'arrivée
            datetime_str: Date/heure au format YYYYMMDDThhmmss (optionnel)
            datetime_represents: "departure" ou "arrival" (défaut: "departure")
            data_freshness: "base_schedule" ou "realtime" (défaut: "realtime")
            max_transfers: Nombre max de correspondances (optionnel)
            
        Returns:
            SNCFRouteResult avec les détails de l'itinéraire
        """
        if not self.api_key:
            return SNCFRouteResult(
                success=False,
                message="Clé API SNCF non configurée. Configurez-la dans les paramètres."
            )
        
        # Convertir les noms de gares en identifiants Navitia
        from_id = self._build_navitia_id(departure)
        to_id = self._build_navitia_id(arrival)
        
        if not from_id:
            # Essayer de donner plus d'infos
            uic_code = self._find_uic_code(departure)
            code_insee = self._insee_map.get(departure.lower().strip()) if self._insee_map else None
            
            error_msg = f"Gare de départ '{departure}' non trouvée."
            if uic_code:
                error_msg += f" Code UIC trouvé: {uic_code}, mais identifiant Navitia non trouvé."
            elif code_insee:
                error_msg += f" Code INSEE trouvé: {code_insee}."
            else:
                error_msg += " Aucun code UIC ou INSEE trouvé dans la base de données."
            
            return SNCFRouteResult(
                success=False,
                message=error_msg
            )
        
        if not to_id:
            # Essayer de donner plus d'infos
            uic_code = self._find_uic_code(arrival)
            code_insee = self._insee_map.get(arrival.lower().strip()) if self._insee_map else None
            
            error_msg = f"Gare d'arrivée '{arrival}' non trouvée."
            if uic_code:
                error_msg += f" Code UIC trouvé: {uic_code}, mais identifiant Navitia non trouvé."
            elif code_insee:
                error_msg += f" Code INSEE trouvé: {code_insee}."
            else:
                error_msg += " Aucun code UIC ou INSEE trouvé dans la base de données."
            
            return SNCFRouteResult(
                success=False,
                message=error_msg
            )
        
        # Construire l'URL avec les paramètres
        params = {
            "from": from_id,
            "to": to_id,
            "datetime_represents": datetime_represents,
            "data_freshness": data_freshness
        }
        
        # Ajouter datetime si fourni
        if datetime_str:
            params["datetime"] = datetime_str
        else:
            # Par défaut, utiliser maintenant + 1 heure
            now = datetime.now() + timedelta(hours=1)
            params["datetime"] = now.strftime("%Y%m%dT%H%M%S")
        
        # Ajouter max_transfers si fourni
        if max_transfers is not None:
            params["max_nb_transfers"] = max_transfers
        
        # Faire la requête à l'API SNCF
        # Authentification : Username = clé API, Password = vide
        try:
            # Utiliser Basic Auth avec username=clé API et password vide
            response = requests.get(
                self.JOURNEYS_ENDPOINT, 
                params=params, 
                auth=(self.api_key, ''),  # Username = clé API, Password = vide
                timeout=10
            )
            
            if response.status_code != 200:
                error_details = ""
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = error_data["error"].get("message", "")
                        error_id = error_data["error"].get("id", "")
                        error_details = f" ({error_id}: {error_msg})"
                except:
                    pass
                
                return SNCFRouteResult(
                    success=False,
                    message=f"Erreur API SNCF {response.status_code}: {response.text[:200]}{error_details}. "
                           f"Identifiants utilisés: from={from_id}, to={to_id}"
                )
            
            data = response.json()
            
            # Parser la réponse
            return self._parse_response(data, departure, arrival)
            
        except requests.exceptions.Timeout:
            return SNCFRouteResult(
                success=False,
                message="Timeout lors de l'appel à l'API SNCF. Vérifiez votre connexion internet."
            )
        except requests.exceptions.RequestException as e:
            return SNCFRouteResult(
                success=False,
                message=f"Erreur de connexion à l'API SNCF: {str(e)}"
            )
        except Exception as e:
            return SNCFRouteResult(
                success=False,
                message=f"Erreur inattendue: {str(e)}"
            )
    
    def _format_time(self, time_str: str) -> Optional[str]:
        """
        Formate une date/heure au format YYYYMMDDThhmmss en HH:MM.
        
        Args:
            time_str: Date/heure au format YYYYMMDDThhmmss
            
        Returns:
            Heure formatée en HH:MM ou None
        """
        if not time_str or len(time_str) < 13:
            return None
        
        try:
            # Extraire l'heure (après le 'T')
            if 'T' in time_str:
                time_part = time_str.split('T')[1]
                if len(time_part) >= 4:
                    return f"{time_part[:2]}:{time_part[2:4]}"
        except:
            pass
        
        return None
    
    def _parse_response(self, data: Dict, departure: str, arrival: str) -> SNCFRouteResult:
        """
        Parse la réponse JSON de l'API SNCF.
        
        Args:
            data: Données JSON de la réponse
            departure: Nom de la gare de départ (pour référence)
            arrival: Nom de la gare d'arrivée (pour référence)
            
        Returns:
            SNCFRouteResult parsé
        """
        journeys = data.get("journeys", [])
        
        if not journeys:
            return SNCFRouteResult(
                success=False,
                message="Aucun itinéraire trouvé entre ces deux gares."
            )
        
        # Prendre le premier itinéraire (le plus rapide/prochain)
        journey = journeys[0]
        
        # Extraire les informations principales
        sections = journey.get("sections", [])
        
        # Construire la liste des gares du trajet
        route = [departure]
        sections_details = []
        
        # Parcourir les sections pour trouver les gares intermédiaires et extraire les détails
        for section in sections:
            section_type = section.get("type", "")
            
            # Si c'est un transport public (train), extraire les détails
            if section_type == "public_transport":
                to_stop = section.get("to", {})
                from_stop = section.get("from", {})
                
                # Gare d'arrivée de la section
                to_stop_point = to_stop.get("stop_point", {})
                to_stop_area = to_stop_point.get("stop_area", {})
                to_stop_name = to_stop_area.get("name", "")
                
                # Gare de départ de la section
                from_stop_point = from_stop.get("stop_point", {})
                from_stop_area = from_stop_point.get("stop_area", {})
                from_stop_name = from_stop_area.get("name", "")
                
                # Informations du transport
                display_info = section.get("display_informations", {})
                line_name = display_info.get("commercial_mode", "") or display_info.get("name", "") or "Train"
                
                # Horaires de la section
                section_dep_time = section.get("departure_date_time", "")
                section_arr_time = section.get("arrival_date_time", "")
                
                # Détails de la section
                section_detail = {
                    "type": "train",
                    "from": from_stop_name,
                    "to": to_stop_name,
                    "line": line_name,
                    "departure_time": section_dep_time,
                    "arrival_time": section_arr_time,
                    "duration": section.get("duration", 0)
                }
                sections_details.append(section_detail)
                
                # Ajouter la gare d'arrivée si elle n'est pas déjà dans la route (comparaison insensible à la casse)
                if to_stop_name:
                    # Normaliser pour comparaison (minuscules)
                    to_stop_normalized = to_stop_name.lower().strip()
                    route_normalized = [r.lower().strip() for r in route]
                    if to_stop_normalized not in route_normalized:
                        route.append(to_stop_name)
            
            elif section_type == "transfer":
                # Correspondance
                sections_details.append({
                    "type": "transfer",
                    "duration": section.get("duration", 0)
                })
        
        # S'assurer que l'arrivée est à la fin (comparaison insensible à la casse)
        arrival_normalized = arrival.lower().strip() if arrival else ""
        route_normalized = [r.lower().strip() for r in route]
        if arrival_normalized and arrival_normalized not in route_normalized:
            route.append(arrival)
        elif arrival_normalized:
            # Si l'arrivée est déjà dans la route mais pas à la fin, déplacer à la fin
            # Trouver l'index de l'arrivée (insensible à la casse)
            for i, r in enumerate(route):
                if r.lower().strip() == arrival_normalized and i != len(route) - 1:
                    # Supprimer de sa position et ajouter à la fin
                    route.pop(i)
                    route.append(arrival)  # Utiliser la version original de arrival
                    break
        
        # Extraire les autres informations
        departure_time = journey.get("departure_date_time", "")
        arrival_time = journey.get("arrival_date_time", "")
        duration_seconds = journey.get("duration", 0)
        
        # Formater les heures pour affichage
        departure_time_formatted = self._format_time(departure_time)
        arrival_time_formatted = self._format_time(arrival_time)
        
        # Le prochain train est le train du premier itinéraire retourné
        # (l'API retourne déjà les trains par ordre chronologique)
        next_train_departure = departure_time_formatted
        
        # Compter les correspondances
        transfers = sum(1 for s in sections if s.get("type") == "transfer")
        
        # Récupérer les codes UIC pour le deeplink SNCF Connect
        departure_uic = self._find_uic_code(departure)
        arrival_uic = self._find_uic_code(arrival)
        
        return SNCFRouteResult(
            success=True,
            route=route,
            departure_time=departure_time,
            arrival_time=arrival_time,
            departure_time_formatted=departure_time_formatted,
            arrival_time_formatted=arrival_time_formatted,
            duration_seconds=duration_seconds,
            transfers=transfers,
            next_train_departure=next_train_departure,
            sections_details=sections_details,
            raw_response=data,
            departure_uic=departure_uic,
            arrival_uic=arrival_uic
        )
