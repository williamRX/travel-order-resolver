#!/usr/bin/env python3
"""
Script pour configurer un kernel Jupyter avec PyTorch MPS dans Cursor
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Exécute une commande et affiche le résultat"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} réussi")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de {description}: {e}")
        print(f"Output: {e.output}")
        return False

def main():
    print("🚀 Configuration du kernel Jupyter avec PyTorch MPS pour Cursor")
    print("=" * 60)

    project_dir = Path(__file__).parent
    venv_dir = project_dir / "venv"

    # 1. Créer l'environnement virtuel
    if not venv_dir.exists():
        print(f"Création de l'environnement virtuel dans {venv_dir}")
        # Essayer différentes méthodes pour créer venv
        methods = [
            f"python3 -m venv {venv_dir}",
            f"/usr/bin/python3 -m venv {venv_dir}",
            f"virtualenv {venv_dir}",
        ]

        success = False
        for method in methods:
            if run_command(method, f"Création venv avec {method.split()[0]}"):
                success = True
                break

        if not success:
            print("❌ Impossible de créer l'environnement virtuel")
            print("💡 Essayez : pip install virtualenv && python -m virtualenv venv")
            return False
    else:
        print(f"✅ Environnement virtuel existe déjà dans {venv_dir}")

    # 2. Activer l'environnement et installer les packages
    activate_script = venv_dir / "bin" / "activate"
    if not activate_script.exists():
        activate_script = venv_dir / "Scripts" / "activate"  # Windows

    if activate_script.exists():
        print("\n🔧 Installation des packages...")        # Installation de PyTorch avec MPS
        packages = [
            "torch torchvision torchaudio",
            "transformers accelerate",
            "scikit-learn pandas numpy tqdm jupyter ipykernel"
        ]

        for package in packages:
            cmd = f"source {activate_script} && pip install {package}"
            if not run_command(cmd, f"Installation de {package}"):
                print(f"⚠️  Échec installation {package}, continuation...")

        # 3. Installer le kernel Jupyter
        kernel_name = "ml-gpu"
        cmd = f"source {activate_script} && python -m ipykernel install --user --name {kernel_name} --display-name 'ML GPU (MPS)'"
        run_command(cmd, f"Installation du kernel Jupyter '{kernel_name}'")

        # 4. Vérifier l'installation
        print("\n🔍 Vérification de l'installation...")
        test_cmd = f"source {activate_script} && python -c \"import torch; print('PyTorch:', torch.__version__); print('MPS:', torch.backends.mps.is_available())\""
        run_command(test_cmd, "Test PyTorch MPS")

        print("\n🎉 Configuration terminée!")
        print("=" * 60)
        print("📝 Instructions pour utiliser dans Cursor:")
        print("1. Ouvrez le notebook 03_validity_classifier_camembert.ipynb")
        print("2. Cliquez sur 'Select Kernel' en haut à droite")
        print("3. Choisissez 'ML GPU (MPS)' dans la liste")
        print("4. Le notebook utilisera automatiquement votre GPU M4 Pro!")
        print("")
        print("💡 Si le kernel n'apparaît pas, redémarrez Cursor")

    else:
        print(f"❌ Script d'activation introuvable: {activate_script}")
        return False

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
