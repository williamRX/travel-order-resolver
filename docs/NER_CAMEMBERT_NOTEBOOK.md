# Notebook NER avec CamemBERT - Guide de Complétion

Le notebook `02_ner_training_camembert.ipynb` a été créé avec les cellules de base. Voici les cellules supplémentaires à ajouter pour compléter le notebook.

## 📋 Cellules à ajouter

### Cellule 3 : Imports et Vérification Device

```python
# ============================================================================
# IMPORTS - Toutes les dépendances nécessaires
# ============================================================================

import pandas as pd
import numpy as np
import json
from sklearn.model_selection import train_test_split
from seqeval.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report as seqeval_classification_report

# PyTorch et Transformers
import torch
from torch.utils.data import Dataset
from transformers import (
    CamembertTokenizer,
    CamembertForTokenClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback
)

# Utilitaires
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

print("✅ Tous les imports effectués avec succès")
```

### Cellule 4 : Vérification MPS

```python
# ============================================================================
# VÉRIFICATION ET CONFIGURATION DU DEVICE (GPU MPS ou CPU)
# ============================================================================

print("\n🔍 Vérification de l'accélération matérielle...")
print("=" * 70)

print(f"🖥️  Système: Apple Silicon (Mac M4)")
print(f"🐍 PyTorch: {torch.__version__}")

if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
    device = torch.device("mps")
    USE_MPS = True
    print(f"\n✅ GPU Apple Silicon (MPS) détecté et disponible!")
    print(f"   Device: {device}")
else:
    device = torch.device("cpu")
    USE_MPS = False
    print(f"\n⚠️  MPS non disponible, utilisation du CPU")
    print(f"   Device: {device}")

print("=" * 70)
print(f"✅ Configuration terminée - Device sélectionné: {device}")
```

### Cellule 5 : Chargement des Données

```python
# Fonction pour charger le dataset JSONL
def load_jsonl(file_path, limit=None):
    """Charge un fichier JSONL et retourne une liste de dictionnaires."""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if limit and i >= limit:
                break
            if line.strip():
                data.append(json.loads(line))
    return data

# Charger les données
print(f"📂 Chargement du dataset depuis {DATASET_PATH}...")
raw_data = load_jsonl(DATASET_PATH, limit=DATASET_LIMIT)
print(f"✅ {len(raw_data)} phrases chargées")

# Statistiques
total_entities = sum(len(item["entities"]) for item in raw_data)
departures = sum(1 for item in raw_data for ent in item["entities"] if ent[2] == "DEPARTURE")
arrivals = sum(1 for item in raw_data for ent in item["entities"] if ent[2] == "ARRIVAL")

print(f"\n📊 Statistiques du dataset:")
print(f"   Total d'entités: {total_entities}")
print(f"   Départs (DEPARTURE): {departures}")
print(f"   Arrivées (ARRIVAL): {arrivals}")
```

### Cellule 6 : Tokenizer et Alignement

```python
# Charger le tokenizer
print(f"🔄 Chargement du tokenizer {MODEL_NAME}...")
tokenizer = CamembertTokenizer.from_pretrained(MODEL_NAME)
print(f"✅ Tokenizer chargé")

# Fonction pour aligner tokens avec entités
def align_tokens_with_entities(text, entities, tokenizer):
    """Aligne les tokens avec les entités et retourne les labels IOB."""
    encoding = tokenizer(
        text,
        max_length=MAX_LENGTH,
        padding='max_length',
        truncation=True,
        return_offsets_mapping=True,
        return_tensors=None
    )
    
    tokens = tokenizer.convert_ids_to_tokens(encoding['input_ids'])
    offset_mapping = encoding['offset_mapping']
    labels = ['O'] * len(tokens)
    
    for start_char, end_char, entity_label in entities:
        entity_tokens = []
        for i, (token_start, token_end) in enumerate(offset_mapping):
            if token_start == token_end == 0:
                continue
            if not (token_end <= start_char or token_start >= end_char):
                entity_tokens.append(i)
        
        if entity_tokens:
            labels[entity_tokens[0]] = f"B-{entity_label}"
            for token_idx in entity_tokens[1:]:
                labels[token_idx] = f"I-{entity_label}"
    
    return tokens, labels, encoding

print("✅ Fonction d'alignement définie")
```

### Cellule 7 : Préparation des Données

```python
# Préparer les données
print("🔄 Préparation des données (alignement tokens/entités)...")
prepared_data = []

for item in tqdm(raw_data, desc="Traitement"):
    try:
        tokens, labels, encoding = align_tokens_with_entities(
            item['text'],
            item['entities'],
            tokenizer
        )
        label_ids = [LABEL2ID.get(label, 0) for label in labels]
        
        prepared_data.append({
            'input_ids': encoding['input_ids'],
            'attention_mask': encoding['attention_mask'],
            'labels': label_ids,
            'text': item['text']
        })
    except Exception as e:
        continue

print(f"✅ {len(prepared_data)} exemples préparés")
```

### Cellule 8 : Split et Dataset

