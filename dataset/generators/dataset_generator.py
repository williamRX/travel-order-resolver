#!/usr/bin/env python3
"""
Generate a JSONL dataset (~10k rows) of French travel-intent sentences.
Each line contains: {"sentence": "...", "departure": "... or null", "arrival": "... or null", "is_valid": 0/1}
"""

import json
import random
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

TOTAL_SENTENCES = 10_000
INVALID_RATIO = 0.30  # ~30% invalid sentences
OUTPUT_FILE = Path(__file__).resolve().parent.parent / "json" / "dataset.jsonl"
GARES_JSON = Path(__file__).resolve().parent.parent / "json" / "gares-francaises.json"

# --- Data sources ---
def load_french_cities_from_json(json_path: Path) -> List[str]:
    """Charge les villes françaises depuis le fichier JSON des gares."""
    try:
        with json_path.open("r", encoding="utf-8") as f:
            gares_data = json.load(f)
        # Extraire les noms uniques de villes/gares
        cities = set()
        for gare in gares_data:
            if "nom" in gare:
                cities.add(gare["nom"])
        return sorted(list(cities))
    except Exception as e:
        print(f"⚠️  Erreur lors du chargement de {json_path}: {e}")
        print("   Utilisation d'une liste de villes par défaut.")
        return [
            "Paris", "Lyon", "Marseille", "Toulouse", "Nice", "Nantes", "Strasbourg",
            "Montpellier", "Bordeaux", "Lille", "Rennes", "Reims", "Le Havre"
        ]

CITIES: List[str] = load_french_cities_from_json(GARES_JSON)

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

# Transports valides pour le pattern spécial (train uniquement)
VALID_TRANSPORTS: List[str] = ["train", "tgv", "ter", "tram", "metro", "rer", "transilien", "sncf"]

# Transports invalides pour le pattern spécial
INVALID_TRANSPORTS: List[str] = ["bateau", "ferry", "avion", "voiture", "covoiturage", "velo", "scooter", "car", "taxi", "uber", "bus"]

