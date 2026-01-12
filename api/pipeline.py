#!/usr/bin/env python3
"""
Pipeline complet : Classifieur CamemBERT + NLP
Charge les modèles et effectue la prédiction complète.
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, Optional, Tuple

# Ajouter le répertoire racine au path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import torch
import spacy
import json
from transformers import (
    CamembertTokenizer, 
    CamembertTokenizerFast,
    CamembertForSequenceClassification,
    CamembertForTokenClassification
)

# Import du module pathfinding
try:
    from pathfinding import RouteFinder
    PATHFINDING_AVAILABLE = True
except ImportError:
    PATHFINDING_AVAILABLE = False
    print("⚠️  Module pathfinding non disponible")


class TravelIntentPipeline:
    """Pipeline complet pour l'extraction des intentions de voyage."""
    
    def __init__(
        self,
        classifier_model_path: Optional[Path] = None,
        nlp_model_path: Optional[Path] = None,
        use_camembert: bool = True,
        use_camembert_ner: Optional[bool] = None,  # None = auto-détection
        use_pathfinding: bool = True,  # Activer le pathfinding
        pathfinding_algorithm: str = "dijkstra"  # "dijkstra" ou "astar"
    ):
        """
        Initialise le pipeline avec les chemins des modèles.
        
        Args:
            classifier_model_path: Chemin vers le modèle de classifieur (CamemBERT ou ancien)
            nlp_model_path: Chemin vers le modèle NLP (SpaCy ou CamemBERT NER)
            use_camembert: Si True, utilise CamemBERT pour le classifieur, sinon utilise l'ancien modèle TF-IDF
            use_camembert_ner: Si True, utilise CamemBERT NER, si False utilise SpaCy, si None détecte automatiquement
            use_pathfinding: Si True, active le module pathfinding pour trouver les itinéraires (défaut: True)
            pathfinding_algorithm: Algorithme à utiliser ("dijkstra" ou "astar", défaut: "dijkstra")
        """
        self.project_root = PROJECT_ROOT
        self.use_camembert = use_camembert
        self.use_camembert_ner = use_camembert_ner
        self.use_pathfinding = use_pathfinding and PATHFINDING_AVAILABLE
        self.pathfinding_algorithm = pathfinding_algorithm
        
        # Configurer le device (GPU MPS si disponible, sinon CPU)
        if torch.backends.mps.is_available():
            self.device = torch.device("mps")
            print("✅ GPU MPS détecté et utilisé")
        else:
            self.device = torch.device("cpu")
            print("⚠️  GPU MPS non disponible, utilisation du CPU")
        
        # Chemins par défaut
        if classifier_model_path is None:
            if use_camembert:
                classifier_model_path = self._find_latest_camembert_model()
            else:
                classifier_model_path = self._find_latest_classifier_model()
        
        if nlp_model_path is None:
            nlp_model_path = self._find_latest_nlp_model()
        
        # Charger le classifieur
        print(f"🔄 Chargement du classifieur depuis {classifier_model_path}...")
        if use_camembert:
            self.tokenizer = CamembertTokenizer.from_pretrained(str(classifier_model_path))
            self.classifier = CamembertForSequenceClassification.from_pretrained(str(classifier_model_path))
            self.classifier.to(self.device)
            self.classifier.eval()
            self.max_length = 128  # Longueur maximale pour CamemBERT
            print("✅ Classifieur CamemBERT chargé")
        else:
            # Ancien modèle (TF-IDF + Logistic Regression)
            import joblib
            self.classifier = joblib.load(classifier_model_path)
            self.vectorizer = joblib.load(self._find_latest_classifier_vectorizer())
            print("✅ Classifieur basique chargé")
        
        # Détecter le type de modèle NER si non spécifié
        if self.use_camembert_ner is None:
            self.use_camembert_ner = self._detect_ner_model_type(nlp_model_path)
        
        # Charger le modèle NLP
        print(f"🔄 Chargement du modèle NLP depuis {nlp_model_path}...")
        if self.use_camembert_ner:
            self._load_camembert_ner_model(nlp_model_path)
            print("✅ Modèle NLP CamemBERT chargé")
        else:
            self.nlp = spacy.load(str(nlp_model_path))
            print("✅ Modèle NLP SpaCy chargé")
        
        # Charger la liste des villes/gares pour le post-processing (commun aux deux modèles)
        self._load_cities_list()
        
        # Initialiser le module pathfinding si disponible
        self.route_finder = None
        if self.use_pathfinding:
            try:
                print("🔄 Initialisation du module pathfinding...")
                self.route_finder = RouteFinder()
                print("✅ Module pathfinding initialisé")
            except Exception as e:
                print(f"⚠️  Erreur lors de l'initialisation du pathfinding: {e}")
                self.use_pathfinding = False
                self.route_finder = None
        
        print("✅ Pipeline initialisé et prêt à l'emploi!")
    
    def _find_latest_camembert_model(self) -> Path:
        """Trouve le modèle CamemBERT le plus récent."""
        models_dir = self.project_root / "classifier" / "models"
        model_dirs = [d for d in models_dir.iterdir() 
                     if d.is_dir() and d.name.startswith("validity_classifier_camembert_")]
        if not model_dirs:
            raise FileNotFoundError(
                "Aucun modèle CamemBERT trouvé. "
                "Entraînez d'abord un modèle avec le notebook 03_validity_classifier_camembert_gpu.ipynb"
            )
        return sorted(model_dirs)[-1]
    
    def _find_latest_classifier_model(self) -> Path:
        """Trouve le modèle de classifieur basique le plus récent."""
        models_dir = self.project_root / "classifier" / "models"
        model_files = list(models_dir.glob("logistic_regression_*.joblib"))
        if not model_files:
            raise FileNotFoundError("Aucun modèle de classifieur trouvé")
        return sorted(model_files)[-1]
    
    def _find_latest_classifier_vectorizer(self) -> Path:
        """Trouve le vectorizer le plus récent."""
        models_dir = self.project_root / "classifier" / "models"
        vectorizer_files = list(models_dir.glob("vectorizer_*.joblib"))
        if not vectorizer_files:
            raise FileNotFoundError("Aucun vectorizer trouvé")
        return sorted(vectorizer_files)[-1]
    
    def _find_latest_nlp_model(self) -> Path:
        """Trouve le modèle NLP le plus récent (CamemBERT ou SpaCy)."""
        models_dir = self.project_root / "nlp" / "models"
        # Chercher d'abord les modèles CamemBERT NER
        camembert_dirs = [d for d in models_dir.iterdir() 
                         if d.is_dir() and d.name.startswith("ner_camembert_")]
        # Ensuite les modèles SpaCy
        spacy_dirs = [d for d in models_dir.iterdir() 
                     if d.is_dir() and d.name.startswith("spacy_ner_")]
        
        # Priorité aux modèles CamemBERT
        if camembert_dirs:
            return sorted(camembert_dirs)[-1]
        elif spacy_dirs:
            return sorted(spacy_dirs)[-1]
        else:
            raise FileNotFoundError(
                "Aucun modèle NLP trouvé. "
                "Entraînez un modèle avec les notebooks NER (SpaCy ou CamemBERT)"
            )
    
    def _detect_ner_model_type(self, model_path: Path) -> bool:
        """
        Détecte si le modèle est un modèle CamemBERT NER ou SpaCy.
        
        Args:
            model_path: Chemin vers le modèle
            
        Returns:
            True si CamemBERT NER, False si SpaCy
        """
        # Vérifier le nom du dossier
        if "ner_camembert" in model_path.name.lower():
            return True
        elif "spacy_ner" in model_path.name.lower():
            return False
        
        # Vérifier la présence de fichiers caractéristiques
        if (model_path / "config.json").exists() and (model_path / "tokenizer.json").exists():
            # C'est probablement un modèle Transformers (CamemBERT)
            return True
        elif (model_path / "meta.json").exists() or (model_path / "tokenizer").exists():
            # C'est probablement un modèle SpaCy
            return False
        
        # Par défaut, essayer SpaCy puis CamemBERT en cas d'échec
        return False
    
    def _load_camembert_ner_model(self, model_path: Path):
        """Charge le modèle NER CamemBERT."""
        # Charger le tokenizer Fast (nécessaire pour return_offsets_mapping)
        self.ner_tokenizer = CamembertTokenizerFast.from_pretrained(str(model_path))
        
        # Charger le modèle
        self.ner_model = CamembertForTokenClassification.from_pretrained(str(model_path))
        self.ner_model.to(self.device)
        self.ner_model.eval()
        
        # Charger les métadonnées pour récupérer les labels
        metrics_file = model_path / "metrics.json"
        if metrics_file.exists():
            import json
            with open(metrics_file, 'r', encoding='utf-8') as f:
                metrics = json.load(f)
                self.ner_labels = metrics.get('labels', ["O", "B-DEPARTURE", "I-DEPARTURE", "B-ARRIVAL", "I-ARRIVAL"])
        else:
            # Labels par défaut
            self.ner_labels = ["O", "B-DEPARTURE", "I-DEPARTURE", "B-ARRIVAL", "I-ARRIVAL"]
        
        # Créer les mappings
        self.ner_id2label = {i: label for i, label in enumerate(self.ner_labels)}
        self.ner_max_length = 128  # Longueur maximale pour CamemBERT
    
    def _load_cities_list(self):
        """Charge la liste des villes/gares depuis gares-francaises.json pour le post-processing."""
        gares_file = self.project_root / "dataset" / "shared" / "gares-francaises.json"
        self.known_cities = set()
        
        try:
            if gares_file.exists():
                with open(gares_file, 'r', encoding='utf-8') as f:
                    gares = json.load(f)
                    for gare in gares:
                        nom = gare.get('nom', '').strip()
                        if nom:
                            # Ajouter le nom complet
                            self.known_cities.add(nom.lower())
                            # Ajouter les parties si la ville contient " - " (séparateur de gares composées)
                            if " - " in nom:
                                parts = nom.split(" - ")
                                for part in parts:
                                    part_clean = part.strip()
                                    if part_clean:
                                        self.known_cities.add(part_clean.lower())
                            # Pour les villes avec tirets (ex: "Villeneuve-d'Ascq"), garder aussi le nom simplifié
                            # en enlevant les parties après le premier tiret simple
                            if "-" in nom and " - " not in nom:
                                # Garder juste la première partie avant le tiret pour certaines villes
                                first_part = nom.split("-")[0].strip()
                                if first_part and len(first_part) > 2:
                                    self.known_cities.add(first_part.lower())
                
                print(f"✅ {len(self.known_cities)} villes/gares chargées pour le post-processing")
            else:
                print("⚠️  Fichier gares-francaises.json non trouvé, post-processing limité")
                self.known_cities = set()
        except Exception as e:
            print(f"⚠️  Erreur lors du chargement des villes: {e}")
            self.known_cities = set()
    
    def _is_likely_city(self, text: str) -> bool:
        """
        Vérifie si un texte ressemble à une ville connue.
        
        Args:
            text: Texte à vérifier
            
        Returns:
            True si le texte ressemble à une ville connue
        """
        if not text or len(text) < 2:
            return False
        
        text_lower = text.lower().strip()
        
        # Vérification exacte
        if text_lower in self.known_cities:
            return True
        
        # Vérification si le texte correspond au début d'une ville connue
        # (ex: "Marseille" dans "Marseille Blancarde", "Marseille Saint-Charles")
        for city in self.known_cities:
            # Correspondance exacte au début
            if city.startswith(text_lower + " ") or city == text_lower:
                return True
            # Correspondance si la ville commence par le texte
            if text_lower.startswith(city.split()[0]) and len(text_lower) >= 3:
                return True
        
        # Si le texte fait plus de 3 caractères et correspond à une partie de ville
        if len(text_lower) >= 4:
            for city in self.known_cities:
                # Vérifier si le texte est présent dans le nom de la ville
                # mais uniquement s'il fait au moins 4 caractères pour éviter les faux positifs
                if text_lower in city and len(text_lower) >= 4:
                    # Vérifier que c'est au début ou séparé par un espace/tiret
                    if city.startswith(text_lower) or f" {text_lower}" in city or f"-{text_lower}" in city:
                        return True
        
        return False
    
    def _extract_city_name_from_text(self, text: str) -> Optional[str]:
        """
        Extrait le nom de ville depuis un texte qui peut contenir des préfixes
        comme "la gare de", "l'aéroport de", "station de", etc.
        
        Exemples:
        - "la gare de Lille" → "Lille"
        - "l'aéroport de Lyon" → "Lyon"
        - "gare de Paris" → "Paris"
        - "station de Marseille" → "Marseille"
        - "Lille" → "Lille" (déjà un nom de ville)
        
        Args:
            text: Texte contenant potentiellement un nom de ville
            
        Returns:
            Nom de ville extrait et capitalisé, ou None si non trouvé
        """
        if not text:
            return None
        
        text = text.strip()
        
        # Patterns pour extraire le nom de ville après "gare de", "aéroport de", etc.
        patterns = [
            r'(?:la|le|les|l\')\s+(?:gare|station|aéroport)\s+de\s+(.+)',  # "la gare de X"
            r'(?:gare|station|aéroport)\s+de\s+(.+)',  # "gare de X"
            r'vers\s+(.+)',  # "vers X"
            r'à\s+(.+)',  # "à X"
            r'de\s+(.+)',  # "de X" (mais attention aux faux positifs)
        ]
        
        # Essayer d'extraire avec les patterns
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                potential_city = match.group(1).strip()
                # Vérifier que c'est une ville connue
                if self._is_likely_city(potential_city):
                    return self._capitalize_city_name(potential_city)
        
        # Si aucun pattern ne correspond, vérifier si le texte entier est une ville
        if self._is_likely_city(text):
            return self._capitalize_city_name(text)
        
        # Sinon, chercher une ville connue dans le texte
        text_lower = text.lower()
        for city in self.known_cities:
            city_lower = city.lower()
            # Chercher la ville dans le texte (mot complet)
            if re.search(r'\b' + re.escape(city_lower) + r'\b', text_lower):
                return self._capitalize_city_name(city)
        
        return None
    
    def _capitalize_city_name(self, city_name: str) -> str:
        """
        Capitalise correctement un nom de ville français.
        
        Exemples:
        - "nantes" → "Nantes"
        - "paris" → "Paris"
        - "saint-etienne" → "Saint-Etienne"
        - "lille" → "Lille"
        
        Args:
            city_name: Nom de ville en minuscules ou mixte
            
        Returns:
            Nom de ville correctement capitalisé
        """
        if not city_name:
            return city_name
        
        # Trouver la ville correspondante dans known_cities pour avoir la bonne capitalisation
        city_lower = city_name.lower()
        for known_city in self.known_cities:
            if known_city.lower() == city_lower:
                return known_city
        
        # Si pas trouvé, capitaliser intelligemment
        # Capitaliser la première lettre de chaque mot, sauf les prépositions
        words = city_name.split()
        prepositions = {'de', 'du', 'des', 'le', 'la', 'les', 'sur', 'sous', 'en', 'à', 'au', 'aux'}
        
        capitalized_words = []
        for word in words:
            if word.lower() in prepositions:
                capitalized_words.append(word.lower())
            else:
                # Capitaliser la première lettre
                capitalized_words.append(word.capitalize())
        
        result = ' '.join(capitalized_words)
        
        # Gérer les tirets (ex: "saint-etienne" → "Saint-Etienne")
        if '-' in result:
            parts = result.split('-')
            result = '-'.join([part.capitalize() for part in parts])
        
        return result
    
    def _clean_entity_text(self, text: str) -> str:
        """
        Nettoie le texte d'une entité en supprimant les caractères spéciaux
        qui n'apparaissent jamais dans les noms de gares.
        
        Caractères supprimés : / " ? ( )
        Caractères conservés : ' (apostrophe légitime dans les noms français)
        
        Args:
            text: Texte à nettoyer
            
        Returns:
            Texte nettoyé
        """
        if not text:
            return text
        
        # Caractères à supprimer (vérifiés : aucune occurrence dans gares-francaises.json)
        # Note: ' (apostrophe) est conservée car elle apparaît légitimement dans 90 gares
        # Exemples: "Bois-d'Oingt", "l'Aillerie", "d'Estrétefonds"
        chars_to_remove = ['/', '"', '?', '(', ')']
        
        cleaned = text
        for char in chars_to_remove:
            cleaned = cleaned.replace(char, '')
        
        # Nettoyer les espaces multiples et les espaces en début/fin
        cleaned = ' '.join(cleaned.split())
        
        return cleaned.strip()
    
    def _post_process_entities(self, sentence: str, departure: Optional[str], arrival: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        """
        Post-processing des entités pour gérer les cas "Ville-Ville" mal détectés.
        
        Exemple: "Trajet Marseille-Lyon" → départ="Marseille-Lyon", arrivée=None
        Devrait devenir: départ="Marseille", arrivée="Lyon"
        
        Args:
            sentence: Phrase originale
            departure: Entité départ détectée
            arrival: Entité arrivée détectée
            
        Returns:
            Tuple (departure, arrival) corrigé
        """
        sentence_lower = sentence.lower()
        
        # Cas principal : départ détecté avec tiret, pas d'arrivée
        if departure and "-" in departure and not arrival:
            parts = departure.split("-")
            if len(parts) == 2:
                part1, part2 = parts[0].strip(), parts[1].strip()
                
                # Vérifier que les deux parties sont des villes valides
                part1_valid = self._is_likely_city(part1)
                part2_valid = self._is_likely_city(part2)
                
                # Vérifier aussi qu'elles ont une longueur raisonnable (éviter "Ma-Ly")
                if part1_valid and part2_valid and len(part1) >= 3 and len(part2) >= 3:
                    # Vérifier le contexte : phrases de trajet
                    trajet_keywords = ["trajet", "de", "depuis", "vers", "à", "aller", "billet", "train", "voyage"]
                    has_trajet_context = any(keyword in sentence_lower for keyword in trajet_keywords)
                    
                    # Si c'est dans un contexte de trajet OU si la phrase commence par une des villes
                    if has_trajet_context or sentence_lower.startswith(part1.lower()):
                        # Nettoyer avant de retourner
                        return self._clean_entity_text(part1), self._clean_entity_text(part2)
        
        # Cas similaire pour l'arrivée
        if arrival and "-" in arrival and not departure:
            parts = arrival.split("-")
            if len(parts) == 2:
                part1, part2 = parts[0].strip(), parts[1].strip()
                part1_valid = self._is_likely_city(part1)
                part2_valid = self._is_likely_city(part2)
                
                if part1_valid and part2_valid and len(part1) >= 3 and len(part2) >= 3:
                    trajet_keywords = ["trajet", "de", "depuis", "vers", "à", "aller", "billet", "train", "voyage"]
                    has_trajet_context = any(keyword in sentence_lower for keyword in trajet_keywords)
                    
                    if has_trajet_context or sentence_lower.startswith(part1.lower()):
                        # Nettoyer avant de retourner
                        return self._clean_entity_text(part1), self._clean_entity_text(part2)
        
        # Cas où départ contient un tiret ET on a aussi une arrivée
        # Vérifier si le départ devrait être séparé (doublon possible)
        if departure and "-" in departure and arrival:
            parts = departure.split("-")
            if len(parts) == 2:
                part1, part2 = parts[0].strip(), parts[1].strip()
                # Si la partie après le tiret correspond exactement à l'arrivée, c'est suspect
                if part2.lower() == arrival.lower() or part2.lower() in arrival.lower():
                    # Probablement un doublon, vérifier si part1 est une ville valide
                    if self._is_likely_city(part1) and len(part1) >= 3:
                        # Nettoyer avant de retourner
                        return self._clean_entity_text(part1), self._clean_entity_text(arrival)
        
        # Nettoyer les entités finales avant de retourner
        departure_cleaned = self._clean_entity_text(departure) if departure else None
        arrival_cleaned = self._clean_entity_text(arrival) if arrival else None
        
        # Extraire les noms de villes depuis des phrases comme "la gare de Lille"
        if departure_cleaned:
            extracted_departure = self._extract_city_name_from_text(departure_cleaned)
            if extracted_departure:
                departure_cleaned = extracted_departure
        
        if arrival_cleaned:
            extracted_arrival = self._extract_city_name_from_text(arrival_cleaned)
            if extracted_arrival:
                arrival_cleaned = extracted_arrival
        
        return departure_cleaned, arrival_cleaned
    
    def _predict_validity_camembert(self, sentence: str) -> bool:
        """Prédit si une phrase est valide avec CamemBERT."""
        # Tokeniser
        encoded = self.tokenizer(
            sentence,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        ).to(self.device)
        
        # Prédire
        with torch.no_grad():
            outputs = self.classifier(**encoded)
            logits = outputs.logits
            prediction = torch.argmax(logits, dim=1).item()
        
        return prediction == 1
    
    def _predict_validity_basic(self, sentence: str) -> bool:
        """Prédit si une phrase est valide avec l'ancien modèle."""
        sentence_vectorized = self.vectorizer.transform([sentence])
        is_valid = self.classifier.predict(sentence_vectorized)[0] == 1
        return is_valid
    
    def predict(self, sentence: str) -> Dict:
        """
        Prédit les destinations de départ et d'arrivée à partir d'une phrase.
        Si le pathfinding est activé, trouve également l'itinéraire optimal.
        
        Args:
            sentence: Phrase à analyser
            
        Returns:
            Dictionnaire avec:
            - valid: bool - Si la phrase est valide
            - message: str - Message d'erreur si non valide
            - departure: Optional[str] - Ville de départ
            - arrival: Optional[str] - Ville d'arrivée
            - route: Optional[List[str]] - Itinéraire complet avec étapes (si pathfinding activé)
            - route_distance: Optional[float] - Distance totale en km (si pathfinding activé)
            - route_time: Optional[float] - Temps estimé en heures (si pathfinding activé)
        """
        # Étape 1: Vérifier avec le classifieur
        if self.use_camembert:
            is_valid = self._predict_validity_camembert(sentence)
        else:
            is_valid = self._predict_validity_basic(sentence)
        
        if not is_valid:
            return {
                "valid": False,
                "message": "Cette phrase ne contient pas d'intention de trajet valide. Veuillez reformuler votre demande.",
                "departure": None,
                "arrival": None,
                "route": None,
                "route_distance": None,
                "route_time": None
            }
        
        # Étape 2: Extraire les entités avec le NLP
        if self.use_camembert_ner:
            departure, arrival = self._extract_entities_camembert(sentence)
        else:
            departure, arrival = self._extract_entities_spacy(sentence)
        
        # Étape 3: Post-processing pour corriger les cas "Ville-Ville"
        departure, arrival = self._post_process_entities(sentence, departure, arrival)
        
        # Étape 4: Pathfinding (si activé et si on a départ et arrivée)
        route = None
        route_distance = None
        route_time = None
        
        if self.use_pathfinding and self.route_finder and departure and arrival:
            try:
                pathfinding_result = self.route_finder.find_route(
                    departure,
                    arrival,
                    algorithm=self.pathfinding_algorithm
                )
                
                if pathfinding_result.success:
                    route = pathfinding_result.route
                    route_distance = pathfinding_result.total_distance
                    route_time = pathfinding_result.estimated_time
                # Si échec, on garde departure et arrival mais pas de route
            except Exception as e:
                # En cas d'erreur, on continue sans pathfinding
                print(f"⚠️  Erreur pathfinding: {e}")
        
        return {
            "valid": True,
            "message": None,
            "departure": departure,
            "arrival": arrival,
            "route": route,
            "route_distance": route_distance,
            "route_time": route_time
        }
    
    def _extract_entities_spacy(self, sentence: str) -> Tuple[Optional[str], Optional[str]]:
        """Extrait les entités DEPARTURE et ARRIVAL avec SpaCy."""
        doc = self.nlp(sentence)
        
        departure = None
        arrival = None
        
        for ent in doc.ents:
            if ent.label_ == "DEPARTURE":
                departure = ent.text.strip()
            elif ent.label_ == "ARRIVAL":
                arrival = ent.text.strip()
        
        return departure, arrival
    
    def _extract_entities_camembert(self, sentence: str) -> Tuple[Optional[str], Optional[str]]:
        """Extrait les entités DEPARTURE et ARRIVAL avec CamemBERT NER."""
        # Tokeniser avec offset mapping pour récupérer les positions originales
        encoding = self.ner_tokenizer(
            sentence,
            max_length=self.ner_max_length,
            padding='max_length',
            truncation=True,
            return_offsets_mapping=True,
            return_tensors='pt'
        )
        
        # Extraire offset_mapping avant de passer au modèle (le modèle ne l'accepte pas)
        offset_mapping = encoding.pop('offset_mapping')[0].cpu().numpy()
        
        # Déplacer les autres inputs sur le device
        encoding = {k: v.to(self.device) for k, v in encoding.items()}
        
        # Prédire
        with torch.no_grad():
            outputs = self.ner_model(**encoding)
            predictions = torch.argmax(outputs.logits, dim=-1)
        
        # Convertir les prédictions en labels
        predictions = predictions[0].cpu().numpy()
        
        # Extraire les entités depuis les labels IOB
        departure_spans = []
        arrival_spans = []
        current_entity = None
        entity_start_char = None
        entity_end_char = None
        
        for i, (pred_id, (start_offset, end_offset)) in enumerate(zip(predictions, offset_mapping)):
            # Ignorer les tokens spéciaux (padding, [CLS], [SEP])
            if start_offset == 0 and end_offset == 0:
                # Si on était en train de collecter une entité, la terminer
                if current_entity is not None and entity_start_char is not None:
                    if current_entity == "DEPARTURE":
                        departure_spans.append((entity_start_char, entity_end_char))
                    elif current_entity == "ARRIVAL":
                        arrival_spans.append((entity_start_char, entity_end_char))
                    current_entity = None
                    entity_start_char = None
                    entity_end_char = None
                continue
            
            label = self.ner_id2label[pred_id]
            
            if label.startswith("B-"):
                # Nouvelle entité - sauvegarder la précédente si elle existe
                if current_entity is not None and entity_start_char is not None:
                    if current_entity == "DEPARTURE":
                        departure_spans.append((entity_start_char, entity_end_char))
                    elif current_entity == "ARRIVAL":
                        arrival_spans.append((entity_start_char, entity_end_char))
                
                # Commencer une nouvelle entité
                if label == "B-DEPARTURE":
                    current_entity = "DEPARTURE"
                    entity_start_char = start_offset
                    entity_end_char = end_offset
                elif label == "B-ARRIVAL":
                    current_entity = "ARRIVAL"
                    entity_start_char = start_offset
                    entity_end_char = end_offset
                else:
                    current_entity = None
                    entity_start_char = None
                    entity_end_char = None
            
            elif label.startswith("I-"):
                # Continuation d'une entité
                if current_entity is not None and (
                    (label == "I-DEPARTURE" and current_entity == "DEPARTURE") or
                    (label == "I-ARRIVAL" and current_entity == "ARRIVAL")
                ):
                    # Étendre la fin de l'entité
                    entity_end_char = end_offset
                else:
                    # Label I- ne correspond pas à l'entité en cours - terminer l'entité précédente
                    if current_entity is not None and entity_start_char is not None:
                        if current_entity == "DEPARTURE":
                            departure_spans.append((entity_start_char, entity_end_char))
                        elif current_entity == "ARRIVAL":
                            arrival_spans.append((entity_start_char, entity_end_char))
                    current_entity = None
                    entity_start_char = None
                    entity_end_char = None
            
            else:  # "O"
                # Fin d'entité si on était en train d'en extraire une
                if current_entity is not None and entity_start_char is not None:
                    if current_entity == "DEPARTURE":
                        departure_spans.append((entity_start_char, entity_end_char))
                    elif current_entity == "ARRIVAL":
                        arrival_spans.append((entity_start_char, entity_end_char))
                current_entity = None
                entity_start_char = None
                entity_end_char = None
        
        # Sauvegarder la dernière entité si elle existe
        if current_entity is not None and entity_start_char is not None:
            if current_entity == "DEPARTURE":
                departure_spans.append((entity_start_char, entity_end_char))
            elif current_entity == "ARRIVAL":
                arrival_spans.append((entity_start_char, entity_end_char))
        
        # Extraire le texte original pour chaque entité
        departure = None
        arrival = None
        
        if departure_spans:
            # Prendre la première occurrence de DEPARTURE
            start_char, end_char = departure_spans[0]
            departure = sentence[start_char:end_char].strip()
        
        if arrival_spans:
            # Prendre la première occurrence de ARRIVAL
            start_char, end_char = arrival_spans[0]
            arrival = sentence[start_char:end_char].strip()
        
        return departure, arrival


def main():
    """Test du pipeline en ligne de commande."""
    try:
        # Essayer d'abord avec CamemBERT
        print("🔄 Tentative de chargement avec CamemBERT...")
        pipeline = TravelIntentPipeline(use_camembert=True)
    except FileNotFoundError as e:
        print(f"⚠️  CamemBERT non trouvé: {e}")
        print("🔄 Utilisation du modèle basique...")
        pipeline = TravelIntentPipeline(use_camembert=False)
    
    # Tests
    test_sentences = [
        "Je vais de Paris à Lyon",
        "Billet Marseille Nice demain",
        "Bonjour comment allez-vous?",
        "Trajet la gare de Lille vers l'aéroport de Lyon",
        "Je mange une pomme"
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
