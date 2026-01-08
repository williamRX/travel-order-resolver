#!/usr/bin/env python3
"""
Générateur de dataset pour le modèle NLP d'extraction des destinations.

Génère un dataset JSONL au format Spacy avec des phrases valides uniquement.
Chaque ligne contient : {"text": "...", "entities": [[start, end, "LABEL"], ...]}

- 150 patterns différents de phrases valides
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

COUNTRIES_REGIONS: List[str] = [
    "Espagne", "Italie", "Allemagne", "Suisse", "Belgique", "Royaume-Uni",
    "Portugal", "Etats-Unis", "Canada", "Japon", "Australie", "Maroc", "Tunisie",
    "Egypte", "Turquie", "Bresil", "Argentine", "Chili", "Mexique", "Chine",
    "Inde", "Thailande", "Vietnam"
]

TRANSPORTS: List[str] = [
    "train", "tgv", "ter", "bus", "avion", "voiture", "covoiturage", "metro", "tram",
    "bateau", "ferry", "velo", "scooter", "navette", "car", "taxi", "uber"
]

NOISE_TOKENS: List[str] = [
    "stp", "svp", "merci", "please", "plz", "mdr", "lol", "svp c urgent",
    "please asap", "ptdr", "hein", "ok", "svp vite"
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
    if random.random() < 0.3:
        noise = random.choice(NOISE_TOKENS)
        if random.random() < 0.5:
            sentence = f"{noise} {sentence}"
        else:
            sentence = f"{sentence} {noise}"
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

def find_entity_positions(text: str, entity_text: str, label: str) -> List[Tuple[int, int, str]]:
    """Trouve les positions d'une entité dans le texte (insensible à la casse)."""
    entities = []
    # Recherche insensible à la casse
    pattern = re.escape(entity_text)
    for match in re.finditer(pattern, text, re.IGNORECASE):
        entities.append((match.start(), match.end(), label))
    return entities

def extract_entities(text: str, dep_gare: Optional[str], arr_gare: Optional[str], dep_txt: Optional[str], arr_txt: Optional[str]) -> List[List[Union[int, str]]]:
    """Extrait les entités DEPARTURE et ARRIVAL du texte."""
    entities = []
    
    # Chercher le départ (priorité au texte avec variante, puis au nom de gare)
    if dep_gare:
        if dep_txt:
            dep_entities = find_entity_positions(text, dep_txt, "DEPARTURE")
            if not dep_entities:
                dep_entities = find_entity_positions(text, dep_gare, "DEPARTURE")
        else:
            dep_entities = find_entity_positions(text, dep_gare, "DEPARTURE")
        entities.extend(dep_entities)
    
    # Chercher l'arrivée si présente
    if arr_gare:
        if arr_txt:
            arr_entities = find_entity_positions(text, arr_txt, "ARRIVAL")
            if not arr_entities:
                arr_entities = find_entity_positions(text, arr_gare, "ARRIVAL")
        else:
            arr_entities = find_entity_positions(text, arr_gare, "ARRIVAL")
        entities.extend(arr_entities)
    
    # Trier par position de début
    entities.sort(key=lambda x: x[0])
    
    # Convertir en format Spacy [[start, end, "LABEL"], ...]
    return [[start, end, label] for start, end, label in entities]

# --- Sentence patterns (150 patterns valides) ---
PatternFunc = Callable[[Dict[str, str]], Tuple[str, str, Optional[str], str, Optional[str]]]
# Retourne: (sentence, dep_gare, arr_gare, dep_txt, arr_txt)

