#!/bin/sh

# Note: uses python2
python plot-single.py -d1 8000-25000-penrose.json -d2 8000-25000-quasi.json -c 8000-25000-control.json -n 4 -o 'center-single.png'
python plot-multi.py -d1 8000-25000-penrose.json -d2 8000-25000-quasi.json -c 8000-25000-control.json -o 'all-plots.png'
