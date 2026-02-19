# Vérification Jupyter + GPU pour Entraînement NLP

Ce guide vous aide à vérifier que tout est prêt pour entraîner votre modèle NLP en local avec GPU (MPS sur Mac Apple Silicon).

---

## 🔍 Vérification Rapide

### Option 1 : Script automatique (avec environnement virtuel)

```bash
# Activer l'environnement virtuel
source $HOME/ml_env/bin/activate

# Lancer la vérification
python scripts/check_jupyter_gpu.py
```

### Option 2 : Vérification manuelle

```bash
# 1. Activer l'environnement virtuel
source $HOME/ml_env/bin/activate

# 2. Vérifier PyTorch + MPS
python3 -c "
import torch
print(f'PyTorch: {torch.__version__}')
print(f'MPS disponible: {torch.backends.mps.is_available()}')
if torch.backends.mps.is_available():
    device = torch.device('mps')
    x = torch.randn(10, 10).to(device)
    print('✅ MPS fonctionne!')
else:
    print('❌ MPS non disponible')
"

# 3. Vérifier le dataset
ls -lh dataset/nlp/json/nlp_training_data.jsonl

# 4. Vérifier le notebook
ls -lh nlp/notebooks/02_ner_training_camembert.ipynb
```

---

## ✅ Checklist de Vérification

### 1. Environnement virtuel
- [ ] Environnement `ml_env` existe dans `$HOME/ml_env`
- [ ] PyTorch installé avec support MPS
- [ ] Dépendances installées (transformers, datasets, seqeval)

### 2. Dataset NLP
- [ ] Dataset généré : `dataset/nlp/json/nlp_training_data.jsonl`
- [ ] Dataset contient des phrases (vérifier avec `wc -l`)

### 3. Notebook
- [ ] Notebook existe : `nlp/notebooks/02_ner_training_camembert.ipynb`
- [ ] Notebook configuré pour MPS (détection automatique)

### 4. GPU MPS
- [ ] Mac Apple Silicon (M1/M2/M3/M4)
- [ ] PyTorch avec support MPS
- [ ] Test MPS réussi

---

## 🚀 Lancement de Jupyter

### Méthode 1 : Script simplifié (recommandé)

```bash
./lancer_jupyter_simple.sh
```

Ce script :
- ✅ Active automatiquement l'environnement virtuel
- ✅ Vérifie que MPS fonctionne
- ✅ Lance Jupyter sur un port libre
- ✅ Configure le token d'accès

### Méthode 2 : Manuel

```bash
# 1. Activer l'environnement
source $HOME/ml_env/bin/activate

# 2. Lancer Jupyter
jupyter notebook --notebook-dir=$(pwd) --port=8888
```

---

## 📝 Utilisation du Notebook

1. **Ouvrir le notebook** : `nlp/notebooks/02_ner_training_camembert.ipynb`

2. **Vérifier le device** : La première cellule vérifie automatiquement MPS
   - Si MPS disponible → `device = mps` (GPU)
   - Sinon → `device = cpu` (CPU, plus lent)

3. **Générer le nouveau dataset** (si nécessaire) :
   ```python
   # Dans une cellule du notebook ou en ligne de commande
   !python dataset/generators/nlp/dataset_generator.py
   ```

4. **Entraîner le modèle** : Exécutez toutes les cellules du notebook

---

## ⚠️ Problèmes Courants

### PyTorch non installé
```bash
source $HOME/ml_env/bin/activate
pip install torch torchvision torchaudio
```

### MPS non disponible
- Vérifiez que vous êtes sur un Mac Apple Silicon
- Vérifiez que PyTorch 2.0+ est installé
- Vérifiez que macOS est à jour

### Dataset manquant
```bash
# Générer le dataset avec les nouveaux patterns
python dataset/generators/nlp/dataset_generator.py
```

### Environnement virtuel manquant
```bash
# Créer l'environnement
./setup_mac_ml.sh
```

---

## 🎯 Résultat Attendu

Quand tout fonctionne, vous devriez voir :

```
✅ GPU Apple Silicon (MPS) détecté et disponible!
   Device: mps
   🚀 Accélération GPU activée pour l'entraînement NER avec CamemBERT
   ✅ Test MPS réussi - Prêt pour l'entraînement!
```

L'entraînement sera alors **beaucoup plus rapide** (30-60 min avec GPU vs 3-6h avec CPU).

---

## 📊 Performance Attendue

- **Avec GPU MPS** : ~30-60 minutes pour 3 époques
- **Sans GPU (CPU)** : ~3-6 heures pour 3 époques

Le GPU accélère l'entraînement d'environ **6-10x** !
