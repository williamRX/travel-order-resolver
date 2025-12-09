#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de génération d'un dataset de 15 000 phrases pour NLP
- 5 000 VALID
- 10 000 INVALID
"""

import csv
import random
from typing import Set, List

# Villes françaises variées
VILLES = [
    'Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice', 'Nantes', 'Strasbourg',
    'Montpellier', 'Bordeaux', 'Lille', 'Rennes', 'Reims', 'Le Havre', 'Saint-Étienne',
    'Toulon', 'Grenoble', 'Dijon', 'Angers', 'Nîmes', 'Villeurbanne', 'Saint-Denis',
    'Le Mans', 'Aix-en-Provence', 'Clermont-Ferrand', 'Brest', 'Limoges', 'Tours',
    'Amiens', 'Perpignan', 'Metz', 'Besançon', 'Boulogne-Billancourt', 'Orléans',
    'Mulhouse', 'Caen', 'Rouen', 'Nancy', 'Argenteuil', 'Montreuil', 'Saint-Paul',
    'Roubaix', 'Tourcoing', 'Nanterre', 'Avignon', 'Créteil', 'Dunkirk', 'Poitiers',
    'Asnières-sur-Seine', 'Versailles', 'Courbevoie', 'Vitry-sur-Seine', 'Colombes',
    'Aulnay-sous-Bois', 'La Rochelle', 'Champigny-sur-Marne', 'Rueil-Malmaison',
    'Antibes', 'Bourges', 'Cannes', 'Calais', 'Béziers', 'Mérignac', 'Drancy',
    'Mantes-la-Jolie', 'Saint-Maur-des-Fossés', 'Noisy-le-Grand', 'Colmar',
    'Issy-les-Moulineaux', 'Évry', 'Cergy', 'Pessac', 'Valence', 'Antony',
    'La Seyne-sur-Mer', 'Clichy', 'Troyes', 'Neuilly-sur-Seine', 'Villeneuve-d\'Ascq',
    'Pau', 'Hyères', 'Lorient', 'Montauban', 'Sète', 'Pantin', 'Niort', 'Vannes',
    'Belfort', 'Épinay-sur-Seine', 'Sartrouville', 'Bayonne', 'Bondy', 'Cannes',
    'Meaux', 'Grasse', 'Alès', 'Bobigny', 'Évreux', 'Laval', 'Chartres', 'Arles',
    'Clamart', 'Vincennes', 'Fontenay-sous-Bois', 'Sèvres', 'Châlons-en-Champagne',
    'Brive-la-Gaillarde', 'Châteauroux', 'Blois', 'Annecy', 'Lons-le-Saunier',
    'Auxerre', 'Nevers', 'Moulins', 'Gap', 'Digne-les-Bains', 'Briançon', 'Privas',
    'Mende', 'Rodez', 'Millau', 'Albi', 'Castres', 'Foix', 'Tarbes', 'Auch',
    'Mont-de-Marsan', 'Dax', 'Périgueux', 'Bergerac', 'Agen', 'Cahors', 'Figeac',
    'Gourdon', 'Sarlat-la-Canéda', 'Bergerac', 'Libourne', 'Arcachon', 'Biarritz',
    'Saint-Jean-de-Luz', 'Hendaye', 'Toulouse', 'Carcassonne', 'Narbonne', 'Perpignan',
    'Figueres', 'Girona', 'Barcelona', 'Valencia', 'Madrid', 'Bilbao', 'San Sebastián'
]

# Variations de mots pour VALID
VERBES_DEPART = ['aller', 'partir', 'quitter', 'rejoindre', 'me rendre', 'me déplacer', 'voyager']
VERBES_ARRIVEE = ['aller', 'rejoindre', 'arriver', 'me rendre', 'me déplacer', 'voyager']
PREPOSITIONS = ['de', 'depuis', 'à partir de', 'en partant de', 'quittant']
PREPOSITIONS_ARRIVEE = ['à', 'vers', 'jusqu\'à', 'en direction de', 'pour']
MOTS_TRAJET = ['trajet', 'itinéraire', 'voyage', 'déplacement', 'parcours', 'chemin']
MOTS_DEPART = ['départ', 'origine', 'point de départ', 'ville de départ']
MOTS_ARRIVEE = ['arrivée', 'destination', 'point d\'arrivée', 'ville d\'arrivée']

# Patterns pour INVALID
INVALID_PATTERNS = [
    lambda: f"J'aime {random.choice(VILLES)} c'est une belle ville",
    lambda: f"{random.choice(VILLES)} c'est loin je crois",
    lambda: f"Je suis à {random.choice(VILLES)}",
    lambda: f"{random.choice(VILLES)} {random.choice(VILLES)} c'est un bon match",
    lambda: "Je veux aller quelque part mais je sais pas où",
    lambda: "Train train train lalala",
    lambda: "J'ai perdu mon billet hier",
    lambda: "Est-ce que la SNCF est ouverte dimanche",
    lambda: f"je dois appeler ma mère à {random.choice(VILLES)}",
    lambda: f"Je vais acheter un vélo pour {random.choice(VILLES)}",
    lambda: "Donne-moi une liste de gares françaises",
    lambda: "vers où aller",
    lambda: "J'ai envie de voyager un jour peut-être",
    lambda: "le train c'est trop cher",
    lambda: "BONJOUR",
    lambda: "je veux aller la bas",
    lambda: f"{random.choice(VILLES)} {random.choice(VILLES)} ce sont mes amis",
    lambda: f"quelle heure est-il à {random.choice(VILLES)}",
    lambda: "Je veux partir mais aucune destination précise",
    lambda: "As-tu des infos sur les retards SNCF",
    lambda: f"Je lis un article sur {random.choice(VILLES)}",
    lambda: "Je ne veux pas prendre le train aujourd'hui",
    lambda: "J'aimerais cuisiner des pâtes à la carbonara",
    lambda: "depart ??? dest ???",
    lambda: "je veux aller de chez moi à l'école",
    lambda: f"{random.choice(VILLES)}… ou peut-être {random.choice(VILLES)}… je sais pas",
    lambda: f"Quel temps fait-il à {random.choice(VILLES)}",
    lambda: "Je n'aime pas les TGV",
    lambda: f"{random.choice(VILLES)} est joli voilà",
    lambda: "Peux-tu trouver un itinéraire",
    lambda: f"Mon chat s'appelle {random.choice(VILLES)}",
    lambda: f"{random.choice(VILLES)} c'est mon chien",
    lambda: "Je pars bientôt en vacances mais je ne sais pas où",
    lambda: f"route {random.choice(VILLES)} {random.choice(VILLES)} voiture",
    lambda: f"traiiin trajet {random.choice(VILLES)} lolz",
    lambda: "aller de * * * * *",
    lambda: f"mon copain {random.choice(VILLES)} veut venir ce soir",
    lambda: "TEST DATA 123456",
    lambda: f"J'ai entendu que {random.choice(VILLES)} est belle mais je ne voyage pas",
    lambda: "Je ne vais nulle part aujourd'hui",
    lambda: "Peux-tu me raconter l'histoire des trains",
    lambda: "J'aime les gares anciennes",
    lambda: f"{random.choice(VILLES)} sera toujours {random.choice(VILLES)}",
    lambda: "Ma destination préférée c'est la mer",
    lambda: "Pourquoi les trains sont rouges",
    lambda: "Je voudrais juste dormir",
    lambda: f"Quel est le meilleur sandwich à {random.choice(VILLES)}",
    lambda: f"Je mange un croissant à {random.choice(VILLES)}",
    lambda: f"Est-ce que {random.choice(VILLES)} fait du bon pain d'épices",
    lambda: "Je veux juste marcher un peu dehors",
    lambda: "Ceci n'est pas une phrase de trajet",
    lambda: f"J'aime le mot {random.choice(VILLES)}",
    lambda: f"Regarde cette vidéo sur {random.choice(VILLES)}",
    lambda: "Mon chien a mangé mon ticket",
    lambda: "Je suis perdu mais je ne sais pas où",
    lambda: "Peux-tu me rappeler de boire de l'eau",
    lambda: "Je veux aller très loin un jour mais pas maintenant",
    lambda: f"{random.choice(VILLES)} est jolie en été",
    lambda: "Je vais peut-être éventuellement songer à partir",
    lambda: "Les trains font trop de bruit",
    lambda: "Je suis fatigué",
    lambda: f"Est-ce que {random.choice(VILLES)} est une bonne ville pour étudier",
    lambda: f"{random.choice(VILLES)} ça s'écrit comment déjà",
    lambda: "Je dois acheter un cadeau",
    lambda: f"Le ciel est bleu à {random.choice(VILLES)}",
    lambda: "Je prends ma voiture aujourd'hui",
    lambda: "Je n'ai pas envie de sortir",
    lambda: "Qu'est-ce qu'un TGV exactement",
    lambda: f"{random.choice(VILLES)} est-elle une capitale",
    lambda: "Je fais la cuisine",
    lambda: "Je vais au sport",
    lambda: "C'est quoi la définition d'un train",
    lambda: "Je suis déjà arrivé",
    lambda: f"Un jour j'irai peut-être à {random.choice(VILLES)}",
    lambda: "Je n'ai pas de destination",
    lambda: "Je dois marcher jusqu'au supermarché",
    lambda: "Je vais juste dehors pour prendre l'air",
    lambda: f"Peux-tu écrire un poème sur {random.choice(VILLES)}",
    lambda: f"Je veux parler de {random.choice(VILLES)} mais pas y aller",
    lambda: "Ce texte est un test",
    lambda: "Je suis dans mon salon",
    lambda: "J'ai du travail à faire",
    lambda: "Peux-tu traduire ce mot",
    lambda: "Je veux aller bien dans ma vie",
    lambda: "Il fait froid",
    lambda: "Je regarde Netflix",
    lambda: "Le train c'est cool mais bref",
    lambda: f"Peux-tu me donner un synonyme de {random.choice(VILLES)}",
    lambda: "Je n'ai pas décidé si je voyage",
    lambda: "Faut-il un billet pour voyager en avion",
    lambda: "J'aime écouter de la musique",
    lambda: "Je suis juste curieux",
    lambda: "Je dois ranger ma chambre",
    lambda: "J'attends un message",
    lambda: "Ceci est une phrase totalement hors sujet"
]

def load_existing_sentences(filename: str) -> Set[str]:
    """Charge les phrases existantes pour éviter les doublons"""
    existing = set()
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing.add(row['Sentence'].lower().strip())
    except FileNotFoundError:
        pass
    return existing

def apply_typos(text: str, prob: float = 0.3) -> str:
    """Applique des fautes d'orthographe aléatoires"""
    if random.random() > prob:
        return text
    
    typos = {
        'à': ['a', 'a'],
        'é': ['e', 'e'],
        'è': ['e', 'e'],
        'ê': ['e', 'e'],
        'ç': ['c', 'c'],
        'ô': ['o', 'o'],
        'û': ['u', 'u'],
        'î': ['i', 'i'],
        'je veux': ['je veu', 'je veux'],
        'aller': ['alé', 'aller'],
        'voudrais': ['voudré', 'voudrais'],
        'depuis': ['depui', 'depuis'],
        'trajet': ['traje', 'trajet'],
        'itinéraire': ['itinerair', 'itinéraire'],
        'arrivée': ['arrivé', 'arrivée'],
        'départ': ['depart', 'départ'],
        'destination': ['dest', 'destination']
    }
    
    result = text
    for correct, wrongs in typos.items():
        if correct in result.lower() and random.random() < 0.2:
            result = result.replace(correct, random.choice(wrongs), 1)
    
    return result