# Villes fictives pour les patterns invalides
FICTIVE_CITIES: List[str] = [
    "Villefictive", "Nouvelleville", "Villeneuve", "Saint-Fictif", "Port-Imaginaire",
    "Mont-Fantôme", "Rivage-Inventé", "Cité-Virtuelle", "Bourg-Fabriqué", "Hameau-Inventé",
    "Ville-Rêvée", "Cité-Fantôme", "Port-Fictif", "Mont-Inventé", "Rivage-Imaginaire",
    "Nouvelle-Cité", "Ville-Inventée", "Bourg-Fictif", "Hameau-Fabriqué", "Cité-Rêvée"
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


def pick_city(exclude: Optional[str] = None) -> str:
    pool = [city for city in CITIES if city != exclude]
    return random.choice(pool)


def pick_country() -> str:
    return random.choice(COUNTRIES_REGIONS)


def add_location_variant(city: str) -> str:
    roll = random.random()
    if roll < 0.18:
        return f"la gare de {city}"
    if roll < 0.30:
        return f"l'aéroport de {city}"
    if roll < 0.36:
        return f"centre de {city}"
    if roll < 0.42:
        return f"port de {city}"
    return city


def introduce_typos(text: str) -> str:
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


def maybe_multiline(sentence: str) -> str:
    # Désactivé : on ne veut pas de retours à la ligne dans les phrases
    # Les phrases multi-lignes sont remplacées par des virgules
    if random.random() < 0.1:
        if "," in sentence:
            return sentence.replace(",", ", ", 1)
        parts = sentence.split(" ", 1)
        if len(parts) == 2:
            return f"{parts[0]}, {parts[1]}"
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


def random_city_text(city: str) -> str:
    text = add_location_variant(city)
    # Parfois enlever la majuscule (30% de chance)
    if random.random() < 0.30:
        # Enlever la majuscule du premier mot si c'est une ville simple
        # Pour les variantes comme "la gare de Paris", on enlève la majuscule de la ville
        if text.startswith("la gare de "):
            text = f"la gare de {text[12:].lower()}"
        elif text.startswith("l'aéroport de "):
            text = f"l'aéroport de {text[15:].lower()}"
        elif text.startswith("centre de "):
            text = f"centre de {text[10:].lower()}"
        elif text.startswith("port de "):
            text = f"port de {text[8:].lower()}"
        else:
            # Ville simple, enlever la majuscule
            text = text.lower()
    if random.random() < 0.55:
        text = introduce_typos(text)
    return text


def build_context() -> Dict[str, str]:
    dep = pick_city()
    arr = pick_city(exclude=dep)
    via = pick_city(exclude=dep)
    if via == arr:
        via = pick_city(exclude=dep)
    return {
        "dep": dep,
        "arr": arr,
        "via": via,
        "dep_txt": random_city_text(dep),
        "arr_txt": random_city_text(arr),
        "via_txt": random_city_text(via),
        "country": pick_country(),
        "transport": random_transport(),
        "time": random_time_phrase(),
        "date": random_date_phrase(),
    }


def finalize_sentence(sentence: str) -> str:
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
    if random.random() < 0.1:
        sentence = maybe_multiline(sentence)
    # Nettoyer tous les retours à la ligne et les remplacer par des espaces
    sentence = sentence.replace("\n", " ").replace("\r", " ")
    # Nettoyer les espaces multiples
    while "  " in sentence:
        sentence = sentence.replace("  ", " ")
    return sentence.strip()


# --- Sentence patterns ---
PatternFunc = Callable[[Dict[str, str]], Tuple[str, Optional[str], Optional[str]]]
InvalidPatternFunc = Callable[[Dict[str, str]], str]

# Poids par défaut pour chaque pattern (ajustables)
# Les poids déterminent la probabilité relative d'utilisation de chaque pattern
# Plus le poids est élevé, plus le pattern sera utilisé fréquemment
DEFAULT_VALID_PATTERN_WEIGHTS: List[float] = [
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 1-10
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 11-20
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 21-30
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 31-40
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 41-50
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 51-60
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 61-70
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 71-80
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 81-90
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 91-100
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 101-110
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 111-120
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 121-130
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 131-140
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 141-150
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 151-160
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 161-170
    1.0, 1.0, 1.0, 1.0,  # 171-174
]

# Poids par défaut pour les patterns invalides (166 patterns)
DEFAULT_INVALID_PATTERN_WEIGHTS: List[float] = [
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 1-10
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 11-20
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 21-30
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 31-40
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 41-50
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 51-60
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 61-70
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 71-80
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 81-90
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 91-100
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 101-110
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 111-120
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 121-130
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 131-140
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 141-150
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 151-166
]


def weighted_choice(items: List, weights: List[float]) -> int:
    """Sélectionne un index selon les poids fournis."""
    if len(items) != len(weights):
        raise ValueError(f"Le nombre d'items ({len(items)}) doit correspondre au nombre de poids ({len(weights)})")
    total_weight = sum(weights)
    if total_weight == 0:
        return random.randint(0, len(items) - 1)
    r = random.uniform(0, total_weight)
    cumulative = 0
    for i, weight in enumerate(weights):
        cumulative += weight
        if r <= cumulative:
            return i
    return len(items) - 1


def valid_patterns() -> List[PatternFunc]:
    return [
        # 1. Standard forms
        lambda c: (f"Je vais de {c['dep_txt']} à {c['arr_txt']}.", c["dep"], c["arr"]),
        # 2. Inverse order
        lambda c: (f"Pour aller à {c['arr_txt']}, je pars de {c['dep_txt']}.", c["dep"], c["arr"]),
        # 3. Implicit departure
        lambda c: (f"Je vais à {c['arr_txt']}.", None, c["arr"]),
        # 4. Implicit arrival
        lambda c: (f"Je quitte {c['dep_txt']}.", c["dep"], None),
        # 5. Informal speech
        lambda c: (f"Je bouge de {c['dep_txt']} à {c['arr_txt']}.", c["dep"], c["arr"]),
        # 6. French-specific expression
        lambda c: (f"Je descends sur {c['arr_txt']} depuis {c['dep_txt']}.", c["dep"], c["arr"]),
        # 7. SMS / abbreviation
        lambda c: (f"Jvé d {c['dep_txt']} a {c['arr_txt']}", c["dep"], c["arr"]),
        # 8. Typos and misspellings
        lambda c: (f"Je veu alé de {c['dep_txt']} a {c['arr_txt']}", c["dep"], c["arr"]),
        # 9. With time/date
        lambda c: (f"Je pars de {c['dep_txt']} {c['time']} pour {c['arr_txt']} {c['date']}", c["dep"], c["arr"]),
        # 10. With transport
        lambda c: (f"En {c['transport']} de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"]),
        # 11. Long sentences with noise
        lambda c: (f"Salut, je dois aller de {c['dep_txt']} à {c['arr_txt']} {c['date']} {c['time']} pour un rdv important", c["dep"], c["arr"]),
        # 12. Multi-line sentences (sans retours à la ligne)
        lambda c: (f"Bonjour, je voudrais partir de {c['dep_txt']} vers {c['arr_txt']} {c['date']}", c["dep"], c["arr"]),
        # 13. Sentences without verbs
        lambda c: (f"{c['dep_txt']} → {c['arr_txt']}", c["dep"], c["arr"]),
        # 14. Indirect requests
        lambda c: (f"Comment aller de {c['dep_txt']} à {c['arr_txt']} ?", c["dep"], c["arr"]),
        # 15. Multi-destinations
        lambda c: (f"{c['dep_txt']} → {c['via_txt']} → {c['arr_txt']}", c["dep"], c["arr"]),
        # 16. Ambiguities
        lambda c: (f"Je passe par {c['via_txt']} mais je vais à {c['arr_txt']}.", None, c["arr"]),
        # 17. With emojis
        lambda c: (f"🚆 {c['dep_txt']} → {c['arr_txt']}", c["dep"], c["arr"]),
        # 18. Regions/countries
        lambda c: (f"Je vais en {c['country']} depuis {c['dep_txt']}.", c["dep"], c["country"]),
        # 19. Conditional
        lambda c: (f"Si je pars de {c['dep_txt']}, je vais à {c['arr_txt']} ?", c["dep"], c["arr"]),
        # 20. Questions
        lambda c: (f"{c['dep_txt']} vers {c['arr_txt']} ?", c["dep"], c["arr"]),
        # 21. Places like gare, aeroport
        lambda c: (f"Je pars de la gare de {c['dep']} pour {c['arr_txt']}", c["dep"], c["arr"]),
        # 22. Different French cities
        lambda c: (f"Je pars de {c['via']} pour {c['arr_txt']}", c["via"], c["arr"]),
        # 23. Future tense
        lambda c: (f"Je vais partir de {c['dep_txt']} pour {c['arr_txt']} {c['date']}", c["dep"], c["arr"]),
        # 24. Need-based
        lambda c: (f"J'ai besoin d'aller de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"]),
        # 25. Want-based
        lambda c: (f"Je veux me rendre de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"]),
        # 26. Must-based
        lambda c: (f"Je dois me déplacer de {c['dep_txt']} vers {c['arr_txt']}", c["dep"], c["arr"]),
        # 27. Would like
        lambda c: (f"J'aimerais voyager de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"]),
        # 28. Looking for
        lambda c: (f"Je cherche un trajet {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        # 29. Ticket request
        lambda c: (f"Un billet de {c['dep_txt']} pour {c['arr_txt']} {c['date']}", c["dep"], c["arr"]),
        # 30. Route request
        lambda c: (f"Quel est le trajet entre {c['dep_txt']} et {c['arr_txt']}", c["dep"], c["arr"]),
        # 31. Duration question
        lambda c: (f"Combien de temps pour aller de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"]),
        # 32. Price question
        lambda c: (f"Quel est le prix d'un billet {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        # 33. Schedule question
        lambda c: (f"Y a-t-il des trains {c['dep_txt']} {c['arr_txt']} {c['date']}", c["dep"], c["arr"]),
        # 34. Direct question
        lambda c: (f"Trajet direct {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        # 35. With return
        lambda c: (f"Aller-retour {c['dep_txt']} {c['arr_txt']} {c['date']}", c["dep"], c["arr"]),
        # 36. One way
        lambda c: (f"Aller simple {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        # 37. Urgent
        lambda c: (f"Urgent ! Je dois aller de {c['dep_txt']} à {c['arr_txt']} {c['time']}", c["dep"], c["arr"]),
        # 38. Business context
        lambda c: (f"Voyage professionnel {c['dep_txt']} {c['arr_txt']} {c['date']}", c["dep"], c["arr"]),
        # 39. Vacation context
        lambda c: (f"Partir en vacances de {c['dep_txt']} vers {c['arr_txt']}", c["dep"], c["arr"]),
        # 40. Family visit
        lambda c: (f"Rendre visite à ma famille {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        # 41. With luggage
        lambda c: (f"Voyage avec bagages {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        # 42. First class
        lambda c: (f"Première classe {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        # 43. Second class
        lambda c: (f"Deuxième classe {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        # 44. With stopover
        lambda c: (f"Trajet avec escale {c['dep_txt']} {c['via_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        # 45. Early morning
        lambda c: (f"Départ tôt le matin de {c['dep_txt']} pour {c['arr_txt']}", c["dep"], c["arr"]),
        # 46. Evening
        lambda c: (f"Partir en soirée de {c['dep_txt']} vers {c['arr_txt']}", c["dep"], c["arr"]),
        # 47. Weekend
        lambda c: (f"Voyage le weekend {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        # 48. Group travel
        lambda c: (f"Voyage en groupe de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"]),
        # 49. Student discount
        lambda c: (f"Tarif étudiant {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        # 50. Senior discount
        lambda c: (f"Tarif senior {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        # 51. With bike
        lambda c: (f"Voyage avec vélo {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        # 52. With pet
        lambda c: (f"Voyage avec animal {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        # 53. Pattern avec transport conditionnel (valid pour train, invalid pour autres)
        lambda c: _generate_transport_conditional_pattern(c),
        # 54. Question sur les horaires de trains
        lambda c: (f"A quelle heure y a-t-il des trains vers {c['arr_txt']} en partance de {c['dep_txt']} ?", c["dep"], c["arr"]),
        # 55-64. Formulations naturelles
        lambda c: (f"Je dois aller à {c['arr_txt']} depuis {c['dep_txt']}", c["dep"], c["arr"]),
        lambda c: (f"J'ai besoin d'aller de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Je souhaite me rendre de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Je dois me déplacer de {c['dep_txt']} vers {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Je veux me rendre de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Je dois partir de {c['dep_txt']} pour aller à {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Je dois rejoindre {c['arr_txt']} depuis {c['dep_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Je dois me rendre à {c['arr_txt']} en partant de {c['dep_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Je dois aller de {c['dep_txt']} jusqu'à {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Je dois me déplacer entre {c['dep_txt']} et {c['arr_txt']}", c["dep"], c["arr"]),
        # 65-74. Abrégées
        lambda c: (f"{c['dep_txt']}→{c['arr_txt']} ?", c["dep"], c["arr"]),
        lambda c: (f"trajet {c['dep_txt']} {c['arr_txt']} urgent", c["dep"], c["arr"]),
        lambda c: (f"{c['dep_txt']} {c['arr_txt']} svp", c["dep"], c["arr"]),
        lambda c: (f"train {c['dep_txt']} {c['arr_txt']} stp", c["dep"], c["arr"]),
        lambda c: (f"{c['dep_txt']} > {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"dep {c['dep_txt']} arr {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"de {c['dep_txt']} a {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"{c['dep_txt']} -> {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"billet {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"itinéraire {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        # 75-84. Patterns variés et utiles
        lambda c: (f"Je recherche un itinéraire {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Donne-moi les horaires {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Je veux voyager {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Propose-moi un trajet {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Je dois me rendre de {c['dep_txt']} jusqu'à {c['arr_txt']} {c['date']}", c["dep"], c["arr"]),
        lambda c: (f"Connection {c['dep_txt']} {c['arr_txt']} s'il te plaît", c["dep"], c["arr"]),
        lambda c: (f"Réservation {c['dep_txt']} {c['arr_txt']} pour {c['date']}", c["dep"], c["arr"]),
        lambda c: (f"Je cherche comment aller de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Informations trajet {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Besoin d'un transport {c['dep_txt']} {c['arr_txt']} {c['time']}", c["dep"], c["arr"]),
        # 85-94. Contraintes
        lambda c: (f"Le moins cher de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Éviter les correspondances {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Trajet direct {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Le plus rapide de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Le plus court {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Trajet sans correspondance {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Le meilleur prix {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Option économique {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Trajet avec le moins d'escales {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Le plus confortable {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        # 95-104. Contexte temporel
        lambda c: (f"demain matin de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"avant {c['time']} de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"{c['date']} matin {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"ce soir {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"cet après-midi {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"la semaine prochaine {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"dans 2 heures {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"après {c['time']} {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"vers {c['time']} {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"le {c['date']} {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        # 105-114. Polies
        lambda c: (f"Pourriez-vous m'indiquer un trajet de {c['dep_txt']} à {c['arr_txt']} ?", c["dep"], c["arr"]),
        lambda c: (f"Pourriez-vous me trouver un train de {c['dep_txt']} à {c['arr_txt']} ?", c["dep"], c["arr"]),
        lambda c: (f"Auriez-vous l'amabilité de me donner un itinéraire {c['dep_txt']} {c['arr_txt']} ?", c["dep"], c["arr"]),
        lambda c: (f"Serait-il possible d'avoir un billet {c['dep_txt']} {c['arr_txt']} ?", c["dep"], c["arr"]),
        lambda c: (f"Je vous serais reconnaissant de me fournir un trajet {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Pourriez-vous m'aider à trouver un train {c['dep_txt']} {c['arr_txt']} ?", c["dep"], c["arr"]),
        lambda c: (f"Merci de me proposer un itinéraire de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Je vous prie de bien vouloir me donner un trajet {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Seriez-vous en mesure de me trouver un billet {c['dep_txt']} {c['arr_txt']} ?", c["dep"], c["arr"]),
        lambda c: (f"Je vous demande poliment un trajet de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"]),
        # 115-124. Argotiques
        lambda c: (f"je me casse de {c['dep_txt']} pour {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"je me barre de {c['dep_txt']} vers {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"je me tire de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"je me taille de {c['dep_txt']} pour {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"je me tire de {c['dep_txt']} vers {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"je me barre de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"je me casse de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"je me tire de {c['dep_txt']} pour {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"je me taille de {c['dep_txt']} vers {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"je me barre de {c['dep_txt']} pour {c['arr_txt']}", c["dep"], c["arr"]),
        # 125-134. Fautes courantes
        lambda c: (f"je veu alé de {c['dep_txt']} a {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"je veu aller de {c['dep_txt']} a {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"je veu alé a {c['arr_txt']}", None, c["arr"]),
        lambda c: (f"depui {c['dep_txt']} vers {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"depui {c['dep_txt']} a {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"je pars depui {c['dep_txt']} pour {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"trajet depui {c['dep_txt']} a {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"aller depui {c['dep_txt']} vers {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"je veu partir depui {c['dep_txt']} pour {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"billet depui {c['dep_txt']} a {c['arr_txt']}", c["dep"], c["arr"]),
        # 135-144. Transport spécifique
        lambda c: (f"En bus de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"En TER de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"En TGV de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"En train de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Par le {c['transport']} de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"En {c['transport']} de {c['dep_txt']} vers {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Prendre le {c['transport']} {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Un {c['transport']} {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Le {c['transport']} de {c['dep_txt']} à {c['arr_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Via {c['transport']} {c['dep_txt']} {c['arr_txt']}", c["dep"], c["arr"]),
        # 145-154. Questions techniques
        lambda c: (f"Y a-t-il un train direct {c['dep_txt']} {c['arr_txt']} ?", c["dep"], c["arr"]),
        lambda c: (f"Est-ce qu'il y a des correspondances {c['dep_txt']} {c['arr_txt']} ?", c["dep"], c["arr"]),
        lambda c: (f"Quels sont les horaires {c['dep_txt']} {c['arr_txt']} ?", c["dep"], c["arr"]),
        lambda c: (f"Combien de temps pour aller de {c['dep_txt']} à {c['arr_txt']} ?", c["dep"], c["arr"]),
        lambda c: (f"Quelle est la durée du trajet {c['dep_txt']} {c['arr_txt']} ?", c["dep"], c["arr"]),
        lambda c: (f"Y a-t-il plusieurs trains par jour {c['dep_txt']} {c['arr_txt']} ?", c["dep"], c["arr"]),
        lambda c: (f"Quel est le premier train {c['dep_txt']} {c['arr_txt']} ?", c["dep"], c["arr"]),
        lambda c: (f"Quel est le dernier train {c['dep_txt']} {c['arr_txt']} ?", c["dep"], c["arr"]),
        lambda c: (f"Y a-t-il des trains de nuit {c['dep_txt']} {c['arr_txt']} ?", c["dep"], c["arr"]),
        lambda c: (f"Combien coûte un billet {c['dep_txt']} {c['arr_txt']} ?", c["dep"], c["arr"]),
        # 155-164. Internationaux
        lambda c: (f"Je vais en {c['country']} depuis {c['dep_txt']}", c["dep"], c["country"]),
        lambda c: (f"Trajet vers {c['country']} en partant de {c['dep_txt']}", c["dep"], c["country"]),
        lambda c: (f"Aller en {c['country']} depuis {c['dep_txt']}", c["dep"], c["country"]),
        lambda c: (f"Voyage en {c['country']} depuis {c['dep_txt']}", c["dep"], c["country"]),
        lambda c: (f"Billet pour {c['country']} depuis {c['dep_txt']}", c["dep"], c["country"]),
        lambda c: (f"Je pars de {c['dep_txt']} pour aller en {c['country']}", c["dep"], c["country"]),
        lambda c: (f"Trajet {c['dep_txt']} {c['country']}", c["dep"], c["country"]),
        lambda c: (f"Comment aller en {c['country']} depuis {c['dep_txt']} ?", c["dep"], c["country"]),
        lambda c: (f"Je veux me rendre en {c['country']} depuis {c['dep_txt']}", c["dep"], c["country"]),
        lambda c: (f"Aller de {c['dep_txt']} vers {c['country']}", c["dep"], c["country"]),
        # 165-174. Conversationnels
        lambda c: (f"Salut, j'ai un rdv à {c['arr_txt']} {c['date']}, je pars de {c['dep_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Bonjour, je dois aller à {c['arr_txt']} depuis {c['dep_txt']} {c['time']}", c["dep"], c["arr"]),
        lambda c: (f"Hey, je cherche un train {c['dep_txt']} {c['arr_txt']} {c['date']}", c["dep"], c["arr"]),
        lambda c: (f"Coucou, j'ai besoin d'aller de {c['dep_txt']} à {c['arr_txt']} rapidement", c["dep"], c["arr"]),
        lambda c: (f"Salut, trajet urgent {c['dep_txt']} {c['arr_txt']} {c['time']}", c["dep"], c["arr"]),
        lambda c: (f"Bonjour, je dois me rendre à {c['arr_txt']} en partant de {c['dep_txt']} {c['date']}", c["dep"], c["arr"]),
        lambda c: (f"Salut, j'ai un rendez-vous à {c['arr_txt']}, je suis à {c['dep_txt']}", c["dep"], c["arr"]),
        lambda c: (f"Hey, je veux aller de {c['dep_txt']} à {c['arr_txt']} {c['date']} {c['time']}", c["dep"], c["arr"]),
        lambda c: (f"Bonjour, je dois partir de {c['dep_txt']} pour {c['arr_txt']} {c['date']}", c["dep"], c["arr"]),
        lambda c: (f"Salut, un billet {c['dep_txt']} {c['arr_txt']} {c['date']} stp", c["dep"], c["arr"]),
    ]


def _generate_transport_conditional_pattern(context: Dict[str, str]) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Génère un pattern de type "[ville] et je vais à [ville] en [transport]"
    Retourne valid si transport est train/tgv/etc, invalid sinon.
    Note: Cette fonction est appelée depuis valid_patterns mais peut générer invalid.
    Le système de génération doit gérer ce cas spécial.
    """
    dep = context["dep"]
    arr = context["arr"]
    dep_txt = context["dep_txt"]
    arr_txt = context["arr_txt"]
    
    # Choisir un transport : 50% valid, 50% invalid
    if random.random() < 0.5:
        transport = random.choice(VALID_TRANSPORTS)
    else:
        transport = random.choice(INVALID_TRANSPORTS)
    
    # Variantes de phrases
    patterns = [
        f"{dep_txt} et je vais à {arr_txt} en {transport}",
        f"Je suis à {dep_txt} et je vais à {arr_txt} en {transport}",
        f"Partir de {dep_txt} et aller à {arr_txt} en {transport}",
        f"De {dep_txt} je vais à {arr_txt} en {transport}",
        f"Je pars de {dep_txt} et je vais à {arr_txt} en {transport}",
    ]
    
    sentence = random.choice(patterns)
    
    # Vérifier si le transport est valide
    is_valid_transport = transport.lower() in [t.lower() for t in VALID_TRANSPORTS]
    
    if is_valid_transport:
        return (sentence, dep, arr)
    else:
        # Pour invalid, on retourne None pour departure/arrival
        return (sentence, None, None)


INVALID_PATTERNS: List[InvalidPatternFunc] = [
    # 1. Nonsense général
    lambda c: "Je mange une pomme",
    # 2. SMS/informel incompréhensible
    lambda c: "mdrrr t ki",
    # 3. Caractères aléatoires
    lambda c: "asdadadasd",
    # 4. Erreur technique
    lambda c: "peux pas afficher la page",
    # 5. Phrase hors contexte
    lambda c: "J'ai perdu mes clés",
    # 6. Opinion sur le train
    lambda c: f"le {c['transport']} c'est trop cher",
    # 7. Action personnelle
    lambda c: "je dois appeler ma mère",
    # 8. Cuisine
    lambda c: "j'aimerais cuisiner des pâtes",
    # 9. Absence de destination
    lambda c: "Je ne vais nulle part aujourd'hui",
    # 10. État personnel
    lambda c: "Je voudrais juste dormir",
    # 11. Activité de loisir
    lambda c: "Je regarde Netflix",
    # 12. État de fatigue
    lambda c: "Je suis fatigué",
    # 13. Destination vague
    lambda c: "je veux aller la bas",
    # 14. Question sur le TGV
    lambda c: "Qu'est-ce qu'un TGV exactement",
    # 15. Hésitation entre villes
    lambda c: f"j'hésite entre {c['dep_txt']} et {c['arr_txt']}",
    # 16. Affection pour une ville
    lambda c: f"j'aime {c['dep_txt']}",
    # 17. Position actuelle
    lambda c: f"je suis à {c['dep_txt']}",
    # 18. Description d'une ville
    lambda c: f"{c['dep_txt']} est jolie",
    # 19. Nom d'animal
    lambda c: f"mon chat s'appelle {c['dep']}",
    # 20. Intention vague future
    lambda c: f"je dois aller peut etre {c['arr_txt']} un jour",
    # 21. Choix indécis
    lambda c: f"{c['dep_txt']} ou {c['arr_txt']} ???",
    # 22. Lecture d'article
    lambda c: f"Je lis un article sur {c['dep_txt']}",
    # 23. Match sportif
    lambda c: f"Je regarde un match à {c['dep_txt']}",
    # 24. Pas de voyage
    lambda c: f"je reste à la maison pas de voyage",
    # 25. Question historique
    lambda c: f"peux tu me raconter l'histoire de {c['dep_txt']}",
    # 26. Tâche ménagère
    lambda c: "je dois ranger ma chambre",
    # 27. Absence de destination
    lambda c: "je n'ai pas de destination",
    # 28. Phrase explicite non-trajet
    lambda c: "Ceci n'est pas une phrase de trajet",
    # 29. Pattern avec caractères génériques
    lambda c: "aller de * * * * *",
    # 30. Pattern incomplet
    lambda c: f"train machin truc ??",
    # 31. Intention incertaine
    lambda c: f"peut etre {c['arr_txt']} mais j'sais pas",
    # 32. Passage pour autre raison
    lambda c: f"Je passe par {c['via_txt']} pour manger",
    # 33. Expression métaphorique
    lambda c: f"Je veux aller bien dans ma vie",
    # 34. Intention très vague
    lambda c: "Je vais peut-être éventuellement songer à partir",
    # 35. Ponctuation seule
    lambda c: "???",
    # 36. Ponctuation seule
    lambda c: "!!!",
    # 37. Ponctuation seule
    lambda c: "...",
    # 38. Ville fictive - départ simple
    lambda c: f"Je vais à {random.choice(FICTIVE_CITIES)}",
    # 39. Ville fictive - départ
    lambda c: f"Je pars de {random.choice(FICTIVE_CITIES)}",
    # 40. Ville fictive - trajet complet
    lambda c: f"Je vais de {random.choice(FICTIVE_CITIES)} à {random.choice(FICTIVE_CITIES)}",
    # 41. Ville fictive - trajet court
    lambda c: f"Trajet {random.choice(FICTIVE_CITIES)} {random.choice(FICTIVE_CITIES)}",
    # 42. Ville fictive - aller vers
    lambda c: f"Aller de {random.choice(FICTIVE_CITIES)} vers {random.choice(FICTIVE_CITIES)}",
    # 43. Ville fictive - se rendre
    lambda c: f"Je dois me rendre à {random.choice(FICTIVE_CITIES)} depuis {random.choice(FICTIVE_CITIES)}",
    # 44. Ville fictive - voyage
    lambda c: f"Voyage {random.choice(FICTIVE_CITIES)} {random.choice(FICTIVE_CITIES)}",
    # 45. Ville fictive - billet
    lambda c: f"Billet {random.choice(FICTIVE_CITIES)} {random.choice(FICTIVE_CITIES)}",
    # 46. Récit d'un ami (pas une demande de trajet)
    lambda c: f"Mon ami m'a dit qu'il partait de {c['dep_txt']} pour aller a {c['arr_txt']}",
    # 47-56. Messages non liés au voyage - Météo
    lambda c: "Il fait beau aujourd'hui",
    lambda c: "Quel temps fait-il ?",
    lambda c: f"La météo à {c['dep_txt']} est bonne",
    lambda c: "Il pleut beaucoup",
    lambda c: "C'est ensoleillé",
    lambda c: "Quelle température fait-il ?",
    lambda c: "Le vent souffle fort",
    lambda c: "Il neige",
    lambda c: "C'est nuageux",
    lambda c: "La météo est pourrie",
    # 57-66. Messages non liés - Humeur/Santé
    lambda c: "Je suis de bonne humeur",
    lambda c: "Je me sens mal",
    lambda c: "J'ai mal à la tête",
    lambda c: "Je suis fatigué",
    lambda c: "Je suis content",
    lambda c: "Je suis triste",
    lambda c: "Je suis stressé",
    lambda c: "Je me sens bien",
    lambda c: "J'ai faim",
    lambda c: "Je suis en forme",
    # 67-76. Messages non liés - Tâches
    lambda c: "Je dois faire les courses",
    lambda c: "J'ai un rendez-vous chez le médecin",
    lambda c: "Je dois appeler ma mère",
    lambda c: "J'ai du travail à faire",
    lambda c: "Je dois laver la vaisselle",
    lambda c: "Je dois faire le ménage",
    lambda c: "J'ai un examen demain",
    lambda c: "Je dois préparer le dîner",
    lambda c: "J'ai une réunion importante",
    lambda c: "Je dois aller au supermarché",
    # 77-86. Bruit - Phrases incomplètes
    lambda c: "je veux",
    lambda c: "aller",
    lambda c: "train",
    lambda c: "de",
    lambda c: "à",
    lambda c: "depuis",
    lambda c: "vers",
    lambda c: "trajet",
    lambda c: "billet",
    lambda c: "voyage",
    # 87-96. Bruit - Mots aléatoires/Emoji seuls
    lambda c: "🚆",
    lambda c: "✈️",
    lambda c: "🚄",
    lambda c: "mdr lol",
    lambda c: "asdf",
    lambda c: "qwerty",
    lambda c: "123456",
    lambda c: "test test",
    lambda c: "blabla",
    lambda c: "truc machin",
    # 97-106. Questions générales non liées
    lambda c: f"Quelle est la population de {c['dep_txt']} ?",
    lambda c: f"Quelle est l'histoire de {c['arr_txt']} ?",
    lambda c: f"Où se trouve {c['dep_txt']} sur la carte ?",
    lambda c: f"Quel est le code postal de {c['arr_txt']} ?",
    lambda c: f"Quelle est la superficie de {c['dep_txt']} ?",
    lambda c: f"Quels sont les monuments de {c['arr_txt']} ?",
    lambda c: f"Quelle est la capitale de la région de {c['dep_txt']} ?",
    lambda c: f"Combien d'habitants à {c['arr_txt']} ?",
    lambda c: f"Quel est le maire de {c['dep_txt']} ?",
    lambda c: f"Quelle est la spécialité culinaire de {c['arr_txt']} ?",
    # 107-116. Métalangage
    lambda c: "Peux-tu me donner un exemple de phrase ?",
    lambda c: "Comment formuler une demande de trajet ?",
    lambda c: "Qu'est-ce qu'une phrase valide ?",
    lambda c: "Montre-moi un exemple",
    lambda c: "Comment dire que je veux voyager ?",
    lambda c: "Quelle est la syntaxe correcte ?",
    lambda c: "Peux-tu m'expliquer comment demander un trajet ?",
    lambda c: "Donne-moi un modèle de phrase",
    lambda c: "Comment écrire une demande ?",
    lambda c: "Quel est le format attendu ?",
    # 117-126. Pièges "aller" hors contexte
    lambda c: "Je vais bien",
    lambda c: "Je vais manger",
    lambda c: "Je vais dormir",
    lambda c: "Je vais travailler",
    lambda c: "Je vais faire du sport",
    lambda c: "Je vais prendre une douche",
    lambda c: "Je vais lire un livre",
    lambda c: "Je vais regarder la télé",
    lambda c: "Je vais cuisiner",
    lambda c: "Je vais me reposer",
    # 127-136. Parle d'un autre voyageur
    lambda c: f"Mon frère va de {c['dep_txt']} à {c['arr_txt']}",
    lambda c: f"Ma sœur part de {c['dep_txt']} pour {c['arr_txt']}",
    lambda c: f"Mon père va à {c['arr_txt']} depuis {c['dep_txt']}",
    lambda c: f"Ma mère part de {c['dep_txt']} vers {c['arr_txt']}",
    lambda c: f"Mon collègue va de {c['dep_txt']} à {c['arr_txt']}",
    lambda c: f"Mon voisin part de {c['dep_txt']} pour {c['arr_txt']}",
    lambda c: f"Mon ami va de {c['dep_txt']} à {c['arr_txt']} demain",
    lambda c: f"Ma copine part de {c['dep_txt']} vers {c['arr_txt']}",
    lambda c: f"Mon copain va de {c['dep_txt']} à {c['arr_txt']}",
    lambda c: f"Mon cousin part de {c['dep_txt']} pour {c['arr_txt']}",
    # 137-146. Fictif/Impossible
    lambda c: "Je vais de la Terre à Mars",
    lambda c: "Trajet vers la Lune",
    lambda c: f"Je pars de {random.choice(FICTIVE_CITIES)} pour aller sur Jupiter",
    lambda c: "Voyage vers une autre galaxie",
    lambda c: f"Billet {random.choice(FICTIVE_CITIES)} Alpha Centauri",
    lambda c: "Aller dans le passé",
    lambda c: "Voyage dans le futur",
    lambda c: f"Trajet {random.choice(FICTIVE_CITIES)} Atlantide",
    lambda c: "Je vais à Shangri-La",
    lambda c: "Partir vers l'El Dorado",
    # 147-156. Infos ferroviaires sans demande
    lambda c: "Il y a des retards sur la ligne",
    lambda c: "La grève est prévue demain",
    lambda c: "Les trains sont en panne",
    lambda c: "La SNCF annonce des perturbations",
    lambda c: "Les billets sont en rupture",
    lambda c: "Le TGV est complet",
    lambda c: "Il y a des travaux sur la voie",
    lambda c: "La ligne est fermée",
    lambda c: "Les trains sont annulés",
    lambda c: "Il y a un incident technique",
    # 157-166. Récits
    lambda c: f"Dans mon livre, le héros va de {c['dep_txt']} à {c['arr_txt']}",
    lambda c: f"Dans le film, ils partent de {c['dep_txt']} vers {c['arr_txt']}",
    lambda c: f"L'histoire raconte un voyage de {c['dep_txt']} à {c['arr_txt']}",
    lambda c: f"Le personnage principal va de {c['dep_txt']} à {c['arr_txt']}",
    lambda c: f"Dans la série, ils voyagent de {c['dep_txt']} à {c['arr_txt']}",
    lambda c: f"Le roman parle d'un trajet de {c['dep_txt']} à {c['arr_txt']}",
    lambda c: f"Dans la pièce de théâtre, il va de {c['dep_txt']} à {c['arr_txt']}",
    lambda c: f"L'auteur décrit un voyage de {c['dep_txt']} à {c['arr_txt']}",
    lambda c: f"Le scénario montre un trajet de {c['dep_txt']} à {c['arr_txt']}",
    lambda c: f"Dans la nouvelle, ils partent de {c['dep_txt']} vers {c['arr_txt']}",
]


# --- Generation ---
def generate_valid_sentence(
    pattern_func: PatternFunc,
    valid_patterns_list: Optional[List[PatternFunc]] = None,
    valid_weights: Optional[List[float]] = None
) -> Dict[str, Optional[str]]:
    context = build_context()
    sentence, dep_label, arr_label = pattern_func(context)
    sentence = finalize_sentence(sentence)
    
    # Cas spécial : si dep_label et arr_label sont None, c'est un pattern invalid
    # (ex: pattern avec transport invalid comme bateau/avion)
    is_valid = 1 if (dep_label is not None or arr_label is not None) else 0
    
    return {
        "sentence": sentence,
        "departure": dep_label,
        "arrival": arr_label,
        "is_valid": is_valid,
    }


def generate_invalid_sentence(
    invalid_patterns_list: Optional[List[InvalidPatternFunc]] = None,
    invalid_weights: Optional[List[float]] = None
) -> Dict[str, Optional[str]]:
    if invalid_patterns_list is None:
        invalid_patterns_list = INVALID_PATTERNS
    if invalid_weights is None:
        invalid_weights = DEFAULT_INVALID_PATTERN_WEIGHTS
    
    # Ajuster les poids si nécessaire
    if len(invalid_weights) < len(invalid_patterns_list):
        invalid_weights = invalid_weights + [1.0] * (len(invalid_patterns_list) - len(invalid_weights))
    elif len(invalid_weights) > len(invalid_patterns_list):
        invalid_weights = invalid_weights[:len(invalid_patterns_list)]
    
    # Créer un contexte pour les patterns invalides (comme pour les patterns valides)
    context = build_context()
    
    pattern_idx = weighted_choice(invalid_patterns_list, invalid_weights)
    sentence = invalid_patterns_list[pattern_idx](context)
    sentence = finalize_sentence(sentence)
    return {"sentence": sentence, "departure": None, "arrival": None, "is_valid": 0}


def generate_dataset(
    total: int = TOTAL_SENTENCES,
    invalid_ratio: float = INVALID_RATIO,
    seed: Optional[int] = 42,
    output_file: Path = OUTPUT_FILE,
    valid_pattern_weights: Optional[List[float]] = None,
    invalid_pattern_weights: Optional[List[float]] = None,
) -> None:
    """
    Génère un dataset de phrases de voyage.
    
    Args:
        total: Nombre total de phrases à générer
        invalid_ratio: Proportion de phrases invalides (0.0 à 1.0)
        seed: Graine aléatoire pour la reproductibilité
        output_file: Fichier de sortie
        valid_pattern_weights: Poids pour chaque pattern valide (174 patterns)
        invalid_pattern_weights: Poids pour chaque pattern invalide (166 patterns)
    """
    if seed is not None:
        random.seed(seed)

    invalid_target = max(1, int(round(total * invalid_ratio)))
    valid_target = max(1, total - invalid_target)

    patterns = valid_patterns()
    
    # Utiliser les poids fournis ou les poids par défaut
    if valid_pattern_weights is None:
        valid_pattern_weights = DEFAULT_VALID_PATTERN_WEIGHTS.copy()
    
    # Ajuster les poids si nécessaire
    if len(valid_pattern_weights) < len(patterns):
        valid_pattern_weights = valid_pattern_weights + [1.0] * (len(patterns) - len(valid_pattern_weights))
    elif len(valid_pattern_weights) > len(patterns):
        valid_pattern_weights = valid_pattern_weights[:len(patterns)]
    
    if invalid_pattern_weights is None:
        invalid_pattern_weights = DEFAULT_INVALID_PATTERN_WEIGHTS.copy()
    
    # Ajuster les poids invalides si nécessaire
    if len(invalid_pattern_weights) < len(INVALID_PATTERNS):
        invalid_pattern_weights = invalid_pattern_weights + [1.0] * (len(INVALID_PATTERNS) - len(invalid_pattern_weights))
    elif len(invalid_pattern_weights) > len(INVALID_PATTERNS):
        invalid_pattern_weights = invalid_pattern_weights[:len(INVALID_PATTERNS)]

    entries: List[Dict[str, Optional[str]]] = []
    seen: set[str] = set()

    # Générer les phrases valides avec pondération
    valid_count = 0
    max_attempts = valid_target * 10  # Limite pour éviter les boucles infinies
    attempts = 0
    
    while valid_count < valid_target and attempts < max_attempts:
        attempts += 1
        pattern_idx = weighted_choice(patterns, valid_pattern_weights)
        pattern_func = patterns[pattern_idx]
        record = generate_valid_sentence(pattern_func)
        key = record["sentence"].lower().strip()
        if key in seen:
            continue
        seen.add(key)
        entries.append(record)
        valid_count += 1

    # Générer les phrases invalides avec pondération
    invalid_count = 0
    max_attempts = invalid_target * 10
    attempts = 0
    
    while invalid_count < invalid_target and attempts < max_attempts:
        attempts += 1
        record = generate_invalid_sentence(INVALID_PATTERNS, invalid_pattern_weights)
        key = record["sentence"].lower().strip()
        if key in seen:
            continue
        seen.add(key)
        entries.append(record)
        invalid_count += 1

    random.shuffle(entries)
    output_file = Path(output_file)
    with output_file.open("w", encoding="utf-8") as f:
        for row in entries:
            json.dump(row, f, ensure_ascii=False)
            f.write("\n")

    print(f"✅ Generated {len(entries)} sentences -> {output_file}")
    print(f"   Valid: {valid_count} | Invalid: {invalid_count}")
    if valid_count < valid_target or invalid_count < invalid_target:
        print(f"   ⚠️  Attention: Objectif non atteint (trop de doublons)")


if __name__ == "__main__":
    # Exemple d'utilisation avec poids personnalisés :
    # 
    # # Augmenter la probabilité des patterns 1-5 (formes standard)
    # custom_valid_weights = DEFAULT_VALID_PATTERN_WEIGHTS.copy()
    # custom_valid_weights[0:5] = [3.0, 3.0, 3.0, 3.0, 3.0]  # Patterns 1-5 plus fréquents
    # 
    # # Réduire la probabilité de certains patterns invalides
    # custom_invalid_weights = DEFAULT_INVALID_PATTERN_WEIGHTS.copy()
    # custom_invalid_weights[0:5] = [0.5, 0.5, 0.5, 0.5, 0.5]  # Patterns 1-5 moins fréquents
    # 
    # generate_dataset(
    #     valid_pattern_weights=custom_valid_weights,
    #     invalid_pattern_weights=custom_invalid_weights
    # )
    
    generate_dataset()

