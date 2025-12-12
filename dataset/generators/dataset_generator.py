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

# Poids par défaut pour chaque pattern (ajustables)
# Les poids déterminent la probabilité relative d'utilisation de chaque pattern
# Plus le poids est élevé, plus le pattern sera utilisé fréquemment
DEFAULT_VALID_PATTERN_WEIGHTS: List[float] = [
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 1-10
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 11-20
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 21-30
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 31-40
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 41-50
    1.0, 1.0,  # 51-52
]

# Poids par défaut pour les patterns invalides (37 patterns)
DEFAULT_INVALID_PATTERN_WEIGHTS: List[float] = [
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 1-10
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 11-20
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 21-30
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # 31-37
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
    ]


INVALID_PATTERNS: List[Callable[[], str]] = [
    lambda: "Je mange une pomme",
    lambda: "mdrrr t ki",
    lambda: "asdadadasd",
    lambda: "peux pas afficher la page",
    lambda: "J'ai perdu mes clés",
    lambda: "le train c'est trop cher",
    lambda: "je dois appeler ma mère",
    lambda: "j'aimerais cuisiner des pâtes",
    lambda: "Je ne vais nulle part aujourd'hui",
    lambda: "Je voudrais juste dormir",
    lambda: "Je regarde Netflix",
    lambda: "Je suis fatigué",
    lambda: "je veux aller la bas",
    lambda: "Qu'est-ce qu'un TGV exactement",
    lambda: f"j'hésite entre {pick_city()} et {pick_city()}",
    lambda: f"j'aime {pick_city()}",
    lambda: f"je suis à {pick_city()}",
    lambda: f"{pick_city()} est jolie",
    lambda: f"mon chat s'appelle {pick_city()}",
    lambda: f"je dois aller peut etre {pick_city()} un jour",
    lambda: f"{pick_city()} ou {pick_city()} ???",
    lambda: f"Je lis un article sur {pick_city()}",
    lambda: f"Je regarde un match à {pick_city()}",
    lambda: f"je reste à la maison pas de voyage",
    lambda: f"peux tu me raconter l'histoire de {pick_city()}",
    lambda: "je dois ranger ma chambre",
    lambda: "je n'ai pas de destination",
    lambda: "Ceci n'est pas une phrase de trajet",
    lambda: "aller de * * * * *",
    lambda: "train machin truc ??",
    lambda: f"peut etre {pick_city()} mais j'sais pas",
    lambda: f"Je passe par {pick_city()} pour manger",
    lambda: f"Je veux aller bien dans ma vie",
    lambda: "Je vais peut-être éventuellement songer à partir",
    lambda: "???",
    lambda: "!!!",
    lambda: "..."
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
    return {
        "sentence": sentence,
        "departure": dep_label,
        "arrival": arr_label,
        "is_valid": 1,
    }


def generate_invalid_sentence(
    invalid_patterns_list: Optional[List[Callable[[], str]]] = None,
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
    
    pattern_idx = weighted_choice(invalid_patterns_list, invalid_weights)
    sentence = invalid_patterns_list[pattern_idx]()
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
        valid_pattern_weights: Poids pour chaque pattern valide (52 patterns)
        invalid_pattern_weights: Poids pour chaque pattern invalide (37 patterns)
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