def apply_case_variations(text: str) -> str:
    """Applique des variations de casse"""
    if random.random() < 0.1:
        return text.upper()
    elif random.random() < 0.2:
        return text.lower()
    elif random.random() < 0.3:
        # Première lettre en majuscule
        return text[0].upper() + text[1:].lower() if text else text
    return text

def remove_punctuation(text: str) -> str:
    """Supprime la ponctuation"""
    return text.replace('.', '').replace('!', '').replace('?', '').replace(',', '')

def generate_valid_sentence() -> str:
    """Génère une phrase VALID avec variations"""
    ville_depart = random.choice(VILLES)
    ville_arrivee = random.choice([v for v in VILLES if v != ville_depart])
    
    patterns = [
        lambda: f"je veux {random.choice(VERBES_DEPART)} {random.choice(PREPOSITIONS)} {ville_depart} {random.choice(PREPOSITIONS_ARRIVEE)} {ville_arrivee}",
        lambda: f"trajet {random.choice(PREPOSITIONS)} {ville_depart} vers {ville_arrivee}",
        lambda: f"aller {random.choice(PREPOSITIONS)} {ville_depart} {random.choice(PREPOSITIONS_ARRIVEE)} {ville_arrivee}",
        lambda: f"je pars {random.choice(PREPOSITIONS)} {ville_depart} pour {random.choice(VERBES_ARRIVEE)} {ville_arrivee}",
        lambda: f"{random.choice(MOTS_DEPART)} {ville_depart} {random.choice(MOTS_ARRIVEE)} {ville_arrivee}",
        lambda: f"depuis {ville_depart} direction {ville_arrivee}",
        lambda: f"je voudrais {random.choice(VERBES_DEPART)} {random.choice(PREPOSITIONS)} {ville_depart} {random.choice(PREPOSITIONS_ARRIVEE)} {ville_arrivee}",
        lambda: f"{random.choice(MOTS_TRAJET)} {ville_depart} {ville_arrivee}",
        lambda: f"je cherche un train {random.choice(PREPOSITIONS)} {ville_depart} vers {ville_arrivee}",
        lambda: f"donne moi un {random.choice(MOTS_TRAJET)} {random.choice(PREPOSITIONS)} {ville_depart} {random.choice(PREPOSITIONS_ARRIVEE)} {ville_arrivee}",
        lambda: f"peux-tu me trouver un train {random.choice(PREPOSITIONS)} {ville_depart} {random.choice(PREPOSITIONS_ARRIVEE)} {ville_arrivee}",
        lambda: f"je dois aller {random.choice(PREPOSITIONS_ARRIVEE)} {ville_arrivee} {random.choice(PREPOSITIONS)} {ville_depart}",
        lambda: f"je souhaite me rendre {random.choice(PREPOSITIONS_ARRIVEE)} {ville_arrivee} {random.choice(PREPOSITIONS)} {ville_depart}",
        lambda: f"j'aimerais aller {random.choice(PREPOSITIONS)} {ville_depart} {random.choice(PREPOSITIONS_ARRIVEE)} {ville_arrivee}",
        lambda: f"je veux rejoindre {ville_arrivee} {random.choice(PREPOSITIONS)} {ville_depart}",
        lambda: f"je pars {random.choice(PREPOSITIONS)} {ville_depart} arrivée {ville_arrivee}",
        lambda: f"depart {ville_depart} dest {ville_arrivee}",
        lambda: f"aller simple {random.choice(PREPOSITIONS)} {ville_depart} {random.choice(PREPOSITIONS_ARRIVEE)} {ville_arrivee}",
        lambda: f"itinéraire {ville_depart} {ville_arrivee}",
        lambda: f"train {ville_depart} {ville_arrivee}",
        lambda: f"{ville_depart} → {ville_arrivee}",
        lambda: f"{ville_depart} - {ville_arrivee}",
        lambda: f"de {ville_depart} à {ville_arrivee}",
        lambda: f"depuis {ville_depart} jusqu'à {ville_arrivee}",
        lambda: f"je veux quitter {ville_depart} pour aller {random.choice(PREPOSITIONS_ARRIVEE)} {ville_arrivee}",
        lambda: f"je vais {random.choice(PREPOSITIONS)} {ville_depart} {random.choice(PREPOSITIONS_ARRIVEE)} {ville_arrivee}",
        lambda: f"direction {ville_arrivee} {random.choice(PREPOSITIONS)} {ville_depart}",
        lambda: f"arrivée {ville_arrivee} {random.choice(MOTS_DEPART)} {ville_depart}",
        lambda: f"billet {ville_depart} {ville_arrivee}",
        lambda: f"voyage {ville_depart} {ville_arrivee}"
    ]
    
    sentence = random.choice(patterns)()
    
    # Appliquer variations
    if random.random() < 0.4:
        sentence = apply_typos(sentence)
    if random.random() < 0.3:
        sentence = apply_case_variations(sentence)
    
    sentence = remove_punctuation(sentence)
    return sentence.strip()

