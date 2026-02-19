#!/usr/bin/env python3
"""
Module d'augmentation de données pour le modèle NLP.

Implémente trois techniques d'augmentation :
1. Bruit de frappe (typos) - Inverser lettres, supprimer lettres, remplacer par voisine clavier
2. Casse et ponctuation - Variations de casse et suppression ponctuation
3. Mots parasites (filler words) - Ajout de "euh", "je pense", "du coup", etc.
"""

import random
import re
from typing import Dict, List, Tuple

# Mots parasites (filler words) pour l'augmentation
FILLER_WORDS = [
    "euh", "heu", "ben", "bah", "bon", "alors", "donc", "du coup",
    "je pense", "je crois", "je veux dire", "en fait", "genre",
    "s'il vous plaît", "svp", "stp", "please", "plz",
    "voilà", "voilà voilà", "c'est ça", "tu vois", "tu sais"
]

# Clavier QWERTY français pour les erreurs de frappe
KEYBOARD_NEIGHBORS = {
    'a': ['q', 'z', 'e', 's'],
    'b': ['v', 'g', 'h', 'n'],
    'c': ['x', 'd', 'f', 'v'],
    'd': ['s', 'e', 'r', 'f', 'c', 'x'],
    'e': ['é', 'è', 'ê', 'd', 'f', 'r'],
    'f': ['d', 'r', 't', 'g', 'v', 'c'],
    'g': ['f', 't', 'y', 'h', 'b', 'v'],
    'h': ['g', 'y', 'u', 'j', 'n', 'b'],
    'i': ['u', 'j', 'k', 'o', 'î', 'ï'],
    'j': ['h', 'u', 'i', 'k', 'm', 'n'],
    'k': ['j', 'i', 'o', 'l', 'm'],
    'l': ['k', 'o', 'p', 'm'],
    'm': ['l', 'p', 'n', 'j'],
    'n': ['b', 'h', 'j', 'm'],
    'o': ['i', 'k', 'l', 'p'],
    'p': ['o', 'l', 'm'],
    'q': ['a', 's', 'w'],
    'r': ['e', 'd', 'f', 't'],
    's': ['a', 'z', 'e', 'd', 'x', 'w'],
    't': ['r', 'f', 'g', 'y'],
    'u': ['y', 'h', 'j', 'i'],
    'v': ['c', 'f', 'g', 'b'],
    'w': ['q', 's', 'x'],
    'x': ['z', 's', 'd', 'c', 'w'],
    'y': ['t', 'g', 'h', 'u'],
    'z': ['a', 's', 'x', 'w'],
    'é': ['e', 'è', 'ê'],
    'è': ['é', 'e', 'ê'],
    'ê': ['é', 'è', 'e'],
    'à': ['a', 'q'],
    'ç': ['c', 'x'],
    'ù': ['u', 'i'],
    'ô': ['o', 'p'],
    'î': ['i', 'u'],
    'ï': ['i', 'u'],
    'û': ['u', 'i'],
    'â': ['a', 'q'],
    'ë': ['e', 'd'],
    'ü': ['u', 'i'],
    'ö': ['o', 'p'],
}

