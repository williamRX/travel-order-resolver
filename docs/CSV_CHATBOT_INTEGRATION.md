# Intégration CSV dans le Chatbot

Documentation de l'intégration du traitement CSV dans le chatbot web.

---

## ✅ Implémentation complétée

### Fonctionnalités ajoutées

1. **Endpoint API** : `POST /process_csv`
   - Accepte un fichier CSV uploadé
   - Traite chaque ligne au format `sentenceID,sentence`
   - Retourne un CSV avec les résultats

2. **Interface frontend** :
   - Zone d'upload de fichier CSV
   - Affichage des résultats
   - Téléchargement du CSV de sortie

---

## 📋 Format conforme au sujet

### Format d'entrée

✅ Format : `sentenceID,sentence` (une ligne par phrase)

**Exemple :**
```csv
1,Je vais de Paris à Lyon
2,Billet Marseille Nice demain
3,Bonjour comment allez-vous?
```

### Format de sortie

✅ Phrases **valides** : `sentenceID,Departure,Destination`
✅ Phrases **invalides** : `sentenceID,INVALID`

**Exemple de sortie :**
```csv
1,Paris,Lyon
2,Marseille,Nice
3,INVALID
```

---

## 🎯 Utilisation dans le chatbot

### 1. Accéder au chatbot

Ouvrez le chatbot : **http://localhost:3000**

### 2. Utiliser la section CSV

1. **Section "📄 Traitement par fichier CSV"** en haut du chatbot
2. **Cliquez sur "📁 Choisir un fichier CSV"**
3. **Sélectionnez un fichier CSV** au format `sentenceID,sentence`
4. **Cliquez sur "🔄 Traiter le fichier CSV"**
5. **Attendez le traitement** (indicateur de chargement)
6. **Consultez les résultats** (affichés dans une zone dédiée)
7. **Téléchargez les résultats** (bouton "💾 Télécharger les résultats")

### 3. Exemple de fichier CSV

Créez un fichier `test.csv` :
```csv
1,Je vais de Paris à Lyon
2,Billet Marseille Nice demain
3,Bonjour comment allez-vous?
4,Trajet Lille Lyon
5,Je mange une pomme
```

**Résultat attendu :**
```csv
1,Paris,Lyon
2,Marseille,Nice
3,INVALID
4,Lille,Lyon
5,INVALID
```

---

## 🔧 Détails techniques

### Endpoint API

**Route :** `POST /process_csv`

**Paramètres :**
- `file` : Fichier CSV (multipart/form-data)

**Réponse :**
- Type : `text/csv`
- Headers : `Content-Disposition: attachment; filename=results_<nom_fichier>.csv`
- Contenu : CSV avec résultats

**Exemple avec curl :**
```bash
curl -X POST "http://localhost:8000/process_csv" \
     -F "file=@test.csv" \
     -o results.csv
```

### Interface frontend

**Composants :**
- Input file : `csvFileInput` (masqué, accessible via label)
- Label : "📁 Choisir un fichier CSV"
- Button : "🔄 Traiter le fichier CSV"
- Zone de résultats : `csvResults` (affichage préformaté)
- Lien de téléchargement : `downloadLink` (généré dynamiquement)

**Fonctions JavaScript :**
- `handleFileSelect(event)` : Gère la sélection de fichier
- `processCsvFile()` : Traite le fichier CSV
- `escapeHtml(text)` : Échappe le HTML pour l'affichage

---

## 📊 Flux de traitement

```
1. Utilisateur sélectionne un fichier CSV
   ↓
2. Frontend envoie le fichier à POST /process_csv
   ↓
3. API lit le fichier CSV ligne par ligne
   ↓
4. Pour chaque ligne (sentenceID,sentence) :
   - Pipeline NLP analyse la phrase
   - Génère sentenceID,Departure,Destination ou sentenceID,INVALID
   ↓
5. API retourne le CSV de résultats
   ↓
6. Frontend affiche les résultats et permet le téléchargement
```

---

## ✅ Conformité avec le sujet

Le sujet demande :

> "The main NLP component should be able to:
> - receive some text file in input:
>   - To be evaluated (and possibly compared to the work of other groups), your NLP part shall read sentences (one per line) from any file or URL.
>   - Each line shall start have the following format : sentenceID,sentence
>   - The sentenceID will not be directly used by your program, but simply printed with the result, for validation.
> - for each sentence, optionally check if the text is a valid trip order:
>   - return a negative answer if it isn't, using the format : sentenceID,Code, where code can be 'INVALID' or more precise
>   - return a triplet sentenceID,Departure,Destination if it is."

**✅ Implémenté :**
- ✅ Lecture depuis fichier CSV
- ✅ Format d'entrée : `sentenceID,sentence`
- ✅ Format de sortie VALIDE : `sentenceID,Departure,Destination`
- ✅ Format de sortie INVALIDE : `sentenceID,INVALID`
- ✅ sentenceID conservé et retourné dans les résultats
- ✅ Vérification si le texte est une commande de trajet valide
- ✅ Encodage UTF-8

**Note :** L'URL est supportée via le script CLI (`process_input.py`), pas directement dans le chatbot web.

---

## 🧪 Tests

### Test 1 : Fichier simple

1. Créez `test.csv` :
   ```csv
   1,Je vais de Paris à Lyon
   2,Bonjour
   ```

2. Ouvrez http://localhost:3000
3. Upload le fichier
4. Traitez
5. Vérifiez : `1,Paris,Lyon` et `2,INVALID`

### Test 2 : Fichier avec plusieurs phrases

Utilisez `scripts/example_input.csv` comme exemple.

---

## 🎨 Interface utilisateur

L'interface CSV est intégrée dans le chatbot web :

- **Section dédiée** en haut de la page (avant le chat)
- **Design cohérent** avec le reste du chatbot
- **Feedback visuel** (loading, résultats, erreurs)
- **Téléchargement** des résultats en un clic

---

## 📝 Notes importantes

### Limitations

- **Taille de fichier** : Pas de limite explicite, mais très gros fichiers peuvent être lents
- **Format** : Seulement fichiers CSV (`.csv`)
- **Encodage** : UTF-8 uniquement

### Bonnes pratiques

- **Format d'entrée** : Respecter `sentenceID,sentence` (une ligne par phrase)
- **Virgules dans les phrases** : Fonctionnent car split uniquement sur la première virgule
- **Lignes vides** : Ignorées automatiquement

---

## 🔗 Liens

- **Script CLI** : `scripts/process_input.py` (format CSV en ligne de commande)
- **Documentation CLI** : `docs/PROCESS_INPUT_USAGE.md`
- **Différence Chatbot vs CLI** : `docs/CHATBOT_VS_CLI.md`
- **API Documentation** : http://localhost:8000/docs (quand l'API est lancée)

---

**Date d'implémentation :** 2025-01-09  
**Statut :** ✅ Complété et intégré au chatbot
