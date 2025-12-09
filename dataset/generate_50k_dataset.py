#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génération d'un dataset de 50 000 phrases françaises pour NLP
Format CSV avec équilibre 40% VALID / 60% INVALID (20k / 30k)
"""

import csv
import random
from typing import Set

# Villes françaises et gares
VILLES = [
    'Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice', 'Nantes', 'Strasbourg',
    'Montpellier', 'Bordeaux', 'Lille', 'Rennes', 'Reims', 'Le Havre', 'Saint-Étienne',
    'Toulon', 'Grenoble', 'Dijon', 'Angers', 'Nîmes', 'Villeurbanne', 'Saint-Denis',
    'Le Mans', 'Aix-en-Provence', 'Clermont-Ferrand', 'Brest', 'Limoges', 'Tours',
    'Amiens', 'Perpignan', 'Metz', 'Besançon', 'Boulogne-Billancourt', 'Orléans',
    'Mulhouse', 'Caen', 'Rouen', 'Nancy', 'Roubaix', 'Tourcoing', 'Nanterre',
    'Avignon', 'Créteil', 'Dunkirk', 'Poitiers', 'Versailles', 'Courbevoie',
    'La Rochelle', 'Champigny-sur-Marne', 'Rueil-Malmaison', 'Antibes', 'Bourges',
    'Cannes', 'Calais', 'Béziers', 'Mérignac', 'Drancy', 'Colmar', 'Issy-les-Moulineaux',
    'Évry', 'Cergy', 'Pessac', 'Valence', 'Antony', 'La Seyne-sur-Mer', 'Clichy',
    'Troyes', 'Neuilly-sur-Seine', 'Villeneuve-d\'Ascq', 'Pau', 'Hyères', 'Lorient',
    'Montauban', 'Sète', 'Pantin', 'Niort', 'Vannes', 'Belfort', 'Sartrouville',
    'Bayonne', 'Meaux', 'Grasse', 'Alès', 'Bobigny', 'Évreux', 'Laval', 'Chartres',
    'Arles', 'Clamart', 'Vincennes', 'Fontenay-sous-Bois', 'Châlons-en-Champagne',
    'Brive-la-Gaillarde', 'Châteauroux', 'Blois', 'Annecy', 'Auxerre', 'Nevers',
    'Moulins', 'Gap', 'Digne-les-Bains', 'Briançon', 'Privas', 'Mende', 'Rodez',
    'Millau', 'Albi', 'Castres', 'Foix', 'Tarbes', 'Auch', 'Mont-de-Marsan', 'Dax',
    'Périgueux', 'Bergerac', 'Agen', 'Cahors', 'Figeac', 'Gourdon', 'Sarlat-la-Canéda',
    'Libourne', 'Arcachon', 'Biarritz', 'Saint-Jean-de-Luz', 'Hendaye', 'Carcassonne',
    'Narbonne', 'Figueres', 'Genève', 'Lausanne', 'Bruxelles', 'Luxembourg'
]

# Variations avec fautes
def add_typos(ville: str) -> str:
    """Ajoute des fautes d'orthographe"""
    if random.random() > 0.4:
        return ville
    
    typos_map = {
        'Paris': ['pariis', 'paris', 'Pari', 'parri'],
        'Toulouse': ['toulousse', 'toulouse', 'toulouze', 'toulouz'],
        'Marseille': ['marseile', 'marseille', 'marseil', 'marseylle'],
        'Lyon': ['lyon', 'Lyon', 'lyonn', 'lion'],
        'Bordeaux': ['bordo', 'bordeaux', 'bordaux', 'bordoeux'],
        'Lille': ['lille', 'Lille', 'lil', 'lillee'],
        'Nice': ['nice', 'Nice', 'nise', 'niss'],
        'Nantes': ['nantes', 'Nantes', 'nante', 'nant'],
        'Strasbourg': ['strasbourg', 'Strasbourg', 'strasbour', 'strasburg'],
        'Montpellier': ['montpelié', 'montpellier', 'montpelier', 'montpel'],
        'Grenoble': ['grenoble', 'Grenoble', 'grenoblle', 'grenob'],
        'Dijon': ['dijon', 'Dijon', 'dijonn', 'dij'],
        'Limoges': ['limoge', 'limoges', 'limog', 'limogess'],
        'Rennes': ['rennes', 'Rennes', 'renne', 'ren'],
        'Reims': ['reims', 'Reims', 'reim', 'reimss'],
        'Orléans': ['orleans', 'orléans', 'orlean', 'orléan'],
        'Caen': ['caen', 'Caen', 'caenn', 'can'],
        'Rouen': ['rouen', 'Rouen', 'rouenn', 'rou'],
        'Nancy': ['nancy', 'Nancy', 'nancie', 'nanc'],
        'Tours': ['tours', 'Tours', 'tour', 'toursse'],
        'Angers': ['angers', 'Angers', 'anger', 'ang'],
        'Avignon': ['avignon', 'Avignon', 'avignonn', 'avign'],
        'Nîmes': ['nimes', 'nîmes', 'nime', 'nim'],
        'Poitiers': ['poitiers', 'Poitiers', 'poitier', 'poit'],
        'Perpignan': ['perpignan', 'Perpignan', 'perpign', 'perp'],
        'Brest': ['brest', 'Brest', 'brestt', 'bres'],
        'Toulon': ['toulon', 'Toulon', 'toulonn', 'toul'],
        'Mulhouse': ['mulhouse', 'Mulhouse', 'mulhous', 'mulh'],
        'Besançon': ['besancon', 'besançon', 'besanc', 'besan'],
        'Annecy': ['annecy', 'Annecy', 'anneci', 'anne'],
        'Valence': ['valence', 'Valence', 'valenc', 'val'],
        'Clermont-Ferrand': ['clermont ferrand', 'clermont-ferrand', 'clermont', 'clerm'],
        'Saint-Étienne': ['saint etienne', 'saint-étienne', 'st etienne', 'st-étienne'],
        'Le Havre': ['le havre', 'Le Havre', 'havre', 'hav'],
        'Le Mans': ['le mans', 'Le Mans', 'mans', 'man'],
        'Pau': ['pau', 'Pau', 'pauu', 'pa'],
        'Bayonne': ['bayonne', 'Bayonne', 'bayonn', 'bay'],
        'Biarritz': ['biarritz', 'Biarritz', 'biaritz', 'biar'],
        'Cannes': ['cannes', 'Cannes', 'cann', 'can'],
        'Calais': ['calais', 'Calais', 'calai', 'cal'],
        'Dunkirk': ['dunkerque', 'Dunkerque', 'dunk', 'dun'],
        'Luxembourg': ['luxembourg', 'Luxembourg', 'lux', 'luxemb'],
        'Bruxelles': ['bruxelles', 'Bruxelles', 'brux', 'bruxel'],
        'Genève': ['geneve', 'Genève', 'gen', 'gene']
    }
    
    return typos_map.get(ville, ville.lower() if random.random() < 0.5 else ville)

