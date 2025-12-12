#!/usr/bin/env python3
"""
Script pour convertir dataset.jsonl en format spaCy pour l'extraction de villes.

Format spaCy NER:
{
    "text": "Je vais de Paris à Lyon",
    "entities": [[10, 15, "DEPARTURE"], [18, 22, "ARRIVAL"]]
}
"""

import json
import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Chemins
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
INPUT_FILE = PROJECT_ROOT / "dataset" / "json" / "dataset.jsonl"
OUTPUT_DIR = PROJECT_ROOT / "dataset" / "json" / "jsonl_extracteur"
OUTPUT_FILE = OUTPUT_DIR / "spacy_training_data.jsonl"


def normalize_text(text: str) -> str:
    """Normalise le texte pour la comparaison (minuscules, accents, espaces)."""
    # Enlever les accents
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    # Minuscules et normalisation des espaces
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def find_city_position(
    text: str, city: str, case_sensitive: bool = False
) -> Optional[Tuple[int, int]]:
    """
    Trouve la position d'une ville dans le texte.
    Gère les variations : typos, casse, accents, espaces.
    Retourne (start, end) ou None si non trouvé.
    """
    if not city:
        return None

    # Normaliser pour la recherche
    text_lower = text.lower()
    city_lower = city.lower()

    # Méthode 1: Recherche exacte (insensible à la casse)
    match = re.search(re.escape(city_lower), text_lower)
    if match:
        return (match.start(), match.end())

    # Méthode 2: Recherche avec normalisation des accents
    text_norm = normalize_text(text)
    city_norm = normalize_text(city)
    match = re.search(re.escape(city_norm), text_norm, re.IGNORECASE)
    if match:
        # Mapper la position normalisée vers le texte original
        # Approche simple : chercher dans le texte original avec la même stratégie
        match_orig = re.search(re.escape(city), text, re.IGNORECASE)
        if match_orig:
            return (match_orig.start(), match_orig.end())

    # Méthode 3: Recherche par mots clés (pour villes composées avec typos)
    city_words = re.findall(r"\w+", city_norm)
    if len(city_words) >= 2:
        # Chercher les mots principaux dans l'ordre
        pattern = r"\b" + r"\s+".join([re.escape(w) for w in city_words[:2]]) + r"\b"
        match = re.search(pattern, text_norm, re.IGNORECASE)
        if match:
            # Chercher dans le texte original
            words_orig = re.findall(r"\w+", city)
            if len(words_orig) >= 2:
                pattern_orig = r"\b" + r"\s+".join([re.escape(w) for w in words_orig[:2]]) + r"\b"
                match_orig = re.search(pattern_orig, text, re.IGNORECASE)
                if match_orig:
                    return (match_orig.start(), match_orig.end())

    # Méthode 4: Recherche par préfixe (pour typos importantes)
    if len(city_norm) >= 5:
        prefix = city_norm[:5]
        match = re.search(re.escape(prefix), text_norm, re.IGNORECASE)
        if match:
            # Chercher le mot complet à partir de cette position
            word_match = re.search(r"\w+", text_norm[match.start():])
            if word_match:
                start_norm = match.start() + word_match.start()
                end_norm = match.start() + word_match.end()
                # Mapper approximativement
                match_orig = re.search(re.escape(city[:min(10, len(city))]), text, re.IGNORECASE)
                if match_orig:
                    return (match_orig.start(), min(match_orig.end(), len(text)))

    return None


def extract_entities(
    sentence: str, departure: Optional[str], arrival: Optional[str]
) -> List[Tuple[int, int, str]]:
    """
    Extrait les entités (départ, arrivée) d'une phrase.
    Retourne une liste de (start, end, label).
    """
    entities = []

    # Chercher la ville de départ
    if departure:
        dep_pos = find_city_position(sentence, departure)
        if dep_pos:
            entities.append((dep_pos[0], dep_pos[1], "DEPARTURE"))

    # Chercher la ville d'arrivée
    if arrival:
        arr_pos = find_city_position(sentence, arrival)
        if arr_pos:
            # Vérifier qu'elle ne chevauche pas avec le départ
            start, end = arr_pos
            overlap = False
            for dep_start, dep_end, _ in entities:
                if not (end <= dep_start or start >= dep_end):
                    overlap = True
                    break
            if not overlap:
                entities.append((start, end, "ARRIVAL"))

    # Trier par position de début
    entities.sort(key=lambda x: x[0])
    return entities


def convert_to_spacy_format(
    input_file: Path, output_file: Path, min_entities: int = 1
) -> None:
    """
    Convertit dataset.jsonl en format spaCy.
    
    Args:
        input_file: Fichier dataset.jsonl d'entrée
        min_entities: Nombre minimum d'entités requises (1 = au moins départ OU arrivée)
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)

    total = 0
    converted = 0
    skipped_no_entities = 0
    skipped_invalid = 0

    print(f"📖 Lecture de {input_file}...")
    print(f"💾 Écriture dans {output_file}...\n")

    with input_file.open("r", encoding="utf-8") as infile, output_file.open(
        "w", encoding="utf-8"
    ) as outfile:
        for line_num, line in enumerate(infile, 1):
            if not line.strip():
                continue

            try:
                data = json.loads(line)
                total += 1

                sentence = data.get("sentence", "")
                departure = data.get("departure")
                arrival = data.get("arrival")
                is_valid = data.get("is_valid", 1)

                # Ne garder que les phrases valides avec au moins une ville
                if is_valid == 0:
                    skipped_invalid += 1
                    continue

                if not departure and not arrival:
                    skipped_no_entities += 1
                    continue

                # Extraire les entités
                entities = extract_entities(sentence, departure, arrival)

                # Vérifier qu'on a au moins min_entities
                if len(entities) < min_entities:
                    skipped_no_entities += 1
                    continue

                # Formater pour spaCy
                spacy_entry = {
                    "text": sentence,
                    "entities": [[start, end, label] for start, end, label in entities],
                }

                # Écrire en JSONL
                outfile.write(json.dumps(spacy_entry, ensure_ascii=False) + "\n")
                converted += 1

                if line_num % 1000 == 0:
                    print(f"  Traité {line_num} lignes... ({converted} converties)")

            except json.JSONDecodeError as e:
                print(f"⚠️  Erreur JSON ligne {line_num}: {e}")
                continue
            except Exception as e:
                print(f"⚠️  Erreur ligne {line_num}: {e}")
                continue

    print(f"\n✅ Conversion terminée!")
    print(f"   Total de lignes lues: {total}")
    print(f"   Phrases converties: {converted}")
    print(f"   Ignorées (invalid): {skipped_invalid}")
    print(f"   Ignorées (pas d'entités): {skipped_no_entities}")
    print(f"   Fichier de sortie: {output_file}")


if __name__ == "__main__":
    if not INPUT_FILE.exists():
        print(f"❌ Fichier introuvable: {INPUT_FILE}")
        exit(1)

    convert_to_spacy_format(INPUT_FILE, OUTPUT_FILE, min_entities=1)
    print(f"\n📊 Statistiques du dataset généré:")
    print(f"   Format: spaCy NER (JSONL)")
    print(f"   Labels: DEPARTURE, ARRIVAL")

