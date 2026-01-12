# Différence entre Chatbot et Script CLI

Ce document explique la différence entre le chatbot web et le script CLI `process_input.py`.

---

## 🎯 Deux systèmes différents

### 1. **Chatbot Web** (actuel) - Interface interactive

**Technologie :**
- **Frontend** : HTML/JavaScript (`frontend/index.html`)
- **Backend** : API REST FastAPI (`api/main.py`)
- **Format** : JSON

**Communication :**
```
Frontend (JavaScript) → POST /predict → API (FastAPI) → Pipeline NLP → Réponse JSON
```

**Format d'échange :**
- **Requête** (JSON) : `{ "sentence": "Je vais de Paris à Lyon" }`
- **Réponse** (JSON) : 
  ```json
  {
    "valid": true,
    "message": null,
    "departure": "Paris",
    "arrival": "Lyon"
  }
  ```

**Usage :**
- Interface web interactive
- Une phrase à la fois
- Réponse immédiate dans le navigateur
- Utilisé pour démonstration/test interactif

---

### 2. **Script CLI** (`process_input.py`) - Format spécifié par le sujet

**Technologie :**
- **Script Python** : CLI standalone
- **Format** : CSV (format spécifié par le sujet)

**Communication :**
```
Fichier CSV → Script CLI → Pipeline NLP → Fichier CSV
```

**Format d'échange :**
- **Entrée** (CSV) : `sentenceID,sentence`
  ```
  1,Je vais de Paris à Lyon
  2,Bonjour comment allez-vous?
  ```
- **Sortie** (CSV) : `sentenceID,Departure,Destination` ou `sentenceID,INVALID`
  ```
  1,Paris,Lyon
  2,INVALID
  ```

**Usage :**
- Traitement batch (plusieurs phrases)
- Format conforme au sujet
- Utilisable en ligne de commande
- Intégration dans des scripts/automatisation

---

## 🔍 Support URL : Clarification

### Dans le script CLI (`process_input.py`)

Le support URL dans `process_input.py` permet de **lire un fichier CSV distant** pour le traiter :

```bash
# Lire un fichier CSV depuis une URL et le traiter
python scripts/process_input.py --url http://example.com/sentences.csv
```

**Ce que ça fait :**
1. Télécharge le fichier CSV depuis l'URL
2. Lit chaque ligne (`sentenceID,sentence`)
3. Traite chaque phrase avec le pipeline NLP
4. Génère le format de sortie (`sentenceID,Departure,Destination`)

**Exemple concret :**
```bash
# Si vous avez un fichier CSV hébergé quelque part
python scripts/process_input.py --url https://mon-site.com/phrases.csv > results.csv
```

**⚠️ Ce n'est PAS :**
- ❌ Une connexion au chatbot web
- ❌ Une API REST
- ❌ Un format JSON

C'est simplement une façon de **télécharger et traiter un fichier CSV distant**.

---

### Dans le chatbot web (actuel)

Le chatbot web **n'a pas** de support URL pour le format CSV.

**Le chatbot actuel :**
- ✅ Accepte des requêtes POST JSON via l'API REST
- ✅ Une phrase à la fois
- ✅ Réponse JSON immédiate
- ❌ Ne supporte PAS le format CSV
- ❌ Ne lit PAS depuis URL

**Si vous voulez que le chatbot puisse aussi traiter du CSV :**
Il faudrait ajouter un nouvel endpoint à l'API FastAPI, par exemple :
```python
@app.post("/process_csv")
async def process_csv(file: UploadFile):
    # Traiter un fichier CSV uploadé
    ...
```

Mais ce n'est **pas requis par le sujet** - le format CSV est pour le script CLI.

---

## 📊 Comparaison

| Aspect | Chatbot Web | Script CLI |
|--------|-------------|------------|
| **Format** | JSON | CSV |
| **Interface** | Web (navigateur) | Ligne de commande |
| **Traitement** | Une phrase à la fois | Batch (plusieurs phrases) |
| **Entrée** | POST JSON à `/predict` | Fichier/stdin/URL CSV |
| **Sortie** | JSON | CSV |
| **Usage** | Démonstration/test interactif | Format spécifié par le sujet |
| **Support URL** | N/A (API REST) | ✅ Oui (télécharger CSV) |

---

## 🎯 Quand utiliser quoi ?

### Utiliser le **Chatbot Web** quand :
- ✅ Vous voulez tester interactivement
- ✅ Vous voulez une démonstration visuelle
- ✅ Vous traitez une phrase à la fois
- ✅ Vous voulez une interface utilisateur

### Utiliser le **Script CLI** quand :
- ✅ Vous avez un fichier CSV à traiter
- ✅ Vous voulez le format spécifié par le sujet
- ✅ Vous devez traiter plusieurs phrases en batch
- ✅ Vous voulez intégrer dans un script/automatisation
- ✅ Vous voulez traiter un fichier CSV distant (URL)

---

## 🔧 Exemples d'utilisation

### Chatbot Web

```javascript
// Dans le navigateur (automatique)
fetch('http://localhost:8000/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sentence: "Je vais de Paris à Lyon" })
})
```

**Ou simplement :** Ouvrir http://localhost:3000 et taper dans le chat

### Script CLI

```bash
# Depuis un fichier local
python scripts/process_input.py --file input.csv > output.csv

# Depuis stdin
cat input.csv | python scripts/process_input.py

# Depuis URL (télécharger et traiter un CSV distant)
python scripts/process_input.py --url http://example.com/phrases.csv > results.csv
```

---

## ✅ Résumé

**Le support URL dans `process_input.py`** permet de :
- ✅ Télécharger un fichier CSV depuis une URL
- ✅ Traiter ce fichier CSV
- ✅ Générer le format de sortie spécifié par le sujet

**Ce n'est PAS :**
- ❌ Une connexion au chatbot web
- ❌ Une API REST
- ❌ Un remplacement du chatbot

Les deux systèmes coexistent et servent des besoins différents :
- **Chatbot** = Interface interactive (JSON)
- **Script CLI** = Format spécifié par le sujet (CSV)
