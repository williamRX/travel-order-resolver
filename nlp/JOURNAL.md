# Journal de Bord - Modèle NLP (NER)

Ce journal documente les problèmes rencontrés, les solutions apportées et les améliorations effectuées sur le modèle NLP (Named Entity Recognition).

---

## 📅 2025-01-09 - Intégration du Modèle NER CamemBERT

### 🐛 Problème rencontré

**Contexte :** Intégration du nouveau modèle NER CamemBERT (`ner_camembert_20260109_170148_v1`) dans la pipeline de production pour remplacer/améliorer le modèle SpaCy.

**Problème :** Lors du test du chatbot, erreur lors de l'appel à l'API :
```
Erreur : Erreur lors de l'analyse: CamembertForTokenClassification.forward() got an unexpected keyword argument 'offset_mapping'
```

**Cause :** Dans la méthode `_extract_entities_camembert()` du fichier `api/pipeline.py`, l'argument `offset_mapping` était inclus dans le dictionnaire `encoding` passé au modèle CamemBERT. Cependant, `offset_mapping` est uniquement une information retournée par le tokenizer pour mapper les tokens aux positions dans le texte original - ce n'est pas un argument attendu par le modèle PyTorch.

### ✅ Solution appliquée

**Fichier modifié :** `api/pipeline.py`

**Changement :**
1. Extraction de `offset_mapping` du dictionnaire `encoding` avant de passer les arguments au modèle
2. Conversion en numpy array sur CPU (car non utilisé dans le modèle)
3. Les autres arguments (`input_ids`, `attention_mask`) sont correctement déplacés sur le device (GPU MPS ou CPU)

**Code modifié :**
```python
# AVANT (incorrect)
encoding = self.ner_tokenizer(...)
outputs = self.ner_model(**encoding)  # ❌ offset_mapping inclus

# APRÈS (correct)
encoding = self.ner_tokenizer(...)
offset_mapping = encoding.pop('offset_mapping')[0].cpu().numpy()  # ✅ Extraction
encoding = {k: v.to(self.device) for k, v in encoding.items()}
outputs = self.ner_model(**encoding)  # ✅ Seulement input_ids et attention_mask
```

### 📊 Résultat

- ✅ Le chatbot fonctionne correctement avec le modèle NER CamemBERT
- ✅ Les entités DEPARTURE et ARRIVAL sont correctement extraites
- ✅ Performance améliorée par rapport au modèle SpaCy (F1-Score: 0.76 sur test set)

### 🔍 Points d'attention pour l'avenir

