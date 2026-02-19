# Intégration API SNCF - Documentation

## 📋 API SNCF (Navitia)

L'API SNCF utilise **Navitia** comme moteur de recherche d'itinéraires.

### Endpoint principal

```
GET https://api.sncf.com/v1/coverage/sncf/journeys
```

### Authentification

- **Type** : Basic Authentication (HTTP Basic Auth)
- **Username** : Votre clé API SNCF (ex: `16c814cd-07a8-412e-805c-ec3bde6fa9d0`)
- **Password** : Laissez vide (`''`)
- **Méthode** : Utiliser Basic Auth avec `requests` : `auth=(api_key, '')`
- **Alternative** : Inclure directement dans l'URL (si supporté)
- **Obtention** : Inscription sur https://www.sncf-connect.com/open-data/api

### Paramètres principaux

| Paramètre | Type | Obligatoire | Description | Exemple |
|-----------|------|-------------|-------------|---------|
| `from` | string | ✅ Oui | Identifiant de la gare de départ | `stop_area:FR:SA:87391003` |
| `to` | string | ✅ Oui | Identifiant de la gare d'arrivée | `stop_area:FR:SA:87581009` |
| `datetime` | string | ❌ Non | Date/heure du trajet | `20260116T080000` (format: `YYYYMMDDThhmmss`) |
| `datetime_represents` | string | ❌ Non | `departure` ou `arrival` (défaut: `departure`) | `departure` |
| `data_freshness` | string | ❌ Non | `base_schedule` ou `realtime` | `realtime` |
| `max_nb_transfers` | int | ❌ Non | Nombre max de correspondances | `2` |

### Format des identifiants de gares

**Format Navitia SNCF** : `stop_area:SNCF:XXXXX`

Où `XXXXX` est le **code UIC** de la gare (8 chiffres).

**Note** : L'API SNCF utilise le préfixe `stop_area:SNCF:` (pas `stop_area:FR:SA:`).

**Exemple** :
- Gare "Paris Gare du Nord" : Code UIC = `87271007` → Identifiant = `stop_area:SNCF:87271007`
- Gare "Lyon Part-Dieu" : Code UIC = `87722025` → Identifiant = `stop_area:SNCF:87722025`

**Alternatives** : L'API supporte aussi les codes administratifs (`admin:fr:XXXXX`) mais nous utilisons les codes UIC pour les gares.

### Conversion nom de gare → Code UIC

Les gares dans `gares-francaises.json` contiennent :
```json
{
  "nom": "Paris Gare du Nord",
  "codes_uic": "87271007"
}
```

Pour obtenir l'identifiant Navitia :
```
stop_area:FR:SA:{codes_uic}
```

### Exemple de requête complète

```http
GET https://api.sncf.com/v1/coverage/sncf/journeys?
  from=stop_area:SNCF:87391003&
  to=stop_area:SNCF:87581009&
  datetime=20260116T080000&
  datetime_represents=departure&
  data_freshness=realtime&
  max_nb_transfers=2

# Authentification : Basic Auth
# Username: <votre_clé_api>
# Password: (vide)
```

**Exemple avec Python requests** :
```python
import requests

api_key = "16c814cd-07a8-412e-805c-ec3bde6fa9d0"
response = requests.get(
    "https://api.sncf.com/v1/coverage/sncf/journeys",
    params={
        "from": "stop_area:SNCF:87391003",
        "to": "stop_area:SNCF:87581009",
        "datetime": "20260116T080000"
    },
    auth=(api_key, '')  # Username=clé API, Password=vide
)
```

### Format de réponse JSON

La réponse contient un objet `journeys` avec :
- `sections` : Tableaux de sections du trajet
- `duration` : Durée totale en secondes
- `departure_date_time` : Date/heure de départ
- `arrival_date_time` : Date/heure d'arrivée
- `type` : Type de section (`waiting`, `public_transport`, `transfer`, etc.)

### Avantages de l'API SNCF

✅ **Données réelles** : Horaires en temps réel
✅ **Itinéraires optimisés** : Recherche avec correspondances réelles
✅ **Informations complètes** : Durées, horaires, correspondances

### Limitations

⚠️ **Clé API requise** : Nécessite une inscription et une clé API SNCF
⚠️ **Quotas** : Limite de requêtes par jour/mois selon le type de compte
⚠️ **Dépendance réseau** : Requiert une connexion internet active
⚠️ **Codes UIC manquants** : Toutes les gares n'ont pas forcément un code UIC dans notre fichier

### Comparaison avec le système de graphe actuel

| Caractéristique | Graphe (A*/Dijkstra) | API SNCF |
|----------------|---------------------|----------|
| **Données** | Basé sur distances géographiques | Horaires réels SNCF |
| **Internet** | ❌ Pas nécessaire | ✅ Requis |
| **Clé API** | ❌ Pas nécessaire | ✅ Requise |
| **Performance** | ⚡ Rapide (local) | 🌐 Plus lent (appel réseau) |
| **Précision** | ⚠️ Approximation (distances) | ✅ Réaliste (horaires) |
| **Correspondances** | ⚠️ Estimation | ✅ Réelles |
