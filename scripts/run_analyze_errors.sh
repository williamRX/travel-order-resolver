#!/bin/bash
# Script pour exécuter l'analyse des erreurs NER avec l'environnement conda activé

# Activer l'environnement conda
source $(conda info --base)/etc/profile.d/conda.sh
conda activate t-aia-911-lil3

# Exécuter le script d'analyse
cd "$(dirname "$0")/.."
python scripts/analyze_ner_errors.py
