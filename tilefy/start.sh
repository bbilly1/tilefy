#!/bin/bash
# container start up script

mkdir -p /data/{"tiles","logos","fonts"}

uwsgi --ini uwsgi.ini
