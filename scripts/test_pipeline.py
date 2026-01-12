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
        print("🔄 Chargement du pipeline...")
        pipeline = TravelIntentPipeline()
        print("✅ Pipeline chargé avec succès!\n")
        
        # Afficher le type de modèle NER utilisé
        if hasattr(pipeline, 'use_camembert_ner') and pipeline.use_camembert_ner:
            print("📌 Modèle NER utilisé: CamemBERT")
        else:
            print("📌 Modèle NER utilisé: SpaCy")
        print()
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Phrases de test
    test_cases = [
        # Phrases valides avec départ et arrivée
        ("Je vais de Paris à Lyon", True, True, True),
        ("Billet Marseille Nice demain", True, True, True),
        ("Trajet la gare de Lille vers l'aéroport de Lyon", True, True, True),
        ("Je veux aller de Bordeaux à Toulouse", True, True, True),
        ("J'aimerais un trajet de Nantes à Rennes", True, True, True),
        ("train Strasbourg Metz svp", True, True, True),
        
        # Phrases valides avec seulement arrivée
        ("Je vais à Paris", True, False, True),
        ("Billet pour Lyon", True, False, True),
        
        # Phrases invalides
        ("Bonjour comment allez-vous?", False, False, False),
        ("Quel temps fait-il?", False, False, False),
        ("Je suis content", False, False, False),
    ]
    
    print("🧪 Tests en cours...\n")
    print("-" * 80)
    
    passed = 0
    failed = 0
    
    for i, (sentence, should_be_valid, should_have_departure, should_have_arrival) in enumerate(test_cases, 1):
        try:
            result = pipeline.predict(sentence)
            
            # Vérifier les résultats
            is_valid = result["valid"]
            has_departure = result["departure"] is not None
            has_arrival = result["arrival"] is not None
            
            # Validation (plus souple pour les tests)
            valid_ok = is_valid == should_be_valid
            departure_ok = (not should_have_departure) or has_departure
            arrival_ok = (not should_have_arrival) or has_arrival
            
            # Pour les phrases invalides, on accepte qu'elles soient rejetées
            if not should_be_valid:
                test_passed = not is_valid
            else:
                test_passed = valid_ok and departure_ok and arrival_ok
            
            if test_passed:
                passed += 1
                status = "✅"
            else:
                failed += 1
                status = "❌"
            
            print(f"\n{status} Test {i}: \"{sentence}\"")
            print(f"   Valid: {is_valid} (attendu: {should_be_valid})")
            if is_valid:
                print(f"   Départ: {result['departure'] or 'Non trouvé'}")
                print(f"   Arrivée: {result['arrival'] or 'Non trouvé'}")
                if not test_passed:
                    print(f"   ⚠️  Problème détecté:")
                    if not departure_ok:
                        print(f"      - Départ attendu mais non trouvé")
                    if not arrival_ok:
                        print(f"      - Arrivée attendue mais non trouvée")
            else:
                print(f"   Message: {result['message']}")
                
        except Exception as e:
            failed += 1
            print(f"\n❌ Test {i}: \"{sentence}\"")
            print(f"   Erreur: {e}")
            import traceback
            traceback.print_exc()
        
        print("-" * 80)
    
    print(f"\n{'=' * 80}")
    print(f"📊 RÉSULTATS FINAUX")
    print(f"{'=' * 80}")
    print(f"✅ Tests réussis: {passed}/{len(test_cases)}")
    print(f"❌ Tests échoués: {failed}/{len(test_cases)}")
    print(f"{'=' * 80}")
    
    if failed == 0:
        print("\n🎉 Tous les tests sont passés avec succès!")
    else:
        print(f"\n⚠️  {failed} test(s) ont échoué. Vérifiez les résultats ci-dessus.")


if __name__ == "__main__":
    test_pipeline()

