#!/usr/bin/env python3
"""
Générateur de dataset pour le modèle NLP d'extraction des destinations.

Génère un dataset JSONL au format Spacy avec des phrases valides et semi-valides.
Chaque ligne contient : {"text": "...", "entities": [[start, end, "LABEL"], ...]}

- Patterns de phrases valides avec exactement 1 départ ET 1 arrivée
- Patterns de phrases semi-valides avec exactement 1 départ OU 1 arrivée (crucial pour la robustesse)
- Basé sur gares-francaises.json pour piocher les gares
- Format de sortie : JSONL Spacy avec annotations DEPARTURE et ARRIVAL
"""

import json
import random
import re
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple, Union

TOTAL_SENTENCES = 20_000  # Plus de phrases pour l'entraînement NLP
# Le générateur est dans dataset/generators/nlp/, on remonte de 3 niveaux pour accéder à la racine
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUTPUT_FILE = PROJECT_ROOT / "dataset" / "nlp" / "json" / "nlp_training_data.jsonl"
GARES_JSON = PROJECT_ROOT / "dataset" / "shared" / "gares-francaises.json"

# --- Data sources ---
def load_gares_from_json(json_path: Path) -> List[Dict[str, any]]:
    """Charge les gares françaises depuis le fichier JSON."""
    try:
        with json_path.open("r", encoding="utf-8") as f:
            gares_data = json.load(f)
        return gares_data
    except Exception as e:
        print(f"⚠️  Erreur lors du chargement de {json_path}: {e}")
        return []

def get_gare_names(gares_data: List[Dict[str, any]]) -> List[str]:
    """Extrait les noms de gares."""
    return [gare["nom"] for gare in gares_data if "nom" in gare]

GARES_DATA = load_gares_from_json(GARES_JSON)
GARE_NAMES = get_gare_names(GARES_DATA)

# Liste des pays (filtrée pour éviter les faux positifs - les pays ne sont pas des gares)
# Note: Les pays peuvent être utilisés dans d'autres contextes mais pas comme entités de trajet
COUNTRIES_REGIONS: List[str] = [
    "Espagne", "Italie", "Allemagne", "Suisse", "Royaume-Uni",
    "Etats-Unis", "Canada", "Japon", "Australie", "Tunisie",
    "Turquie", "Bresil", "Argentine", "Chili", "Mexique", "Chine",
    "Inde", "Thailande", "Vietnam"
]
# Pays retirés car souvent détectés comme villes: "Maroc", "Egypte", "Portugal", "Belgique"

# Noms d'amis qui ressemblent à des villes (pour patterns avec confusion)
# Ces noms peuvent être des prénoms OU des noms de villes/gares
FRIEND_NAMES_LIKE_CITIES: List[str] = [
    # Prénoms masculins (qui sont aussi des noms de gares)
    "albert",      # Gare de la Somme
    "auray",       # Gare du Morbihan
    "charles",     # Gare de Charles-de-Gaulle
    "denis",       # Gare de Saint-Denis
    "etienne",     # Gare de Saint-Étienne
    "gaspard",     # Gare de Saint-Gaspard
    "germain",     # Gare de Saint-Germain-en-Laye
    "grégoire",    # Gare de Saint-Grégoire
    "jacques",     # Gare de Saint-Jacques
    "jean",        # Gare de Saint-Jean / Bordeaux Saint-Jean
    "laurent",     # Gare de Saint-Laurent-du-Var
    "léon",        # Gare de Saint-Léon
    "malo",        # Gare de Saint-Malo
    "nazaire",     # Gare de Saint-Nazaire
    "omer",        # Gare de Saint-Omer
    "quentin",     # Gare de Saint-Quentin
    "rémy",        # Gare de Saint-Rémy
    "sébastien",   # Gare de Saint-Sébastien
    # Prénoms féminins (qui sont aussi des noms de gares)
    "adélaïde",    # Gare de Sainte-Adélaïde
    "anne",        # Gare de Sainte-Anne
    "catherine",   # Gare de Sainte-Catherine
    "colombe",     # Gare de La Garenne-Colombes / Sainte-Colombe
    "florence",    # Gare de Sainte-Florence
    "lourdes",     # Gare de Lourdes
    "lucie",       # Gare de Sainte-Lucie
    "nancy",       # Gare de Nancy-Ville
    "pazanne",     # Gare de Sainte-Pazanne
    "soline",      # Gare de Sainte-Soline
    # Villes pures (qui peuvent être confondues avec des prénoms)
    "agen",        # Gare d'Agen
    "dax",         # Gare de Dax
    "dieppe",      # Gare de Dieppe
    "orange",      # Gare d'Orange
    "sens",        # Gare de Sens
    "valence",     # Gare de Valence-Ville / Valence TGV
    "vichy",        # Gare de Vichy
    # Autres villes communes qui peuvent être des prénoms
    "paris",       # Peut être un prénom
    "lyon",        # Peut être un prénom
    "nice",        # Peut être un prénom
    "nantes",      # Peut être un prénom
    "tours",       # Peut être un prénom
]

TRANSPORTS: List[str] = [
    "train", "tgv", "ter", "bus", "avion", "voiture", "covoiturage", "metro", "tram",
    "bateau", "ferry", "velo", "scooter", "navette", "car", "taxi", "uber"
]

NOISE_TOKENS: List[str] = [
    "stp", "svp", "merci", "please", "plz", "mdr", "lol", "svp c urgent",
    "please asap", "ptdr", "hein", "ok", "svp vite"
]

# Suffixes à ajouter après les villes (pour diversité et éviter que le modèle "mange" les mots après)
CITY_SUFFIXES: List[str] = [
    "rapidement", "svp", "merci", "stp", "please", "plz", "urgent",
    "vite", "asap", "ok", "hein", "c urgent", "svp vite"
]

EMOJIS: List[str] = ["🚆", "✈️", "🚌", "🚍", "🚄", "🚅", "🚇", "🚉", "📍", "🎫", "🧳", "🚢", "🚗"]

ACCENT_MAP = str.maketrans({
    "à": "a", "â": "a", "ä": "a", "á": "a",
    "é": "e", "è": "e", "ê": "e", "ë": "e", "ó": "o", "ò": "o",
    "ï": "i", "î": "i", "ö": "o", "ô": "o", "ü": "u", "û": "u", "ù": "u",
    "ç": "c", "ñ": "n",
    "À": "A", "Â": "A", "Ä": "A", "Á": "A",
    "É": "E", "È": "E", "Ê": "E", "Ë": "E", "Ó": "O", "Ò": "O",
    "Ï": "I", "Î": "I", "Ö": "O", "Ô": "O", "Ü": "U", "Û": "U", "Ù": "U",
    "Ç": "C", "Ñ": "N"
})

# --- Helpers ---
def remove_accents(text: str) -> str:
    return text.translate(ACCENT_MAP)

def pick_gare(exclude: Optional[str] = None) -> str:
    """Sélectionne une gare aléatoire."""
    pool = [gare for gare in GARE_NAMES if gare != exclude]
    return random.choice(pool) if pool else "Paris"

def pick_country() -> str:
    return random.choice(COUNTRIES_REGIONS)

def add_location_variant(gare: str) -> str:
    """Ajoute une variante de localisation (gare, aéroport, etc.)."""
    roll = random.random()
    if roll < 0.20:
        return f"la gare de {gare}"
    if roll < 0.35:
        return f"l'aéroport de {gare}"
    if roll < 0.42:
        return f"centre de {gare}"
    if roll < 0.48:
        return f"port de {gare}"
    return gare

def introduce_typos(text: str) -> str:
    """Introduit des fautes de frappe dans le texte."""
    words = text.split()
    mutated: List[str] = []
    for word in words:
        w = word
        if random.random() < 0.25:
            w = remove_accents(w)
        if len(w) > 4 and random.random() < 0.18:
            idx = random.randint(1, len(w) - 2)
            w = w[:idx] + w[idx + 1 :]
        if len(w) > 3 and random.random() < 0.12:
            idx = random.randint(0, len(w) - 1)
            w = w[:idx] + w[idx] + w[idx:]
        if random.random() < 0.12:
            replacements = {"qu": "k", "ai": "é", "ou": "u", "er": "é"}
            for src, tgt in replacements.items():
                if src in w.lower():
                    w = w.lower().replace(src, tgt, 1)
                    break
        if random.random() < 0.08:
            w = w.lower()
        if random.random() < 0.05:
            w = w.upper()
        mutated.append(w)
    sentence = " ".join(mutated)
    if random.random() < 0.1:
        sentence = sentence.replace(" de ", " d ").replace(" à ", " a ")
    if random.random() < 0.08:
        sentence = sentence.replace(" ", "  ")
    return sentence

def random_case_variation(text: str) -> str:
    roll = random.random()
    if roll < 0.1:
        return text.upper()
    if roll < 0.2:
        return text.lower()
    if roll < 0.35:
        return " ".join(word.capitalize() if random.random() < 0.6 else word.lower() for word in text.split())
    return text

def random_spacing(text: str) -> str:
    if random.random() < 0.12:
        return text.replace(" ", "  ")
    return text

