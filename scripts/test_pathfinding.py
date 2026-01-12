#!/usr/bin/env python3
"""
Script de test pour comparer les algorithmes Dijkstra et A*.
"""

import sys
import time
from pathlib import Path

# Ajouter le répertoire racine au path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pathfinding import RouteFinder


def test_algorithm(route_finder: RouteFinder, departure: str, destination: str, algorithm: str):
    """
    Teste un algorithme et retourne les résultats.
    
    Args:
        route_finder: Instance de RouteFinder
        departure: Ville de départ
        destination: Ville d'arrivée
        algorithm: "dijkstra" ou "astar"
    
    Returns:
        Tuple (result, execution_time_ms)
    """
    start_time = time.time()
    result = route_finder.find_route(departure, destination, algorithm=algorithm, return_stats=True)
    execution_time = (time.time() - start_time) * 1000  # en millisecondes
    
    return result, execution_time


def compare_algorithms():
    """Compare les performances de Dijkstra et A*."""
    
    print("=" * 80)
    print("COMPARAISON DIJKSTRA vs A*")
    print("=" * 80)
    print()
    
    # Initialiser le route finder
    print("🔄 Initialisation du RouteFinder...")
    route_finder = RouteFinder()
    print()
    
    # Tests à effectuer
    test_cases = [
        ("Paris", "Lyon"),
        ("Bordeaux", "Toulouse"),
        ("Brest", "Marseille"),
        ("Lille", "Nice"),
        ("Nantes", "Strasbourg"),
        ("Rennes", "Lyon"),
        ("Marseille", "Paris"),
        ("Toulouse", "Lille"),
    ]
    
    print(f"📊 Test de {len(test_cases)} trajets différents\n")
    print("-" * 80)
    
    # Résultats globaux
    dijkstra_times = []
    astar_times = []
    dijkstra_nodes = []
    astar_nodes = []
    
    for i, (departure, destination) in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}/{len(test_cases)}: {departure} → {destination}")
        print("-" * 80)
        
        # Test Dijkstra
        result_dijkstra, time_dijkstra = test_algorithm(
            route_finder, departure, destination, "dijkstra"
        )
        
        # Test A*
        result_astar, time_astar = test_algorithm(
            route_finder, departure, destination, "astar"
        )
        
        # Afficher les résultats
        if result_dijkstra.success and result_astar.success:
            print(f"✅ DIJKSTRA:")
            print(f"   Route: {' → '.join(result_dijkstra.route)}")
            print(f"   Distance: {result_dijkstra.total_distance:.1f} km")
            print(f"   Temps estimé: {result_dijkstra.estimated_time:.2f} h")
            print(f"   Temps d'exécution: {time_dijkstra:.2f} ms")
            print(f"   Nœuds explorés: {result_dijkstra.stats.get('nodes_explored', 'N/A')}")
            print(f"   Arêtes explorées: {result_dijkstra.stats.get('edges_explored', 'N/A')}")
            
            print(f"\n✅ A*:")
            print(f"   Route: {' → '.join(result_astar.route)}")
            print(f"   Distance: {result_astar.total_distance:.1f} km")
            print(f"   Temps estimé: {result_astar.estimated_time:.2f} h")
            print(f"   Temps d'exécution: {time_astar:.2f} ms")
            print(f"   Nœuds explorés: {result_astar.stats.get('nodes_explored', 'N/A')}")
            print(f"   Arêtes explorées: {result_astar.stats.get('edges_explored', 'N/A')}")
            
            # Comparaison
            if result_dijkstra.total_distance == result_astar.total_distance:
                print(f"\n✓ Les deux algorithmes trouvent le même chemin optimal")
            else:
                print(f"\n⚠️  Différence de distance: Dijkstra={result_dijkstra.total_distance:.1f} km, A*={result_astar.total_distance:.1f} km")
            
            speedup = time_dijkstra / time_astar if time_astar > 0 else 0
            if speedup > 1:
                print(f"⚡ A* est {speedup:.2f}x plus rapide que Dijkstra")
            elif speedup < 1 and speedup > 0:
                print(f"⚡ Dijkstra est {1/speedup:.2f}x plus rapide que A*")
            else:
                print(f"⚡ Temps d'exécution similaire")
            
            # Enregistrer pour statistiques globales
            dijkstra_times.append(time_dijkstra)
            astar_times.append(time_astar)
            dijkstra_nodes.append(result_dijkstra.stats.get('nodes_explored', 0))
            astar_nodes.append(result_astar.stats.get('nodes_explored', 0))
        else:
            print(f"❌ Erreur:")
            if not result_dijkstra.success:
                print(f"   Dijkstra: {result_dijkstra.message}")
            if not result_astar.success:
                print(f"   A*: {result_astar.message}")
    
    # Statistiques globales
    print("\n" + "=" * 80)
    print("📈 STATISTIQUES GLOBALES")
    print("=" * 80)
    
    if dijkstra_times and astar_times:
        avg_dijkstra = sum(dijkstra_times) / len(dijkstra_times)
        avg_astar = sum(astar_times) / len(astar_times)
        
        print(f"\n⏱️  Temps d'exécution moyen:")
        print(f"   Dijkstra: {avg_dijkstra:.2f} ms")
        print(f"   A*: {avg_astar:.2f} ms")
        print(f"   Amélioration: {((avg_dijkstra - avg_astar) / avg_dijkstra * 100):.1f}%")
        
        print(f"\n🔍 Nœuds explorés moyen:")
        if dijkstra_nodes and astar_nodes:
            avg_dijkstra_nodes = sum(dijkstra_nodes) / len(dijkstra_nodes)
            avg_astar_nodes = sum(astar_nodes) / len(astar_nodes)
            print(f"   Dijkstra: {avg_dijkstra_nodes:.1f} nœuds")
            print(f"   A*: {avg_astar_nodes:.1f} nœuds")
            print(f"   Réduction: {((avg_dijkstra_nodes - avg_astar_nodes) / avg_dijkstra_nodes * 100):.1f}%")
    
    print("\n" + "=" * 80)
    print("✅ Tests terminés!")
    print("=" * 80)


if __name__ == "__main__":
    compare_algorithms()
