# Générateur de Dataset NLP

Générateur de dataset pour l'entraînement du modèle NLP d'extraction des destinations.

## 🎯 Objectif

Génère un dataset JSONL au format Spacy avec des phrases **uniquement valides** contenant des intentions de trajet, annotées avec les entités `DEPARTURE` et `ARRIVAL`.

## 📊 Format de Sortie

Format JSONL Spacy :
```json
{
  "text": "Je vais de Paris à Lyon",
  "entities": [
    [10, 15, "DEPARTURE"],
    [18, 22, "ARRIVAL"]
  ]
}
```

- `text` : La phrase complète
- `entities` : Liste d'entités avec `[start, end, "LABEL"]`
  - `start` : Position de début (caractère)
  - `end` : Position de fin (caractère)
  - `LABEL` : `"DEPARTURE"` ou `"ARRIVAL"`

## 🔧 Utilisation

```bash
# Depuis la racine du projet
python dataset/generators/nlp/dataset_generator.py
```

Le dataset sera généré dans `dataset/nlp/json/nlp_training_data.jsonl`.

## 📝 Paramètres

- **TOTAL_SENTENCES** : 20 000 phrases par défaut
- **Patterns** : 150 patterns différents de phrases valides
- **Source** : Gares françaises depuis `dataset/shared/gares-francaises.json`

## 🎨 Types de Patterns

Les 150 patterns couvrent :
- Formes standard (Je vais de X à Y)
- Questions (Comment aller de X à Y ?)
- Billets et tarifs
- Destinations internationales
- Expressions françaises familières
- Patterns avec typos
- Patterns avec transports spécifiques
- Patterns avec horaires et dates
- Patterns "mais je vais à X"
- Et bien d'autres...

## 🔍 Détection des Entités

Le générateur détecte automatiquement les positions des gares dans le texte :
1. Cherche d'abord le texte avec variantes (ex: "la gare de Paris")
2. Si non trouvé, cherche le nom de gare seul
3. Gère les variations de casse et les typos

## 📦 Dépendances

- `json` : Pour lire les gares et écrire le JSONL
- `random` : Pour la génération aléatoire
- `re` : Pour la détection des entités dans le texte
- `pathlib` : Pour la gestion des chemins

## 🚀 Exemple de Sortie

```json
{"text": "Je vais de la gare de Paris à Lyon", "entities": [[10, 25, "DEPARTURE"], [28, 32, "ARRIVAL"]]}
{"text": "Billet Paris Marseille demain", "entities": [[7, 12, "DEPARTURE"], [13, 21, "ARRIVAL"]]}
{"text": "Je passe par Lyon mais je vais à Marseille.", "entities": [[18, 22, "ARRIVAL"]]}
```