def maybe_add_noise(sentence: str) -> str:
    # Ajouter du bruit après la phrase dans 30% des cas (pour éviter que le modèle "mange" les mots après les villes)
    if random.random() < 0.30:
        noise = random.choice(CITY_SUFFIXES)
        sentence = f"{sentence} {noise}"
    # Ajouter du bruit au début dans 15% des cas (original)
    elif random.random() < 0.15:
        noise = random.choice(NOISE_TOKENS)
        sentence = f"{noise} {sentence}"
    if random.random() < 0.08:
        sentence += random.choice([" !!!", " ??", " ...", "?!"])
    return sentence

def maybe_add_emoji(sentence: str) -> str:
    if random.random() < 0.2:
        emoji = random.choice(EMOJIS)
        if random.random() < 0.5:
            return f"{emoji} {sentence}"
        return f"{sentence} {emoji}"
    return sentence

def random_time_phrase() -> str:
    time_phrases = [
        "à 6h", "à 7h30", "à 8h", "vers 9h", "à midi", "vers 13h15", "à 15h",
        "à 18h", "ce matin", "cet aprem", "ce soir", "dans 10min", "dans 2h",
        "avant 21h", "après 22h"
    ]
    return random.choice(time_phrases)

def random_date_phrase() -> str:
    date_phrases = [
        "aujourd'hui", "demain", "apres-demain", "ce weekend", "la semaine prochaine",
        "lundi", "mardi", "vendredi soir", "samedi matin", "dimanche",
        "le 12/08", "le 05-11", "le 1er mai", "le 24 dec", "dans 3 jours"
    ]
    return random.choice(date_phrases)

def random_transport() -> str:
    return random.choice(TRANSPORTS)

def random_gare_text(gare: str) -> str:
    """Génère un texte avec variantes pour une gare."""
    text = add_location_variant(gare)
    if random.random() < 0.30:
        if text.startswith("la gare de "):
            text = f"la gare de {text[12:].lower()}"
        elif text.startswith("l'aéroport de "):
            text = f"l'aéroport de {text[15:].lower()}"
        elif text.startswith("centre de "):
            text = f"centre de {text[10:].lower()}"
        elif text.startswith("port de "):
            text = f"port de {text[8:].lower()}"
        else:
            text = text.lower()
    if random.random() < 0.55:
        text = introduce_typos(text)
    return text

def pick_friend_name() -> str:
    """Sélectionne un nom d'ami qui ressemble à une ville."""
    return random.choice(FRIEND_NAMES_LIKE_CITIES)

def build_context() -> Dict[str, str]:
    """Construit un contexte avec gares de départ et d'arrivée."""
    dep = pick_gare()
    arr = pick_gare(exclude=dep)
    via = pick_gare(exclude=dep)
    if via == arr:
        via = pick_gare(exclude=dep)
    return {
        "dep": dep,
        "arr": arr,
        "via": via,
        "dep_txt": random_gare_text(dep),
        "arr_txt": random_gare_text(arr),
        "via_txt": random_gare_text(via),
        "country": pick_country(),
        "transport": random_transport(),
        "time": random_time_phrase(),
        "date": random_date_phrase(),
        "friend1": pick_friend_name(),
        "friend2": pick_friend_name(),
    }

def finalize_sentence(sentence: str) -> str:
    """Finalise une phrase avec variations."""
    if random.random() < 0.35:
        sentence = introduce_typos(sentence)
    if random.random() < 0.2:
        sentence = random_case_variation(sentence)
    if random.random() < 0.15:
        sentence = random_spacing(sentence)
    if random.random() < 0.25:
        sentence = maybe_add_noise(sentence)
    if random.random() < 0.2:
        sentence = maybe_add_emoji(sentence)
    sentence = sentence.replace("\n", " ").replace("\r", " ")
    while "  " in sentence:
        sentence = sentence.replace("  ", " ")
    return sentence.strip()

def extract_city_name_from_text(text_variant: str, gare_name: str) -> str:
    """
    Extrait uniquement le nom de ville depuis un texte avec préfixe.
    Gère les variantes avec fautes de frappe (ex: "Centre D" au lieu de "centre de", "ccentre" au lieu de "centre").
    
    Exemples:
        "la gare de Paris" -> "Paris"
        "l'aéroport de Lyon" -> "Lyon"
        "port de Marseille" -> "Marseille"
        "Centre D millaau" -> "millaau"
        "ccentre de Monnerville" -> "Monnerville"
        "céroons" -> "céroons" (pas de préfixe)
        "Paris" -> "Paris"
    """
    # Liste des préfixes à retirer (avec variantes)
    prefixes = [
        "la gare de ", "la gare d ", "la gare ",
        "l'aéroport de ", "l'aéroport d ", "l'aéroportt de ", "l'aéroportt d ",
        "le aéroport de ", "le aéroport d ",
        "centre de ", "centre d ", "Centre D ", "Centre de ", "Centre d ",
        "ccentre de ", "ccentre d ", "ccentre ",  # Typo: double c
        "port de ", "port d ",
        "les gares de ", "les gares d ",
        "les aéroports de ", "les aéroports d ",
    ]
    
    text_lower = text_variant.lower()
    
    # 1. Recherche exacte des préfixes
    for prefix in prefixes:
        prefix_lower = prefix.lower()
        if text_lower.startswith(prefix_lower):
            city_part = text_variant[len(prefix):]
            return city_part.strip()
    
    # 2. Recherche approximative pour gérer les typos dans les préfixes
    # Chercher des patterns comme "ccentre", "aéroportt", etc.
    prefix_patterns = [
        (r"^[cl]'?a\s*gare\s+d[eu]\s+", "la gare de "),
        (r"^[cl]'?aéroportt?\s+d[eu]\s+", "l'aéroport de "),
        (r"^c+entre\s+d[eu]?\s+", "centre de "),
        (r"^port\s+d[eu]?\s+", "port de "),
    ]
    
    for pattern, replacement in prefix_patterns:
        match = re.match(pattern, text_lower)
        if match:
            # Retirer la partie correspondante
            matched_len = len(match.group(0))
            city_part = text_variant[matched_len:]
            return city_part.strip()
    
    # 3. Si le texte commence par un mot qui ressemble à un préfixe mais avec typo
    # Chercher "ccentre", "aéroportt", etc. au début
    if text_lower.startswith("ccentre") or text_lower.startswith("c centre"):
        # Extraire après "ccentre de" ou similaire
        match = re.match(r"^c+entre\s+d[eu]?\s+", text_lower)
        if match:
            city_part = text_variant[len(match.group(0)):]
            return city_part.strip()
    
    # Si pas de préfixe, retourner le texte tel quel (ou le nom de gare si fourni)
    return text_variant if text_variant else gare_name

