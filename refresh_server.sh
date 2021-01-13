#!/bin/sh

UPSTREAM=${1:-'@{u}'}
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse "$UPSTREAM")


while true; do 
    if [ ! $LOCAL = $REMOTE ]; then # Si il y a un nouveau commit sur l'upstream
        echo "Mise à jour du serveur web..."
        echo `date` >> log.txt
        echo `git log --pretty=format:'%h : %s' --graph $LOCAL $REMOTE` >> log.log
        echo "\n\n\n" >> log.txt
        git pull &>/dev/null
        echo "Restarting nginx"
        systemctl restart nginx &>/dev/null
        echo "Restarting uwsgi"
        systemctl restart uwsgi.service &>/dev/null
        echo "Mise à jour terminée"
    fi
    sleep(60)
done