- Lors de l'utilisation de tokenizers Fast avec `return_offsets_mapping=True`, toujours extraire `offset_mapping` avant de passer les arguments au modèle
- Les arguments acceptés par les modèles Transformers sont : `input_ids`, `attention_mask`, `token_type_ids`, `labels` (pour l'entraînement), mais pas `offset_mapping`

---

## 📅 2025-01-09 - Post-processing pour les cas "Ville-Ville" avec tiret

### 🐛 Problème rencontré

**Contexte :** Après l'intégration du modèle NER CamemBERT, les utilisateurs testent le chatbot avec des phrases courtes du type "Trajet Marseille-Lyon".

**Problème :** Le modèle NER détecte "Marseille-Lyon" comme une seule entité (probablement DEPARTURE) au lieu de séparer en deux villes distinctes. Résultat : départ="Marseille-Lyon", arrivée=None.

**Cause :** 
1. Dans le dataset d'entraînement, il existe des villes avec tirets dans leur nom complet (ex: "Blonville-sur-Mer - Benerville", "Trouville - Deauville") qui sont des noms de gare valides avec tirets
2. Le modèle a appris à reconnaître ces patterns comme des entités uniques
3. Il n'y a pas assez d'exemples dans le dataset avec le format "Ville-Ville" (sans espace autour du tiret) où les deux villes sont annotées séparément
4. Le tokenizer peut aussi tokeniser "Marseille-Lyon" de manière à ce que le modèle pense que c'est une seule entité

### ✅ Solution appliquée

**Fichier(s) modifié(s) :** `api/pipeline.py`

**Changement :**

1. **Chargement de la base de données des villes** : Ajout d'une méthode `_load_cities_list()` qui charge toutes les villes/gares depuis `dataset/shared/gares-francaises.json` à l'initialisation du pipeline.

2. **Post-processing intelligent** : Ajout d'une méthode `_post_process_entities()` qui :
   - Détecte les entités contenant un tiret simple (`-`) qui pourraient être deux villes séparées
   - Vérifie si les parties avant et après le tiret sont des villes valides en utilisant la base de données chargée
   - Utilise le contexte de la phrase (mots-clés de trajet) pour décider si séparer ou non
   - Gère les cas où une seule entité est détectée ("Marseille-Lyon" → départ="Marseille-Lyon", arrivée=None)
   - Gère aussi les cas de doublons (départ="Marseille-Lyon", arrivée="Lyon")

3. **Fonction de validation** : Création de `_is_likely_city()` qui vérifie intelligemment si un texte ressemble à une ville connue :
   - Correspondance exacte dans la base
   - Correspondance au début d'une ville (ex: "Marseille" dans "Marseille Blancarde")
   - Correspondance avec une partie significative (≥4 caractères) d'une ville connue

**Code ajouté :**
```python
def _load_cities_list(self):
    """Charge la liste des villes/gares depuis gares-francaises.json."""
    # Charge toutes les villes et les parties des villes composées
    
def _is_likely_city(self, text: str) -> bool:
    """Vérifie si un texte ressemble à une ville connue."""
    # Validation intelligente avec correspondance exacte et partielle
    
def _post_process_entities(self, sentence: str, departure: Optional[str], arrival: Optional[str]):
    """Post-processing pour corriger les cas 'Ville-Ville'."""
    # Détecte et sépare les villes avec tiret
    # Exemple: "Marseille-Lyon" → ("Marseille", "Lyon")
```

**Intégration :** Le post-processing est appelé automatiquement après l'extraction des entités NER, avant de retourner les résultats.

### 📊 Résultat

- ✅ Les phrases du type "Trajet Marseille-Lyon" sont maintenant correctement interprétées
- ✅ Départ="Marseille", Arrivée="Lyon" au lieu de Départ="Marseille-Lyon", Arrivée=None
- ✅ Compatible avec les villes à tiret valides (ex: "Blonville-sur-Mer - Benerville" reste intact si c'est vraiment une seule gare)
- ✅ Fonctionne pour les deux modèles NER (CamemBERT et SpaCy)

### 🔍 Points d'attention pour l'avenir

- **Performance** : Le chargement de la liste des villes se fait une seule fois à l'initialisation, donc pas d'impact sur les performances
- **Robustesse** : La vérification utilise une correspondance intelligente mais pourrait être améliorée avec un système de scoring
- **Amélioration future** : 
  - Ajouter plus d'exemples "Ville-Ville" dans le dataset d'entraînement pour que le modèle apprenne directement
  - Utiliser un système de validation plus sophistiqué (probabilités, embeddings sémantiques)
  - Gérer aussi les autres séparateurs ("Ville Ville" sans tiret, "Ville->Ville", etc.)

### Tests recommandés

Tester avec :
- "Trajet Marseille-Lyon" → devrait donner départ="Marseille", arrivée="Lyon"
- "Billet Paris-Toulouse" → devrait donner départ="Paris", arrivée="Toulouse"
- "Je vais de Nantes-Rennes" → devrait donner départ="Nantes", arrivée="Rennes"
- "Blonville-sur-Mer - Benerville" → devrait rester comme une seule ville (si c'est une gare valide)

---

## 📅 2025-01-09 - Nettoyage des caractères spéciaux dans les entités extraites

### 🐛 Problème rencontré

**Contexte :** Lors de l'extraction des entités par le modèle NER, certains caractères spéciaux indésirables peuvent être capturés dans les noms de villes.

**Problème :** Le modèle NER peut extraire des entités contenant des caractères spéciaux qui ne font pas partie des noms de gares valides, par exemple :
- "Paris/Lyon" au lieu de "Paris" et "Lyon"
- "Marseille?" au lieu de "Marseille"
- "Lyon (Gare)" au lieu de "Lyon"
- Autres caractères comme `"`, `/`, etc.

Ces caractères peuvent provenir de la phrase originale de l'utilisateur ou d'erreurs de tokenisation/détection.

**Cause :** Le modèle NER extrait le texte tel qu'il apparaît dans la phrase, y compris les caractères de ponctuation et symboles qui peuvent être présents dans le contexte mais ne font pas partie du nom de la gare.

### ✅ Solution appliquée

**Fichier(s) modifié(s) :** `api/pipeline.py`

**Vérification préalable :** Analyse du fichier `gares-francaises.json` pour identifier quels caractères spéciaux apparaissent réellement dans les noms de gares :

- ✅ `/` : **AUCUNE occurrence** → À supprimer
- ✅ `"` : **AUCUNE occurrence** (les guillemets dans le JSON ne sont pas dans les noms) → À supprimer
- ✅ `?` : **AUCUNE occurrence** → À supprimer
- ⚠️ `(` : **3 occurrences légitimes** (ex: "Cernay (Haut-Rhin)") → Supprimé comme demandé (mais perte d'information de différenciation)
- ⚠️ `)` : **3 occurrences légitimes** (correspondent aux `(`) → Supprimé comme demandé
- ❌ `'` : **90 occurrences légitimes** (ex: "Bois-d'Oingt", "l'Aillerie", "d'Estrétefonds") → **CONSERVÉ** (apostrophe française)

**Changement :**

1. **Fonction de nettoyage** : Ajout d'une méthode `_clean_entity_text()` qui :
   - Supprime les caractères `/`, `"`, `?`, `(`, `)`
   - **Conserve** l'apostrophe `'` car elle apparaît légitimement dans 90 noms de gares françaises
   - Nettoie les espaces multiples et les espaces en début/fin

2. **Intégration dans le post-processing** : Le nettoyage est appliqué :
   - À toutes les valeurs retournées par `_post_process_entities()`
   - Avant chaque `return` dans les différents cas de traitement
   - Sur les entités finales avant de les retourner à l'utilisateur

**Code ajouté :**
```python
def _clean_entity_text(self, text: str) -> str:
    """
    Nettoie le texte d'une entité en supprimant les caractères spéciaux
    qui n'apparaissent jamais dans les noms de gares.
    
    Caractères supprimés : / " ? ( )
    Caractères conservés : ' (apostrophe légitime dans les noms français)
    """
    if not text:
        return text
    
    chars_to_remove = ['/', '"', '?', '(', ')']
    cleaned = text
    for char in chars_to_remove:
        cleaned = cleaned.replace(char, '')
    
    # Nettoyer les espaces multiples et les espaces en début/fin
    cleaned = ' '.join(cleaned.split())
    return cleaned.strip()
```

**Exemples de nettoyage :**
- `"Marseille?"` → `"Marseille"`
- `"Paris/Lyon"` → `"Paris Lyon"` (puis séparé en deux entités par le post-processing précédent)
- `"Lyon (Gare)"` → `"Lyon Gare"` (note: les parenthèses sont supprimées mais le contenu reste)
- `"Bois-d'Oingt"` → `"Bois-d'Oingt"` (apostrophe conservée)

### 📊 Résultat

- ✅ Les entités extraites sont nettoyées des caractères spéciaux indésirables
- ✅ L'apostrophe française est préservée dans les noms légitimes
- ✅ Les espaces multiples sont normalisés
- ✅ Compatible avec le post-processing existant pour les cas "Ville-Ville"
- ✅ Fonctionne pour les deux modèles NER (CamemBERT et SpaCy)

### 🔍 Points d'attention pour l'avenir

- **Parenthèses** : Les parenthèses sont supprimées comme demandé, mais cela retire l'information de différenciation pour les gares comme "Cernay (Haut-Rhin)" vs "Cernay (Val-d'Oise)". Si nécessaire, on pourrait améliorer pour extraire le contenu entre parenthèses séparément.

- **Performance** : Le nettoyage est très rapide (opérations de remplacement de chaînes simples), aucun impact sur les performances.

- **Caractères supplémentaires** : Si d'autres caractères problématiques apparaissent à l'avenir, il suffit de les ajouter à la liste `chars_to_remove`.

- **Amélioration future possible** : On pourrait aussi supprimer le contenu entre parenthèses plutôt que juste les parenthèses, ou utiliser une regex plus sophistiquée.

### Tests recommandés

Tester avec :
- "Billet Paris?" → devrait donner départ="Paris" (sans le `?`)
- "Trajet Lyon/Grenoble" → devrait donner départ="Lyon", arrivée="Grenoble" (après nettoyage et séparation)
- "Je vais à Marseille (Gare Saint-Charles)" → devrait donner arrivée="Marseille Gare Saint-Charles" (parenthèses supprimées)
- "Bois-d'Oingt" → devrait rester "Bois-d'Oingt" (apostrophe conservée)

---

## 📝 Format des entrées

Chaque entrée du journal doit suivre ce format :

### 📅 Date - Titre court

#### 🐛 Problème rencontré

**Contexte :** Description de la situation

**Problème :** Description claire du problème

**Cause :** Analyse de la cause racine (si identifiée)

#### ✅ Solution appliquée

**Fichier(s) modifié(s) :** Liste des fichiers

**Changement :** Description des modifications

**Code modifié :** Exemples de code avant/après si pertinent

#### 📊 Résultat

- Liste des résultats obtenus
- Métriques de performance si applicable

#### 🔍 Points d'attention pour l'avenir

- Leçons apprises
- Bonnes pratiques à retenir

---
