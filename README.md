# Agenda Ludique

## Présentation du site

Le site dispose d'une page d'accueil permettant de s'inscrire ou de se connecter. 
Les utilisateurs qui se connecte à leur agenda ludique accède directement à leur
bibliothèque de jeux. À partir de là, il est possible de naviguer sur tout le
site. Par exemple, l'utilisateur peut accéder à différentes rubrique. Une de ces
rubrique, *communautés*, permet de voir ses groupes ou alors, les gérer, on 
entend par là, en ajouter ou en créer. L'autre rubrique importante, *Compte*, qui 
permet gérer son compte, afin d'y modifier ses informations ou même de supprimer 
son compte ainsi que d'ajouter des jeux.

## Prérequis
Le projet a été fait avec PyCharm, pour l'installer:  
- Arch Linux
```shell script
# pacman -Sy pycharm-community-edition
```
- Debian
```shell script
# snap install pycharm-community --classic
```
- La version Windows est disponible sur le site officiel

## Installation
```shell script
$ git clone https://gitlab.com/Thomas-Jacquet/agenda-ludique.git && cd agenda-ludique/
```

Sur PyCharm:
- File > New Project > Flask
- Dans le champ "Location", mettez le chemin du dossier agenda-ludique
![https://imgur.com/b2yNV8E.png](https://imgur.com/b2yNV8El.png)

## Lancement
Le projet a maintenant un environnement virtuel, il faut font installer les dépendences du projet. Pour cela, ouvrez le terminal situé en bas de la fenêtre :
![https://imgur.com/F9vv3sB.png](https://imgur.com/F9vv3sB.png)

Et entrez cette commande:
```shell script
$ pip3 install -r requirements.txt
``` 
Ensuite dans PyCharm en haut à droite:

![https://imgur.com/IziRzsP.png](https://imgur.com/IziRzsP.png)

Dans le menu déroulant cliquez sur "Edit configuration" et indiquer le chemin du fichier app.py.  

![https://imgur.com/sKVjlar.png](https://imgur.com/sKVjlar.png)

Tout est prêt ! Vous pouvez maintenant lancez le projet avec ![https://imgur.com/plmI8Of.png](https://imgur.com/plmI8Of.png)
