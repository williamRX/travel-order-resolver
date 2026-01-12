#!/usr/bin/env python3
"""
Script de test spécifique pour vérifier l'intégration du modèle NER CamemBERT.
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.pipeline import TravelIntentPipeline


def test_ner_camembert_integration():
    """Test spécifique pour vérifier l'intégration du modèle NER CamemBERT."""
    print("=" * 80)
    print("TEST D'INTÉGRATION DU MODÈLE NER CAMEMBERT")
    print("=" * 80)
    print()
    
    # Initialiser le pipeline
    try:
        print("🔄 Chargement du pipeline...")
        pipeline = TravelIntentPipeline()
        print()
        
        # Vérifier quel type de modèle NER a été chargé
        if hasattr(pipeline, 'use_camembert_ner'):
            if pipeline.use_camembert_ner:
                print("✅ Modèle NER CamemBERT détecté et chargé!")
                print(f"   - Tokenizer: {type(pipeline.ner_tokenizer).__name__}")
                print(f"   - Modèle: {type(pipeline.ner_model).__name__}")
                print(f"   - Device: {pipeline.device}")
                print(f"   - Labels: {pipeline.ner_labels}")
            else:
                print("⚠️  Modèle NER SpaCy chargé (pas CamemBERT)")
        else:
            print("⚠️  Impossible de déterminer le type de modèle NER")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    print("-" * 80)
    print("🧪 TESTS D'EXTRACTION D'ENTITÉS")
    print("-" * 80)
    print()
    
    # Tests spécifiques pour le NER
    test_sentences = [
        "Je vais de Paris à Lyon",
        "Billet Marseille Nice demain",
        "Trajet la gare de Lille vers l'aéroport de Lyon",
        "Je veux aller de Bordeaux à Toulouse",
        "J'aimerais un trajet de Nantes à Rennes",
        "train Strasbourg Metz svp",
        "Je vais à Paris",
    ]
    
    for i, sentence in enumerate(test_sentences, 1):
        try:
            print(f"Test {i}: \"{sentence}\"")
            result = pipeline.predict(sentence)
            
            if result["valid"]:
                print(f"   ✅ Phrase valide")
                print(f"   📍 Départ: {result['departure'] or 'Non trouvé'}")
                print(f"   📍 Arrivée: {result['arrival'] or 'Non trouvé'}")
            else:
                print(f"   ❌ Phrase invalide: {result['message']}")
            
            print()
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
            print()
    
    print("-" * 80)
    print("✅ Tests terminés!")
    print("-" * 80)


if __name__ == "__main__":
    test_ner_camembert_integration()
