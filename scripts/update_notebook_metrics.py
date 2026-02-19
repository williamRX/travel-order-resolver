#!/usr/bin/env python3
"""
Script pour mettre à jour le notebook NLP avec des métriques améliorées.
Ajoute les métriques par type d'entité (DEPARTURE, ARRIVAL) et l'historique d'entraînement.
"""

import json
import sys
from pathlib import Path

def update_notebook():
    """Met à jour le notebook avec les améliorations de métriques."""
    
    notebook_path = Path(__file__).resolve().parent.parent / "nlp" / "notebooks" / "02_ner_training_camembert.ipynb"
    
    if not notebook_path.exists():
        print(f"❌ Notebook non trouvé: {notebook_path}")
        return 1
    
    print(f"📖 Lecture du notebook: {notebook_path}")
    
    # Lire le notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    # Code amélioré pour la cellule d'évaluation
    improved_evaluation_code = """# Calculer les métriques globales
test_accuracy = accuracy_score(true_labels, true_predictions)
test_precision = precision_score(true_labels, true_predictions)
test_recall = recall_score(true_labels, true_predictions)
test_f1 = f1_score(true_labels, true_predictions)

print(f"\\n📈 Métriques globales sur le test set:")
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
print(f"\\n📋 Rapport de classification (par entité):")
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

print(f"\\n📊 Métriques par type d'entité:")
for entity_type, metrics in test_metrics_per_type.items():
    print(f"   {entity_type}:")
    print(f"      Precision: {metrics['precision']:.4f}")
    print(f"      Recall:    {metrics['recall']:.4f}")
    print(f"      F1-Score:  {metrics['f1']:.4f}")
    print(f"      Support:   {metrics['support']}")"""
    
    # Code amélioré pour la sauvegarde
    improved_save_code = """    # Préparer l'historique d'entraînement
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
        print(f"   📈 Historique d'entraînement sauvegardé ({len(training_history)} époques)")"""
    
    # Chercher et remplacer les cellules
    updated = False
    
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            
            # Remplacer la section d'évaluation
            if '# Calculer les métriques' in source and 'test_accuracy = accuracy_score' in source:
                if 'test_metrics_per_type' not in source:
                    print("🔄 Mise à jour de la cellule d'évaluation...")
                    # Trouver le début et la fin
                    lines = cell['source']
                    new_lines = []
                    skip = False
                    
                    for i, line in enumerate(lines):
                        if '# Calculer les métriques' in line:
                            skip = True
                            new_lines.extend(improved_evaluation_code.split('\n'))
                            new_lines = [l + '\n' for l in new_lines if l]
                            new_lines[-1] = new_lines[-1].rstrip('\n')
                        elif skip and 'print(seqeval_classification_report(true_labels, true_predictions))' in line:
                            skip = False
                            continue
                        elif not skip:
                            new_lines.append(line)
                        elif skip:
                            continue
                    
                    cell['source'] = new_lines
                    updated = True
            
            # Remplacer la section de sauvegarde
            if '# Sauvegarder les métriques' in source and "'test_accuracy': float(test_accuracy)" in source:
                if "'per_type'" not in source:
                    print("🔄 Mise à jour de la cellule de sauvegarde...")
                    lines = cell['source']
                    new_lines = []
                    skip = False
                    in_metrics = False
                    
                    for i, line in enumerate(lines):
                        if '# Sauvegarder les métriques' in line:
                            in_metrics = True
                            new_lines.append(line)
                        elif in_metrics and "'test_accuracy':" in line:
                            skip = True
                            new_lines.extend(improved_save_code.split('\n'))
                            new_lines = [l + '\n' for l in new_lines if l]
                            new_lines[-1] = new_lines[-1].rstrip('\n')
                        elif skip and "metrics_file = model_dir / \"metrics.json\"" in line:
                            skip = False
                            continue
                        elif not skip:
                            new_lines.append(line)
                        elif skip:
                            continue
                        else:
                            new_lines.append(line)
                    
                    cell['source'] = new_lines
                    updated = True
    
    if updated:
        # Créer une sauvegarde
        backup_path = notebook_path.with_suffix('.ipynb.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1, ensure_ascii=False)
        print(f"💾 Sauvegarde créée: {backup_path}")
        
        # Sauvegarder le notebook mis à jour
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1, ensure_ascii=False)
        print(f"✅ Notebook mis à jour: {notebook_path}")
        return 0
    else:
        print("ℹ️  Notebook déjà à jour ou structure différente")
        print("💡 Consultez nlp/notebooks/METRICS_IMPROVEMENT.md pour les instructions manuelles")
        return 0

if __name__ == "__main__":
    sys.exit(update_notebook())