def introduce_typos(text: str, probability: float = 0.15) -> str:
    """
    Introduit des fautes de frappe dans le texte.
    
    Techniques :
    - Inverser deux lettres adjacentes (ex: "Paris" -> "Prais")
    - Supprimer une lettre (ex: "Paris" -> "Pris")
    - Remplacer une lettre par sa voisine sur le clavier (ex: "Paris" -> "Parid")
    - Doubler une lettre (ex: "Paris" -> "Pparis")
    
    Args:
        text: Texte à modifier
        probability: Probabilité d'introduire une faute par mot (0.0 à 1.0)
    
    Returns:
        Texte avec fautes de frappe
    """
    if not text or probability <= 0:
        return text
    
    words = text.split()
    modified_words = []
    
    for word in words:
        if len(word) < 3 or random.random() > probability:
            # Mot trop court ou pas de modification
            modified_words.append(word)
            continue
        
        word_lower = word.lower()
        is_upper = word.isupper()
        is_title = word.istitle()
        
        # Choisir une technique aléatoirement
        technique = random.choice(['swap', 'delete', 'replace', 'double'])
        
        if technique == 'swap' and len(word) >= 2:
            # Inverser deux lettres adjacentes
            idx = random.randint(0, len(word) - 2)
            chars = list(word)
            chars[idx], chars[idx + 1] = chars[idx + 1], chars[idx]
            word = ''.join(chars)
        
        elif technique == 'delete' and len(word) >= 3:
            # Supprimer une lettre (pas la première ni la dernière)
            idx = random.randint(1, len(word) - 2)
            word = word[:idx] + word[idx + 1:]
        
        elif technique == 'replace' and len(word) >= 2:
            # Remplacer par une lettre voisine sur le clavier
            idx = random.randint(0, len(word) - 1)
            char = word_lower[idx]
            if char in KEYBOARD_NEIGHBORS:
                neighbors = KEYBOARD_NEIGHBORS[char]
                replacement = random.choice(neighbors)
                # Préserver la casse
                if word[idx].isupper():
                    replacement = replacement.upper()
                elif is_title and idx == 0:
                    replacement = replacement.upper()
                word = word[:idx] + replacement + word[idx + 1:]
        
        elif technique == 'double' and len(word) >= 2:
            # Doubler une lettre
            idx = random.randint(0, len(word) - 1)
            word = word[:idx] + word[idx] + word[idx:]
        
        # Restaurer la casse originale
        if is_upper:
            word = word.upper()
        elif is_title:
            word = word.capitalize()
        
        modified_words.append(word)
    
    return ' '.join(modified_words)


def vary_case_and_punctuation(text: str) -> str:
    """
    Varie la casse et la ponctuation du texte.
    
    Techniques :
    - Tout en minuscules
    - Tout en majuscules
    - Supprimer ponctuation (points, virgules, points d'interrogation)
    - Supprimer espaces multiples
    
    Args:
        text: Texte à modifier
    
    Returns:
        Texte avec variations de casse/ponctuation
    """
    if not text:
        return text
    
    # Choisir une variation - privilégier lower et upper pour améliorer la détection des casse
    # Poids: lower 35%, upper 35%, remove_punct 20%, mixed 10%
    rand = random.random()
    if rand < 0.35:
        variation = 'lower'
    elif rand < 0.70:
        variation = 'upper'
    elif rand < 0.90:
        variation = 'remove_punct'
    else:
        variation = 'mixed'
    
    if variation == 'lower':
        return text.lower()
    
    elif variation == 'upper':
        return text.upper()
    
    elif variation == 'remove_punct':
        # Supprimer ponctuation mais garder les espaces
        text = re.sub(r'[.,!?;:()\[\]{}"\']', '', text)
        # Supprimer espaces multiples
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    elif variation == 'mixed':
        # Mélange de casse aléatoire
        words = text.split()
        mixed_words = []
        for word in words:
            if random.random() < 0.3:
                mixed_words.append(word.upper())
            elif random.random() < 0.5:
                mixed_words.append(word.lower())
            else:
                mixed_words.append(word.capitalize())
        return ' '.join(mixed_words)
    
    return text


def add_filler_words(text: str, probability: float = 0.20) -> str:
    """
    Ajoute des mots parasites (filler words) dans le texte.
    
    Techniques :
    - Ajouter "euh", "heu" au début ou au milieu
    - Ajouter "je pense", "je crois" avant une phrase
    - Ajouter "du coup", "en fait" au milieu
    - Ajouter "s'il vous plaît", "svp" à la fin
    
    Args:
        text: Texte à modifier
        probability: Probabilité d'ajouter un filler word (0.0 à 1.0)
    
    Returns:
        Texte avec mots parasites ajoutés
    """
    if not text or probability <= 0 or random.random() > probability:
        return text
    
    filler = random.choice(FILLER_WORDS)
    position = random.choice(['start', 'middle', 'end'])
    
    if position == 'start':
        # Ajouter au début
        return f"{filler} {text}"
    
    elif position == 'middle' and len(text.split()) > 3:
        # Ajouter au milieu (après le premier ou deuxième mot)
        words = text.split()
        insert_pos = random.randint(1, min(3, len(words) - 1))
        words.insert(insert_pos, filler)
        return ' '.join(words)
    
    elif position == 'end':
        # Ajouter à la fin
        return f"{text} {filler}"
    
    return text


