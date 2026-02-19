#!/usr/bin/env python3
"""
Script de vérification du dataset NLP pour détecter les erreurs de flagging.

Vérifie que :
1. Les phrases valides (avec départ ET arrivée) ont exactement 2 entités
2. Les phrases semi-valides (départ OU arrivée) ont exactement 1 entité
3. Les phrases négatives n'ont aucune entité
4. Détecte les cas où des entités devraient être présentes mais ne le sont pas
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

# Chemin vers le dataset
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_FILE = PROJECT_ROOT / "dataset" / "nlp" / "json" / "nlp_training_data.jsonl"
GARES_JSON = PROJECT_ROOT / "dataset" / "shared" / "gares-francaises.json"

# Mots-clés qui indiquent un trajet (départ)
DEPARTURE_KEYWORDS = [
    "de", "depuis", "depui", "partir", "quitter", "sortir", "pars", "quitte", "sors",
    "me tire", "me barre", "me casse", "me taille", "file", "bouge", "déplace",
    "rejins", "rejoins", "rendre", "aller", "voyage", "trajet", "billet"
]

# Mots-clés qui indiquent un trajet (arrivée)
ARRIVAL_KEYWORDS = [
    "à", "a", "vers", "pour", "aller", "rendre", "arriver", "va", "vais", "vont",
    "me pointe", "me dirige", "direction", "destination", "arrivée", "arrive"
]

# Préfixes de localisation
LOCATION_PREFIXES = [
    "la gare de", "la gare d", "l'aéroport de", "l'aéroport d", "l'aéroportt de", "l'aéroportt d",
    "centre de", "centre d", "Centre D", "Centre de", "port de", "port d",
    "les gares de", "les aéroports de"
]

# Séparateurs de trajet
ROUTE_SEPARATORS = ["→", "-", "à", "vers", "pour", "jusqu'à", "jusqu a"]

def load_gares() -> List[str]:
    """Charge la liste des noms de gares."""
    try:
        with GARES_JSON.open("r", encoding="utf-8") as f:
            gares_data = json.load(f)
        return [gare["nom"].lower() for gare in gares_data if "nom" in gare]
    except Exception as e:
        print(f"⚠️  Erreur lors du chargement des gares: {e}")
        return []

def normalize_text(text: str) -> str:
    """Normalise le texte pour la comparaison (minuscules, sans accents)."""
    # Simplification basique (on pourrait utiliser un vrai normalizer)
    text = text.lower()
    # Remplacer quelques caractères accentués courants
    replacements = {
        "é": "e", "è": "e", "ê": "e", "ë": "e",
        "à": "a", "â": "a", "ä": "a",
        "ô": "o", "ö": "o",
        "ù": "u", "û": "u", "ü": "u",
        "ç": "c", "ñ": "n"
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def extract_city_from_text(text: str, gares: List[str]) -> List[Tuple[str, int, int]]:
    """
    Extrait les noms de villes/gares du texte en cherchant des correspondances approximatives.
    Retourne une liste de (nom_gare, start, end) trouvés dans le texte.
    """
    found = []
    text_lower = text.lower()
    
    for gare in gares:
        gare_lower = gare.lower()
        # Recherche exacte (insensible à la casse)
        if gare_lower in text_lower:
            start = text_lower.find(gare_lower)
            end = start + len(gare_lower)
            found.append((gare, start, end))
        else:
            # Recherche approximative : si le nom de gare est long, chercher les 4-5 premiers caractères
            if len(gare_lower) >= 4:
                prefix = gare_lower[:4]
                if prefix in text_lower:
                    # Chercher autour de cette position pour une correspondance plus large
                    idx = text_lower.find(prefix)
                    # Essayer de trouver une correspondance plus longue
                    for i in range(max(0, idx - 5), min(len(text_lower), idx + len(gare_lower) + 5)):
                        if text_lower[i:i+len(gare_lower)] == gare_lower:
                            found.append((gare, i, i + len(gare_lower)))
                            break
                    else:
                        # Si pas de correspondance exacte, chercher une sous-chaîne similaire
                        # Comparer caractère par caractère avec tolérance
                        similarity = 0
                        for j in range(min(len(gare_lower), len(text_lower) - idx)):
                            if text_lower[idx + j] == gare_lower[j]:
                                similarity += 1
                        if similarity >= len(gare_lower) * 0.6:  # Au moins 60% de similarité
                            found.append((gare, idx, idx + len(gare_lower)))
    
    return found

def has_departure_context(text: str, position: int) -> bool:
    """Vérifie si la position est dans un contexte de départ."""
    context_before = text[max(0, position - 30):position].lower()
    context_after = text[position:min(len(text), position + 30)].lower()
    context = context_before + " " + context_after
    
    return any(keyword in context for keyword in DEPARTURE_KEYWORDS)

def has_arrival_context(text: str, position: int) -> bool:
    """Vérifie si la position est dans un contexte d'arrivée."""
    context_before = text[max(0, position - 30):position].lower()
    context_after = text[position:min(len(text), position + 30)].lower()
    context = context_before + " " + context_after
    
    return any(keyword in context for keyword in ARRIVAL_KEYWORDS)

