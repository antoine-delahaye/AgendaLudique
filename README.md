# Question sur le sujet

- Comment considère-t-on qu'un joueur connais les regles


# Agenda Ludique

1) Segment de clientelle:
Association de jeu de société

2) Principaux problemes a ressoudre:
- Quel jeux apporter ?
- Quels sont les jeux déjà disponibles à l'association ?
- Qui souhaiterait jouer à quoi ?
- Qui connaît les règles ?

3) Proposition de valeur unique:


4) Solution:


5) Canaux:


6) Argent:


7) Couts:


8) Indicateurs de performances:


9) Avanatage competitif:

# BDD

 |---------------------| |---------------------| |-------------|
 | JEU                 | | Theme               | | Genre       |
 |---------------------| |---------------------| |-------------|
 | Nom (pk)            | | Nom (pk) (fk JEU)   | | Nom         |
 | Description         | | Nom (pk) (fk Genre) | | Description |
 | Note                | |---------------------| |-------------|
 |---------------------|


 |--------------------------------|
 | Possede                        |
 |--------------------------------|
 | Nom        (pk) (fk Jeu)       |
 | Possesseur (pk) (fk Membre.id) |
 | Date achat                     |
 | Prix vente                     |
 | Etat                           |
 |--------------------------------|


 |----------------| |----------------------------|
 | Membre         | | Aime                       |
 |----------------| |----------------------------|
 | Id (pk)        | | Membre (pk) (fk Membre.Id) |
 | Nom            | | Genre  (pk) (fk Genre.Nom) |
 | Prenom         | |----------------------------|
 | Age            |
 |----------------|
