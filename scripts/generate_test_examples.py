#!/usr/bin/env python3
"""
Script pour générer un fichier CSV de test avec des exemples variés pour vérifier les performances du modèle.

Usage:
    python scripts/generate_test_examples.py
"""

import json
import csv
import random
from pathlib import Path
from typing import Dict, List, Tuple

# Chemin vers les gares
GARES_FILE = Path("dataset/shared/gares-francaises.json")
OUTPUT_CSV = Path("evaluations/test_examples.csv")

def load_gares() -> List[Dict]:
    """Charge les gares depuis le fichier JSON."""
    with open(GARES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Le fichier peut être soit une liste, soit un dictionnaire avec 'gares'
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        return data.get('gares', [])
    else:
        return []

def generate_test_examples(gares: List[Dict], num_examples: int = 50) -> List[Dict]:
    """
    Génère des exemples de test variés.
    
    Args:
        gares: Liste des gares disponibles
        num_examples: Nombre d'exemples à générer
        
    Returns:
        Liste de dictionnaires avec 'text', 'expected_departure', 'expected_arrival'
    """
    # Sélectionner des gares variées (grandes villes + petites villes)
    gare_names = [g['nom'] for g in gares if 'nom' in g]
    large_cities = [g for g in gare_names if len(g) < 25]  # Filtrer les noms trop longs
    random.shuffle(large_cities)
    
    examples = []
    
    # Catégorie 1: Patterns simples "Ville - Ville"
    for _ in range(8):
        dep = random.choice(large_cities)
        arr = random.choice(large_cities)
        while arr == dep:
            arr = random.choice(large_cities)
        examples.append({
            'text': f"{dep} - {arr}",
            'expected_departure': dep,
            'expected_arrival': arr,
            'category': 'Ville - Ville'
        })
    
    # Catégorie 2: Patterns "Ville -> Ville"
    for _ in range(5):
        dep = random.choice(large_cities)
        arr = random.choice(large_cities)
        while arr == dep:
            arr = random.choice(large_cities)
        examples.append({
            'text': f"{dep} -> {arr}",
            'expected_departure': dep,
            'expected_arrival': arr,
            'category': 'Ville -> Ville'
        })
    
    # Catégorie 3: Patterns "Trajet Ville Ville"
    for _ in range(5):
        dep = random.choice(large_cities)
        arr = random.choice(large_cities)
        while arr == dep:
            arr = random.choice(large_cities)
        examples.append({
            'text': f"Trajet {dep} {arr}",
            'expected_departure': dep,
            'expected_arrival': arr,
            'category': 'Trajet Ville Ville'
        })
    
    # Catégorie 4: Patterns "Donne moi un trajet Sncf de Ville à Ville"
    for _ in range(4):
        dep = random.choice(large_cities)
        arr = random.choice(large_cities)
        while arr == dep:
            arr = random.choice(large_cities)
        examples.append({
            'text': f"Donne moi un trajet Sncf de {dep} à {arr}",
            'expected_departure': dep,
            'expected_arrival': arr,
            'category': 'Demande Sncf'
        })
    
    # Catégorie 5: Phrases standard "Je vais de X à Y"
    for _ in range(8):
        dep = random.choice(large_cities)
        arr = random.choice(large_cities)
        while arr == dep:
            arr = random.choice(large_cities)
        examples.append({
            'text': f"Je vais de {dep} à {arr}",
            'expected_departure': dep,
            'expected_arrival': arr,
            'category': 'Phrase standard'
        })
    
    # Catégorie 6: Avec "gare de"
    for _ in range(5):
        dep = random.choice(large_cities)
        arr = random.choice(large_cities)
        while arr == dep:
            arr = random.choice(large_cities)
        examples.append({
            'text': f"Je pars de la gare de {dep} pour {arr}",
            'expected_departure': dep,
            'expected_arrival': arr,
            'category': 'Avec gare'
        })
    
    # Catégorie 7: Avec typos
    for _ in range(5):
        dep = random.choice(large_cities)
        arr = random.choice(large_cities)
        while arr == dep:
            arr = random.choice(large_cities)
        # Ajouter quelques typos typiques
        text = f"Je veu alé de {dep} a {arr}"
        examples.append({
            'text': text,
            'expected_departure': dep,
            'expected_arrival': arr,
            'category': 'Avec typos'
        })
    
    # Catégorie 8: Questions
    for _ in range(5):
        dep = random.choice(large_cities)
        arr = random.choice(large_cities)
        while arr == dep:
            arr = random.choice(large_cities)
        examples.append({
            'text': f"Comment aller de {dep} à {arr} ?",
            'expected_departure': dep,
            'expected_arrival': arr,
            'category': 'Question'
        })
    
    # Catégorie 9: Billets
    for _ in range(3):
        dep = random.choice(large_cities)
        arr = random.choice(large_cities)
        while arr == dep:
            arr = random.choice(large_cities)
        examples.append({
            'text': f"Billet {dep} {arr}",
            'expected_departure': dep,
            'expected_arrival': arr,
            'category': 'Billet'
        })
    
    # Catégorie 10: Cas complexes (villes avec tirets dans leur nom)
    cities_with_dash = [g for g in large_cities if '-' in g][:3]
    for dep in cities_with_dash:
        arr = random.choice(large_cities)
        while arr == dep:
            arr = random.choice(large_cities)
        examples.append({
            'text': f"Trajet {dep} - {arr}",
            'expected_departure': dep,
            'expected_arrival': arr,
            'category': 'Ville avec tiret'
        })
    
    # Mélanger les exemples
    random.shuffle(examples)
    
    # Limiter au nombre demandé
    return examples[:num_examples]

def save_to_csv(examples: List[Dict], output_file: Path):
    """Sauvegarde les exemples dans un fichier CSV."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['text', 'expected_departure', 'expected_arrival', 'category'])
        writer.writeheader()
        writer.writerows(examples)
    
    print(f"✅ {len(examples)} exemples sauvegardés dans {output_file}")

def main():
    """Fonction principale."""
    print("🔄 Génération d'exemples de test...")
    
    # Charger les gares
    print(f"📖 Chargement des gares depuis {GARES_FILE}...")
    gares = load_gares()
    print(f"✅ {len(gares)} gares chargées")
    
    # Générer les exemples
    print(f"🎲 Génération de 50 exemples variés...")
    examples = generate_test_examples(gares, num_examples=50)
    
    # Statistiques par catégorie
    categories = {}
    for ex in examples:
        cat = ex['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\n📊 Répartition par catégorie:")
    for cat, count in sorted(categories.items()):
        print(f"   - {cat}: {count} exemples")
    
    # Sauvegarder
    save_to_csv(examples, OUTPUT_CSV)
    
    print(f"\n✅ Génération terminée!")
    print(f"   Fichier: {OUTPUT_CSV}")
    print(f"   Total: {len(examples)} exemples")

if __name__ == "__main__":
    main()
