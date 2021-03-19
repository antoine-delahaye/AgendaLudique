#!/usr/bin/env bash

python3 -m flask db init
python3 -m flask db migrate
python3 -m flask db upgrade

/usr/bin/supervisord