def find_entity_positions(text: str, entity_text: str, label: str, context_keywords: Optional[List[str]] = None) -> List[Tuple[int, int, str]]:
    """
    Trouve les positions d'une entité dans le texte (insensible à la casse).
    Utilise une recherche flexible pour gérer les fautes de frappe mineures.
    
    Args:
        text: Texte à analyser
        entity_text: Texte de l'entité à chercher (doit être le nom de ville uniquement, pas "la gare de X")
        label: Label de l'entité (DEPARTURE ou ARRIVAL)
        context_keywords: Mots-clés de contexte pour filtrer les occurrences (ex: ["de", "à", "vers"])
                        Si fourni, on ne garde que les occurrences proches de ces mots-clés
    """
    entities = []
    text_lower = text.lower()
    entity_lower = entity_text.lower().strip()
    
    if not entity_lower or len(entity_lower) < 3:
        return entities
    
    # 1. Recherche exacte (insensible à la casse)
    # Utiliser une recherche qui ignore les accents en comparant caractère par caractère
    pattern = re.escape(entity_lower)
    for match in re.finditer(pattern, text_lower):
        start, end = match.start(), match.end()
        
        # Si des mots-clés de contexte sont fournis, vérifier qu'on est dans un contexte de trajet
        if context_keywords:
            context_before = text_lower[max(0, start - 40):start]
            context_after = text_lower[end:min(len(text_lower), end + 40)]
            context = context_before + " " + context_after
            
            has_context = any(keyword.lower() in context for keyword in context_keywords)
            if not has_context:
                continue
        
        entities.append((start, end, label))
    
    # 1b. Si pas trouvé, recherche avec normalisation des accents (pour gérer "Épernay" vs "Epernay")
    if not entities:
        # Normaliser les accents pour la recherche
        def remove_accents_for_search(s: str) -> str:
            """Enlève les accents pour la recherche."""
            replacements = {
                "é": "e", "è": "e", "ê": "e", "ë": "e", "É": "e", "È": "e", "Ê": "e", "Ë": "e",
                "à": "a", "â": "a", "ä": "a", "À": "a", "Â": "a", "Ä": "a",
                "ô": "o", "ö": "o", "Ô": "o", "Ö": "o",
                "ù": "u", "û": "u", "ü": "u", "Ù": "u", "Û": "u", "Ü": "u",
                "ç": "c", "Ç": "c", "ñ": "n", "Ñ": "n",
                "î": "i", "ï": "i", "Î": "i", "Ï": "i"
            }
            result = s.lower()
            for old, new in replacements.items():
                result = result.replace(old, new)
            return result
        
        entity_no_accents = remove_accents_for_search(entity_text)
        text_no_accents = remove_accents_for_search(text)
        
        pattern_no_accents = re.escape(entity_no_accents)
        for match in re.finditer(pattern_no_accents, text_no_accents):
            start, end = match.start(), match.end()
            
            # Vérifier que la longueur correspond (pour éviter les faux positifs)
            if abs(end - start - len(entity_text)) > 2:
                continue
            
            # Si des mots-clés de contexte sont fournis, vérifier qu'on est dans un contexte de trajet
            if context_keywords:
                context_before = text_no_accents[max(0, start - 40):start]
                context_after = text_no_accents[end:min(len(text_no_accents), end + 40)]
                context = context_before + " " + context_after
                
                has_context = any(remove_accents_for_search(keyword) in context for keyword in context_keywords)
                if not has_context:
                    continue
            
            # Utiliser les positions du texte original (approximation)
            entities.append((start, end, label))
            break  # Prendre la première correspondance
    
    # 2. Si pas trouvé, recherche approximative par préfixe (pour gérer les typos)
    if not entities and len(entity_lower) >= 4:
        # Chercher les 4-5 premiers caractères du nom de ville
        prefix = entity_lower[:min(5, len(entity_lower))]
        prefix_pattern = re.escape(prefix)
        
        for match in re.finditer(prefix_pattern, text_lower):
            start = match.start()
            # Estimer la fin basée sur la longueur originale
            estimated_end = start + len(entity_lower)
            
            # Vérifier que la zone correspond approximativement
            if estimated_end <= len(text_lower):
                # Extraire le texte potentiel
                potential_text = text_lower[start:estimated_end]
                
                # Calculer une similarité simple (caractères communs)
                common_chars = sum(1 for i, c in enumerate(potential_text) 
                                 if i < len(entity_lower) and c == entity_lower[i])
                similarity = common_chars / max(len(entity_lower), len(potential_text))
                
                # Accepter si similarité >= 60% et longueur similaire (±2 caractères)
                if similarity >= 0.6 and abs(len(potential_text) - len(entity_lower)) <= 2:
                    # Vérifier le contexte si nécessaire
                    if context_keywords:
                        context_before = text_lower[max(0, start - 40):start]
                        context_after = text_lower[estimated_end:min(len(text_lower), estimated_end + 40)]
                        context = context_before + " " + context_after
                        
                        has_context = any(keyword.lower() in context for keyword in context_keywords)
                        if not has_context:
                            continue
                    
                    # Utiliser la longueur réelle trouvée
                    actual_end = start + len(potential_text)
                    entities.append((start, actual_end, label))
                    break  # Prendre la première correspondance
    
    # 3. Si toujours pas trouvé et que le nom est court, chercher des sous-chaînes
    if not entities and len(entity_lower) >= 6:
        # Pour les noms plus longs, chercher une sous-chaîne de 4-5 caractères au milieu
        mid_start = len(entity_lower) // 2 - 2
        mid_end = mid_start + 4
        if mid_start >= 0 and mid_end <= len(entity_lower):
            substring = entity_lower[mid_start:mid_end]
            substring_pattern = re.escape(substring)
            
            for match in re.finditer(substring_pattern, text_lower):
                start = match.start() - mid_start
                if start < 0:
                    continue
                estimated_end = start + len(entity_lower)
                
                if estimated_end <= len(text_lower):
                    potential_text = text_lower[start:estimated_end]
                    common_chars = sum(1 for i, c in enumerate(potential_text) 
                                     if i < len(entity_lower) and c == entity_lower[i])
                    similarity = common_chars / max(len(entity_lower), len(potential_text))
                    
                    if similarity >= 0.55 and abs(len(potential_text) - len(entity_lower)) <= 3:
                        if context_keywords:
                            context_before = text_lower[max(0, start - 40):start]
                            context_after = text_lower[estimated_end:min(len(text_lower), estimated_end + 40)]
                            context = context_before + " " + context_after
                            
                            has_context = any(keyword.lower() in context for keyword in context_keywords)
                            if not has_context:
                                continue
                        
                        actual_end = start + len(potential_text)
                        entities.append((start, actual_end, label))
                        break
    
    return entities

def extract_entities(text: str, dep_gare: Optional[str], arr_gare: Optional[str], dep_txt: Optional[str], arr_txt: Optional[str], has_explicit_dash: bool = False) -> List[List[Union[int, str]]]:
    """
    Extrait les entités DEPARTURE et ARRIVAL du texte.
    
    IMPORTANT: 
    - Annote uniquement le nom de ville, pas le préfixe ("la gare de", "l'aéroport de").
    - Utilise dep_txt/arr_txt (qui peuvent contenir des fautes) pour la recherche, pas dep_gare/arr_gare (noms exacts).
    - Gère les patterns sans prépositions en ajoutant des mots-clés de contexte supplémentaires.
    
    Exemple: "la gare de Paris" -> seule "Paris" est annotée comme DEPARTURE.
    
    GESTION DES TIRETS: 
    - Si on a dep_gare ET arr_gare ET que le texte contient " - ", c'est probablement deux villes séparées
    - Si une seule ville contient " - " et qu'elle existe comme gare composée, c'est un nom composé (1 entité)
    - Pour les listes "Ville1 - Ville2 - Ville3 - Ville4", seule la première est DEPARTURE et la dernière est ARRIVAL.
    """
    entities = []
    
    # Détecter si le texte contient un pattern "Ville1 - Ville2" (deux villes séparées)
    # Si dep_gare et arr_gare sont différents ET que le texte contient " - ", c'est deux villes
    # OU si has_explicit_dash est True (le pattern utilise explicitement le format "Ville1 - Ville2")
    has_dash_pattern = has_explicit_dash or (" - " in text and dep_gare and arr_gare and dep_gare != arr_gare)
    
    # Mots-clés de contexte pour départ (pour éviter d'annoter les noms d'amis)
    # Ajout de mots-clés supplémentaires pour les patterns sans prépositions
    dep_context_keywords = [
        "de", "depuis", "depui", "partir", "quitter", "sortir", "-",
        "bagages", "trajet", "billet", "voyage", "aller", "option", "tarif",
        "connection", "direct", "correspondances", "horaires", "prix"
    ]
    # Mots-clés de contexte pour arrivée
    arr_context_keywords = [
        "à", "a", "vers", "pour", "aller", "rendre", "arriver", "-", "→",
        "bagages", "trajet", "billet", "voyage", "option", "tarif",
        "connection", "direct", "correspondances", "horaires", "prix"
    ]
    
    # Chercher le départ
    if dep_gare and dep_txt:
        # IMPORTANT: Utiliser dep_txt (qui peut contenir des fautes) pour extraire le nom de ville
        # car c'est ce qui apparaît dans le texte, pas le nom exact dep_gare
        city_name = extract_city_name_from_text(dep_txt, dep_gare)
        
        # GESTION DES TIRETS: Si la ville contient " - " (tiret avec espaces)
        # IMPORTANT: 
        # - Certaines gares ont des noms composés avec tirets (ex: "Schirmeck - La Broque") = 1 entité
        # - Certains patterns utilisent "Ville1 - Ville2" = 2 entités séparées
        # On doit détecter les deux cas
        if " - " in city_name:
            # Si on a un pattern avec deux villes séparées (has_dash_pattern), chercher la première partie
            if has_dash_pattern:
                # C'est deux villes séparées : chercher la première comme DEPARTURE
                parts = city_name.split(" - ")
                if parts:
                    first_part = parts[0].strip()
                    if first_part and len(first_part) >= 3:
                        dep_entities = find_entity_positions(text, first_part, "DEPARTURE", dep_context_keywords)
                        entities.extend(dep_entities)
            else:
                # C'est probablement un nom de gare composé : chercher le nom complet
                full_name_entities = find_entity_positions(text, city_name, "DEPARTURE", dep_context_keywords)
                if full_name_entities:
                    entities.extend(full_name_entities)
                else:
                    # Si le nom complet n'est pas trouvé (typos), essayer de trouver la première partie
                    parts = city_name.split(" - ")
                    if parts:
                        first_part = parts[0].strip()
                        if first_part and len(first_part) >= 3:
                            dep_entities = find_entity_positions(text, first_part, "DEPARTURE", dep_context_keywords)
                            entities.extend(dep_entities)
        else:
            # Chercher le nom de ville dans le texte
            # Essayer d'abord avec le nom exact depuis dep_txt
            dep_entities = find_entity_positions(text, city_name, "DEPARTURE", dep_context_keywords)
            # Si pas trouvé, essayer avec le nom exact de la gare (fallback)
            if not dep_entities and dep_gare:
                dep_entities = find_entity_positions(text, dep_gare, "DEPARTURE", dep_context_keywords)
            # Si toujours pas trouvé, essayer une recherche plus permissive (sans contexte strict)
            if not dep_entities:
                # Recherche sans filtrage par contexte (pour gérer les cas où le contexte est mal détecté)
                dep_entities_no_context = find_entity_positions(text, city_name, "DEPARTURE", None)
                if dep_entities_no_context:
                    # Filtrer manuellement : garder seulement si on a un mot-clé de départ à proximité
                    filtered = []
                    for start, end, label in dep_entities_no_context:
                        context_before = text[max(0, start - 40):start].lower()
                        context_after = text[end:min(len(text), end + 40)].lower()
                        context = context_before + " " + context_after
                        if any(kw in context for kw in dep_context_keywords):
                            filtered.append((start, end, label))
                    dep_entities = filtered
            entities.extend(dep_entities)
    
    # Chercher l'arrivée si présente
    if arr_gare and arr_txt:
        # IMPORTANT: Utiliser arr_txt (qui peut contenir des fautes) pour extraire le nom de ville
        city_name = extract_city_name_from_text(arr_txt, arr_gare)
        
        # GESTION DES TIRETS: Si la ville contient " - " (tiret avec espaces)
        # IMPORTANT: 
        # - Certaines gares ont des noms composés avec tirets (ex: "Schirmeck - La Broque") = 1 entité
        # - Certains patterns utilisent "Ville1 - Ville2" = 2 entités séparées
        # On doit détecter les deux cas
        if " - " in city_name:
            # Si on a un pattern avec deux villes séparées (has_dash_pattern), chercher la dernière partie
            if has_dash_pattern:
                # C'est deux villes séparées : chercher la dernière comme ARRIVAL
                parts = city_name.split(" - ")
                if parts:
                    last_part = parts[-1].strip()
                    if last_part and len(last_part) >= 3:
                        arr_entities = find_entity_positions(text, last_part, "ARRIVAL", arr_context_keywords)
                        entities.extend(arr_entities)
            else:
                # Vérifier si arr_gare contient " - " (c'est peut-être deux villes combinées)
                # Si arr_gare ne contient pas " - " mais arr_txt oui, c'est probablement deux villes
                # OU si has_explicit_dash est True, c'est un pattern avec deux villes séparées
                if has_explicit_dash or (" - " not in arr_gare and " - " in arr_txt):
                    # C'est probablement deux villes combinées dans arr_txt : chercher la dernière partie
                    parts = city_name.split(" - ")
                    if parts:
                        last_part = parts[-1].strip()
                        if last_part and len(last_part) >= 3:
                            arr_entities = find_entity_positions(text, last_part, "ARRIVAL", arr_context_keywords)
                            entities.extend(arr_entities)
                else:
                    # C'est probablement un nom de gare composé : chercher le nom complet
                    full_name_entities = find_entity_positions(text, city_name, "ARRIVAL", arr_context_keywords)
                    if full_name_entities:
                        entities.extend(full_name_entities)
                    else:
                        # Si le nom complet n'est pas trouvé (typos), essayer de trouver la dernière partie
                        parts = city_name.split(" - ")
                        if parts:
                            last_part = parts[-1].strip()
                            if last_part and len(last_part) >= 3:
                                arr_entities = find_entity_positions(text, last_part, "ARRIVAL", arr_context_keywords)
                                entities.extend(arr_entities)
        else:
            # Chercher le nom de ville dans le texte
            # Essayer d'abord avec le nom exact depuis arr_txt
            arr_entities = find_entity_positions(text, city_name, "ARRIVAL", arr_context_keywords)
            # Si pas trouvé, essayer avec le nom exact de la gare (fallback)
            if not arr_entities and arr_gare:
                arr_entities = find_entity_positions(text, arr_gare, "ARRIVAL", arr_context_keywords)
            # Si toujours pas trouvé, essayer une recherche plus permissive (sans contexte strict)
            if not arr_entities:
                # Recherche sans filtrage par contexte (pour gérer les cas où le contexte est mal détecté)
                arr_entities_no_context = find_entity_positions(text, city_name, "ARRIVAL", None)
                if arr_entities_no_context:
                    # Filtrer manuellement : garder seulement si on a un mot-clé d'arrivée à proximité
                    filtered = []
                    for start, end, label in arr_entities_no_context:
                        context_before = text[max(0, start - 40):start].lower()
                        context_after = text[end:min(len(text), end + 40)].lower()
                        context = context_before + " " + context_after
                        if any(kw in context for kw in arr_context_keywords):
                            filtered.append((start, end, label))
                    arr_entities = filtered
            entities.extend(arr_entities)
    
    # Trier par position de début
    entities.sort(key=lambda x: x[0])
    
    # Convertir en format Spacy [[start, end, "LABEL"], ...]
    return [[start, end, label] for start, end, label in entities]

