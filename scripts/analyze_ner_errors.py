#!/usr/bin/env python3
"""
Script d'analyse des erreurs du modèle NER.
Identifie les faux positifs et analyse les patterns d'erreurs pour comprendre pourquoi la précision est faible.
"""

import json
import sys
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Tuple, Set

# Ajouter le chemin du projet
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import torch
    from transformers import CamembertForTokenClassification, CamembertTokenizerFast
    import numpy as np
    from seqeval.metrics import classification_report
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️  Transformers non disponible. Le script nécessite PyTorch et Transformers.")
    sys.exit(1)


def load_model_and_tokenizer(model_path: Path):
    """Charge le modèle et le tokenizer."""
    print(f"📦 Chargement du modèle depuis: {model_path}")
    
    tokenizer = CamembertTokenizerFast.from_pretrained(str(model_path))
    model = CamembertForTokenClassification.from_pretrained(str(model_path))
    
    # Détecter le device
    if torch.backends.mps.is_available():
        device = torch.device("mps")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")
    
    model.to(device)
    model.eval()
    
    # Charger les labels depuis config.json
    config_path = model_path / "config.json"
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
            id2label = {i: label for i, label in enumerate(config['id2label'].values())}
            label2id = {label: i for i, label in enumerate(config['id2label'].values())}
    else:
        # Labels par défaut
        id2label = {0: "O", 1: "B-DEPARTURE", 2: "I-DEPARTURE", 3: "B-ARRIVAL", 4: "I-ARRIVAL"}
        label2id = {v: k for k, v in id2label.items()}
    
    print(f"✅ Modèle chargé sur {device}")
    return model, tokenizer, id2label, label2id, device


