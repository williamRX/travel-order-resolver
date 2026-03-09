#!/usr/bin/env python3
"""
Script de génération des PDFs de documentation NLP.
Convertit les fichiers Markdown en PDF via pandoc ou md-to-pdf.
"""

import subprocess
import sys
from pathlib import Path

# Fichiers à convertir en PDF
DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "exports" / "documentation"

DOCS_TO_CONVERT = [
    "NLP_ARCHITECTURE_COMPLETE.md",
    "NLP_TRAINING_PROCESS.md",
    "NLP_EXAMPLE_WALKTHROUGH.md",
    "NER_F1_IMPROVEMENT_ANALYSIS.md",   # Expériences & résultats NER
    "DATASET_PIPELINE.md",              # Pipeline dataset complet
]

def check_pandoc():
    """Vérifie que pandoc est installé."""
    try:
        result = subprocess.run(["pandoc", "--version"], capture_output=True, text=True)
        print(f"✅ pandoc trouvé: {result.stdout.split(chr(10))[0]}")
        return True
    except FileNotFoundError:
        print("❌ pandoc non trouvé. Installation:")
        print("   brew install pandoc")
        print("   brew install basictex  (pour LaTeX/PDF)")
        return False

def convert_to_pdf(md_file: Path, output_dir: Path) -> bool:
    """Convertit un fichier Markdown en PDF via pandoc."""
    output_file = output_dir / md_file.with_suffix(".pdf").name
    
    cmd = [
        "pandoc",
        str(md_file),
        "-o", str(output_file),
        "--pdf-engine=xelatex",
        "-V", "geometry:margin=2cm",
        "-V", "fontsize=11pt",
        "-V", "mainfont=DejaVu Sans",
        "--highlight-style=tango",
        "--toc",
        "--toc-depth=3",
        "-V", "toc-title=Table des matières",
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"✅ {md_file.name} → {output_file.name}")
            return True
        else:
            print(f"⚠️  Erreur pandoc pour {md_file.name}:")
            print(f"   {result.stderr[:200]}")
            # Essai sans LaTeX (HTML engine)
            return convert_to_pdf_html(md_file, output_dir)
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout pour {md_file.name}")
        return False

def convert_to_pdf_html(md_file: Path, output_dir: Path) -> bool:
    """Fallback: conversion via weasyprint si pandoc/latex échoue."""
    output_file = output_dir / md_file.with_suffix(".pdf").name
    
    cmd = [
        "pandoc",
        str(md_file),
        "-o", str(output_file),
        "--pdf-engine=weasyprint",
        "-V", "geometry:margin=2cm",
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"✅ {md_file.name} → {output_file.name} (weasyprint)")
            return True
        else:
            print(f"❌ Échec weasyprint aussi pour {md_file.name}")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def main():
    print("=" * 60)
    print("📄 Génération des PDFs de documentation NLP")
    print("=" * 60)
    
    if not check_pandoc():
        print("\n💡 Alternative: installer Node.js puis:")
        print("   npm install -g @mermaid-js/mermaid-cli")
        print("   npm install -g md-to-pdf")
        print("   Pour chaque fichier: md-to-pdf docs/NLP_ARCHITECTURE_COMPLETE.md")
        sys.exit(1)
    
    # Créer le dossier de sortie
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n📁 Dossier de sortie: {OUTPUT_DIR}")
    print()
    
    success_count = 0
    for doc_name in DOCS_TO_CONVERT:
        md_file = DOCS_DIR / doc_name
        if not md_file.exists():
            print(f"⚠️  Fichier non trouvé: {md_file}")
            continue
        
        if convert_to_pdf(md_file, OUTPUT_DIR):
            success_count += 1
    
    print()
    print("=" * 60)
    print(f"✅ {success_count}/{len(DOCS_TO_CONVERT)} fichiers convertis en PDF")
    print(f"📂 PDFs disponibles dans: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
