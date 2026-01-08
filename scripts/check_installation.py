#!/usr/bin/env python3
"""
Script de vérification de l'installation.
Vérifie que toutes les dépendances sont installées correctement.
"""

import sys
from pathlib import Path

def check_import(module_name, package_name=None):
    """Vérifie si un module peut être importé."""
    try:
        __import__(module_name)
        print(f"✅ {package_name or module_name}")
        return True
    except ImportError as e:
        print(f"❌ {package_name or module_name} - {e}")
        return False

def check_file(file_path, description):
    """Vérifie si un fichier existe."""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (non trouvé)")
        return False

def main():
    print("=" * 60)
    print("Vérification de l'installation")
    print("=" * 60)
    print()
    
    # Vérifier Python
    print(f"🐍 Python {sys.version}")
    print(f"   Chemin: {sys.executable}")
    print()
    
    # Vérifier les dépendances
    print("📦 Vérification des dépendances:")
    print("-" * 60)
    
    dependencies = [
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("sklearn", "scikit-learn"),
        ("matplotlib", "matplotlib"),
        ("seaborn", "seaborn"),
        ("joblib", "joblib"),
        ("jupyter", "jupyter"),
    ]
    
    all_ok = True
    for module, package in dependencies:
        if not check_import(module, package):
            all_ok = False
    
    print()
    
    # Vérifier les fichiers importants
    print("📁 Vérification des fichiers du projet:")
    print("-" * 60)
    
    files_to_check = [
        ("dataset/json/dataset.jsonl", "Dataset JSONL"),
        ("dataset/json/gares-francaises.json", "Fichier des gares"),
        ("notebooks/02_validity_classifier.ipynb", "Notebook du classifieur"),
        ("dataset/generators/dataset_generator.py", "Générateur de dataset"),
    ]
    
    for file_path, description in files_to_check:
        check_file(file_path, description)
    
    print()
    
    # Vérifier les dossiers
    print("📂 Vérification des dossiers:")
    print("-" * 60)
    
    dirs_to_check = [
        ("models/baseline", "Dossier des modèles"),
        ("checkpoints", "Dossier des checkpoints"),
        ("results", "Dossier des résultats"),
        ("logs", "Dossier des logs"),
    ]
    
    for dir_path, description in dirs_to_check:
        if Path(dir_path).exists():
            print(f"✅ {description}: {dir_path}")
        else:
            print(f"⚠️  {description}: {dir_path} (sera créé automatiquement)")
    
    print()
    
    # Résumé
    print("=" * 60)
    if all_ok:
        print("✅ Toutes les dépendances sont installées !")
        print()
        print("Prochaines étapes:")
        print("1. Générer le dataset: python dataset/generators/dataset_generator.py")
        print("2. Ouvrir Jupyter: jupyter notebook")
        print("3. Ouvrir le notebook: notebooks/02_validity_classifier.ipynb")
    else:
        print("❌ Certaines dépendances manquent.")
        print()
        print("Pour installer les dépendances:")
        print("- Avec pip: pip install -r requirements.txt")
        print("- Avec conda: conda env create -f environment.yml")
    print("=" * 60)

if __name__ == "__main__":
    main()

