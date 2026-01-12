# Accès à Jupyter Notebook/Lab

## 🔍 Vérifier si Jupyter tourne

### Option 1 : Vérifier avec Docker

```bash
# Voir les conteneurs Jupyter en cours d'exécution
docker ps --filter "name=jupyter"

# Voir les logs
docker logs t-aia-911-lil3-jupyter
```

### Option 2 : Vérifier le port 8888

```bash
# Voir ce qui utilise le port 8888
lsof -i :8888

# Ou avec netstat
netstat -an | grep 8888
```

### Option 3 : Tester l'accès

Ouvrez votre navigateur et allez sur : **http://localhost:8888**

---

## 🚀 Lancer Jupyter

### Avec Docker (Recommandé)

```bash
# Lancer uniquement Jupyter
docker-compose up jupyter

# Ou en arrière-plan
docker-compose up -d jupyter
```

**Accès** : http://localhost:8888

### Sans Docker (Local)

Si vous avez un environnement virtuel local :

```bash
# Activer l'environnement
source venv/bin/activate  # ou: conda activate t-aia-911-lil3

# Lancer Jupyter Lab
jupyter lab

# Ou Jupyter Notebook
jupyter notebook
```

**Accès** : http://localhost:8888 (ou le port affiché dans le terminal)

---

## 📋 Ports par défaut

- **Jupyter** : Port **8888**
- **API** : Port **8000**
- **Frontend** : Port **3000**

---

## 🔧 Dépannage

### Le port 8888 est déjà utilisé

Si vous obtenez une erreur "port already in use" :

1. **Vérifier ce qui utilise le port** :
   ```bash
   lsof -i :8888
   ```

2. **Arrêter le processus** :
   ```bash
   # Si c'est Docker
   docker-compose stop jupyter
   
   # Si c'est un processus local
   kill <PID>  # Remplacez <PID> par le numéro du processus
   ```

3. **Ou utiliser un autre port** :
   ```bash
   # Dans docker-compose.yml, changer:
   ports:
     - "8889:8888"  # Utiliser le port 8889 au lieu de 8888
   ```

### Jupyter ne répond pas

1. **Vérifier les logs** :
   ```bash
   docker logs t-aia-911-lil3-jupyter
   ```

2. **Redémarrer Jupyter** :
   ```bash
   docker-compose restart jupyter
   ```

3. **Reconstruire si nécessaire** :
   ```bash
   docker-compose down
   docker-compose build jupyter
   docker-compose up jupyter
   ```

---

## ✅ Vérification rapide

Pour vérifier rapidement si Jupyter est accessible :

```bash
curl http://localhost:8888
```

Si vous obtenez du HTML, Jupyter fonctionne ! 🎉

