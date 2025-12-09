#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conversion du dataset JSON en CSV pour l'entraînement NLP
"""

import json
import csv

def convert_json_to_csv(json_file: str, csv_file: str):
    """Convertit le dataset JSON en CSV"""
    print(f"Lecture de {json_file}...")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Conversion de {len(data)} entrées en CSV...")
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Sentence', 'VALIDITY'])
        
        for item in data:
            writer.writerow([
                item['id'],
                item['sentence'],
                item['validity']
            ])
    
    print(f"✅ Conversion terminée!")
    print(f"   Fichier créé: {csv_file}")
    print(f"   Total: {len(data)} phrases")

if __name__ == '__main__':
    convert_json_to_csv('travel_dataset_50k.json', 'travel_dataset_50k.csv')

