#!/usr/bin/env python3
"""
Script de test pour le pipeline complet.
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.pipeline import TravelIntentPipeline


def test_pipeline():
    """Test le pipeline avec plusieurs phrases."""
    print("=" * 80)
    print("TEST DU PIPELINE COMPLET")
    print("=" * 80)
    print()
    
    # Initialiser le pipeline
    try:
        pipeline = TravelIntentPipeline()
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        return
    
    # Phrases de test
    test_cases = [
        # Phrases valides avec départ et arrivée
        ("Je vais de Paris à Lyon", True, True, True),
        ("Billet Marseille Nice demain", True, True, True),
        ("Trajet la gare de Lille vers l'aéroport de Lyon", True, True, True),
        ("Je veux aller de Bordeaux à Toulouse", True, True, True),
        
        # Phrases valides avec seulement arrivée
        ("Je vais à Paris", True, False, True),
        ("Billet pour Lyon", True, False, True),
        
        # Phrases invalides
        ("Bonjour comment allez-vous?", False, False, False),
        ("Quel temps fait-il?", False, False, False),
        ("Je suis content", False, False, False),
    ]
    
    print("Tests en cours...\n")
    
    passed = 0
    failed = 0
    
    for sentence, should_be_valid, should_have_departure, should_have_arrival in test_cases:
        result = pipeline.predict(sentence)
        
        # Vérifier les résultats
        is_valid = result["valid"]
        has_departure = result["departure"] is not None
        has_arrival = result["arrival"] is not None
        
        # Validation
        valid_ok = is_valid == should_be_valid
        departure_ok = (not should_have_departure) or has_departure
        arrival_ok = (not should_have_arrival) or has_arrival
        
        test_passed = valid_ok and departure_ok and arrival_ok
        
        if test_passed:
            passed += 1
            status = "✅"
        else:
            failed += 1
            status = "❌"
        
        print(f"{status} Phrase: \"{sentence}\"")
        print(f"   Valid: {is_valid} (attendu: {should_be_valid})")
        if is_valid:
            print(f"   Départ: {result['departure']}")
            print(f"   Arrivée: {result['arrival']}")
        else:
            print(f"   Message: {result['message']}")
        print()
    
    print("=" * 80)
    print(f"Résultats: {passed} tests réussis, {failed} tests échoués")
    print("=" * 80)


if __name__ == "__main__":
    test_pipeline()