# --- Sentence patterns (patterns valides avec exactement 1 départ ET 1 arrivée) ---
PatternFunc = Callable[[Dict[str, str]], Tuple[str, str, Optional[str], str, Optional[str]]]
# Retourne: (sentence, dep_gare, arr_gare, dep_txt, arr_txt)
# IMPORTANT: Tous les patterns doivent avoir dep_gare != None ET arr_gare != None

# --- Sentence patterns semi-valides (départ OU arrivée uniquement) ---
SemiValidPatternFunc = Callable[[Dict[str, str]], Tuple[str, Optional[str], Optional[str], Optional[str], Optional[str]]]
# Retourne: (sentence, dep_gare, arr_gare, dep_txt, arr_txt)
# IMPORTANT: Les patterns semi-valides ont soit dep_gare != None (arr_gare = None), soit arr_gare != None (dep_gare = None)

def nlp_patterns() -> List[PatternFunc]:
    """Retourne les patterns pour générer des phrases valides avec exactement 1 départ ET 1 arrivée."""
    return [
        # 1-10: Formes standard
        lambda c: (f"Je vais de {c['dep_txt']} à {c['arr_txt']}.", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Pour aller à {c['arr_txt']}, je pars de {c['dep_txt']}.", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je bouge de {c['dep_txt']} à {c['arr_txt']}.", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je descends sur {c['arr_txt']} depuis {c['dep_txt']}.", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Jvé d {c['dep_txt']} a {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je veu alé de {c['dep_txt']} a {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je pars de {c['dep_txt']} {c['time']} pour {c['arr_txt']} {c['date']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"En {c['transport']} de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        
        # 11-20: Phrases longues avec contexte
        lambda c: (f"Salut, je dois aller de {c['dep_txt']} à {c['arr_txt']} {c['date']} {c['time']} pour un rdv important", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Bonjour, je voudrais partir de {c['dep_txt']} vers {c['arr_txt']} {c['date']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"{c['dep_txt']} → {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Comment aller de {c['dep_txt']} à {c['arr_txt']} ?", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"🚆 {c['dep_txt']} → {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Si je pars de {c['dep_txt']}, je vais à {c['arr_txt']} ?", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"{c['dep_txt']} vers {c['arr_txt']} ?", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je dois me rendre de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je veux aller de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je cherche un trajet de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        
        # 21-30: Places spécifiques (gare, aéroport)
        lambda c: (f"Je pars de la gare de {c['dep']} pour {c['arr_txt']}", c["dep"], c["arr"], f"la gare de {c['dep']}", c["arr_txt"]),
        lambda c: (f"Je vais partir de {c['dep_txt']} pour {c['arr_txt']} {c['date']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"J'ai besoin d'aller de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je veux me rendre de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je dois me déplacer de {c['dep_txt']} vers {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"J'aimerais voyager de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je recherche un itinéraire de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je cherche comment aller de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je souhaite me rendre de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        
        # 31-40: Questions
        lambda c: (f"Quel est le trajet {c['dep_txt']} {c['arr_txt']} ?", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Comment me rendre de {c['dep_txt']} à {c['arr_txt']} ?", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Quel train pour aller de {c['dep_txt']} à {c['arr_txt']} ?", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Y a-t-il un train {c['dep_txt']} {c['arr_txt']} ?", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Quel est le prix d'un billet {c['dep_txt']} {c['arr_txt']} ?", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Quelle est la durée du trajet {c['dep_txt']} {c['arr_txt']} ?", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Quels sont les horaires {c['dep_txt']} {c['arr_txt']} ?", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Quel est le premier train {c['dep_txt']} {c['arr_txt']} ?", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Quel est le dernier train {c['dep_txt']} {c['arr_txt']} ?", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Y a-t-il des trains de nuit {c['dep_txt']} {c['arr_txt']} ?", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        
        # 41-50: Billets et tarifs
        lambda c: (f"Billet {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Un billet pour {c['arr_txt']} depuis {c['dep_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je veux un billet {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Combien coûte un billet {c['dep_txt']} {c['arr_txt']} ?", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Tarif {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Prix d'un billet {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Aller simple {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Aller-retour {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Première classe {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Deuxième classe {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        
        # 51-60: Patterns supplémentaires avec départ et arrivée
        lambda c: (f"Je dois partir de {c['dep_txt']} pour arriver à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je souhaite partir de {c['dep_txt']} et arriver à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je voudrais partir de {c['dep_txt']} pour me rendre à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je dois quitter {c['dep_txt']} pour aller à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je veux quitter {c['dep_txt']} et me rendre à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je dois partir de {c['dep_txt']} en direction de {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je souhaite partir de {c['dep_txt']} en direction de {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je voudrais partir de {c['dep_txt']} en direction de {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je dois quitter {c['dep_txt']} pour me rendre à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je veux quitter {c['dep_txt']} pour aller à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        
        # 61-70: Conversationnels
        lambda c: (f"Salut, j'ai un rdv à {c['arr_txt']} {c['date']}, je pars de {c['dep_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Bonjour, je dois aller à {c['arr_txt']} depuis {c['dep_txt']} {c['time']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Hey, je cherche un train {c['dep_txt']} {c['arr_txt']} {c['date']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Coucou, j'ai besoin d'aller de {c['dep_txt']} à {c['arr_txt']} rapidement", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Salut, trajet urgent {c['dep_txt']} {c['arr_txt']} {c['time']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Bonjour, je dois me rendre à {c['arr_txt']} en partant de {c['dep_txt']} {c['date']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Salut, j'ai un rendez-vous à {c['arr_txt']}, je suis à {c['dep_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Hey, je veux aller de {c['dep_txt']} à {c['arr_txt']} {c['date']} {c['time']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Bonjour, je dois partir de {c['dep_txt']} pour {c['arr_txt']} {c['date']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Salut, un billet {c['dep_txt']} {c['arr_txt']} {c['date']} stp", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        
        # 71-80: Patterns supplémentaires avec départ et arrivée
        lambda c: (f"Je dois me déplacer de {c['dep_txt']} jusqu'à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je veux me déplacer de {c['dep_txt']} jusqu'à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je dois voyager de {c['dep_txt']} jusqu'à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je veux voyager de {c['dep_txt']} jusqu'à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je dois me rendre de {c['dep_txt']} jusqu'à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je veux me rendre de {c['dep_txt']} jusqu'à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je dois partir de {c['dep_txt']} pour arriver à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je veux partir de {c['dep_txt']} pour arriver à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je dois quitter {c['dep_txt']} pour arriver à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je veux quitter {c['dep_txt']} pour arriver à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        
        # 81-90: Avec beaucoup de typos
        lambda c: (f"Je veu alé de {c['dep_txt']} a {c['arr_txt']} svp c urgent", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"depui {c['dep_txt']} vers {c['arr_txt']} stp vite", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"trajet {c['dep_txt']} {c['arr_txt']} urgent please", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"je pars depui {c['dep_txt']} pour {c['arr_txt']} demain", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"besoin d'aller de {c['dep_txt']} a {c['arr_txt']} rapidement", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"je veu parttir de {c['dep_txt']} vers {c['arr_txt']} ce soir", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"trajet depui {c['dep_txt']} arr {c['arr_txt']} urgent", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"je dois aller de {c['dep_txt']} jusqu'a {c['arr_txt']} demain", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"aller depui {c['dep_txt']} a {c['arr_txt']} svp", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"je me tire de {c['dep_txt']} pour {c['arr_txt']} rapidement", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        
        # 91-100: Expressions françaises
        lambda c: (f"Je me casse de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je me barre de {c['dep_txt']} pour {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je me taille de {c['dep_txt']} vers {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je me tire de {c['dep_txt']} pour {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je bouge de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je me déplace de {c['dep_txt']} vers {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je me rends de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je file de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je me pointe à {c['arr_txt']} depuis {c['dep_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je me dirige vers {c['arr_txt']} en partant de {c['dep_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        
        # 101-110: Avec transports spécifiques
        lambda c: (f"En TGV de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"En TER de {c['dep_txt']} vers {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Par le train de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"En bus de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"En avion de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"En voiture de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"En covoiturage de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Par le métro de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"En tram de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"En RER de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        
        # 111-120: Avec horaires
        lambda c: (f"Train {c['dep_txt']} {c['arr_txt']} {c['time']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Billet {c['dep_txt']} {c['arr_txt']} {c['date']} {c['time']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Trajet {c['dep_txt']} {c['arr_txt']} {c['date']} {c['time']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Aller {c['dep_txt']} {c['arr_txt']} {c['time']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je pars {c['time']} de {c['dep_txt']} pour {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je vais {c['time']} de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Train {c['date']} {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Billet {c['date']} {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Trajet {c['date']} {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Aller {c['date']} {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        
        # 121-130: Avec bagages et options
        lambda c: (f"Voyage avec bagages {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Trajet avec vélo {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Option économique {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Option confort {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Tarif étudiant {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Tarif senior {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Tarif réduit {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Connection {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Trajet direct {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Éviter les correspondances {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        
        # 131-140: Formes impératives et demandes
        lambda c: (f"Trouve-moi un trajet {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Propose-moi un trajet {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Donne-moi un billet {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Cherche un train {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Trouve un billet {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Pourriez-vous me trouver un train {c['dep_txt']} {c['arr_txt']} ?", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Serait-il possible d'avoir un billet {c['dep_txt']} {c['arr_txt']} ?", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je vous prie de bien vouloir me donner un trajet {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Pourriez-vous m'aider à trouver un train {c['dep_txt']} {c['arr_txt']} ?", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Seriez-vous en mesure de me trouver un billet {c['dep_txt']} {c['arr_txt']} ?", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        
        # 141-150: Variantes avec prépositions et connecteurs
        lambda c: (f"De {c['dep_txt']} jusqu'à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Entre {c['dep_txt']} et {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Depuis {c['dep_txt']} jusqu'à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Partir de {c['dep_txt']} et arriver à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Aller de {c['dep_txt']} jusqu'à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Voyager de {c['dep_txt']} jusqu'à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Se rendre de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Partir depuis {c['dep_txt']} pour aller à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Aller depuis {c['dep_txt']} jusqu'à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Voyager depuis {c['dep_txt']} jusqu'à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        
        # 151-165: Patterns avec noms d'amis qui ressemblent à des villes (variations variées)
        lambda c: (f"Avec mes amis {c['friend1']} et {c['friend2']}, je voudrais aller de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je vais avec mon ami {c['friend1']} de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Mes amis {c['friend1']} et {c['friend2']} veulent aller de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Mon copain {c['friend1']} et moi, on part de {c['dep_txt']} pour {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je voyage avec {c['friend1']} depuis {c['dep_txt']} jusqu'à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"En compagnie de {c['friend1']} et {c['friend2']}, je me rends de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Mon pote {c['friend1']} m'accompagne de {c['dep_txt']} vers {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je pars avec {c['friend1']} de {c['dep_txt']} pour rejoindre {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Accompagné de mes amis {c['friend1']} et {c['friend2']}, je vais de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je fais le trajet avec {c['friend1']} qui part de {c['dep_txt']} et arrive à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Mon ami {c['friend1']} et sa copine {c['friend2']} partent de {c['dep_txt']} en direction de {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je rejoins {c['friend1']} à {c['dep_txt']} et on va ensemble à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Mon meilleur pote {c['friend1']} veut qu'on aille de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je me déplace avec {c['friend1']} et {c['friend2']} de {c['dep_txt']} vers {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Mon collègue {c['friend1']} et moi devons nous rendre de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        
        # 166-180: Patterns avec format "Ville - Ville" (tiret) - variations variées
        lambda c: (f"Donne moi le voyage le plus optimisé pour faire le voyage suivant : {c['dep']} - {c['arr']}", c["dep"], c["arr"], c["dep"], c["arr"]),
        lambda c: (f"Donne-moi le voyage le plus optimisé pour faire le voyage suivant : {c['dep']} - {c['arr']}", c["dep"], c["arr"], c["dep"], c["arr"]),
        lambda c: (f"Trajet {c['dep']} - {c['arr']}", c["dep"], c["arr"], c["dep"], c["arr"]),
        lambda c: (f"Je veux aller de {c['dep']} - {c['arr']}", c["dep"], c["arr"], c["dep"], c["arr"]),
        lambda c: (f"Je cherche le meilleur itinéraire pour {c['dep']} - {c['arr']}", c["dep"], c["arr"], c["dep"], c["arr"]),
        lambda c: (f"Quel est le trajet optimal entre {c['dep']} - {c['arr']} ?", c["dep"], c["arr"], c["dep"], c["arr"]),
        lambda c: (f"Billet pour le trajet {c['dep']} - {c['arr']}", c["dep"], c["arr"], c["dep"], c["arr"]),
        lambda c: (f"Je souhaite voyager de {c['dep']} - {c['arr']}", c["dep"], c["arr"], c["dep"], c["arr"]),
        lambda c: (f"Horaires pour {c['dep']} - {c['arr']}", c["dep"], c["arr"], c["dep"], c["arr"]),
        lambda c: (f"Prix d'un billet {c['dep']} - {c['arr']}", c["dep"], c["arr"], c["dep"], c["arr"]),
        lambda c: (f"Je recherche un itinéraire {c['dep']} - {c['arr']}", c["dep"], c["arr"], c["dep"], c["arr"]),
        lambda c: (f"Quel serait le meilleur trajet {c['dep']} - {c['arr']} ?", c["dep"], c["arr"], c["dep"], c["arr"]),
        lambda c: (f"Je dois me rendre de {c['dep']} - {c['arr']}", c["dep"], c["arr"], c["dep"], c["arr"]),
        lambda c: (f"Trouve-moi un billet {c['dep']} - {c['arr']}", c["dep"], c["arr"], c["dep"], c["arr"]),
        lambda c: (f"Je voudrais connaître les horaires {c['dep']} - {c['arr']}", c["dep"], c["arr"], c["dep"], c["arr"]),
        
        # 181-185: Patterns avec format "Ville -> Ville" (flèche)
        lambda c: (f"Trajet {c['dep_txt']} -> {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je vais de {c['dep_txt']} -> {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Billet {c['dep_txt']} -> {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Aller de {c['dep_txt']} -> {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Voyage {c['dep_txt']} -> {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        
        # 186-190: Patterns "Trajet Ville Ville" (sans préposition)
        lambda c: (f"Trajet {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Billet {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Train {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Aller {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Voyage {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        
        # 191-195: Patterns avec "Donne moi un trajet Sncf de Ville à Ville"
        lambda c: (f"Donne moi un trajet Sncf de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Donne-moi un trajet Sncf de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je veux un trajet Sncf de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Trouve-moi un trajet Sncf de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Cherche un trajet Sncf de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
    ]

def nlp_patterns_semi_valid() -> List[SemiValidPatternFunc]:
    """
    Retourne les patterns pour générer des phrases semi-valides (départ OU arrivée uniquement).
    Ces patterns sont cruciaux pour la robustesse : ils apprennent au modèle que DEPARTURE et ARRIVAL sont indépendants.
    """
    return [
        # Patterns avec DÉPART uniquement (arrivée = None)
        lambda c: (f"Je pars de {c['dep_txt']}.", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Je quitte {c['dep_txt']}.", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Je sors de {c['dep_txt']}.", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Je me tire de {c['dep_txt']}.", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Je me barre de {c['dep_txt']}.", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Je me casse de {c['dep_txt']}.", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Je pars depuis {c['dep_txt']} {c['time']}.", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Je quitte {c['dep_txt']} {c['date']}.", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Je sors de {c['dep_txt']} {c['time']} {c['date']}.", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Je pars de la gare de {c['dep']}.", c["dep"], None, f"la gare de {c['dep']}", None),
        lambda c: (f"Je quitte l'aéroport de {c['dep']}.", c["dep"], None, f"l'aéroport de {c['dep']}", None),
        lambda c: (f"Je me tire de {c['dep_txt']} rapidement.", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Je me barre de {c['dep_txt']} maintenant.", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Je pars de {c['dep_txt']} {c['time']}.", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Je quitte {c['dep_txt']} {c['date']} {c['time']}.", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Je sors de {c['dep_txt']} pour un rdv.", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Je pars de {c['dep_txt']} en {c['transport']}.", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Je quitte {c['dep_txt']} avec mes bagages.", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Je me tire de {c['dep_txt']} svp.", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Je pars de {c['dep_txt']} urgent.", c["dep"], None, c["dep_txt"], None),
        
        # Patterns avec ARRIVÉE uniquement (départ = None)
        lambda c: (f"Je voudrais un billet pour {c['arr_txt']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je veux aller à {c['arr_txt']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je dois me rendre à {c['arr_txt']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je vais à {c['arr_txt']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je me pointe à {c['arr_txt']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je me dirige vers {c['arr_txt']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je voudrais un billet pour {c['arr_txt']} {c['date']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je veux aller à {c['arr_txt']} {c['time']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je dois me rendre à {c['arr_txt']} {c['date']} {c['time']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je vais à la gare de {c['arr']}.", None, c["arr"], None, f"la gare de {c['arr']}"),
        lambda c: (f"Je me rends à l'aéroport de {c['arr']}.", None, c["arr"], None, f"l'aéroport de {c['arr']}"),
        lambda c: (f"Je voudrais un billet pour {c['arr_txt']} rapidement.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je veux aller à {c['arr_txt']} maintenant.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je dois me rendre à {c['arr_txt']} {c['time']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je vais à {c['arr_txt']} {c['date']} {c['time']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je me pointe à {c['arr_txt']} pour un rdv.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je me dirige vers {c['arr_txt']} en {c['transport']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je voudrais un billet pour {c['arr_txt']} avec bagages.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je veux aller à {c['arr_txt']} svp.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je dois me rendre à {c['arr_txt']} urgent.", None, c["arr"], None, c["arr_txt"]),
        
        # Patterns avec DÉPART uniquement - variantes conversationnelles
        lambda c: (f"Salut, je pars de {c['dep_txt']}.", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Bonjour, je quitte {c['dep_txt']} {c['date']}.", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Hey, je me tire de {c['dep_txt']} {c['time']}.", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Coucou, je pars de {c['dep_txt']} maintenant.", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Salut, je quitte {c['dep_txt']} rapidement.", c["dep"], None, c["dep_txt"], None),
        
        # Patterns avec ARRIVÉE uniquement - variantes conversationnelles
        lambda c: (f"Salut, je voudrais un billet pour {c['arr_txt']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Bonjour, je veux aller à {c['arr_txt']} {c['date']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Hey, je dois me rendre à {c['arr_txt']} {c['time']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Coucou, je vais à {c['arr_txt']} maintenant.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Salut, je me pointe à {c['arr_txt']} rapidement.", None, c["arr"], None, c["arr_txt"]),
        
        # Patterns avec DÉPART uniquement - questions
        lambda c: (f"Quel train part de {c['dep_txt']} ?", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Quels sont les horaires depuis {c['dep_txt']} ?", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Y a-t-il un train qui part de {c['dep_txt']} ?", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Quel est le prochain train depuis {c['dep_txt']} ?", c["dep"], None, c["dep_txt"], None),
        
        # Patterns avec ARRIVÉE uniquement - questions
        lambda c: (f"Quel train va à {c['arr_txt']} ?", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Quels sont les horaires pour {c['arr_txt']} ?", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Y a-t-il un train pour {c['arr_txt']} ?", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Quel est le prochain train vers {c['arr_txt']} ?", None, c["arr"], None, c["arr_txt"]),
        
        # Patterns avec DÉPART uniquement - typos
        lambda c: (f"Je pars depui {c['dep_txt']}.", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Je quitte {c['dep_txt']} stp.", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Je me tire de {c['dep_txt']} vite.", c["dep"], None, c["dep_txt"], None),
        lambda c: (f"Je pars de {c['dep_txt']} urgent please.", c["dep"], None, c["dep_txt"], None),
        
        # Patterns avec ARRIVÉE uniquement - typos
        lambda c: (f"Je veu alé a {c['arr_txt']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je voudrais un billet pour {c['arr_txt']} stp.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je dois me rendre a {c['arr_txt']} vite.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je veux aller a {c['arr_txt']} urgent please.", None, c["arr"], None, c["arr_txt"]),
    ]

# --- Generation ---
def adjust_entity_positions(original_text: str, modified_text: str, entities: List[List[Union[int, str]]]) -> List[List[Union[int, str]]]:
    """
    Ajuste les positions des entités après modification du texte.
    
    Stratégie améliorée: 
    1. Cherche d'abord l'entité exacte (insensible à la casse)
    2. Si pas trouvée, cherche une sous-chaîne similaire (pour gérer les fautes de frappe)
    3. Utilise une zone de recherche élargie pour plus de flexibilité
    """
    adjusted_entities = []
    
    for start, end, label in entities:
        # Extraire le texte de l'entité depuis le texte original
        entity_text = original_text[start:end]
        entity_lower = entity_text.lower().strip()
        
        # Ignorer les entités trop courtes (probablement des erreurs)
        if len(entity_lower) < 3:
            continue
        
        # Chercher cette entité dans le texte modifié (insensible à la casse)
        # Zone de recherche élargie autour de la position originale
        search_start = max(0, start - 30)
        search_end = min(len(modified_text), end + 50)
        search_zone = modified_text[search_start:search_end]
        search_lower = search_zone.lower()
        
        found = False
        
        # 1. Recherche exacte (insensible à la casse)
        idx = search_lower.find(entity_lower)
        if idx != -1:
            # Vérifier que c'est un mot complet (pas une sous-chaîne)
            before = search_zone[max(0, idx-1):idx] if idx > 0 else ""
            after = search_zone[idx+len(entity_lower):idx+len(entity_lower)+1] if idx+len(entity_lower) < len(search_zone) else ""
            
            # Accepter si c'est au début/fin de la zone ou entouré de caractères non-alphanumériques
            if (idx == 0 or not before[-1].isalnum()) and (idx+len(entity_lower) == len(search_zone) or not after[0].isalnum()):
                new_start = search_start + idx
                new_end = new_start + len(entity_text)
                adjusted_entities.append([new_start, new_end, label])
                found = True
        
        # 2. Si pas trouvé, recherche par sous-chaîne (pour gérer les fautes de frappe)
        if not found:
            # Chercher une sous-chaîne qui commence par les 3-4 premiers caractères
            if len(entity_lower) >= 4:
                prefix = entity_lower[:4]
                idx = search_lower.find(prefix)
                if idx != -1:
                    # Vérifier que la longueur est similaire (tolérance de ±2 caractères)
                    potential_end = idx + len(entity_lower)
                    if potential_end <= len(search_zone):
                        # Vérifier que c'est un mot complet
                        before = search_zone[max(0, idx-1):idx] if idx > 0 else ""
                        after = search_zone[potential_end:potential_end+1] if potential_end < len(search_zone) else ""
                        if (idx == 0 or not before[-1].isalnum()) and (potential_end == len(search_zone) or not after[0].isalnum()):
                            new_start = search_start + idx
                            # Utiliser la longueur originale pour l'end
                            new_end = new_start + len(entity_text)
                            adjusted_entities.append([new_start, new_end, label])
                            found = True
        
        # 3. Fallback: chercher dans tout le texte (insensible à la casse)
        if not found:
            idx = modified_text.lower().find(entity_lower)
            if idx != -1:
                adjusted_entities.append([idx, idx + len(entity_text), label])
                found = True
        
        # Si toujours pas trouvé, on ignore cette entité
        # (elle a peut-être été modifiée au point d'être méconnaissable)
    
    return adjusted_entities

def generate_nlp_sentence(pattern_func: PatternFunc, expected_entities: int = 2) -> Dict[str, any]:
    """
    Génère une phrase avec annotations pour le NLP.
    
    IMPORTANT: Valide que la phrase générée contient exactement le nombre d'entités attendues.
    
    Args:
        pattern_func: Fonction de pattern qui génère la phrase
        expected_entities: Nombre d'entités attendues (2 pour phrases complètes, 1 pour semi-valides)
    """
    context = build_context()
    sentence, dep_gare, arr_gare, dep_txt, arr_txt = pattern_func(context)
    
    # Validation: s'assurer qu'on a exactement 1 départ ET 1 arrivée pour les phrases complètes
    if expected_entities == 2:
        if not dep_gare or not arr_gare:
            # Si le pattern ne fournit pas dep_gare et arr_gare, on ne peut pas générer une phrase valide
            # Retourner None pour que le générateur réessaie
            return None
    
    # Détecter si le pattern utilise explicitement le format "Ville1 - Ville2"
    # Si dep_txt ou arr_txt contient " - " ET que dep_gare et arr_gare sont différents,
    # c'est probablement un pattern avec deux villes séparées
    has_explicit_dash = (" - " in (dep_txt or "") or " - " in (arr_txt or "")) and dep_gare and arr_gare and dep_gare != arr_gare
    
    # Extraire les entités sur le texte original (avant modifications)
    # pour que extract_city_name_from_text() puisse reconnaître les préfixes
    # Passer l'information sur le pattern avec tiret explicite
    entities = extract_entities(sentence, dep_gare, arr_gare, dep_txt, arr_txt, has_explicit_dash=has_explicit_dash)
    
    # Sauvegarder le texte original pour ajuster les positions
    original_text = sentence
    
    # Finaliser la phrase (ajoute du bruit après les villes dans 30% des cas via maybe_add_noise)
    sentence = finalize_sentence(sentence)
    
    # Ajuster les positions des entités après les modifications du texte
    if original_text != sentence:
        entities = adjust_entity_positions(original_text, sentence, entities)
    
    # Validation finale: compter les entités DEPARTURE et ARRIVAL
    departure_count = sum(1 for e in entities if e[2] == "DEPARTURE")
    arrival_count = sum(1 for e in entities if e[2] == "ARRIVAL")
    total_entities = len(entities)
    
    # VALIDATION STRICTE: Vérifier le nombre exact d'entités attendues
    if total_entities != expected_entities:
        # Si le nombre d'entités détectées ne correspond pas au nombre attendu, retourner None
        return None
    
    # Pour les phrases complètes (2 entités), vérifier qu'on a exactement 1 départ ET 1 arrivée
    if expected_entities == 2:
        if departure_count != 1 or arrival_count != 1:
            return None
    
    # Pour les phrases semi-valides (1 entité), vérifier qu'on a exactement 1 départ OU 1 arrivée
    if expected_entities == 1:
        if not ((departure_count == 1 and arrival_count == 0) or (departure_count == 0 and arrival_count == 1)):
            return None
    
    return {
        "text": sentence,
        "entities": entities
    }

def generate_nlp_sentence_semi_valid(pattern_func: SemiValidPatternFunc) -> Dict[str, any]:
    """
    Génère une phrase semi-valide avec annotations pour le NLP.
    
    IMPORTANT: Valide que la phrase générée contient exactement 1 départ OU 1 arrivée (pas les deux).
    Ces phrases sont cruciales pour la robustesse : elles apprennent au modèle que DEPARTURE et ARRIVAL sont indépendants.
    """
    context = build_context()
    sentence, dep_gare, arr_gare, dep_txt, arr_txt = pattern_func(context)
    
    # Validation: s'assurer qu'on a exactement 1 départ OU 1 arrivée (pas les deux)
    if (dep_gare and arr_gare) or (not dep_gare and not arr_gare):
        # Si le pattern fournit les deux ou aucun, ce n'est pas une phrase semi-valide
        # Retourner None pour que le générateur réessaie
        return None
    
    # Extraire les entités sur le texte original (avant modifications)
    # pour que extract_city_name_from_text() puisse reconnaître les préfixes
    # Pour les phrases semi-valides, has_explicit_dash n'est pas applicable (une seule ville)
    entities = extract_entities(sentence, dep_gare, arr_gare, dep_txt, arr_txt, has_explicit_dash=False)
    
    # Sauvegarder le texte original pour ajuster les positions
    original_text = sentence
    
    # Finaliser la phrase (ajoute du bruit après les villes dans 30% des cas via maybe_add_noise)
    sentence = finalize_sentence(sentence)
    
    # Ajuster les positions des entités après les modifications du texte
    if original_text != sentence:
        entities = adjust_entity_positions(original_text, sentence, entities)
    
    # Validation finale: compter les entités DEPARTURE et ARRIVAL
    departure_count = sum(1 for e in entities if e[2] == "DEPARTURE")
    arrival_count = sum(1 for e in entities if e[2] == "ARRIVAL")
    total_entities = len(entities)
    
    # VALIDATION STRICTE: Les phrases semi-valides doivent avoir exactement 1 entité détectée
    if total_entities != 1:
        # Si le nombre d'entités détectées n'est pas exactement 1, retourner None pour réessayer
        return None
    
    # Si on n'a pas exactement 1 départ OU 1 arrivée (mais pas les deux), retourner None pour réessayer
    if not ((departure_count == 1 and arrival_count == 0) or (departure_count == 0 and arrival_count == 1)):
        return None
    
    return {
        "text": sentence,
        "entities": entities
    }

def negative_patterns() -> List[Callable[[Dict[str, str]], str]]:
    """
    Retourne une liste de patterns pour générer des exemples négatifs (sans entités).
    Ces patterns aident le modèle à distinguer les noms propres, pays, et villes hors contexte.
    """
    return [
        # Patterns avec noms propres (prénoms)
        lambda c: f"Mon ami {c['friend1']} veut partir",
        lambda c: f"Je vais voir {c['friend1']} demain",
        lambda c: f"{c['friend1']} et {c['friend2']} sont là",
        lambda c: f"Mon copain {c['friend1']} arrive",
        lambda c: f"Je parle avec {c['friend1']}",
        lambda c: f"{c['friend1']} m'a dit bonjour",
        lambda c: f"Mon pote {c['friend1']} est sympa",
        lambda c: f"Je rencontre {c['friend1']} ce soir",
        lambda c: f"Mon ami {c['friend1']} habite ici",
        lambda c: f"{c['friend1']} et moi on va au ciné",
        
        # Patterns avec pays (pas des gares)
        lambda c: f"Je vais en {c['country']}",
        lambda c: f"Je pars pour la {c['country']}",
        lambda c: f"Voyage en {c['country']}",
        lambda c: f"Je reviens de {c['country']}",
        lambda c: f"Vacances en {c['country']}",
        lambda c: f"Je suis allé en {c['country']}",
        lambda c: f"Direction {c['country']}",
        lambda c: f"Je visite {c['country']}",
        
        # Patterns avec villes hors contexte (pas d'intention de trajet)
        lambda c: f"{c['dep']} est une belle ville",
        lambda c: f"J'aime beaucoup {c['dep']}",
        lambda c: f"{c['dep']} est au sud",
        lambda c: f"Le monument de {c['dep']} est beau",
        lambda c: f"La gare de {c['dep']} est grande",
        lambda c: f"Je connais {c['dep']}",
        lambda c: f"{c['dep']} c'est sympa",
        lambda c: f"J'ai visité {c['dep']}",
        lambda c: f"{c['dep']} est magnifique",
        lambda c: f"Le centre de {c['dep']} est joli",
        
        # Patterns avec noms composés non-gares (restaurants, monuments, etc.)
        lambda c: f"Le restaurant Le {c['dep']} est bon",
        lambda c: f"Le café de {c['dep']} est ouvert",
        lambda c: f"Le musée de {c['dep']} est intéressant",
        lambda c: f"L'hôtel {c['dep']} est confortable",
        lambda c: f"Le parc de {c['dep']} est vert",
        lambda c: f"La place de {c['dep']} est animée",
        lambda c: f"Le théâtre de {c['dep']} est moderne",
        lambda c: f"L'école de {c['dep']} est grande",
        
        # Patterns conversationnels sans intention de trajet
        lambda c: f"Comment allez-vous ?",
        lambda c: f"Quel temps fait-il ?",
        lambda c: f"Bonjour comment ça va ?",
        lambda c: f"Qu'est-ce que tu fais ?",
        lambda c: f"Tu veux manger ?",
        lambda c: f"On se voit demain ?",
        lambda c: f"C'est sympa ici",
        lambda c: f"J'ai faim",
        lambda c: f"Je suis fatigué",
        lambda c: f"Quelle heure est-il ?",
        
        # Patterns négatifs PLUS LONGS pour éviter le biais de longueur
        lambda c: f"Salut, comment ça va aujourd'hui ? J'espère que tu vas bien et que tout se passe comme prévu de ton côté.",
        lambda c: f"Bonjour, je voulais juste te dire que j'ai passé un excellent weekend avec mes amis et qu'on a fait plein d'activités sympas ensemble.",
        lambda c: f"Hey, est-ce que tu pourrais me donner des nouvelles de ta famille ? J'aimerais savoir comment ils vont et s'ils ont des projets intéressants.",
        lambda c: f"Coucou, je me demandais si tu avais des recommandations de restaurants dans le coin. J'ai envie de découvrir de nouveaux endroits pour manger.",
        lambda c: f"Salut, j'ai regardé un super film hier soir et je voulais te le recommander. C'était vraiment captivant du début à la fin.",
        lambda c: f"Bonjour, j'espère que tu passes une bonne journée. Moi je suis un peu fatigué mais ça va, je vais me reposer ce soir.",
        lambda c: f"Hey, est-ce que tu sais où je peux trouver un bon livre à lire ? J'ai terminé mon dernier roman et je cherche quelque chose de nouveau.",
        lambda c: f"Coucou, j'ai fait une super randonnée ce matin dans la forêt. Le paysage était magnifique et l'air était vraiment frais.",
        lambda c: f"Salut, je me demandais si tu avais des idées pour occuper mon weekend. J'aimerais faire quelque chose d'amusant et de relaxant.",
        lambda c: f"Bonjour, j'ai cuisiné un excellent repas hier soir avec des ingrédients frais du marché. C'était délicieux et j'ai bien mangé.",
        lambda c: f"Hey, est-ce que tu connais de bons endroits pour faire du shopping ? J'ai besoin de renouveler ma garde-robe pour la saison.",
        lambda c: f"Coucou, j'ai passé la journée à lire dans le parc. C'était très agréable et reposant, exactement ce dont j'avais besoin.",
        lambda c: f"Salut, je voulais te remercier pour ton aide la semaine dernière. C'était vraiment sympa de ta part et ça m'a beaucoup aidé.",
        lambda c: f"Bonjour, j'ai regardé un documentaire intéressant sur l'histoire hier soir. C'était très instructif et j'ai appris plein de choses.",
        lambda c: f"Hey, est-ce que tu veux qu'on aille boire un café ensemble un de ces jours ? Ça ferait plaisir de se revoir et de discuter.",
        lambda c: f"Coucou, j'ai fait du sport ce matin et je me sens vraiment bien maintenant. L'exercice me fait toujours du bien mentalement.",
        lambda c: f"Salut, j'ai visité un musée intéressant ce weekend. Il y avait des expositions vraiment captivantes sur l'art moderne et contemporain.",
        lambda c: f"Bonjour, je me demandais si tu avais des suggestions de musique à écouter. J'aimerais découvrir de nouveaux artistes et styles.",
        lambda c: f"Hey, j'ai passé une excellente soirée hier avec des amis. On a bien rigolé et c'était vraiment agréable de passer du temps ensemble.",
        lambda c: f"Coucou, est-ce que tu sais où je peux trouver de bonnes recettes de cuisine ? J'aimerais essayer de nouvelles choses en cuisine.",
        lambda c: f"Salut, j'ai regardé un match de foot hier soir à la télé. C'était passionnant et le résultat était vraiment serré jusqu'à la fin.",
        lambda c: f"Bonjour, j'espère que tu vas bien. Moi je suis un peu stressé par le travail mais ça va, je vais gérer ça progressivement.",
        lambda c: f"Hey, est-ce que tu veux qu'on organise une sortie ensemble bientôt ? J'aimerais qu'on passe du bon temps et qu'on se détende.",
        lambda c: f"Coucou, j'ai fait une longue promenade dans la ville aujourd'hui. J'ai découvert de nouveaux quartiers et c'était vraiment sympa.",
        lambda c: f"Salut, j'ai lu un article intéressant sur la technologie ce matin. Il y avait des informations vraiment fascinantes sur les innovations.",
        lambda c: f"Bonjour, je me demandais si tu avais des plans pour les prochaines vacances. J'aimerais organiser quelque chose d'agréable et de reposant.",
        lambda c: f"Hey, j'ai essayé un nouveau restaurant hier soir et c'était délicieux. La nourriture était excellente et le service était impeccable.",
        lambda c: f"Coucou, est-ce que tu connais de bons endroits pour faire du sport en extérieur ? J'aimerais varier mes activités physiques.",
        lambda c: f"Salut, j'ai regardé un spectacle de théâtre la semaine dernière. C'était vraiment bien joué et l'histoire était captivante du début à la fin.",
        lambda c: f"Bonjour, j'espère que tu passes une bonne semaine. Moi je suis assez occupé mais je prends le temps de me détendre quand même.",
    ]

def generate_negative_example() -> Dict[str, any]:
    """
    Génère un exemple négatif (phrase sans entités DEPARTURE/ARRIVAL).
    Ces exemples aident le modèle à distinguer les noms propres, pays, et villes hors contexte.
    """
    patterns = negative_patterns()
    context = build_context()
    
    # Sélectionner un pattern aléatoire
    pattern_func = random.choice(patterns)
    sentence = pattern_func(context)
    
    # Finaliser la phrase (ajouter variations, typos, etc.)
    sentence = finalize_sentence(sentence)
    
    # Retourner avec entities vide (pas d'entités)
    return {
        "text": sentence,
        "entities": []  # Pas d'entités pour les exemples négatifs
    }

def generate_dataset(
    total: int = TOTAL_SENTENCES,
    seed: Optional[int] = 42,
    output_file: Path = OUTPUT_FILE,
    negative_ratio: float = 0.12,  # 12% d'exemples négatifs par défaut
    semi_valid_ratio: float = 0.15,  # 15% de phrases semi-valides (départ OU arrivée uniquement) par défaut
) -> None:
    """
    Génère un dataset NLP de phrases valides avec annotations.
    Inclut également des exemples négatifs (sans entités) et des phrases semi-valides pour améliorer la robustesse.
    
    Args:
        total: Nombre total de phrases à générer (incluant les exemples négatifs et semi-valides)
        seed: Graine aléatoire pour la reproductibilité
        output_file: Fichier de sortie
        negative_ratio: Ratio d'exemples négatifs (0.12 = 12% d'exemples négatifs)
        semi_valid_ratio: Ratio de phrases semi-valides (0.15 = 15% de phrases avec départ OU arrivée uniquement)
    """
    if seed is not None:
        random.seed(seed)

    patterns = nlp_patterns()
    patterns_semi_valid = nlp_patterns_semi_valid()
    entries: List[Dict[str, any]] = []
    seen: set[str] = set()

    # Calculer le nombre d'exemples de chaque type
    num_negative = int(total * negative_ratio)
    num_semi_valid = int(total * semi_valid_ratio)
    num_positive = total - num_negative - num_semi_valid

    print(f"📊 Génération du dataset:")
    print(f"   - Exemples positifs (départ ET arrivée): {num_positive}")
    print(f"   - Exemples semi-valides (départ OU arrivée): {num_semi_valid}")
    print(f"   - Exemples négatifs (sans entités): {num_negative}")
    print(f"   - Total: {total}")

    # Générer les phrases positives (départ ET arrivée) - 2 entités attendues
    count_positive = 0
    max_attempts = num_positive * 10
    attempts = 0
    
    while count_positive < num_positive and attempts < max_attempts:
        attempts += 1
        pattern_func = random.choice(patterns)
        # Pour les phrases complètes, on attend exactement 2 entités (1 départ + 1 arrivée)
        record = generate_nlp_sentence(pattern_func, expected_entities=2)
        # Ignorer les records None (phrases invalides sans exactement 2 entités)
        if record is None:
            continue
        key = record["text"].lower().strip()
        if key in seen:
            continue
        seen.add(key)
        entries.append(record)
        count_positive += 1

    # Générer les phrases semi-valides (départ OU arrivée uniquement) - 1 entité attendue
    count_semi_valid = 0
    max_attempts_semi = num_semi_valid * 10
    attempts_semi = 0
    
    while count_semi_valid < num_semi_valid and attempts_semi < max_attempts_semi:
        attempts_semi += 1
        pattern_func = random.choice(patterns_semi_valid)
        # Pour les phrases semi-valides, on attend exactement 1 entité (1 départ OU 1 arrivée)
        record = generate_nlp_sentence_semi_valid(pattern_func)
        # Ignorer les records None (phrases invalides sans exactement 1 entité)
        if record is None:
            continue
        key = record["text"].lower().strip()
        if key in seen:
            continue
        seen.add(key)
        entries.append(record)
        count_semi_valid += 1

    # Générer les exemples négatifs
    count_negative = 0
    max_attempts_neg = num_negative * 10
    attempts_neg = 0
    
    while count_negative < num_negative and attempts_neg < max_attempts_neg:
        attempts_neg += 1
        record = generate_negative_example()
        key = record["text"].lower().strip()
        if key in seen:
            continue
        seen.add(key)
        entries.append(record)
        count_negative += 1

    random.shuffle(entries)
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with output_file.open("w", encoding="utf-8") as f:
        for row in entries:
            json.dump(row, f, ensure_ascii=False)
            f.write("\n")

    # Statistiques
    positive_count = sum(1 for e in entries if len(e.get("entities", [])) > 0)
    negative_count = sum(1 for e in entries if len(e.get("entities", [])) == 0)
    
    # Compter les phrases semi-valides (avec exactement 1 entité)
    semi_valid_count = sum(1 for e in entries if len(e.get("entities", [])) == 1)
    # Compter les phrases complètes (avec exactement 2 entités)
    full_count = sum(1 for e in entries if len(e.get("entities", [])) == 2)
    
    print(f"✅ Generated {len(entries)} sentences -> {output_file}")
    print(f"   - Exemples complets (départ ET arrivée): {full_count} ({full_count/len(entries)*100:.1f}%)")
    print(f"   - Exemples semi-valides (départ OU arrivée): {semi_valid_count} ({semi_valid_count/len(entries)*100:.1f}%)")
    print(f"   - Exemples négatifs (sans entités): {negative_count} ({negative_count/len(entries)*100:.1f}%)")
    print(f"   - Patterns complets utilisés: {len(patterns)}")
    print(f"   - Patterns semi-valides utilisés: {len(patterns_semi_valid)}")
    print(f"   - Patterns négatifs utilisés: {len(negative_patterns())}")
    if count_positive < num_positive or count_semi_valid < num_semi_valid or count_negative < num_negative:
        print(f"   ⚠️  Attention: Objectif non atteint (trop de doublons)")

if __name__ == "__main__":
    generate_dataset()

