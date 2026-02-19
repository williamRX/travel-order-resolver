#!/usr/bin/env python3
"""
Script pour corriger l'erreur de syntaxe dans le notebook.
Supprime le code dupliqué et mal formaté dans la cellule de sauvegarde.
"""

import json
from pathlib import Path

def fix_notebook():
    """Corrige le notebook en supprimant le code dupliqué."""
    
    notebook_path = Path(__file__).resolve().parent.parent / "nlp" / "notebooks" / "02_ner_training_camembert.ipynb"
    
    print(f"📖 Lecture du notebook: {notebook_path}")
    
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    # Trouver la cellule avec SAVE_FINAL_MODEL
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            if 'if SAVE_FINAL_MODEL:' in source:
                print(f"🔧 Correction de la cellule {i}...")
                
                # Code correct pour la cellule
                correct_code = """if SAVE_FINAL_MODEL:
    print("💾 Sauvegarde du modèle final...")
    
    # Chemins de sauvegarde
    model_dir = MODELS_DIR / f"{EXPERIMENT_NAME}_{VERSION}"
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # Sauvegarder le modèle et le tokenizer
    model.save_pretrained(str(model_dir))
    tokenizer.save_pretrained(str(model_dir))
    
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
else:
    print("ℹ️  Sauvegarde du modèle désactivée (SAVE_FINAL_MODEL=False)")
"""
                
                # Remplacer le contenu de la cellule
                cell['source'] = [line + '\n' for line in correct_code.split('\n')]
                # Supprimer le dernier '\n' de la dernière ligne
                if cell['source']:
                    cell['source'][-1] = cell['source'][-1].rstrip('\n')
                
                # Réinitialiser execution_count
                cell['execution_count'] = None
                cell['outputs'] = []
                
                print(f"✅ Cellule {i} corrigée")
                break
    
    # Créer une sauvegarde
    backup_path = notebook_path.with_suffix('.ipynb.backup2')
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)
    print(f"💾 Sauvegarde créée: {backup_path}")
    
    # Sauvegarder le notebook corrigé
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)
    print(f"✅ Notebook corrigé: {notebook_path}")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(fix_notebook())
