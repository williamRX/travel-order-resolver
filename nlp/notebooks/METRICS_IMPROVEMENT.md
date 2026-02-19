# Amélioration de la Sauvegarde des Métriques

## 📋 Code à Copier dans le Notebook

### Cellule 15 - Évaluation (Améliorée)

**Remplacez** la section qui calcule les métriques par ce code :

```python
# Calculer les métriques globales
test_accuracy = accuracy_score(true_labels, true_predictions)
test_precision = precision_score(true_labels, true_predictions)
test_recall = recall_score(true_labels, true_predictions)
test_f1 = f1_score(true_labels, true_predictions)

print(f"\n📈 Métriques globales sur le test set:")
print(f"   Accuracy:  {test_accuracy:.4f}")
print(f"   Precision: {test_precision:.4f}")
print(f"   Recall:    {test_recall:.4f}")
print(f"   F1-Score:  {test_f1:.4f}")

# Extraire les métriques par type d'entité depuis le classification_report
classification_report_dict = seqeval_classification_report(
    true_labels, 
    true_predictions, 
    output_dict=True
)

# Rapport détaillé (format texte)
print(f"\n📋 Rapport de classification (par entité):")
print(seqeval_classification_report(true_labels, true_predictions, output_dict=False))

# Extraire les métriques par type d'entité
test_metrics_per_type = {}
for entity_type in ['DEPARTURE', 'ARRIVAL']:
    if entity_type in classification_report_dict:
        test_metrics_per_type[entity_type] = {
            'precision': float(classification_report_dict[entity_type]['precision']),
            'recall': float(classification_report_dict[entity_type]['recall']),
            'f1': float(classification_report_dict[entity_type]['f1-score']),
            'support': int(classification_report_dict[entity_type]['support'])
        }
    else:
        # Si l'entité n'est pas dans le rapport (peut arriver si aucune prédiction de ce type)
        test_metrics_per_type[entity_type] = {
            'precision': 0.0,
            'recall': 0.0,
            'f1': 0.0,
            'support': 0
        }

print(f"\n📊 Métriques par type d'entité:")
for entity_type, metrics in test_metrics_per_type.items():
    print(f"   {entity_type}:")
    print(f"      Precision: {metrics['precision']:.4f}")
    print(f"      Recall:    {metrics['recall']:.4f}")
    print(f"      F1-Score:  {metrics['f1']:.4f}")
    print(f"      Support:   {metrics['support']}")
```

### Cellule 16 - Sauvegarde (Améliorée)

**Remplacez** la section de sauvegarde des métriques par ce code :

```python
    # Préparer l'historique d'entraînement
    training_history = []
    if hasattr(trainer, 'state') and trainer.state.log_history:
        eval_logs = [log for log in trainer.state.log_history if 'eval_loss' in log]
        for log in eval_logs:
            epoch_metrics = {
                'epoch': float(log.get('epoch', 0)),
                'step': int(log.get('step', 0)),
                'eval_loss': float(log.get('eval_loss', 0)),
                'eval_accuracy': float(log.get('eval_accuracy', 0)),
                'eval_precision': float(log.get('eval_precision', 0)),
                'eval_recall': float(log.get('eval_recall', 0)),
                'eval_f1': float(log.get('eval_f1', 0))
            }
            training_history.append(epoch_metrics)
    
    # Sauvegarder les métriques avec détails par type d'entité
    metrics = {
        'test_metrics': {
            'accuracy': float(test_accuracy),
            'precision': float(test_precision),
            'recall': float(test_recall),
            'f1': float(test_f1),
            'per_type': test_metrics_per_type  # Métriques par type d'entité (DEPARTURE, ARRIVAL)
        },
        'model_name': MODEL_NAME,
        'max_length': MAX_LENGTH,
        'batch_size': BATCH_SIZE,
        'learning_rate': LEARNING_RATE,
        'num_epochs': NUM_EPOCHS,
        'labels': LABELS,
        'experiment_name': EXPERIMENT_NAME,
        'version': VERSION,
        'created_at': datetime.now().isoformat()
    }
    
    # Ajouter l'historique d'entraînement si disponible
    if training_history:
        metrics['training_history'] = training_history
    
    metrics_file = model_dir / "metrics.json"
    with open(metrics_file, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Modèle sauvegardé dans: {model_dir}")
    print(f"   Modèle: {model_dir / 'pytorch_model.bin'}")
    print(f"   Tokenizer: {model_dir / 'tokenizer.json'}")
    print(f"   Métriques: {metrics_file}")
    print(f"   📊 Métriques par type sauvegardées: DEPARTURE, ARRIVAL")
    if training_history:
        print(f"   📈 Historique d'entraînement sauvegardé ({len(training_history)} époques)")
```

## 📊 Format de Sortie Amélioré

Le fichier `metrics.json` aura maintenant ce format :

```json
{
  "test_metrics": {
    "accuracy": 0.9836,
    "precision": 0.7467,
    "recall": 0.8989,
    "f1": 0.8158,
    "per_type": {
      "DEPARTURE": {
        "precision": 0.7300,
        "recall": 0.8800,
        "f1": 0.7900,
        "support": 2871
      },
      "ARRIVAL": {
        "precision": 0.7700,
        "recall": 0.9200,
        "f1": 0.8400,
        "support": 2607
      }
    }
  },
  "training_history": [
    {
      "epoch": 1.0,
      "step": 100,
      "eval_loss": 0.1234,
      "eval_f1": 0.7500,
      ...
    },
    ...
  ],
  "model_name": "camembert-base",
  "max_length": 128,
  "batch_size": 16,
  "learning_rate": 2e-05,
  "num_epochs": 3,
  "labels": ["O", "B-DEPARTURE", "I-DEPARTURE", "B-ARRIVAL", "I-ARRIVAL"],
  "experiment_name": "ner_camembert_20260112_215327",
  "version": "v1",
  "created_at": "2026-01-12T21:53:27.123456"
}
```

## ✅ Avantages

1. **Métriques par type** : Identifie si DEPARTURE ou ARRIVAL pose plus de problèmes
2. **Historique d'entraînement** : Permet de voir l'évolution des métriques
3. **Support** : Nombre d'exemples par type (utile pour comprendre la distribution)
4. **Timestamp** : Date de création du modèle

## 🔍 Utilisation

Avec ces métriques, vous pourrez facilement comparer :
- F1-DEPARTURE vs F1-ARRIVAL
- Precision vs Recall pour chaque type
- Évolution des métriques au cours de l'entraînement
