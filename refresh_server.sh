#!/bin/sh

while true; do 
    if ! git pull origin master | grep "Already up to date" ; then
        echo "Mise à jour du serveur web..."
        echo "`date`  <-- Mise à jour" >> log.txt
        echo "\n\n\n" >> log.txt
        echo "Restarting nginx"
        systemctl restart nginx &>/dev/null
        echo "Restarting uwsgi"
        systemctl restart uwsgi.service &>/dev/null
        echo "Mise à jour terminée"
    fi
    sleep 60
done