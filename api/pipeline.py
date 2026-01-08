#!/usr/bin/env python3
"""
Pipeline complet : Classifieur + NLP
Charge les modèles et effectue la prédiction complète.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

# Ajouter le répertoire racine au path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import spacy


class TravelIntentPipeline:
    """Pipeline complet pour l'extraction des intentions de voyage."""
    
    def __init__(
        self,
        classifier_model_path: Optional[Path] = None,
        classifier_vectorizer_path: Optional[Path] = None,
        nlp_model_path: Optional[Path] = None
    ):
        """
        Initialise le pipeline avec les chemins des modèles.
        
        Args:
            classifier_model_path: Chemin vers le modèle de classifieur
            classifier_vectorizer_path: Chemin vers le vectorizer du classifieur
            nlp_model_path: Chemin vers le modèle NLP Spacy
        """
        self.project_root = PROJECT_ROOT
        
        # Chemins par défaut (utiliser les modèles les plus récents)
        if classifier_model_path is None:
            classifier_model_path = self._find_latest_classifier_model()
        if classifier_vectorizer_path is None:
            classifier_vectorizer_path = self._find_latest_classifier_vectorizer()
        if nlp_model_path is None:
            nlp_model_path = self._find_latest_nlp_model()
        
        # Charger les modèles
        print(f"🔄 Chargement du classifieur depuis {classifier_model_path}...")
        self.classifier = joblib.load(classifier_model_path)
        self.vectorizer = joblib.load(classifier_vectorizer_path)
        print("✅ Classifieur chargé")
        
        print(f"🔄 Chargement du modèle NLP depuis {nlp_model_path}...")
        self.nlp = spacy.load(nlp_model_path)
        print("✅ Modèle NLP chargé")
        
        print("✅ Pipeline initialisé et prêt à l'emploi!")
    
    def _find_latest_classifier_model(self) -> Path:
        """Trouve le modèle de classifieur le plus récent."""
        models_dir = self.project_root / "classifier" / "models"
        model_files = list(models_dir.glob("logistic_regression_*.joblib"))
        if not model_files:
            raise FileNotFoundError("Aucun modèle de classifieur trouvé")
        # Retourner le plus récent (par nom de fichier)
        return sorted(model_files)[-1]
    
    def _find_latest_classifier_vectorizer(self) -> Path:
        """Trouve le vectorizer le plus récent."""
        models_dir = self.project_root / "classifier" / "models"
        vectorizer_files = list(models_dir.glob("vectorizer_*.joblib"))
        if not vectorizer_files:
            raise FileNotFoundError("Aucun vectorizer trouvé")
        return sorted(vectorizer_files)[-1]
    
    def _find_latest_nlp_model(self) -> Path:
        """Trouve le modèle NLP le plus récent."""
        models_dir = self.project_root / "nlp" / "models"
        # Chercher les dossiers de modèles Spacy
        model_dirs = [d for d in models_dir.iterdir() if d.is_dir() and d.name.startswith("spacy_ner_")]
        if not model_dirs:
            raise FileNotFoundError("Aucun modèle NLP trouvé")
        return sorted(model_dirs)[-1]
    
    def predict(self, sentence: str) -> Dict:
        """
        Prédit les destinations de départ et d'arrivée à partir d'une phrase.
        
        Args:
            sentence: Phrase à analyser
            
        Returns:
            Dictionnaire avec:
            - valid: bool - Si la phrase est valide
            - message: str - Message d'erreur si non valide
            - departure: Optional[str] - Ville de départ
            - arrival: Optional[str] - Ville d'arrivée
        """
        # Étape 1: Vérifier avec le classifieur
        sentence_vectorized = self.vectorizer.transform([sentence])
        is_valid = self.classifier.predict(sentence_vectorized)[0] == 1
        
        if not is_valid:
            return {
                "valid": False,
                "message": "Merci de rentrer une phrase valide",
                "departure": None,
                "arrival": None
            }
        
        # Étape 2: Extraire les entités avec le NLP
        doc = self.nlp(sentence)
        
        departure = None
        arrival = None
        
        for ent in doc.ents:
            if ent.label_ == "DEPARTURE":
                departure = ent.text.strip()
            elif ent.label_ == "ARRIVAL":
                arrival = ent.text.strip()
        
        return {
            "valid": True,
            "message": None,
            "departure": departure,
            "arrival": arrival
        }


def main():
    """Test du pipeline en ligne de commande."""
    pipeline = TravelIntentPipeline()
    
    # Tests
    test_sentences = [
        "Je vais de Paris à Lyon",
        "Billet Marseille Nice demain",
        "Bonjour comment allez-vous?",
        "Trajet la gare de Lille vers l'aéroport de Lyon"
    ]
    
    print("\n" + "="*80)
    print("TESTS DU PIPELINE")
    print("="*80 + "\n")
    
    for sentence in test_sentences:
        print(f"Phrase: {sentence}")
        result = pipeline.predict(sentence)
        print(f"Résultat: {result}\n")


if __name__ == "__main__":
    main()