def load_test_dataset(dataset_path: Path, limit: int = None):
    """Charge le dataset de test."""
    print(f"📂 Chargement du dataset depuis: {dataset_path}")
    
    data = []
    with open(dataset_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if limit and i >= limit:
                break
            if line.strip():
                data.append(json.loads(line))
    
    print(f"✅ {len(data)} exemples chargés")
    return data


def predict_entities(model, tokenizer, text: str, id2label: Dict, device):
    """Prédit les entités pour un texte."""
    encoding = tokenizer(
        text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=128,
        return_offsets_mapping=True
    )
    
    offset_mapping = encoding.pop('offset_mapping')[0].cpu().numpy()
    encoding = {k: v.to(device) for k, v in encoding.items()}
    
    with torch.no_grad():
        outputs = model(**encoding)
        predictions = torch.argmax(outputs.logits, dim=-1)[0].cpu().numpy()
    
    # Convertir les prédictions en labels
    labels = [id2label[pred] for pred in predictions]
    
    # Extraire les entités avec leurs positions
    entities = []
    current_entity = None
    
    for i, label in enumerate(labels):
        if label == "O":
            if current_entity:
                entities.append(current_entity)
                current_entity = None
        elif label.startswith("B-"):
            if current_entity:
                entities.append(current_entity)
            entity_type = label.split("-")[1]
            start, end = offset_mapping[i]
            current_entity = {"start": int(start), "end": int(end), "label": entity_type}
        elif label.startswith("I-"):
            if current_entity:
                entity_type = label.split("-")[1]
                if entity_type == current_entity["label"]:
                    _, end = offset_mapping[i]
                    current_entity["end"] = int(end)
    
    if current_entity:
        entities.append(current_entity)
    
    # Extraire le texte des entités
    predicted_entities = []
    for ent in entities:
        text_span = text[ent["start"]:ent["end"]]
        predicted_entities.append({
            "text": text_span,
            "label": ent["label"],
            "start": ent["start"],
            "end": ent["end"]
        })
    
    return predicted_entities


def convert_entities_to_dict(entities: List[List], text: str) -> Dict[str, List[str]]:
    """Convertit les entités au format [[start, end, label]] en dictionnaire par type."""
    result = {"DEPARTURE": [], "ARRIVAL": []}
    for start, end, label in entities:
        entity_text = text[start:end]
        if label in result:
            result[label].append(entity_text)
    return result


def analyze_errors(test_data: List[Dict], model, tokenizer, id2label: Dict, device, sample_size: int = 500):
    """Analyse les erreurs du modèle."""
    
    print(f"\n🔍 Analyse des erreurs sur {min(sample_size, len(test_data))} exemples...")
    
    false_positives = []  # Entités prédites qui n'existent pas
    false_negatives = []  # Entités réelles qui n'ont pas été prédites
    true_positives = []   # Entités correctement prédites
    error_patterns = defaultdict(list)
    
    # Statistiques par type
    stats = {
        "DEPARTURE": {"fp": [], "fn": [], "tp": []},
        "ARRIVAL": {"fp": [], "fn": [], "tp": []}
    }
    
    for i, example in enumerate(test_data[:sample_size]):
        text = example["text"]
        true_entities = example["entities"]
        
        # Prédire
        predicted_entities = predict_entities(model, tokenizer, text, id2label, device)
        
        # Convertir au format comparable
        true_dict = convert_entities_to_dict(true_entities, text)
        pred_dict = {"DEPARTURE": [], "ARRIVAL": []}
        
        for pred in predicted_entities:
            pred_dict[pred["label"]].append(pred["text"])
        
        # Comparer pour chaque type
        for entity_type in ["DEPARTURE", "ARRIVAL"]:
            true_set = set(true_dict[entity_type])
            pred_set = set(pred_dict[entity_type])
            
            # True Positives
            tp = true_set & pred_set
            stats[entity_type]["tp"].extend(tp)
            
            # False Positives
            fp = pred_set - true_set
            stats[entity_type]["fp"].extend(fp)
            for entity in fp:
                false_positives.append({
                    "text": text,
                    "predicted": entity,
                    "type": entity_type,
                    "context": extract_context(text, entity, window=30)
                })
            
            # False Negatives
            fn = true_set - pred_set
            stats[entity_type]["fn"].extend(fn)
            for entity in fn:
                false_negatives.append({
                    "text": text,
                    "missing": entity,
                    "type": entity_type,
                    "context": extract_context(text, entity, window=30)
                })
    
    return stats, false_positives, false_negatives


def extract_context(text: str, entity: str, window: int = 30) -> str:
    """Extrait le contexte autour d'une entité."""
    idx = text.find(entity)
    if idx == -1:
        return text[:window]
    
    start = max(0, idx - window)
    end = min(len(text), idx + len(entity) + window)
    context = text[start:end]
    
    if start > 0:
        context = "..." + context
    if end < len(text):
        context = context + "..."
    
    return context


def analyze_patterns(false_positives: List[Dict]):
    """Analyse les patterns dans les faux positifs."""
    
    print("\n📊 Analyse des patterns d'erreurs...")
    
    patterns = {
        "noms_propres": [],  # Mots qui commencent par majuscule
        "mots_communs": [],  # Mots en minuscules
        "gares_mentionnees": [],  # "gare de X", "gares de Y"
        "lieux_mentionnes": [],  # "ville de X", "à X", "de X"
    }
    
    gare_keywords = ["gare", "gares", "aéroport", "station"]
    lieu_keywords = ["ville", "villes", "de", "à", "depuis", "vers", "pour"]
    
    for fp in false_positives:
        predicted = fp["predicted"].lower()
        context_lower = fp["context"].lower()
        
        # Vérifier si c'est un nom propre (commence par majuscule dans le texte original)
        if fp["predicted"][0].isupper():
            patterns["noms_propres"].append(fp)
        
        # Vérifier si c'est dans un contexte de gare
        if any(kw in context_lower for kw in gare_keywords):
            patterns["gares_mentionnees"].append(fp)
        
        # Vérifier si c'est dans un contexte de lieu
        if any(kw in context_lower for kw in lieu_keywords):
            patterns["lieux_mentionnes"].append(fp)
    
    return patterns


def print_statistics(stats: Dict, false_positives: List[Dict], false_negatives: List[Dict], patterns: Dict):
    """Affiche les statistiques d'analyse."""
    
    print("\n" + "="*80)
    print("📈 RÉSUMÉ DES ERREURS")
    print("="*80)
    
    total_fp = len(false_positives)
    total_fn = len(false_negatives)
    
    for entity_type in ["DEPARTURE", "ARRIVAL"]:
        fp_count = len(stats[entity_type]["fp"])
        fn_count = len(stats[entity_type]["fn"])
        tp_count = len(stats[entity_type]["tp"])
        
        precision = tp_count / (tp_count + fp_count) if (tp_count + fp_count) > 0 else 0
        recall = tp_count / (tp_count + fn_count) if (tp_count + fn_count) > 0 else 0
        
        print(f"\n🔸 {entity_type}:")
        print(f"   True Positives:  {tp_count}")
        print(f"   False Positives: {fp_count} ({fp_count/(tp_count+fp_count)*100:.1f}% des prédictions)")
        print(f"   False Negatives: {fn_count}")
        print(f"   Precision: {precision:.3f}")
        print(f"   Recall: {recall:.3f}")
    
    print("\n" + "="*80)
    print("🔍 TOP 20 FAUX POSITIFS LES PLUS FRÉQUENTS")
    print("="*80)
    
    fp_counter = Counter([fp["predicted"].lower() for fp in false_positives])
    for entity, count in fp_counter.most_common(20):
        print(f"   '{entity}': {count} fois")
    
    print("\n" + "="*80)
    print("📝 EXEMPLES DE FAUX POSITIFS")
    print("="*80)
    
    # Afficher quelques exemples de chaque pattern
    print("\n🔸 Noms propres détectés comme villes:")
    for fp in patterns["noms_propres"][:10]:
        print(f"   Prédit: '{fp['predicted']}' (type: {fp['type']})")
        print(f"   Contexte: {fp['context']}")
        print()
    
    print("\n🔸 Entités dans contexte 'gare de X':")
    for fp in patterns["gares_mentionnees"][:10]:
        print(f"   Prédit: '{fp['predicted']}' (type: {fp['type']})")
        print(f"   Contexte: {fp['context']}")
        print()
    
    print("\n" + "="*80)
    print("💡 AXES D'AMÉLIORATION")
    print("="*80)
    
    print("\n1. **Enrichir le dataset avec plus d'exemples négatifs**")
    print("   - Ajouter des phrases avec des noms de personnes qui ne sont PAS des villes")
    print("   - Ajouter des phrases avec des mots qui ressemblent à des villes mais n'en sont pas")
    
    print("\n2. **Améliorer les patterns d'entraînement**")
    print("   - Ajouter des patterns où des noms de villes apparaissent mais ne sont PAS des entités de trajet")
    print("   - Exemples: 'Mon ami Paris habite à Lyon' → ne devrait pas annoter 'Paris' et 'Lyon'")
    
    print("\n3. **Post-processing intelligent**")
    print("   - Utiliser une liste de villes valides pour filtrer les faux positifs")
    print("   - Vérifier que les entités prédites sont dans la liste des gares françaises")
    
    print("\n4. **Ajuster les hyperparamètres d'entraînement**")
    print("   - Augmenter la régularisation (weight_decay)")
    print("   - Réduire légèrement le learning_rate")
    print("   - Entraîner plus longtemps avec early stopping basé sur la précision")
    
    print("\n5. **Analyser les erreurs spécifiques**")
    print(f"   - Les {len(patterns['noms_propres'])} faux positifs avec noms propres suggèrent une confusion avec des noms de personnes")
    print(f"   - Les {len(patterns['gares_mentionnees'])} faux positifs dans contexte 'gare' suggèrent une sur-annotation")


def main():
    """Point d'entrée principal."""
    
    if len(sys.argv) > 1:
        model_name = sys.argv[1]
    else:
        # Utiliser le dernier modèle
        models_dir = PROJECT_ROOT / "nlp" / "models"
        model_dirs = sorted([d for d in models_dir.iterdir() if d.is_dir() and d.name.startswith("ner_camembert_")])
        if not model_dirs:
            print("❌ Aucun modèle trouvé dans nlp/models/")
            sys.exit(1)
        model_name = model_dirs[-1].name
        print(f"📁 Utilisation du dernier modèle: {model_name}")
    
    model_path = PROJECT_ROOT / "nlp" / "models" / model_name
    dataset_path = PROJECT_ROOT / "dataset" / "nlp" / "json" / "nlp_training_data.jsonl"
    
    if not model_path.exists():
        print(f"❌ Modèle non trouvé: {model_path}")
        sys.exit(1)
    
    if not dataset_path.exists():
        print(f"❌ Dataset non trouvé: {dataset_path}")
        sys.exit(1)
    
    # Charger le modèle
    model, tokenizer, id2label, label2id, device = load_model_and_tokenizer(model_path)
    
    # Charger le dataset (prendre un échantillon pour l'analyse)
    test_data = load_test_dataset(dataset_path, limit=1000)
    
    # Analyser les erreurs
    stats, false_positives, false_negatives = analyze_errors(
        test_data, model, tokenizer, id2label, device, sample_size=500
    )
    
    # Analyser les patterns
    patterns = analyze_patterns(false_positives)
    
    # Afficher les statistiques
    print_statistics(stats, false_positives, false_negatives, patterns)
    
    # Sauvegarder les résultats détaillés
    results_path = PROJECT_ROOT / "nlp" / "results" / f"error_analysis_{model_name}.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    
    results = {
        "model": model_name,
        "sample_size": 500,
        "false_positives_count": len(false_positives),
        "false_negatives_count": len(false_negatives),
        "top_false_positives": dict(Counter([fp["predicted"].lower() for fp in false_positives]).most_common(50)),
        "false_positives_samples": false_positives[:100],  # Garder 100 exemples
        "false_negatives_samples": false_negatives[:100],
    }
    
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Résultats détaillés sauvegardés dans: {results_path}")


if __name__ == "__main__":
    main()