def augment_sentence(text: str, entities: List[List], apply_typos: bool = True, 
                    apply_case: bool = True, apply_fillers: bool = True) -> Tuple[str, List[List]]:
    """
    Applique l'augmentation de données à une phrase et ajuste les positions des entités.
    
    IMPORTANT: Applique UNE SEULE technique à la fois pour mieux contrôler l'ajustement des entités.
    
    Args:
        text: Texte original
        entities: Liste des entités [[start, end, label], ...]
        apply_typos: Appliquer les typos
        apply_case: Appliquer les variations de casse
        apply_fillers: Appliquer les mots parasites
    
    Returns:
        Tuple (texte augmenté, entités ajustées)
    """
    if not entities:
        # Si pas d'entités, on peut appliquer n'importe quelle technique
        techniques = []
        if apply_typos:
            techniques.append('typos')
        if apply_case:
            techniques.append('case')
        if apply_fillers:
            techniques.append('fillers')
        
        if not techniques:
            return text, entities
        
        technique = random.choice(techniques)
        if technique == 'typos':
            return introduce_typos(text, probability=0.15), entities
        elif technique == 'case':
            return vary_case_and_punctuation(text), entities
        elif technique == 'fillers':
            return add_filler_words(text, probability=0.20), entities
    
    # Si on a des entités, choisir une technique qui préserve mieux les positions
    # Priorité: case > typos > fillers (car case ne change pas les positions)
    augmented_text = text
    adjusted_entities = entities.copy()
    
    # Choisir UNE technique aléatoirement (pas toutes en même temps)
    techniques = []
    if apply_case:
        techniques.append('case')  # Priorité car ne change pas les positions
    if apply_typos:
        techniques.append('typos')
    if apply_fillers:
        techniques.append('fillers')
    
    if not techniques:
        return text, entities
    
    technique = random.choice(techniques)
    
    if technique == 'case':
        # Variations de casse - ne change pas les positions
        augmented_text = vary_case_and_punctuation(augmented_text)
        # Pas besoin d'ajuster les entités
    
    elif technique == 'typos':
        # Typos - peut changer légèrement les positions
        augmented_text = introduce_typos(augmented_text, probability=0.15)
        adjusted_entities = adjust_entities_after_typos(text, augmented_text, adjusted_entities)
    
    elif technique == 'fillers':
        # Mots parasites - change les positions
        augmented_text = add_filler_words(augmented_text, probability=0.20)
        if augmented_text != text:
            adjusted_entities = adjust_entities_after_fillers(text, augmented_text, adjusted_entities)
    
    return augmented_text, adjusted_entities


def adjust_entities_after_typos(original_text: str, modified_text: str, 
                               entities: List[List]) -> List[List]:
    """
    Ajuste les positions des entités après introduction de typos.
    
    Les typos peuvent changer la longueur du texte, donc on doit réajuster.
    """
    if original_text == modified_text:
        return entities
    
    adjusted = []
    for start, end, label in entities:
        if start >= len(original_text) or end > len(original_text):
            continue
        
        # Extraire le texte de l'entité
        entity_text = original_text[start:end]
        entity_lower = entity_text.lower()
        
        # Chercher dans le texte modifié (insensible à la casse)
        # Zone de recherche autour de la position originale
        search_start = max(0, start - 20)
        search_end = min(len(modified_text), end + 20)
        search_zone = modified_text[search_start:search_end].lower()
        
        # Chercher le texte de l'entité (ou une variante avec typos)
        found = False
        # Essayer d'abord le texte exact
        idx = search_zone.find(entity_lower)
        if idx != -1:
            new_start = search_start + idx
            new_end = new_start + len(entity_text)
            adjusted.append([new_start, new_end, label])
            found = True
        else:
            # Chercher par préfixe (3-4 premiers caractères)
            if len(entity_lower) >= 4:
                prefix = entity_lower[:4]
                idx = search_zone.find(prefix)
                if idx != -1:
                    # Estimer la fin
                    estimated_end = search_start + idx + len(entity_text)
                    if estimated_end <= len(modified_text):
                        adjusted.append([search_start + idx, estimated_end, label])
                        found = True
        
        # Si pas trouvé, essayer de chercher dans tout le texte
        if not found:
            idx = modified_text.lower().find(entity_lower)
            if idx != -1:
                adjusted.append([idx, idx + len(entity_text), label])
    
    return adjusted


