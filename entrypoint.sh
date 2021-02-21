#!/usr/bin/env bash

python3 -m flask db upgrade

/usr/bin/supervisord