def nlp_patterns() -> List[PatternFunc]:
    """Retourne les 150 patterns pour générer des phrases valides."""
    return [
        # 1-10: Formes standard
        lambda c: (f"Je vais de {c['dep_txt']} à {c['arr_txt']}.", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Pour aller à {c['arr_txt']}, je pars de {c['dep_txt']}.", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je vais à {c['arr_txt']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je quitte {c['dep_txt']}.", c["dep"], None, c["dep_txt"], None),
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
        lambda c: (f"{c['dep_txt']} → {c['via_txt']} → {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je passe par {c['via_txt']} mais je vais à {c['arr_txt']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"🚆 {c['dep_txt']} → {c['arr_txt']}", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"Je vais en {c['country']} depuis {c['dep_txt']}.", c["dep"], c["country"], c["dep_txt"], None),
        lambda c: (f"Si je pars de {c['dep_txt']}, je vais à {c['arr_txt']} ?", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        lambda c: (f"{c['dep_txt']} vers {c['arr_txt']} ?", c["dep"], c["arr"], c["dep_txt"], c["arr_txt"]),
        
        # 21-30: Places spécifiques (gare, aéroport)
        lambda c: (f"Je pars de la gare de {c['dep']} pour {c['arr_txt']}", c["dep"], c["arr"], f"la gare de {c['dep']}", c["arr_txt"]),
        lambda c: (f"Je pars de {c['via']} pour {c['arr_txt']}", c["via"], c["arr"], c["via"], c["arr_txt"]),
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
        
        # 51-60: Destinations internationales
        lambda c: (f"Je vais en {c['country']} depuis {c['dep_txt']}", c["dep"], c["country"], c["dep_txt"], None),
        lambda c: (f"Trajet vers {c['country']} en partant de {c['dep_txt']}", c["dep"], c["country"], c["dep_txt"], None),
        lambda c: (f"Aller en {c['country']} depuis {c['dep_txt']}", c["dep"], c["country"], c["dep_txt"], None),
        lambda c: (f"Voyage en {c['country']} depuis {c['dep_txt']}", c["dep"], c["country"], c["dep_txt"], None),
        lambda c: (f"Billet pour {c['country']} depuis {c['dep_txt']}", c["dep"], c["country"], c["dep_txt"], None),
        lambda c: (f"Je pars de {c['dep_txt']} pour aller en {c['country']}", c["dep"], c["country"], c["dep_txt"], None),
        lambda c: (f"Trajet {c['dep_txt']} {c['country']}", c["dep"], c["country"], c["dep_txt"], None),
        lambda c: (f"Comment aller en {c['country']} depuis {c['dep_txt']} ?", c["dep"], c["country"], c["dep_txt"], None),
        lambda c: (f"Je veux me rendre en {c['country']} depuis {c['dep_txt']}", c["dep"], c["country"], c["dep_txt"], None),
        lambda c: (f"Aller de {c['dep_txt']} vers {c['country']}", c["dep"], c["country"], c["dep_txt"], None),
        
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
        
        # 71-80: Patterns "mais je vais à"
        lambda c: (f"Je passe par {c['via_txt']} mais je vais à {c['arr_txt']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je traverse {c['via_txt']} mais je vais à {c['arr_txt']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je m'arrête à {c['via_txt']} mais je vais à {c['arr_txt']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je fais une escale à {c['via_txt']} mais je vais à {c['arr_txt']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je passe par {c['via_txt']} pour manger mais je vais à {c['arr_txt']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je m'arrête à {c['via_txt']} pour faire le plein mais je vais à {c['arr_txt']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je traverse {c['via_txt']} rapidement mais je vais à {c['arr_txt']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je passe par {c['via_txt']} en route mais je vais à {c['arr_txt']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je fais une pause à {c['via_txt']} mais je vais à {c['arr_txt']}.", None, c["arr"], None, c["arr_txt"]),
        lambda c: (f"Je visite {c['via_txt']} brièvement mais je vais à {c['arr_txt']}.", None, c["arr"], None, c["arr_txt"]),
        
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
    ]

# --- Generation ---
def generate_nlp_sentence(pattern_func: PatternFunc) -> Dict[str, any]:
    """Génère une phrase avec annotations pour le NLP."""
    context = build_context()
    sentence, dep_gare, arr_gare, dep_txt, arr_txt = pattern_func(context)
    sentence = finalize_sentence(sentence)
    
    # Extraire les entités
    entities = extract_entities(sentence, dep_gare, arr_gare, dep_txt, arr_txt)
    
    return {
        "text": sentence,
        "entities": entities
    }

def generate_dataset(
    total: int = TOTAL_SENTENCES,
    seed: Optional[int] = 42,
    output_file: Path = OUTPUT_FILE,
) -> None:
    """
    Génère un dataset NLP de phrases valides avec annotations.
    
    Args:
        total: Nombre total de phrases à générer
        seed: Graine aléatoire pour la reproductibilité
        output_file: Fichier de sortie
    """
    if seed is not None:
        random.seed(seed)

    patterns = nlp_patterns()
    entries: List[Dict[str, any]] = []
    seen: set[str] = set()

    # Générer les phrases
    count = 0
    max_attempts = total * 10
    attempts = 0
    
    while count < total and attempts < max_attempts:
        attempts += 1
        pattern_func = random.choice(patterns)
        record = generate_nlp_sentence(pattern_func)
        key = record["text"].lower().strip()
        if key in seen:
            continue
        seen.add(key)
        entries.append(record)
        count += 1

    random.shuffle(entries)
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with output_file.open("w", encoding="utf-8") as f:
        for row in entries:
            json.dump(row, f, ensure_ascii=False)
            f.write("\n")

    print(f"✅ Generated {len(entries)} sentences -> {output_file}")
    print(f"   Patterns used: {len(patterns)}")
    if count < total:
        print(f"   ⚠️  Attention: Objectif non atteint (trop de doublons)")

if __name__ == "__main__":
    generate_dataset()

