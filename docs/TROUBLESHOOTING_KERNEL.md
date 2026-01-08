# Dépannage - Problèmes de Kernel dans Cursor

## Problème : Imports qui bloquent avec le kernel Docker

### Diagnostic

Quand Cursor se connecte au kernel Docker, il peut y avoir plusieurs problèmes :

1. **Le kernel utilise le mauvais Python** : Cursor peut pointer vers un Python local au lieu du Python Docker
2. **Les chemins ne correspondent pas** : Le workspace dans Docker est `/workspace` mais Cursor peut chercher ailleurs
3. **Le kernel n'est pas correctement connecté** : La connexion au serveur Jupyter Docker n'est pas établie

### Solutions

#### Solution 1 : Vérifier la connexion au kernel Docker

Dans Cursor, vérifiez que le kernel est bien connecté :

1. Ouvrez le notebook
2. Regardez en haut à droite : le kernel devrait afficher quelque chose comme `Python 3.10.x` ou `Jupyter Server`
3. Si vous voyez "Select Kernel", cliquez dessus et vérifiez que c'est bien le serveur Docker

#### Solution 2 : Vérifier que Docker tourne

```bash
# Vérifier que le conteneur Jupyter tourne
docker compose ps jupyter

# Voir les logs pour vérifier qu'il n'y a pas d'erreur
docker compose logs jupyter
```

#### Solution 3 : Tester les imports dans Docker directement

```bash
# Exécuter Python dans le conteneur Docker
docker compose exec jupyter python -c "import pandas; import numpy; import sklearn; print('OK')"
```

Si ça fonctionne dans Docker mais pas dans Cursor, c'est un problème de connexion du kernel.

#### Solution 4 : Reconfigurer la connexion au kernel

Dans Cursor :

1. Cliquez sur "Select Kernel" en haut à droite du notebook
2. Choisissez "Existing Jupyter Server"
3. URL : `http://localhost:8888`
4. Token : Si demandé, récupérez-le avec :
   ```bash
   docker compose logs jupyter | grep -i token
   ```
   Ou si pas de token (comme configuré dans docker-entrypoint.sh), laissez vide

#### Solution 5 : Utiliser un kernel local (Alternative)

Si le problème persiste, créez un kernel local :

```bash
# 1. Créer un environnement virtuel (si pas déjà fait)
python3 -m venv venv

# 2. Activer
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Installer ipykernel
pip install ipykernel

# 5. Créer le kernel
python -m ipykernel install --user --name=t-aia-911-lil3-local
```

Puis dans Cursor, sélectionnez le kernel `t-aia-911-lil3-local`.

### Vérification rapide

Dans une cellule du notebook, exécutez :

```python
import sys
import os

print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")

# Tester les imports un par un
try:
    import pandas as pd
    print("✅ pandas")
except ImportError as e:
    print(f"❌ pandas: {e}")

try:
    import numpy as np
    print("✅ numpy")
except ImportError as e:
    print(f"❌ numpy: {e}")

try:
    import sklearn
    print("✅ sklearn")
except ImportError as e:
    print(f"❌ sklearn: {e}")

try:
    import joblib
    print("✅ joblib")
except ImportError as e:
    print(f"❌ joblib: {e}")
```

### Indicateurs que le kernel Docker fonctionne

- `sys.executable` devrait pointer vers `/usr/local/bin/python` ou similaire (dans Docker)
- `os.getcwd()` devrait être `/workspace` (dans Docker)
- Les imports devraient tous fonctionner

### Indicateurs que le kernel local est utilisé

- `sys.executable` pointe vers un chemin local (ex: `/Users/.../venv/bin/python`)
- `os.getcwd()` est le répertoire local du projet
- Les imports peuvent échouer si les dépendances ne sont pas installées localement

## Problème spécifique : "ModuleNotFoundError"

Si vous obtenez `ModuleNotFoundError: No module named 'X'` :

1. **Dans Docker** : Vérifiez que les dépendances sont installées
   ```bash
   docker compose exec jupyter pip list | grep pandas
   ```

2. **Dans Cursor** : Vérifiez que le kernel pointe bien vers Docker
   - Le `sys.executable` devrait être dans Docker
   - Si c'est local, installez les dépendances localement ou reconnectez le kernel Docker

3. **Réinstaller dans Docker** (si nécessaire) :
   ```bash
   docker compose exec jupyter pip install -r requirements.txt
   ```

## Solution de contournement rapide

Si le problème persiste, utilisez l'environnement local :

```bash
# Installer tout localement
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install ipykernel
python -m ipykernel install --user --name=t-aia-911-lil3-local
```

Puis dans Cursor, sélectionnez `t-aia-911-lil3-local` comme kernel.

