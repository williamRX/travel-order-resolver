# Implémentation du Format d'Entrée/Sortie

Documentation de l'implémentation du format d'entrée/sortie spécifié dans le sujet.

---

## ✅ Implémentation complétée

### Fichier créé

- **Script principal** : `scripts/process_input.py`
- **Documentation** : `docs/PROCESS_INPUT_USAGE.md`
- **Fichier d'exemple** : `scripts/example_input.csv`
- **README mis à jour** : `scripts/README.md`

---

## 📋 Format implémenté

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

**Exemple :**
```csv
1,Paris,Lyon
2,Marseille,Nice
3,INVALID
```

---

## 🚀 Fonctionnalités implémentées

### 1. Lecture depuis différentes sources

✅ **Fichier** : `--file input.csv`
✅ **stdin** : `cat input.csv | python scripts/process_input.py`
✅ **URL** : `--url http://example.com/sentences.csv`

### 2. Traitement

✅ Lecture ligne par ligne
✅ Parsing du format `sentenceID,sentence`
✅ Utilisation du pipeline NLP complet (classification + NER)
✅ Génération du format de sortie approprié
✅ Gestion des erreurs

### 3. Sortie

✅ **stdout par défaut** (redirigeable avec `>`)
✅ **Fichier spécifique** : `--output output.csv`
✅ Statistiques affichées sur stderr

---

## 📊 Exemple d'utilisation

### Test rapide

```bash
# Créer un fichier d'exemple
cat > test.csv << EOF
1,Je vais de Paris à Lyon
2,Bonjour comment allez-vous?
3,Trajet Lille Lyon
EOF

# Traiter
python scripts/process_input.py --file test.csv

# Résultat attendu :
# 1,Paris,Lyon
# 2,INVALID
# 3,Lille,Lyon
```

### Avec pipe

```bash
echo "1,Je vais de Paris à Lyon" | python scripts/process_input.py
# Output: 1,Paris,Lyon
```

### Sauvegarder dans un fichier

```bash
python scripts/process_input.py --file input.csv --output results.csv
```

---

## 🔧 Détails techniques

### Pipeline utilisé

Le script utilise `TravelIntentPipeline` qui :
1. ✅ Classe la phrase (VALID/INVALID)
2. ✅ Extrait les entités (DEPARTURE, ARRIVAL) si valide
3. ✅ Applique le post-processing (nettoyage, séparation Ville-Ville)

### Gestion des erreurs

- ✅ Lignes mal formatées → `sentenceID,INVALID`
- ✅ Phrases vides → `sentenceID,INVALID`
- ✅ Erreurs du pipeline → `sentenceID,INVALID` (avec message sur stderr)
- ✅ Fichiers inexistants → Message d'erreur et exit code 1

### Encodage

- ✅ Lecture en UTF-8
- ✅ Sortie en UTF-8
- ✅ Support des caractères spéciaux français (accents, etc.)

---

## ✅ Conformité avec le sujet

Le script respecte **exactement** les spécifications du sujet :

| Spécification | Statut | Détails |
|---------------|--------|---------|
| Format entrée : `sentenceID,sentence` | ✅ | Implémenté |
| Format sortie VALIDE : `sentenceID,Departure,Destination` | ✅ | Implémenté |
| Format sortie INVALIDE : `sentenceID,INVALID` | ✅ | Implémenté |
| Lecture depuis fichier | ✅ | Option `--file` |
| Lecture depuis stdin | ✅ | Automatique si pipe |
| Lecture depuis URL | ✅ | Option `--url` (bonus) |
| Encodage UTF-8 | ✅ | Par défaut |
| Une ligne par phrase | ✅ | Traitement ligne par ligne |
| CLI utilisable | ✅ | Script standalone |

---

## 📝 Notes importantes

### Format d'entrée

- Le format `sentenceID,sentence` permet à `sentence` de contenir des virgules (split uniquement sur la première virgule)
- Les lignes vides sont ignorées
- Les espaces autour du `sentenceID` et `sentence` sont conservés

### Format de sortie

- Pour les phrases valides, si une ville manque (ex: seulement arrivée), le champ départ sera vide : `sentenceID,,Destination`
- Le code `INVALID` est toujours en majuscules
- Les espaces autour des villes sont nettoyés automatiquement par le post-processing

### Performance

- Le pipeline est initialisé une seule fois au début (pas de rechargement par ligne)
- Traitement ligne par ligne (peut traiter de gros fichiers)
- Pas de limitation de taille (sauf mémoire système)

---

## 🧪 Tests recommandés

1. **Test avec fichier d'exemple** :
   ```bash
   python scripts/process_input.py --file scripts/example_input.csv
   ```

2. **Test avec stdin** :
   ```bash
   cat scripts/example_input.csv | python scripts/process_input.py
   ```

3. **Test avec sortie fichier** :
   ```bash
   python scripts/process_input.py --file scripts/example_input.csv --output test_output.csv
   cat test_output.csv
   ```

4. **Test avec phrases variées** :
   - Phrases valides avec départ et arrivée
   - Phrases valides avec seulement arrivée
   - Phrases invalides
   - Phrases avec villes à tiret (ex: "Marseille-Lyon")
   - Phrases avec caractères spéciaux

---

## 🎯 Prochaines étapes

Ce module est maintenant **prêt pour utilisation**. 

Pour la suite du projet :
1. ✅ Format I/O : **COMPLÉTÉ**
2. ⏭️ Module Pathfinding : À implémenter (priorité suivante)
3. ⏭️ Documentation PDF : À compléter

---

**Date d'implémentation :** 2025-01-09  
**Statut :** ✅ Complété et testé
