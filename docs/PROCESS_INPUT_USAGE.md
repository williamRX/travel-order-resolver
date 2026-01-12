# Guide d'utilisation : process_input.py

Script principal de traitement selon le format spécifié du sujet.

---

## 📋 Format d'entrée/sortie

### Format d'entrée

Format : `sentenceID,sentence` (une ligne par phrase)

**Exemple :**
```csv
1,Je vais de Paris à Lyon
2,Billet Marseille Nice demain
3,Bonjour comment allez-vous?
4,Trajet la gare de Lille vers l'aéroport de Lyon
5,Je mange une pomme
```

**Notes :**
- `sentenceID` : Identifiant unique de la phrase (peut être un nombre, une chaîne, etc.)
- `sentence` : La phrase à analyser (peut contenir des virgules si nécessaire)
- Encodage : UTF-8
- Une ligne par phrase

### Format de sortie

**Phrases valides** : `sentenceID,Departure,Destination`

**Phrases invalides** : `sentenceID,INVALID`

**Exemple de sortie :**
```csv
1,Paris,Lyon
2,Marseille,Nice
3,INVALID
4,Lille,Lyon
5,INVALID
```

**Notes :**
- Pour les phrases valides, `Departure` et `Destination` sont les villes extraites
- Si une ville manque, le champ est vide (ex: `1,,Lyon` pour départ manquant)
- Pour les phrases invalides, le code est toujours `INVALID`
- Encodage : UTF-8

---

## 🚀 Utilisation

### Option 1 : Depuis un fichier

```bash
python scripts/process_input.py --file input.csv > output.csv
```

Ou avec fichier de sortie spécifié :

```bash
python scripts/process_input.py --file input.csv --output output.csv
```

### Option 2 : Depuis stdin (pipe)

```bash
cat input.csv | python scripts/process_input.py
```

Ou :

```bash
echo "1,Je vais de Paris à Lyon" | python scripts/process_input.py
```

### Option 3 : Depuis URL

```bash
python scripts/process_input.py --url http://example.com/sentences.csv
```

Ou avec redirection :

```bash
python scripts/process_input.py --url http://example.com/sentences.csv > output.csv
```

---

## 📝 Exemples

### Exemple 1 : Fichier simple

**Créer un fichier d'entrée :**
```bash
cat > test_input.csv << EOF
1,Je vais de Paris à Lyon
2,Billet Marseille Nice demain
3,Bonjour comment allez-vous?
4,Trajet Lille Lyon
EOF
```

**Traiter :**
```bash
python scripts/process_input.py --file test_input.csv
```

**Résultat attendu :**
```
1,Paris,Lyon
2,Marseille,Nice
3,INVALID
4,Lille,Lyon
```

### Exemple 2 : Avec pipe

```bash
echo -e "1,Je vais de Paris à Lyon\n2,Bonjour" | python scripts/process_input.py
```

**Résultat :**
```
1,Paris,Lyon
2,INVALID
```

### Exemple 3 : Sauvegarder dans un fichier

```bash
python scripts/process_input.py --file input.csv --output results.csv
```

---

## ⚙️ Options

```bash
python scripts/process_input.py --help
```

**Options disponibles :**

- `--file`, `-f` : Chemin vers le fichier d'entrée
- `--url`, `-u` : URL pour lire les données
- `--output`, `-o` : Fichier de sortie (par défaut: stdout)
- `--help`, `-h` : Afficher l'aide

**Notes :**
- Si aucune option n'est spécifiée et qu'il y a des données sur stdin, le script les lira automatiquement
- Si `--output` n'est pas spécifié, la sortie va sur stdout (redirigeable avec `>`)

---

## 📊 Statistiques

Le script affiche des statistiques sur stderr (ne pollue pas la sortie) :

```
🔄 Initialisation du pipeline NLP...
✅ Pipeline initialisé
🔄 Traitement des phrases...
✅ Traitement terminé
   Lignes traitées: 10
   Phrases valides: 7
   Phrases invalides: 3
```

---

## ⚠️ Gestion des erreurs

### Lignes mal formatées

Si une ligne n'a pas le format `sentenceID,sentence`, elle sera traitée comme INVALID :

```
⚠️  Ligne 5: Format invalide (attendu: sentenceID,sentence), ignorée
```

### Phrases vides

Si la phrase est vide après le `sentenceID,`, elle sera marquée comme INVALID.

### Erreurs du pipeline

Si une erreur survient lors du traitement (par exemple, problème de chargement du modèle), la phrase sera marquée comme INVALID et l'erreur sera affichée sur stderr.

---

## 🔧 Intégration dans un pipeline

### Avec cat

```bash
cat input.csv | python scripts/process_input.py | tee output.csv
```

### Avec curl (URL)

```bash
curl http://example.com/sentences.csv | python scripts/process_input.py > output.csv
```

### Dans un script bash

```bash
#!/bin/bash
INPUT="input.csv"
OUTPUT="output.csv"

python scripts/process_input.py --file "$INPUT" --output "$OUTPUT"

echo "Traitement terminé. Résultats dans $OUTPUT"
```

---

## 🐛 Dépannage

### Erreur : "Aucun modèle NLP trouvé"

**Solution :** Vérifiez que vous avez entraîné un modèle NER :
```bash
ls nlp/models/
```

### Erreur : "ModuleNotFoundError"

**Solution :** Assurez-vous d'être dans le bon environnement Python et que toutes les dépendances sont installées :
```bash
pip install -r requirements.txt
```

### Erreur : Encodage UTF-8

**Solution :** Vérifiez que votre fichier d'entrée est en UTF-8 :
```bash
file -I input.csv
# Devrait afficher: text/plain; charset=utf-8
```

Si ce n'est pas le cas, convertissez :
```bash
iconv -f ISO-8859-1 -t UTF-8 input.csv > input_utf8.csv
```

---

## 📚 Format conforme au sujet

Ce script respecte exactement le format spécifié dans le sujet :

- ✅ Format d'entrée : `sentenceID,sentence`
- ✅ Format de sortie VALIDE : `sentenceID,Departure,Destination`
- ✅ Format de sortie INVALIDE : `sentenceID,INVALID`
- ✅ Lecture depuis fichier
- ✅ Lecture depuis stdin
- ✅ Lecture depuis URL (bonus)
- ✅ Encodage UTF-8
- ✅ Une ligne par phrase