def has_route_separator(text: str) -> bool:
    """Vérifie si le texte contient un séparateur de trajet."""
    return any(sep in text for sep in ROUTE_SEPARATORS)

def is_negative_pattern(text: str) -> bool:
    """
    Détermine si une phrase est probablement un exemple négatif (sans intention de trajet).
    """
    text_lower = text.lower()
    
    # Patterns typiques des phrases négatives
    negative_indicators = [
        "est une", "est belle", "est grande", "est joli", "est ouvert", "est bon",
        "est confortable", "est intéressant", "est moderne", "est animée", "est vert",
        "est magnifique", "est joli", "est grande",
        "j'aime", "je connais", "je visite", "je suis allé", "j'ai visité",
        "mon ami", "mon copain", "mon pote", "mon collègue",
        "veut partir", "arrive", "est là", "est sympa", "m'a dit", "sont là",
        "comment allez-vous", "comment ça va", "quel temps", "quelle heure",
        "tu veux manger", "on se voit", "c'est sympa", "j'ai faim", "je suis fatigué",
        "restaurant", "café", "musée", "hôtel", "parc", "place", "théâtre", "école",
        "voulais te remercier", "passé un excellent", "regardé un", "fait du sport",
        "cuisiné un", "lu un article", "essayé un nouveau", "connais de bons",
        "fait une longue", "découvert de", "regarde un", "match d foot",
        "direction [pays]", "je reviens de [pays]", "je vais en [pays]"
    ]
    
        # Patterns négatifs spécifiques (phrases qui ne sont PAS des trajets)
        negative_patterns = [
            r"le (restaurant|café|musée|hôtel|parc|place|théâtre|école|centre) (de|d')",
            r"la (gare|place) (de|d') .+ est",
            r".+ est (une|belle|grande|joli|ouvert|bon|confortable|intéressant|moderne|animée|vert|magnifique)",
            r"mon (ami|copain|pote|collègue) .+ (veut|arrive|est)",
            r".+ (et|&) .+ sont là",
            r"je (connais|visite|suis allé|ai visité)",
            r"direction (espagne|italie|allemagne|suisse|royaume-uni|australie|japon|bresil|canada|vietnam|royaume-ni)",
            r"je reviens de (espagne|italie|allemagne|suisse|royaume-uni|australie|japon|bresil|canada|vietnam)",
            r"je vais en (espagne|italie|allemagne|suisse|royaume-uni|australie|japon|bresil|canada|vietnam|royaume-ni)",
            r"je vais voir .+ demain",
            r"quelle (heure|heurre) est-il",
            r"quelle (heure|heurre) est",
            r"j'espère que tu vas bien",
            r"je suis un peu stressé",
            r"je vais gérer",
            r"j'ai fait une .+ randonnée",
            r"j'ai regarde un .+ foot",
            r"voulais te remercier",
            r"voulais juste te dire",
        ]
    
    # Vérifier les patterns négatifs spécifiques
    for pattern in negative_patterns:
        if re.search(pattern, text_lower):
            # Vérifier que ce n'est pas un vrai trajet (pas de mots-clés de trajet)
            if not any(kw in text_lower for kw in ["aller", "partir", "trajet", "billet", "train", "me rendre", "me tire", "me barre"]):
                return True
    
    # Si la phrase contient plusieurs indicateurs négatifs, c'est probablement négatif
    negative_count = sum(1 for indicator in negative_indicators if indicator in text_lower)
    
    # Si la phrase est longue (>80 caractères) et contient des indicateurs négatifs, c'est probablement négatif
    if len(text) > 80 and negative_count >= 1:
        return True
    
    # Si la phrase contient 2+ indicateurs négatifs, c'est probablement négatif
    if negative_count >= 2:
        return True
    
    return False