```python
# Split train/test
train_data, test_data = train_test_split(
    prepared_data,
    test_size=TEST_SIZE,
    random_state=RANDOM_SEED
)

val_size_adjusted = VAL_SIZE / (1 - TEST_SIZE)
train_data, val_data = train_test_split(
    train_data,
    test_size=val_size_adjusted,
    random_state=RANDOM_SEED
)

# Classe Dataset
class NERDataset(Dataset):
    def __init__(self, data):
        self.data = data
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        return {
            'input_ids': torch.tensor(item['input_ids'], dtype=torch.long),
            'attention_mask': torch.tensor(item['attention_mask'], dtype=torch.long),
            'labels': torch.tensor(item['labels'], dtype=torch.long)
        }

train_dataset = NERDataset(train_data)
val_dataset = NERDataset(val_data)
test_dataset = NERDataset(test_data)

print(f"✅ Datasets créés: Train={len(train_dataset)}, Val={len(val_dataset)}, Test={len(test_dataset)}")
```

### Cellule 9 : Modèle

```python
# Charger le modèle
print(f"🔄 Chargement du modèle {MODEL_NAME}...")
model = CamembertForTokenClassification.from_pretrained(
    MODEL_NAME,
    num_labels=NUM_LABELS,
    id2label=ID2LABEL,
    label2id=LABEL2ID
)
model.to(device)
print(f"✅ Modèle chargé sur {device}")
```

### Cellule 10 : Métriques

```python
# Fonction pour calculer les métriques NER
def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=2)
    
    true_predictions = [
        [ID2LABEL[p] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    true_labels = [
        [ID2LABEL[l] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    
    return {
        "accuracy": accuracy_score(true_labels, true_predictions),
        "precision": precision_score(true_labels, true_predictions),
        "recall": recall_score(true_labels, true_predictions),
        "f1": f1_score(true_labels, true_predictions),
    }

print("✅ Fonction de calcul des métriques définie")
```

### Cellule 11 : TrainingArguments

```python
training_args = TrainingArguments(
    output_dir=str(CHECKPOINTS_DIR / EXPERIMENT_NAME),
    num_train_epochs=NUM_EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    learning_rate=LEARNING_RATE,
    weight_decay=WEIGHT_DECAY,
    warmup_steps=WARMUP_STEPS,
    logging_dir=str(LOGS_DIR / EXPERIMENT_NAME),
    logging_steps=10,
    eval_strategy="steps",
    eval_steps=100,
    save_strategy="steps",
    save_steps=200,
    save_total_limit=3,
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    greater_is_better=True,
    report_to="none",
    seed=RANDOM_SEED,
    fp16=torch.cuda.is_available() and not USE_MPS,
    dataloader_pin_memory=False,
)

print("✅ Arguments d'entraînement configurés")
```

### Cellule 12 : Trainer

```python
callbacks = []
if EARLY_STOPPING:
    callbacks.append(EarlyStoppingCallback(early_stopping_patience=EARLY_STOPPING_PATIENCE))

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
    callbacks=callbacks
)

print("✅ Trainer créé")
```

### Cellule 13 : Entraînement

```python
print("🚀 Démarrage de l'entraînement...")
train_result = trainer.train()
print("✅ Entraînement terminé!")
```

### Cellule 14 : Évaluation

```python
print("📊 Évaluation sur le test set...")
test_predictions = trainer.predict(test_dataset)
predictions = np.argmax(test_predictions.predictions, axis=2)
labels = test_predictions.label_ids

true_predictions = [
    [ID2LABEL[p] for (p, l) in zip(prediction, label) if l != -100]
    for prediction, label in zip(predictions, labels)
]
true_labels = [
    [ID2LABEL[l] for (p, l) in zip(prediction, label) if l != -100]
    for prediction, label in zip(predictions, labels)
]

test_accuracy = accuracy_score(true_labels, true_predictions)
test_precision = precision_score(true_labels, true_predictions)
test_recall = recall_score(true_labels, true_predictions)
test_f1 = f1_score(true_labels, true_predictions)

print(f"📈 Métriques sur le test set:")
print(f"   Accuracy:  {test_accuracy:.4f}")
print(f"   Precision: {test_precision:.4f}")
print(f"   Recall:    {test_recall:.4f}")
print(f"   F1-Score:  {test_f1:.4f}")

print(f"\n📋 Rapport de classification:")
print(seqeval_classification_report(true_labels, true_predictions))
```

### Cellule 15 : Sauvegarde

```python
if SAVE_FINAL_MODEL:
    print("💾 Sauvegarde du modèle final...")
    model_dir = MODELS_DIR / f"{EXPERIMENT_NAME}_{VERSION}"
    model_dir.mkdir(parents=True, exist_ok=True)
    
    model.save_pretrained(str(model_dir))
    tokenizer.save_pretrained(str(model_dir))
    
    metrics = {
        'test_accuracy': float(test_accuracy),
        'test_precision': float(test_precision),
        'test_recall': float(test_recall),
        'test_f1': float(test_f1),
        'model_name': MODEL_NAME,
        'labels': LABELS,
        'experiment_name': EXPERIMENT_NAME,
        'version': VERSION
    }
    
    metrics_file = model_dir / "metrics.json"
    with open(metrics_file, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Modèle sauvegardé dans: {model_dir}")
```

## 📝 Notes importantes

1. **seqeval** : Nécessaire pour les métriques NER. Installé via `requirements.txt`
2. **Format IOB** : Les labels sont au format IOB (Inside-Outside-Beginning)
3. **Alignement** : L'alignement tokens/entités est crucial pour NER
4. **Device** : Le notebook détecte automatiquement MPS (GPU Mac)

## 🚀 Prochaines étapes

1. Ajouter les cellules manquantes au notebook
2. Installer seqeval : `pip install seqeval`
3. Exécuter le notebook cellule par cellule
4. Comparer les résultats avec le modèle Spacy