def apply_case_variation(text: str) -> str:
    """Applique des variations de casse"""
    if random.random() < 0.15:
        return text.upper()
    elif random.random() < 0.3:
        return text.lower()
    elif random.random() < 0.2:
        words = text.split()
        return ' '.join(w.capitalize() if random.random() < 0.3 else w.lower() for w in words)
    return text

def add_spaces(text: str) -> str:
    """Ajoute des espaces aléatoires"""
    if random.random() < 0.1:
        return text.replace(' ', '  ').replace('à', ' à ').replace('de', ' de ')
    return text

def remove_accents_prob(text: str) -> str:
    """Supprime parfois les accents"""
    if random.random() < 0.2:
        return text.replace('é', 'e').replace('è', 'e').replace('ê', 'e').replace('à', 'a').replace('ç', 'c').replace('ô', 'o').replace('û', 'u').replace('î', 'i')
    return text

def generate_valid_sentence() -> str:
    """Génère une phrase VALID avec grande diversité"""
    ville_depart = random.choice(VILLES)
    ville_arrivee = random.choice([v for v in VILLES if v != ville_depart])
    
    ville_depart_typo = add_typos(ville_depart)
    ville_arrivee_typo = add_typos(ville_arrivee)
    
    patterns = [
        # Structures classiques
        lambda: f"je veux aller de {ville_depart_typo} à {ville_arrivee_typo}",
        lambda: f"trajet depuis {ville_depart_typo} vers {ville_arrivee_typo}",
        lambda: f"aller de {ville_depart_typo} à {ville_arrivee_typo}",
        lambda: f"je pars de {ville_depart_typo} pour rejoindre {ville_arrivee_typo}",
        lambda: f"depart {ville_depart_typo} dest {ville_arrivee_typo}",
        lambda: f"depuis {ville_depart_typo} direction {ville_arrivee_typo}",
        lambda: f"je voudrais aller de {ville_depart_typo} à {ville_arrivee_typo}",
        lambda: f"je cherche un train de {ville_depart_typo} à {ville_arrivee_typo}",
        lambda: f"donne moi un trajet de {ville_depart_typo} à {ville_arrivee_typo}",
        lambda: f"peux-tu me trouver un train de {ville_depart_typo} à {ville_arrivee_typo}",
        lambda: f"je dois aller à {ville_arrivee_typo} en partant de {ville_depart_typo}",
        lambda: f"je souhaite me rendre à {ville_arrivee_typo} depuis {ville_depart_typo}",
        lambda: f"j'aimerais aller de {ville_depart_typo} jusqu'à {ville_arrivee_typo}",
        lambda: f"je veux rejoindre {ville_arrivee_typo} depuis {ville_depart_typo}",
        lambda: f"je pars de {ville_depart_typo} arrivée {ville_arrivee_typo}",
        lambda: f"aller simple de {ville_depart_typo} à {ville_arrivee_typo}",
        lambda: f"itinéraire {ville_depart_typo} {ville_arrivee_typo}",
        lambda: f"train {ville_depart_typo} {ville_arrivee_typo}",
        lambda: f"{ville_depart_typo} → {ville_arrivee_typo}",
        lambda: f"{ville_depart_typo} - {ville_arrivee_typo}",
        lambda: f"{ville_depart_typo} > {ville_arrivee_typo}",
        lambda: f"de {ville_depart_typo} à {ville_arrivee_typo}",
        lambda: f"depuis {ville_depart_typo} jusqu'à {ville_arrivee_typo}",
        lambda: f"je veux quitter {ville_depart_typo} pour aller à {ville_arrivee_typo}",
        lambda: f"je vais de {ville_depart_typo} à {ville_arrivee_typo}",
        lambda: f"direction {ville_arrivee_typo} depuis {ville_depart_typo}",
        lambda: f"arrivée {ville_arrivee_typo} départ {ville_depart_typo}",
        lambda: f"billet {ville_depart_typo} {ville_arrivee_typo}",
        lambda: f"voyage {ville_depart_typo} {ville_arrivee_typo}",
        
        # Style SMS/colloquial
        lambda: f"jveux aller de {ville_depart_typo} a {ville_arrivee_typo}",
        lambda: f"chui a {ville_depart_typo} je dois aller sur {ville_arrivee_typo}",
        lambda: f"jveux un train pour {ville_arrivee_typo} depuis {ville_depart_typo}",
        lambda: f"aller a {ville_arrivee_typo} depuis {ville_depart_typo}",
        lambda: f"{ville_depart_typo} {ville_arrivee_typo} svp",
        lambda: f"train {ville_depart_typo} {ville_arrivee_typo} stp",
        lambda: f"j'ai besoin d'aller de {ville_depart_typo} a {ville_arrivee_typo}",
        lambda: f"on part d'où pour aller à {ville_arrivee_typo}",
        lambda: f"comment aller a {ville_arrivee_typo} depuis {ville_depart_typo}",
        lambda: f"je veux un train {ville_depart_typo} > {ville_arrivee_typo}",
        
        # Avec contexte
        lambda: f"je veux aller de {ville_depart_typo} à {ville_arrivee_typo} demain matin",
        lambda: f"trajet {ville_depart_typo} {ville_arrivee_typo} pour ce soir",
        lambda: f"aller de {ville_depart_typo} à {ville_arrivee_typo} en passant par {random.choice([v for v in VILLES if v not in [ville_depart, ville_arrivee]])}",
        lambda: f"je dois aller à {ville_arrivee_typo} depuis {ville_depart_typo} pour voir ma mère",
        lambda: f"billet {ville_depart_typo} {ville_arrivee_typo} pour un rdv",
        lambda: f"train {ville_depart_typo} {ville_arrivee_typo} avec mes bagages",
        
        # Questions
        lambda: f"comment me rendre à {ville_arrivee_typo} depuis {ville_depart_typo}",
        lambda: f"quel train existe entre {ville_depart_typo} et {ville_arrivee_typo}",
        lambda: f"peux-tu me calculer un trajet {ville_depart_typo} {ville_arrivee_typo}",
        lambda: f"quels trains sont dispo de {ville_depart_typo} vers {ville_arrivee_typo}",
        
        # Courtes/implicites
        lambda: f"{ville_depart_typo} {ville_arrivee_typo}",
        lambda: f"{ville_depart_typo} -> {ville_arrivee_typo}",
        lambda: f"dep {ville_depart_typo} arr {ville_arrivee_typo}",
        lambda: f"de {ville_depart_typo} vers {ville_arrivee_typo}",
    ]
    
    sentence = random.choice(patterns)()
    
    # Ajouter emojis parfois
    if random.random() < 0.1:
        emojis = ['🚆', '🚂', '💨', '📍', '🎫', '✈️', '🚄']
        if random.random() < 0.5:
            sentence = f"{sentence} {random.choice(emojis)}"
        else:
            sentence = f"{random.choice(emojis)} {sentence}"
    
    # Appliquer variations
    sentence = remove_accents_prob(sentence)
    sentence = apply_case_variation(sentence)
    sentence = add_spaces(sentence)
    
    return sentence.strip()

