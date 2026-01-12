# Guide : Lancer le Chatbot avec le Classifieur CamemBERT

Ce guide vous explique comment lancer votre chatbot avec le classifieur CamemBERT.

## 🎯 Vue d'ensemble

Votre système se compose de :
1. **API FastAPI** : Backend qui utilise le pipeline (Classifieur + NLP)
2. **Frontend HTML** : Interface chatbot dans le navigateur
3. **Pipeline** : Classifieur CamemBERT + Modèle NLP Spacy

---

## 📋 Prérequis

1. **Modèles entraînés** :
   - ✅ Classifieur CamemBERT (dans `classifier/models/validity_classifier_camembert_*/`)
   - ✅ Modèle NLP Spacy (dans `nlp/models/spacy_ner_*/`)

2. **Environnement Python** :
   - Environnement virtuel activé (venv ou conda)
   - Toutes les dépendances installées

---

## 🚀 Lancer le système

### Étape 1 : Activer l'environnement

**Avec venv :**
```bash
source venv/bin/activate
```

**Avec Conda :**
```bash
conda activate t-aia-911-lil3
```

### Étape 2 : Vérifier les dépendances

```bash
pip install fastapi uvicorn transformers torch spacy
```

### Étape 3 : Lancer l'API

```bash
cd /Users/williamroux/Documents/Projets/T-AIA-911-LIL_3
python api/main.py
```

Ou avec uvicorn directement :
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

**L'API sera accessible sur :** http://localhost:8000

### Étape 4 : Ouvrir le chatbot

1. **Ouvrir le fichier HTML** :
   ```bash
   open frontend/index.html
   ```
   
   Ou ouvrir manuellement dans votre navigateur :
   - Fichier : `frontend/index.html`
   - URL : `file:///Users/williamroux/Documents/Projets/T-AIA-911-LIL_3/frontend/index.html`

2. **Le chatbot devrait se connecter automatiquement** à l'API sur `http://localhost:8000`

---

## ✅ Vérification

### Vérifier que l'API fonctionne

1. **Page d'accueil** : http://localhost:8000
2. **Documentation Swagger** : http://localhost:8000/docs
3. **Health check** : http://localhost:8000/health

### Tester l'API directement

```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"sentence": "Je vais de Paris à Lyon"}'
```

Réponse attendue :
```json
{
  "valid": true,
  "message": null,
  "departure": "Paris",
  "arrival": "Lyon"
}
```

---

## 🔧 Dépannage

### Erreur : "Aucun modèle CamemBERT trouvé"

**Solution :**
1. Vérifiez que vous avez entraîné un modèle CamemBERT :
   ```bash
   ls classifier/models/validity_classifier_camembert_*/
   ```

2. Si aucun modèle n'existe, entraînez-en un avec le notebook :
   - `classifier/notebooks/03_validity_classifier_camembert_gpu.ipynb`

### Erreur : "Aucun modèle NLP trouvé"

**Solution :**
1. Vérifiez que vous avez entraîné un modèle NLP :
   ```bash
   ls nlp/models/spacy_ner_*/
   ```

2. Si aucun modèle n'existe, entraînez-en un avec le notebook :
   - `nlp/notebooks/01_ner_training.ipynb`

### Erreur CORS dans le navigateur

**Solution :** L'API est déjà configurée pour accepter les requêtes CORS. Si vous avez des problèmes :
- Assurez-vous que l'API tourne sur `http://localhost:8000`
- Vérifiez que le frontend pointe vers la bonne URL dans `frontend/index.html` (ligne 292)

### Le chatbot ne répond pas

**Vérifications :**
1. L'API est-elle lancée ? (http://localhost:8000/health)
2. Ouvrez la console du navigateur (F12) pour voir les erreurs
3. Vérifiez que l'URL de l'API est correcte dans `frontend/index.html`

---

## 📝 Utilisation

### Dans le chatbot

1. **Ouvrez** `frontend/index.html` dans votre navigateur
2. **Tapez** une phrase dans le champ de texte
3. **Cliquez** sur "Envoyer" ou appuyez sur Entrée
4. **Le chatbot** :
   - Vérifie si la phrase est valide (avec CamemBERT)
   - Si valide, extrait les destinations (avec NLP)
   - Affiche les résultats

### Exemples de phrases

**Phrases valides :**
- "Je vais de Paris à Lyon"
- "Billet Marseille Nice demain"
- "Trajet Lille - Marseille"

**Phrases invalides :**
- "Je mange une pomme"
- "Il fait beau aujourd'hui"
- "Bonjour comment allez-vous ?"

---

## 🎨 Personnalisation

### Changer le port de l'API

Dans `api/main.py`, ligne 136 :
```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # Changez 8000
```

Et dans `frontend/index.html`, ligne 292 :
```javascript
const API_URL = 'http://localhost:8000';  // Changez le port ici aussi
```

### Utiliser l'ancien classifieur (TF-IDF)

Si vous voulez utiliser l'ancien classifieur au lieu de CamemBERT :

Dans `api/pipeline.py`, modifiez l'initialisation :
```python
pipeline = TravelIntentPipeline(use_camembert=False)
```

---

## 🚀 Script de lancement rapide

Créez un script `lancer_chatbot.sh` :

```bash
#!/bin/bash
# Script pour lancer le chatbot

echo "🚀 Lancement du chatbot..."

# Activer l'environnement (ajustez selon votre setup)
source venv/bin/activate  # ou: conda activate t-aia-911-lil3

# Lancer l'API
echo "📡 Démarrage de l'API..."
python api/main.py &
API_PID=$!

# Attendre que l'API soit prête
sleep 3

# Ouvrir le chatbot dans le navigateur
echo "🌐 Ouverture du chatbot..."
open frontend/index.html

echo "✅ Chatbot lancé !"
echo "   API: http://localhost:8000"
echo "   Pour arrêter: kill $API_PID"
```

Rendez-le exécutable :
```bash
chmod +x lancer_chatbot.sh
./lancer_chatbot.sh
```

---

## 📚 Ressources

- **API Documentation** : http://localhost:8000/docs (quand l'API est lancée)
- **Code API** : `api/main.py`
- **Code Pipeline** : `api/pipeline.py`
- **Frontend** : `frontend/index.html`

---

**Besoin d'aide ?** Vérifiez les logs de l'API dans le terminal où vous l'avez lancée.