def adjust_entities_after_fillers(original_text: str, modified_text: str,
                                  entities: List[List]) -> List[List]:
    """
    Ajuste les positions des entités après ajout de mots parasites.
    
    Les filler words ajoutent des caractères, donc on doit décaler les positions.
    Utilise une approche de recherche pour trouver où le filler a été ajouté.
    """
    if original_text == modified_text:
        return entities
    
    # Si le texte modifié commence par un filler, tout est décalé
    for filler in FILLER_WORDS:
        filler_with_space = filler + " "
        if modified_text.lower().startswith(filler_with_space.lower()):
            filler_length = len(filler_with_space)
            adjusted = []
            for start, end, label in entities:
                adjusted.append([start + filler_length, end + filler_length, label])
            return adjusted
    
    # Si le texte modifié se termine par un filler, pas besoin d'ajuster
    for filler in FILLER_WORDS:
        filler_with_space = " " + filler
        if modified_text.lower().endswith(filler_with_space.lower()):
            return entities
    
    # Filler ajouté au milieu - chercher la position d'insertion
    # Comparer les mots pour trouver où le filler a été inséré
    original_words = original_text.split()
    modified_words = modified_text.split()
    
    if len(modified_words) > len(original_words):
        # Un mot a été ajouté - trouver où
        for i in range(min(len(original_words), len(modified_words))):
            if i < len(original_words) and i < len(modified_words):
                if original_words[i] != modified_words[i]:
                    # Filler inséré avant ce mot (index i)
                    # Calculer la position dans le texte original
                    if i == 0:
                        prefix_orig_length = 0
                    else:
                        prefix_orig = ' '.join(original_words[:i])
                        prefix_orig_length = len(prefix_orig) + 1  # +1 pour l'espace
                    
                    # Calculer la position dans le texte modifié
                    if i == 0:
                        prefix_mod_length = 0
                    else:
                        prefix_mod = ' '.join(modified_words[:i])
                        prefix_mod_length = len(prefix_mod) + 1  # +1 pour l'espace
                    
                    # Le filler ajouté fait la différence
                    filler_length = prefix_mod_length - prefix_orig_length
                    
                    adjusted = []
                    for start, end, label in entities:
                        if start >= prefix_orig_length:
                            # Entité après l'insertion - décaler
                            adjusted.append([start + filler_length, end + filler_length, label])
                        else:
                            # Entité avant l'insertion - garder la position
                            adjusted.append([start, end, label])
                    return adjusted
        
        # Si on n'a pas trouvé de différence, le filler est peut-être à la fin
        # (mais on l'a déjà géré ci-dessus)
        pass
    
    # Si pas de changement détecté, retourner tel quel
    return entities


def augment_dataset(dataset: List[Dict], augmentation_ratio: float = 0.10,
                   apply_typos: bool = True, apply_case: bool = True, 
                   apply_fillers: bool = True) -> List[Dict]:
    """
    Applique l'augmentation de données à un dataset.
    
    Args:
        dataset: Liste de dictionnaires avec 'text' et 'entities'
        augmentation_ratio: Ratio de phrases à augmenter (0.10 = 10%)
        apply_typos: Appliquer les typos
        apply_case: Appliquer les variations de casse
        apply_fillers: Appliquer les mots parasites
    
    Returns:
        Dataset augmenté (original + phrases augmentées)
    """
    augmented_dataset = dataset.copy()
    
    # Sélectionner un sous-ensemble de phrases à augmenter
    num_to_augment = int(len(dataset) * augmentation_ratio)
    indices_to_augment = random.sample(range(len(dataset)), min(num_to_augment, len(dataset)))
    
    augmented_examples = []
    for idx in indices_to_augment:
        original = dataset[idx]
        text = original['text']
        entities = original['entities']
        
        # Appliquer l'augmentation
        augmented_text, adjusted_entities = augment_sentence(
            text, entities, apply_typos, apply_case, apply_fillers
        )
        
        # Ne garder que si le texte a changé et qu'on a toujours des entités valides
        if augmented_text != text:
            augmented_examples.append({
                'text': augmented_text,
                'entities': adjusted_entities
            })
    
    # Ajouter les exemples augmentés au dataset
    augmented_dataset.extend(augmented_examples)
    
    return augmented_dataset
