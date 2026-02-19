#!/usr/bin/env python3
"""
Script de vérification rapide pour Jupyter + GPU (MPS)
Vérifie que tout est prêt pour l'entraînement NLP en local avec GPU.
"""

import sys
from pathlib import Path

def check_pytorch_mps():
    """Vérifie que PyTorch avec MPS est disponible."""
    print("🔍 Vérification PyTorch + MPS...")
    try:
        import torch
        print(f"   ✅ PyTorch {torch.__version__} installé")
        
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            print(f"   ✅ MPS (GPU) disponible")
            device = torch.device("mps")
            # Test rapide
            test = torch.randn(10, 10).to(device)
            _ = torch.mm(test, test)
            print(f"   ✅ Test MPS réussi")
            return True, device
        else:
            print(f"   ⚠️  MPS non disponible (utilisera CPU)")
            return False, torch.device("cpu")
    except ImportError:
        print(f"   ❌ PyTorch non installé")
        return None, None
    except Exception as e:
        print(f"   ⚠️  Erreur: {e}")
        return False, torch.device("cpu")

def check_dataset():
    """Vérifie que le dataset NLP existe."""
    print("\n🔍 Vérification du dataset NLP...")
    project_root = Path(__file__).resolve().parent.parent
    dataset_path = project_root / "dataset" / "nlp" / "json" / "nlp_training_data.jsonl"
    
    if dataset_path.exists():
        # Compter les lignes
        with open(dataset_path, 'r', encoding='utf-8') as f:
            lines = sum(1 for _ in f)
        print(f"   ✅ Dataset trouvé: {dataset_path}")
        print(f"   📊 Nombre de phrases: {lines:,}")
        return True
    else:
        print(f"   ❌ Dataset non trouvé: {dataset_path}")
        print(f"   💡 Générez-le avec: python dataset/generators/nlp/dataset_generator.py")
        return False

def check_notebook():
    """Vérifie que le notebook existe."""
    print("\n🔍 Vérification du notebook...")
    project_root = Path(__file__).resolve().parent.parent
    notebook_path = project_root / "nlp" / "notebooks" / "02_ner_training_camembert.ipynb"
    
    if notebook_path.exists():
        print(f"   ✅ Notebook trouvé: {notebook_path}")
        return True
    else:
        print(f"   ❌ Notebook non trouvé: {notebook_path}")
        return False

def check_dependencies():
    """Vérifie les dépendances nécessaires."""
    print("\n🔍 Vérification des dépendances...")
    dependencies = {
        "transformers": "transformers",
        "datasets": "datasets",
        "seqeval": "seqeval",
        "torch": "torch",
    }
    
    all_ok = True
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} manquant")
            all_ok = False
    
    return all_ok

def main():
    """Fonction principale."""
    print("=" * 70)
    print("🚀 Vérification Jupyter + GPU pour entraînement NLP")
    print("=" * 70)
    print()
    
    # Vérifier PyTorch + MPS
    mps_ok, device = check_pytorch_mps()
    if mps_ok is None:
        print("\n❌ PyTorch n'est pas installé. Installez-le d'abord.")
        return 1
    
    # Vérifier le dataset
    dataset_ok = check_dataset()
    
    # Vérifier le notebook
    notebook_ok = check_notebook()
    
    # Vérifier les dépendances
    deps_ok = check_dependencies()
    
    # Résumé
    print("\n" + "=" * 70)
    print("📋 RÉSUMÉ")
    print("=" * 70)
    
    if mps_ok:
        print("✅ GPU MPS disponible - Entraînement accéléré")
    else:
        print("⚠️  GPU MPS non disponible - Entraînement sur CPU (plus lent)")
    
    if dataset_ok:
        print("✅ Dataset NLP prêt")
    else:
        print("❌ Dataset NLP manquant - Générez-le d'abord")
    
    if notebook_ok:
        print("✅ Notebook trouvé")
    else:
        print("❌ Notebook non trouvé")
    
    if deps_ok:
        print("✅ Dépendances installées")
    else:
        print("❌ Dépendances manquantes - Installez-les avec: pip install -r requirements.txt")
    
    print("\n" + "=" * 70)
    
    if mps_ok and dataset_ok and notebook_ok and deps_ok:
        print("✅ TOUT EST PRÊT POUR L'ENTRAÎNEMENT!")
        print("\n📝 Prochaines étapes:")
        print("1. Lancez Jupyter: ./lancer_jupyter_simple.sh")
        print("2. Ouvrez: nlp/notebooks/02_ner_training_camembert.ipynb")
        print("3. Exécutez toutes les cellules")
        print("4. Le modèle utilisera automatiquement votre GPU MPS! 🚀")
        return 0
    else:
        print("⚠️  Certains éléments manquent - Corrigez-les avant de lancer l'entraînement")
        return 1

if __name__ == "__main__":
    sys.exit(main())
