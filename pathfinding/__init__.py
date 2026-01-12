#!/usr/bin/env python3
"""
Module Pathfinding - Recherche d'itinéraires ferroviaires

Ce module permet de trouver des itinéraires optimaux entre deux villes/gares
françaises en utilisant les algorithmes Dijkstra et A*.
"""

from pathfinding.route_finder import RouteFinder, RouteResult
from pathfinding.dijkstra import dijkstra
from pathfinding.astar import astar

__all__ = ['RouteFinder', 'RouteResult', 'dijkstra', 'astar']
