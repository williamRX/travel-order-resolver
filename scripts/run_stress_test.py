#!/usr/bin/env python3
"""
Script de **stress test** pour le pipeline complet (classifieur + NER + post-processing).

Objectif :
- Tester le comportement du système sur des phrases difficiles :
  - Noms de gares/villes complexes (Port-Boulet, Schirmeck - La Broque, Saint-Quentin-en-Yvelines, etc.)
  - Abréviations (St Lazare, G de Lyon, Part Dieu)
  - Casse extrême (tout en majuscules / minuscules)
  - Typos lourdes
  - Phrases qui NE SONT PAS des commandes de trajet (doivent idéalement être rejetées ou ne pas retourner d'entités)

Utilisation :
    python scripts/run_stress_test.py
"""

import sys
from pathlib import Path
from collections import defaultdict

import pandas as pd

# Ajouter le répertoire racine au path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.pipeline import TravelIntentPipeline  # noqa: E402


def normalize(s: str | None) -> str | None:
    """Normalise une chaîne pour comparaison (strip + lower)."""
    if s is None:
        return None
    return s.strip().lower()


def run_stress_test():
    """Exécute le stress test à partir de evaluations/stress_test_examples.csv."""
    print("=" * 80)
    print("🧪 STRESS TEST DU PIPELINE (phrases difficiles / non-standard)")
    print("=" * 80)
    print()

    csv_path = PROJECT_ROOT / "evaluations" / "stress_test_examples.csv"
    if not csv_path.exists():
        print(f"❌ Fichier de stress test introuvable : {csv_path}")
        print("   Créez-le avec les colonnes : text,expected_departure,expected_arrival,category")
        return

    print(f"📂 Chargement des exemples depuis : {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"✅ {len(df)} exemples chargés\n")

    # Initialiser le pipeline sans pathfinding (on teste surtout NER + pré-traitement)
    try:
        print("🔄 Chargement du pipeline (sans pathfinding)...")
        pipeline = TravelIntentPipeline(use_pathfinding=False)
        print("✅ Pipeline chargé avec succès !\n")
    except Exception as e:
        print(f"❌ Erreur lors du chargement du pipeline : {e}")
        import traceback

        traceback.print_exc()
        return

    total = len(df)
    correct = 0
    results = []
    errors_by_category: dict[str, list[dict]] = defaultdict(list)

    print("🧪 Exécution du stress test...\n")

    for idx, row in df.iterrows():
        text = row["text"]
        expected_dep = row["expected_departure"] if pd.notna(row["expected_departure"]) else None
        expected_arr = row["expected_arrival"] if pd.notna(row["expected_arrival"]) else None
        category = row["category"] if "category" in row else "Unknown"

        try:
            result = pipeline.predict(text)
        except Exception as e:
            # En cas d'erreur, considérer comme échec
            errors_by_category[category].append(
                {
                    "text": text,
                    "expected": f"Dep: {expected_dep}, Arr: {expected_arr}",
                    "predicted": f"ERREUR PIPELINE: {e}",
                }
            )
            results.append(
                {
                    "text": text,
                    "category": category,
                    "expected_dep": expected_dep,
                    "expected_arr": expected_arr,
                    "predicted_dep": None,
                    "predicted_arr": None,
                    "valid": None,
                    "dep_match": False,
                    "arr_match": False,
                    "correct": False,
                }
            )
            continue

        pred_dep = result.get("departure")
        pred_arr = result.get("arrival")
        is_valid = result.get("valid", False)

        dep_match = normalize(pred_dep) == normalize(expected_dep)
        arr_match = normalize(pred_arr) == normalize(expected_arr)
        is_correct = dep_match and arr_match

        if is_correct:
            correct += 1
        else:
            errors_by_category[category].append(
                {
                    "text": text,
                    "expected": f"Dep: {expected_dep}, Arr: {expected_arr}",
                    "predicted": f"Dep: {pred_dep}, Arr: {pred_arr}, valid={is_valid}",
                }
            )

        results.append(
            {
                "text": text,
                "category": category,
                "expected_dep": expected_dep,
                "expected_arr": expected_arr,
                "predicted_dep": pred_dep,
                "predicted_arr": pred_arr,
                "valid": is_valid,
                "dep_match": dep_match,
                "arr_match": arr_match,
                "correct": is_correct,
            }
        )

    # Résultats globaux
    accuracy = correct / total if total > 0 else 0.0
    print("\n📊 Résultats globaux (stress test) :")
    print(f"   Exactitude : {accuracy:.2%} ({correct}/{total})")
    print(f"   Erreurs    : {total - correct}/{total}")

    # Résultats par catégorie
    print("\n📋 Résultats par catégorie :")
    for category in df["category"].unique():
        cat_results = [r for r in results if r["category"] == category]
        if not cat_results:
            continue
        cat_correct = sum(1 for r in cat_results if r["correct"])
        cat_accuracy = cat_correct / len(cat_results)
        print(f"   {category}: {cat_accuracy:.2%} ({cat_correct}/{len(cat_results)})")

    # Détail des erreurs
    if errors_by_category:
        print("\n❌ Détails des erreurs par catégorie :")
        print("=" * 80)
        for category, errs in errors_by_category.items():
            print(f"\n   Catégorie : {category} ({len(errs)} erreur(s))")
            for err in errs:
                print(f"      Texte    : {err['text']}")
                print(f"      Attendu  : {err['expected']}")
                print(f"      Prédit   : {err['predicted']}")
                print()

    print("\n" + "=" * 80)
    print("✅ Stress test terminé")
    print("=" * 80)


if __name__ == "__main__":
    run_stress_test()

