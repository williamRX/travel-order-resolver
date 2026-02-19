# Front-end - Chatbot d'Extraction d'Intentions de Voyage

Interface web avec chatbot pour extraire les destinations de départ et d'arrivée.

## Structure

- `index.html` : Interface web complète avec chatbot

## Utilisation

### Avec Docker

```bash
docker compose up frontend
```

Le front-end sera accessible sur `http://localhost:8080`

### Sans Docker

Ouvrez simplement `index.html` dans un navigateur, ou servez-le avec un serveur HTTP :

```bash
# Python
python -m http.server 8080 --directory frontend

# Node.js
npx http-server frontend -p 8080
```

## Configuration

Par défaut, le front-end pointe vers l'API sur `http://localhost:8000`.

Pour changer l'URL de l'API, modifiez la variable `API_URL` dans `index.html` :

```javascript
const API_URL = 'http://votre-api:8000';
```

## Fonctionnalités

- **Interface chatbot moderne et responsive**
- **Reconnaissance vocale (Voice-to-Text)** 🎤
  - Utilise la Web Speech API native du navigateur
  - Supporte le français (fr-FR)
  - Bouton microphone avec feedback visuel
  - Transcription automatique dans le champ de saisie
  - Compatible avec Chrome, Edge, Safari (depuis iOS 14.5)
- Validation des phrases avec le classifieur
- Extraction des destinations avec le modèle NLP
- Affichage des résultats dans un format structuré
- Exemples de phrases cliquables
- Design moderne avec animations

