# Créez une API sécurisée RESTful en utilisant Django REST

## À propos

Formation OpenClassRooms - API REST - Projet 10

Objectifs :

- Sécuriser une API afin qu'elle respecte les normes OWASP et RGPD
- Créer une API RESTful avec Django REST

## Prérequis

Sans

## Installation

Cloner le repository

```bash
git clone https://github.com/Mothraa/OCR_projet10.git
```

Créer l'environnement virtuel avec [pipenv](https://pipenv.pypa.io/en/latest/)

```bash
pip install pipenv
pipenv install
```

Activer l'environnement

```bash
pipenv shell
```

Installer les packages

```bash
pipenv install -r requirements.txt
```

## Génération d'une base vierge

(uniquement si vous ne souhaitez pas utiliser la base fournie en test)

- Création d'une base de donnée (vide)

```bash
cd src
python manage.py db
```

- Génération et éxecution des scripts de migration

```bash
python manage.py makemigrations
python manage.py migrate
```

## Utilisation

- Démarrer le serveur en local :

```bash
cd src
python manage.py runserver
```

La collection de requêtes utilisées lors du developpement est disponible sous Postman [ici](https://www.postman.com/mothraa/shared-workspace/overview/)

## Langages & Librairies

- Python avec [Django](https://www.djangoproject.com/)
- [Django Rest Framework (DRF)](https://www.django-rest-framework.org/) pour la partie API
  - Le plugin Django [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/) pour l'authentification
  - Le plugin [Django filter](https://pypi.org/project/django-filter/) pour permettre le filtrage depuis l'URL
- [SQLite](https://www.sqlite.org/) : stockage des données via l'ORM de Django

## Documentation

De manière exceptionnelle et a titre d'exemple, la base de donnée (.\db.sqlite3) est livré avec le repository.

Il existe deux comptes (dont les accès sont disponibles dans la [collection postman](https://www.postman.com/mothraa/shared-workspace/overview/))
La création de nouveaux comptes est possible via un compte administrateur.

L'application est paramétrée en mode developpement et debug ; elle n'est pas faite telle quelle pour un déploiement et une mise en production.

## Gestion des versions

La dénomination des versions suit la spécification décrite par la [Gestion sémantique de version](https://semver.org/lang/fr/)

Les versions disponibles ainsi que les journaux décrivant les changements apportés sont disponibles depuis [la section releases](https://github.com/Mothraa/OCR_projet10/releases)

## Licence

Voir le fichier [LICENSE](./LICENSE.md) du dépôt.
