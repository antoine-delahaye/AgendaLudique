# Agenda Ludique

![Python](https://img.shields.io/badge/Python-14354C?style=for-the-badge&logo=python&logoColor=white)
&nbsp; ![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
&nbsp; ![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)
&nbsp; ![MariaDB](https://img.shields.io/badge/MariaDB-A57242?style=for-the-badge&logo=mariadb&logoColor=white)
&nbsp; ![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)

## Présentation

Agenda Ludique est une application web ayant pour but d'aider une association à organiser des parties de jeu de société
entre ses membres. L'application possède de nombreuses fonctionnalités comme le catalogue qui permet d'ajouter 
un jeu dans sa collection ; l'utilisateur dispose aussi d'une liste de souhaits, il peut noter des jeux et indiquer s'il
en connait les règles. Les utilisateurs peuvent s'ajouter en amis pour voir quels jeux une personne
possède et il est possible de créer des sessions permettant aux joueurs d'organiser des parties de jeu.

## Équipe de développement

- [Rémi Delanneau](https://github.com/Amki45)
- [Jules Grandjean](https://github.com/julesgdn)
- [Mathis Dupuis](https://gitlab.com/Nagelfox)
- [Tristan Bellot](https://github.com/Arhkalis)
- [Xavier Berault](https://github.com/ranblok)
- [Florian Savouré](https://github.com/P0SlX)
- [Antoine Delahaye](https://github.com/antoine-delahaye)
- [Thomas Jacquet-Francillon](https://github.com/Thomas-Jacquet)

## Prérequis

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/get-docker/)

## Mise en place

Pour mettre en place les conteneurs, il faut créer un fichier `docker-compose.yml` avec le code ci-dessous. Toutefois,
il est nécessaire que les ports 80 et 3306 de la machine soit libres.

```
services:
  app:
    image: ug7z/agenda-ludique
    depends_on:
      - db
    ports:
      - 80:80
    entrypoint: /docker-al/entrypoint.sh
    networks:
      - al_network
  db:
    image: mariadb
    ports:
      - 3306:3306
    environment:
      MYSQL_RANDOM_ROOT_PASSWORD: "yes"
      MYSQL_DATABASE: agendaludique
      MYSQL_USER: al_admin
      MYSQL_PASSWORD: al_admin
    networks:
      - al_network

networks:
  al_network:
```

Après avoir créé le ficher, lancer la commande `docker-compose up` pour que Docker Compose lance l'application.

## Construire le projet

Pour construire le projet avec Docker, cloner le dépôt en annexes puis lancer la commande 
`docker build -t agenda-ludique -f docker/Dockerfile .` à la racine du projet pour construire ce dernier.
Arpès avoir fait celà, dans `docker-compose.yml`, remplacer la ligne `image: ug7z/agenda-ludique` par
`image: agenda-ludique` pour lancer le projet avec l'image local.

## Annexes

- [Dépôt GitLab](https://gitlab.com/Thomas-Jacquet/agenda-ludique)
- [Page Docker Hub](https://hub.docker.com/repository/docker/ug7z/agenda-ludique)

<div style="text-align: center">
    <img src="https://i.imgur.com/PUTSirh.png" alt="IUT Informatique d'Orléans" height="100">
</div>