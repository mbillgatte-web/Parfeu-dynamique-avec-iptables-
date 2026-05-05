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
Installez toutes les bibliothèques nécessaires au bon fonctionnement de l'application via le fichier `Requirement.txt` (qui se trouve actuellement dans le dossier parent de ce répertoire).

```bash
# Si le fichier est dans le dossier parent :
pip install -r ../Requirement.txt

# Si vous déplacez Requirement.txt à la racine de ce dossier :
# pip install -r Requirement.txt
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

## 🔒 Versioning et GitHub

Ce projet est configuré avec un fichier `.gitignore` strict. 
Cela signifie que si vous poussez (push) ce code sur GitHub, les éléments suivants **ne seront pas inclus** :
- Votre dossier d'environnement virtuel (`venv/`, `env/`, etc.)
- Vos fichiers de cache (`__pycache__/`)
- Votre base de données locale (`db.sqlite3`)
- Vos variables d'environnement (`.env`)

Vous pouvez donc faire vos `git add .`, `git commit` et `git push` sans craindre d'exposer vos données locales ou de surcharger le dépôt !