def generate_invalid_sentence() -> str:
    """Génère une phrase INVALID avec grande diversité"""
    patterns = [
        # Nonsense pur
        lambda: "Je mange une pomme",
        lambda: "mdrrr t ki",
        lambda: "asdadadasd",
        lambda: "peux pas afficher la page",
        lambda: "J'ai perdu mes clés",
        lambda: "train machin truc ??",
        lambda: "j'étais a paris avec mon pote marseille",
        lambda: "Paris est mon ami je veux juste le voir",
        lambda: "je dois appeler ma mère",
        lambda: "le train c'est trop cher",
        lambda: "BONJOUR",
        lambda: "je veux aller la bas",
        lambda: "quelle heure est-il",
        lambda: "Je veux partir mais aucune destination précise",
        lambda: "As-tu des infos sur les retards SNCF",
        lambda: "Je ne veux pas prendre le train aujourd'hui",
        lambda: "J'aimerais cuisiner des pâtes",
        lambda: "depart ??? dest ???",
        lambda: "je veux aller de chez moi à l'école",
        lambda: "Quel temps fait-il",
        lambda: "Je n'aime pas les TGV",
        lambda: "Peux-tu trouver un itinéraire",
        lambda: "Mon chat s'appelle Marseille",
        lambda: "paris c'est mon chien",
        lambda: "Je pars bientôt en vacances mais je ne sais pas où",
        lambda: "route marseille paris voiture",
        lambda: "traiiin trajet paris lolz",
        lambda: "aller de * * * * *",
        lambda: "mon copain paris veut venir ce soir",
        lambda: "TEST DATA 123456",
        lambda: "J'ai entendu que Toulouse est belle mais je ne voyage pas",
        lambda: "Je ne vais nulle part aujourd'hui",
        lambda: "Peux-tu me raconter l'histoire des trains",
        lambda: "J'aime les gares anciennes",
        lambda: "Paris sera toujours Paris",
        lambda: "Ma destination préférée c'est la mer",
        lambda: "Pourquoi les trains sont rouges",
        lambda: "Je voudrais juste dormir",
        lambda: "Quel est le meilleur sandwich",
        lambda: "Je mange un croissant",
        lambda: "Je veux juste marcher un peu dehors",
        lambda: "Ceci n'est pas une phrase de trajet",
        lambda: "J'aime le mot Bordeaux",
        lambda: "Regarde cette vidéo",
        lambda: "Mon chien a mangé mon ticket",
        lambda: "Je suis perdu mais je ne sais pas où",
        lambda: "Peux-tu me rappeler de boire de l'eau",
        lambda: "Je veux aller très loin un jour mais pas maintenant",
        lambda: "Je vais peut-être éventuellement songer à partir",
        lambda: "Les trains font trop de bruit",
        lambda: "Je suis fatigué",
        lambda: "Je dois acheter un cadeau",
        lambda: "Je prends ma voiture aujourd'hui",
        lambda: "Je n'ai pas envie de sortir",
        lambda: "Qu'est-ce qu'un TGV exactement",
        lambda: "Je fais la cuisine",
        lambda: "Je vais au sport",
        lambda: "C'est quoi la définition d'un train",
        lambda: "Je suis déjà arrivé",
        lambda: "Je n'ai pas de destination",
        lambda: "Je dois marcher jusqu'au supermarché",
        lambda: "Je vais juste dehors pour prendre l'air",
        lambda: "Ce texte est un test",
        lambda: "Je suis dans mon salon",
        lambda: "J'ai du travail à faire",
        lambda: "Peux-tu traduire ce mot",
        lambda: "Je veux aller bien dans ma vie",
        lambda: "Il fait froid",
        lambda: "Je regarde Netflix",
        lambda: "Le train c'est cool mais bref",
        lambda: "Je n'ai pas décidé si je voyage",
        lambda: "Faut-il un billet pour voyager en avion",
        lambda: "J'aime écouter de la musique",
        lambda: "Je suis juste curieux",
        lambda: "Je dois ranger ma chambre",
        lambda: "J'attends un message",
        lambda: "Ceci est une phrase totalement hors sujet",
        
        # Avec villes mais pas de trajet valide
        lambda: f"je veux aller à {random.choice(VILLES)}",
        lambda: f"je pars de {random.choice(VILLES)}",
        lambda: f"trajet {random.choice(VILLES)}",
        lambda: f"aller {random.choice(VILLES)}",
        lambda: f"depuis {random.choice(VILLES)}",
        lambda: f"direction {random.choice(VILLES)}",
        lambda: f"je voudrais {random.choice(VILLES)}",
        lambda: f"je dois {random.choice(VILLES)}",
        lambda: f"train {random.choice(VILLES)}",
        lambda: f"billet {random.choice(VILLES)}",
        lambda: f"j'aime {random.choice(VILLES)}",
        lambda: f"{random.choice(VILLES)} c'est loin",
        lambda: f"Je suis à {random.choice(VILLES)}",
        lambda: f"quelle heure est-il à {random.choice(VILLES)}",
        lambda: f"Je lis un article sur {random.choice(VILLES)}",
        lambda: f"Le ciel est bleu à {random.choice(VILLES)}",
        lambda: f"Est-ce que {random.choice(VILLES)} est une bonne ville",
        lambda: f"{random.choice(VILLES)} ça s'écrit comment",
        lambda: f"Quel est le meilleur sandwich à {random.choice(VILLES)}",
        lambda: f"Je mange un croissant à {random.choice(VILLES)}",
        
        # Nonsense avec caractères
        lambda: "asdfghjkl",
        lambda: "123456789",
        lambda: "???",
        lambda: "!!!",
        lambda: "...",
        lambda: "azertyuiop",
        lambda: "qwerty",
        lambda: "abcdefgh",
        
        # Phrases tronquées
        lambda: "je veux",
        lambda: "aller",
        lambda: "train",
        lambda: "depuis",
        lambda: "vers",
        lambda: "de",
        lambda: "à",
        
        # Phrases avec erreurs de structure
        lambda: f"je veux aller {random.choice(VILLES)} {random.choice(VILLES)}",
        lambda: f"train {random.choice(VILLES)} {random.choice(VILLES)} {random.choice(VILLES)}",
        lambda: f"aller de {random.choice(VILLES)}",
        lambda: f"depuis {random.choice(VILLES)} vers",
        lambda: f"je dois {random.choice(VILLES)} {random.choice(VILLES)}",
        lambda: f"billet {random.choice(VILLES)}",
        lambda: f"trajet {random.choice(VILLES)}",
        lambda: f"direction {random.choice(VILLES)}",
    ]
    
    sentence = random.choice(patterns)()
    
    # Appliquer variations
    if random.random() < 0.3:
        sentence = remove_accents_prob(sentence)
    if random.random() < 0.2:
        sentence = apply_case_variation(sentence)
    if random.random() < 0.1:
        sentence = add_spaces(sentence)
    
    return sentence.strip()

def generate_dataset(output_file: str = 'travel_dataset_50k.csv', 
                     num_valid: int = 20000, 
                     num_invalid: int = 30000):
    """Génère le dataset complet en CSV"""
    generated = set()
    valid_sentences = []
    invalid_sentences = []
    
    print(f"Génération de {num_valid} phrases VALID...")
    batch_size = 5000
    for batch in range(0, num_valid, batch_size):
        current_batch = min(batch_size, num_valid - batch)
        for _ in range(current_batch * 3):
            sentence = generate_valid_sentence()
            sentence_lower = sentence.lower().strip()
            if sentence_lower not in generated:
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
        for _ in range(current_batch * 3):
            sentence = generate_invalid_sentence()
            sentence_lower = sentence.lower().strip()
            if sentence_lower not in generated:
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
    print(f"   - {len(valid_sentences[:num_valid])} phrases VALID (40%)")
    print(f"   - {len(invalid_sentences[:num_invalid])} phrases INVALID (60%)")
    print(f"   - Total: {id_counter - 1} phrases")
    print(f"   - Fichier: {output_file}")

if __name__ == '__main__':
    random.seed(42)
    generate_dataset()
