# Projet Parfeu

Ce projet est une application web développée avec le framework **Django**. Il contient l'application principale ainsi qu'un module `superAdmin`.

## 🚀 Prérequis

Avant de lancer le projet, assurez-vous d'avoir installé sur votre machine :
- [Python](https://www.python.org/downloads/) (version 3.x)
- pip (le gestionnaire de paquets de Python)

## ⚙️ Installation et Configuration

Voici les étapes à suivre pour configurer et faire tourner l'application correctement sur votre machine.

### 1. Cloner le projet
Si vous venez de récupérer le projet depuis GitHub :
```bash
git clone <url-de-votre-repo>
cd Projet_Parfeu
```

### 2. Créer et activer un environnement virtuel (Très recommandé)
Il est fortement conseillé de travailler dans un environnement virtuel pour ne pas polluer votre installation Python globale.

**Création :**
```bash
python -m venv venv
```

**Activation :**
- **Sous Windows :**
  ```bash
  venv\Scripts\activate
  ```
- **Sous MacOS / Linux :**
  ```bash
  source venv/bin/activate
  ```

*(Une fois activé, vous devriez voir `(venv)` apparaître au début de la ligne de votre terminal.)*

### 3. Installer les dépendances
Installez toutes les bibliothèques nécessaires au bon fonctionnement de l'application via le fichier `requirements.txt` à la racine du projet :

```bash
pip install -r requirements.txt
```

### 4. Appliquer les migrations de base de données
Cette commande permet de créer ou mettre à jour les tables dans la base de données locale (`db.sqlite3`) :

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Créer un Super Utilisateur (Optionnel)
Pour accéder à l'interface d'administration de Django (et potentiellement à votre application `superAdmin`) :

```bash
python manage.py createsuperuser
```
*(Suivez les instructions à l'écran pour définir le nom d'utilisateur, l'email et le mot de passe).*

### 6. Lancer le serveur local
Démarrez le serveur de développement :

```bash
python manage.py runserver
```

L'application est maintenant en cours d'exécution. Vous pouvez y accéder depuis votre navigateur à l'adresse :
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🚂 Déploiement sur Railway

⚠️ Cette application pilote `iptables` via `sudo` sur la machine qui l'héberge (voir `superAdmin/executer_iptables.py`). Sur Railway (conteneurs sans accès root ni `CAP_NET_ADMIN`), le **backend Django tourne normalement** (dashboard, authentification, base de données, chatbot IA), mais les actions qui exécutent réellement `iptables` échoueront puisque le conteneur n'a pas les privilèges nécessaires ni d'accès au vrai pare-feu de l'hôte à protéger.

### 1. Créer le projet sur Railway
- Connecte ton repo GitHub sur [railway.app](https://railway.app)
- Railway détecte automatiquement le projet Python via `requirements.txt` (build via Nixpacks) et lit `railway.json` pour les commandes de build/démarrage

### 2. Ajouter une base PostgreSQL
- Dans le projet Railway : **New → Database → PostgreSQL**
- Dans le service web, ajoute la variable `DATABASE_URL` avec la valeur de référence `${{Postgres.DATABASE_URL}}`

### 3. Configurer les variables d'environnement du service web
Voir `.env.example` pour la liste complète. Au minimum :
```
SECRET_KEY=<une clé secrète générée pour la prod>
DEBUG=False
ALLOWED_HOSTS=<ton-domaine>.up.railway.app
DATABASE_URL=${{Postgres.DATABASE_URL}}
ANTHROPIC_API_KEY=<optionnel, pour le chatbot IA>
```

### 4. Déployer
Railway build puis démarre l'appli avec :
```
python manage.py migrate --noinput   # au démarrage
gunicorn Projet_Parfeu.wsgi --bind 0.0.0.0:$PORT
```
(voir `railway.json` / `Procfile`). Les fichiers statiques sont servis directement par [Whitenoise](https://whitenoise.readthedocs.io/), pas besoin de service séparé.

Crée ensuite un super-utilisateur en une fois via le shell Railway (`railway run python manage.py createsuperuser`) ou l'onglet "Shell" du service.

---

## 🎨 Déploiement sur Render

⚠️ Même remarque que pour Railway : le backend Django tourne normalement, mais les actions `iptables` échoueront (conteneur sans root).

### 1. Créer le Blueprint
- Sur [render.com](https://render.com) : **New → Blueprint**
- Connecte le repo GitHub `Parfeu-dynamique-avec-iptables-`, branche `main`
- Render lit automatiquement `render.yaml` à la racine et propose de créer :
  - un **Web Service** (Python, build via `pip install -r requirements.txt`)
  - une **base PostgreSQL** gratuite, déjà reliée via `DATABASE_URL`
  - `SECRET_KEY` généré automatiquement, `DEBUG=False`
- Clique **"Apply"** pour tout créer d'un coup

### 2. Compléter les variables
Render te demandera juste `ANTHROPIC_API_KEY` (marquée `sync: false` dans le blueprint, donc à saisir manuellement) — optionnelle, pour le chatbot IA. Rien d'autre à faire : `ALLOWED_HOSTS` n'a pas besoin d'être renseigné, le domaine `*.onrender.com` est détecté automatiquement (variable `RENDER_EXTERNAL_HOSTNAME` fournie par Render).

### 3. Déployer
Render build et démarre automatiquement avec la commande définie dans `render.yaml` (collectstatic + migrate + gunicorn). Une fois "Live", ouvre l'URL `https://<nom-du-service>.onrender.com`.

Crée le super-utilisateur via l'onglet **"Shell"** du service Render : `python manage.py createsuperuser`.

⚠️ Sur le plan gratuit Render, le service s'endort après 15 min d'inactivité (le premier chargement après une pause peut prendre ~30s).

---

## 🔒 Versioning et GitHub

Ce projet est configuré avec un fichier `.gitignore` strict. 
Cela signifie que si vous poussez (push) ce code sur GitHub, les éléments suivants **ne seront pas inclus** :
- Votre dossier d'environnement virtuel (`venv/`, `env/`, etc.)
- Vos fichiers de cache (`__pycache__/`)
- Votre base de données locale (`db.sqlite3`)
- Vos variables d'environnement (`.env`)

Vous pouvez donc faire vos `git add .`, `git commit` et `git push` sans craindre d'exposer vos données locales ou de surcharger le dépôt !