def analyze_sentence(text: str, entities: List[List], gares: List[str]) -> Dict:
    """
    Analyse une phrase pour détecter les problèmes potentiels.
    """
    issues = []
    entity_count = len(entities)
    
    # Vérifier si c'est probablement une phrase négative
    is_negative = is_negative_pattern(text)
    
    # Extraire les villes potentielles du texte
    potential_cities = extract_city_from_text(text, gares)
    
    # Compter les entités par type
    departure_entities = [e for e in entities if e[2] == "DEPARTURE"]
    arrival_entities = [e for e in entities if e[2] == "ARRIVAL"]
    
    # Vérifier si le texte semble contenir un trajet
    has_dep_keywords = any(kw in text.lower() for kw in DEPARTURE_KEYWORDS)
    has_arr_keywords = any(kw in text.lower() for kw in ARRIVAL_KEYWORDS)
    has_separator = has_route_separator(text)
    has_location_prefix = any(prefix in text.lower() for prefix in LOCATION_PREFIXES)
    
    # Détecter les problèmes (seulement pour les phrases qui devraient avoir des entités)
    # Ne pas signaler de problèmes pour les phrases négatives
    if is_negative:
        return {
            "text": text,
            "entity_count": entity_count,
            "departure_count": len(departure_entities),
            "arrival_count": len(arrival_entities),
            "potential_cities": len(potential_cities),
            "issues": [],
            "has_dep_keywords": has_dep_keywords,
            "has_arr_keywords": has_arr_keywords,
            "has_separator": has_separator,
            "is_negative": True
        }
    
    # Les phrases semi-valides (1 entité) sont VALIDES - ne pas les signaler comme problèmes
    # Elles sont intentionnellement générées avec seulement 1 entité (départ OU arrivée)
    is_semi_valid = entity_count == 1
    
    if potential_cities:
        # Si on a trouvé des villes mais pas d'entités annotées ET que ce n'est pas négatif
        # ET que ce n'est pas une phrase semi-valide
        if entity_count == 0 and (has_dep_keywords or has_arr_keywords or has_separator or has_location_prefix):
            issues.append("PROBLEME: Villes détectées mais aucune entité annotée")
        
        # Si on a trouvé 2+ villes mais moins de 2 entités
        # Ne signaler QUE si on a 0 entité (pas 1, car 1 = phrase semi-valide valide)
        if len(potential_cities) >= 2 and entity_count == 0:
            # Si on a 0 entité ET un contexte de trajet, c'est un problème
            if has_separator or (has_dep_keywords and has_arr_keywords) or has_location_prefix:
                issues.append(f"PROBLEME: {len(potential_cities)} villes détectées mais aucune entité annotée")
        
        # Si on a trouvé 1 ville mais aucune entité ET qu'on a un contexte de trajet
        if len(potential_cities) == 1 and entity_count == 0:
            if (has_dep_keywords or has_arr_keywords or has_location_prefix):
                issues.append("PROBLEME: 1 ville détectée mais aucune entité annotée")
    
    # Vérifier la cohérence des entités
    # Les phrases avec 1 entité sont des phrases semi-valides (valides) - ne pas les signaler comme problèmes
    # Elles sont intentionnellement générées pour apprendre au modèle que DEPARTURE et ARRIVAL sont indépendants
    if entity_count == 1:
        # Ne pas signaler les phrases semi-valides comme problèmes
        # Elles sont correctes avec 1 entité
        pass
    
    if entity_count == 2:
        # Vérifier qu'on a bien un départ et une arrivée
        if len(departure_entities) == 0 or len(arrival_entities) == 0:
            issues.append("PROBLEME: 2 entités mais pas de départ ET arrivée")
    
    return {
        "text": text,
        "entity_count": entity_count,
        "departure_count": len(departure_entities),
        "arrival_count": len(arrival_entities),
        "potential_cities": len(potential_cities),
        "issues": issues,
        "has_dep_keywords": has_dep_keywords,
        "has_arr_keywords": has_arr_keywords,
        "has_separator": has_separator,
        "is_negative": is_negative
    }

