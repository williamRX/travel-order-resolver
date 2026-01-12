#!/usr/bin/env python3
"""
Script de traitement d'entrée selon le format spécifié du sujet.

Format d'entrée : sentenceID,sentence (une ligne par phrase)
Format de sortie VALIDE : sentenceID,Departure,Destination
Format de sortie INVALIDE : sentenceID,INVALID

Usage:
    # Depuis un fichier
    python scripts/process_input.py input.csv > output.csv
    
    # Depuis stdin
    cat input.csv | python scripts/process_input.py
    
    # Depuis URL
    curl http://example.com/sentences.csv | python scripts/process_input.py
    
    # Spécifier un fichier
    python scripts/process_input.py --file input.csv
    
    # Spécifier une URL
    python scripts/process_input.py --url http://example.com/sentences.csv
"""

import sys
import argparse
import csv
from pathlib import Path
from typing import Optional, TextIO
from urllib.request import urlopen
from urllib.error import URLError

# Ajouter le répertoire parent au path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.pipeline import TravelIntentPipeline


def process_line(line: str, pipeline: TravelIntentPipeline, line_number: int = 0) -> str:
    """
    Traite une ligne d'entrée et retourne la ligne de sortie formatée.
    
    Args:
        line: Ligne d'entrée au format sentenceID,sentence
        pipeline: Pipeline NLP initialisé
        line_number: Numéro de ligne (pour les erreurs)
        
    Returns:
        Ligne de sortie formatée (sentenceID,Departure,Destination ou sentenceID,INVALID)
    """
    line = line.strip()
    
    # Ignorer les lignes vides
    if not line:
        return ""
    
    # Parser la ligne : sentenceID,sentence
    parts = line.split(',', 1)  # Split seulement sur la première virgule
    
    if len(parts) != 2:
        # Format invalide, retourner INVALID
        print(f"⚠️  Ligne {line_number}: Format invalide (attendu: sentenceID,sentence), ignorée", file=sys.stderr)
        # Si on a au moins un ID, l'utiliser, sinon utiliser le numéro de ligne
        sentence_id = parts[0] if parts else str(line_number)
        return f"{sentence_id},INVALID"
    
    sentence_id, sentence = parts
    sentence = sentence.strip()
    
    # Vérifier que la phrase n'est pas vide
    if not sentence:
        return f"{sentence_id},INVALID"
    
    try:
        # Utiliser le pipeline pour prédire
        result = pipeline.predict(sentence)
        
        if result["valid"]:
            # Phrase valide : sentenceID,Departure,Destination
            departure = result.get("departure", "") or ""
            arrival = result.get("arrival", "") or ""
            
            # Si on a au moins une destination, on considère comme valide
            if departure or arrival:
                # Format : sentenceID,Departure,Destination
                return f"{sentence_id},{departure},{arrival}"
            else:
                # Pas de destinations trouvées, considérer comme INVALID
                return f"{sentence_id},INVALID"
        else:
            # Phrase invalide : sentenceID,INVALID
            return f"{sentence_id},INVALID"
            
    except Exception as e:
        # Erreur lors du traitement, considérer comme INVALID
        print(f"⚠️  Ligne {line_number} (ID: {sentence_id}): Erreur: {e}", file=sys.stderr)
        return f"{sentence_id},INVALID"


def read_from_file(file_path: Path) -> TextIO:
    """Ouvre un fichier pour lecture."""
    try:
        return open(file_path, 'r', encoding='utf-8')
    except FileNotFoundError:
        print(f"❌ Erreur: Fichier '{file_path}' non trouvé", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur lors de l'ouverture du fichier: {e}", file=sys.stderr)
        sys.exit(1)


def read_from_url(url: str) -> TextIO:
    """Lit depuis une URL."""
    try:
        response = urlopen(url)
        # Retourner un objet file-like
        return response
    except URLError as e:
        print(f"❌ Erreur lors de la lecture de l'URL: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Traite des phrases selon le format spécifié et extrait départ/destination.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  # Depuis un fichier
  python scripts/process_input.py input.csv > output.csv
  
  # Depuis stdin
  cat input.csv | python scripts/process_input.py
  
  # Depuis URL
  python scripts/process_input.py --url http://example.com/sentences.csv
  
  # Spécifier un fichier
  python scripts/process_input.py --file input.csv

Format d'entrée:
  sentenceID,sentence
  
Format de sortie:
  - Phrase valide: sentenceID,Departure,Destination
  - Phrase invalide: sentenceID,INVALID
        """
    )
    
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Chemin vers le fichier d\'entrée'
    )
    
    parser.add_argument(
        '--url', '-u',
        type=str,
        help='URL pour lire les données'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Fichier de sortie (par défaut: stdout)'
    )
    
    args = parser.parse_args()
    
    # Déterminer la source d'entrée
    input_source = None
    
    if args.url:
        # Lire depuis URL
        input_source = read_from_url(args.url)
    elif args.file:
        # Lire depuis fichier
        input_source = read_from_file(Path(args.file))
    elif not sys.stdin.isatty():
        # Lire depuis stdin (pipe)
        input_source = sys.stdin
    else:
        # Aucune source spécifiée
        print("❌ Erreur: Aucune source d'entrée spécifiée", file=sys.stderr)
        print("   Utilisez --file, --url, ou pipe stdin", file=sys.stderr)
        parser.print_help()
        sys.exit(1)
    
    # Déterminer la sortie
    output_file = sys.stdout
    if args.output:
        try:
            output_file = open(args.output, 'w', encoding='utf-8')
        except Exception as e:
            print(f"❌ Erreur lors de l'ouverture du fichier de sortie: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Initialiser le pipeline
    print("🔄 Initialisation du pipeline NLP...", file=sys.stderr)
    try:
        pipeline = TravelIntentPipeline()
        print("✅ Pipeline initialisé", file=sys.stderr)
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation du pipeline: {e}", file=sys.stderr)
        sys.exit(1)
    
    print("🔄 Traitement des phrases...", file=sys.stderr)
    
    # Traiter ligne par ligne
    line_number = 0
    processed_count = 0
    valid_count = 0
    invalid_count = 0
    
    try:
        for line in input_source:
            line_number += 1
            
            # Décoder si nécessaire (pour les URLs)
            if isinstance(line, bytes):
                line = line.decode('utf-8')
            
            # Traiter la ligne
            output_line = process_line(line, pipeline, line_number)
            
            if output_line:
                # Écrire la sortie
                print(output_line, file=output_file)
                output_file.flush()
                
                processed_count += 1
                
                # Compter valides/invalides
                if ",INVALID" in output_line:
                    invalid_count += 1
                else:
                    valid_count += 1
    
    except KeyboardInterrupt:
        print("\n⚠️  Interruption utilisateur", file=sys.stderr)
    except Exception as e:
        print(f"\n❌ Erreur lors du traitement: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Fermer les fichiers si nécessaire
        if args.output and output_file != sys.stdout:
            output_file.close()
        if args.url and input_source:
            input_source.close()
    
    # Statistiques
    print(f"\n✅ Traitement terminé", file=sys.stderr)
    print(f"   Lignes traitées: {processed_count}", file=sys.stderr)
    print(f"   Phrases valides: {valid_count}", file=sys.stderr)
    print(f"   Phrases invalides: {invalid_count}", file=sys.stderr)


if __name__ == "__main__":
    main()