def generate_invalid_sentence() -> str:
    """Génère une phrase INVALID"""
    if random.random() < 0.7:
        sentence = random.choice(INVALID_PATTERNS)()
    else:
        # Phrases INVALID avec villes mais pas de trajet valide
        patterns = [
            lambda: f"je veux aller à {random.choice(VILLES)}",
            lambda: f"je pars de {random.choice(VILLES)}",
            lambda: f"trajet {random.choice(VILLES)}",
            lambda: f"aller {random.choice(VILLES)}",
            lambda: f"depuis {random.choice(VILLES)}",
            lambda: f"direction {random.choice(VILLES)}",
            lambda: f"je voudrais {random.choice(VILLES)}",
            lambda: f"je dois {random.choice(VILLES)}",
            lambda: f"train {random.choice(VILLES)}",
            lambda: f"billet {random.choice(VILLES)}"
        ]
        sentence = random.choice(patterns)()
    
    # Appliquer variations
    if random.random() < 0.3:
        sentence = apply_typos(sentence)
    if random.random() < 0.2:
        sentence = apply_case_variations(sentence)
    
    sentence = remove_punctuation(sentence)
    return sentence.strip()

def generate_dataset(output_file: str = 'extended_travel_dataset.csv', 
                     num_valid: int = 5000, 
                     num_invalid: int = 10000):
    """Génère le dataset complet"""
    existing = load_existing_sentences('travel_dataset.csv')
    generated = set()
    
    valid_sentences = []
    invalid_sentences = []
    
    print(f"Génération de {num_valid} phrases VALID...")
    batch_size = 1000
    for batch in range(0, num_valid, batch_size):
        current_batch = min(batch_size, num_valid - batch)
        for _ in range(current_batch * 2):  # Générer plus pour avoir assez après déduplication
            sentence = generate_valid_sentence()
            sentence_lower = sentence.lower().strip()
            if sentence_lower not in existing and sentence_lower not in generated:
                generated.add(sentence_lower)
                valid_sentences.append(sentence)
                if len(valid_sentences) >= num_valid:
                    break
        print(f"  Batch {batch//batch_size + 1}: {len(valid_sentences)}/{num_valid} phrases VALID générées")
        if len(valid_sentences) >= num_valid:
            break
    
    print(f"Génération de {num_invalid} phrases INVALID...")
    for batch in range(0, num_invalid, batch_size):
        current_batch = min(batch_size, num_invalid - batch)
        for _ in range(current_batch * 2):
            sentence = generate_invalid_sentence()
            sentence_lower = sentence.lower().strip()
            if sentence_lower not in existing and sentence_lower not in generated:
                generated.add(sentence_lower)
                invalid_sentences.append(sentence)
                if len(invalid_sentences) >= num_invalid:
                    break
        print(f"  Batch {batch//batch_size + 1}: {len(invalid_sentences)}/{num_invalid} phrases INVALID générées")
        if len(invalid_sentences) >= num_invalid:
            break
    
    # Mélanger pour plus de diversité
    random.shuffle(valid_sentences)
    random.shuffle(invalid_sentences)
    
    # Écrire dans le CSV
    print(f"Écriture dans {output_file}...")
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Sentence', 'VALIDITY'])
        
        id_counter = 1
        
        # Écrire VALID
        for sentence in valid_sentences[:num_valid]:
            writer.writerow([id_counter, sentence, 'VALID'])
            id_counter += 1
        
        # Écrire INVALID
        for sentence in invalid_sentences[:num_invalid]:
            writer.writerow([id_counter, sentence, 'INVALID'])
            id_counter += 1
    
    print(f"✅ Dataset généré avec succès!")
    print(f"   - {len(valid_sentences[:num_valid])} phrases VALID")
    print(f"   - {len(invalid_sentences[:num_invalid])} phrases INVALID")
    print(f"   - Total: {id_counter - 1} phrases")

if __name__ == '__main__':
    random.seed(42)  # Pour reproductibilité
    generate_dataset()