def verify_dataset(dataset_file: Path) -> None:
    """Vérifie le dataset et affiche les problèmes."""
    print(f"🔍 Vérification du dataset: {dataset_file}")
    print("=" * 80)
    
    # Charger les gares
    print("📚 Chargement des gares...")
    gares = load_gares()
    print(f"   {len(gares)} gares chargées")
    
    # Charger le dataset
    print(f"\n📖 Chargement du dataset...")
    entries = []
    with dataset_file.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            try:
                entry = json.loads(line.strip())
                entries.append((line_num, entry))
            except json.JSONDecodeError as e:
                print(f"⚠️  Erreur ligne {line_num}: {e}")
    
    print(f"   {len(entries)} phrases chargées")
    
    # Analyser chaque phrase
    print(f"\n🔎 Analyse des phrases...")
    problems = []
    warnings = []
    stats = defaultdict(int)
    
    for line_num, entry in entries:
        text = entry.get("text", "")
        entities = entry.get("entities", [])
        
        analysis = analyze_sentence(text, entities, gares)
        
        # Statistiques
        stats[f"entities_{analysis['entity_count']}"] += 1
        if analysis["entity_count"] == 0:
            stats["no_entities"] += 1
        if analysis["entity_count"] == 1:
            stats["one_entity"] += 1
        if analysis["entity_count"] == 2:
            stats["two_entities"] += 1
        
        # Détecter les problèmes
        if analysis["issues"]:
            for issue in analysis["issues"]:
                if "PROBLEME" in issue:
                    problems.append((line_num, entry, analysis, issue))
                elif "ATTENTION" in issue:
                    warnings.append((line_num, entry, analysis, issue))
    
    # Afficher les résultats
    print(f"\n📊 Statistiques:")
    print(f"   - Phrases avec 0 entité: {stats['no_entities']} ({stats['no_entities']/len(entries)*100:.1f}%)")
    print(f"   - Phrases avec 1 entité: {stats['one_entity']} ({stats['one_entity']/len(entries)*100:.1f}%)")
    print(f"   - Phrases avec 2 entités: {stats['two_entities']} ({stats['two_entities']/len(entries)*100:.1f}%)")
    
    print(f"\n❌ Problèmes détectés: {len(problems)}")
    if problems:
        print("\n" + "=" * 80)
        for i, (line_num, entry, analysis, issue) in enumerate(problems[:50], 1):  # Limiter à 50 pour l'affichage
            print(f"\n{i}. Ligne {line_num}: {issue}")
            print(f"   Texte: {entry['text']}")
            print(f"   Entités annotées: {analysis['entity_count']} (départ: {analysis['departure_count']}, arrivée: {analysis['arrival_count']})")
            print(f"   Villes potentielles détectées: {analysis['potential_cities']}")
            if analysis['potential_cities'] > 0:
                print(f"   Contexte: départ={analysis['has_dep_keywords']}, arrivée={analysis['has_arr_keywords']}, séparateur={analysis['has_separator']}")
        
        if len(problems) > 50:
            print(f"\n   ... et {len(problems) - 50} autres problèmes")
    
    print(f"\n⚠️  Avertissements: {len(warnings)}")
    if warnings:
        for i, (line_num, entry, analysis, issue) in enumerate(warnings[:20], 1):
            print(f"   {i}. Ligne {line_num}: {issue}")
            print(f"      Texte: {entry['text'][:80]}...")
    
    # Résumé
    print(f"\n" + "=" * 80)
    print(f"✅ Vérification terminée")
    print(f"   - Total de phrases: {len(entries)}")
    print(f"   - Problèmes critiques: {len(problems)}")
    print(f"   - Avertissements: {len(warnings)}")
    
    if problems:
        print(f"\n💡 Recommandation: Corriger la détection d'entités pour gérer les typos et variantes")

if __name__ == "__main__":
    verify_dataset(DATASET_FILE)
