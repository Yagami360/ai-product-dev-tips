#!/bin/sh
#set -eu
USE_CONDA=1

pip uninstall flask
pip uninstall Flask-Cors
conda uninstall -y -c anaconda flask
conda uninstall -y -c anaconda flask-cors
conda uninstall -y -c conda-forge uwsgi

if [ ${USE_CONDA} = 0 ] ; then
    pip install flask
    pip install Flask-Cors
    pip install uWSGI
else
    conda install -y -c anaconda flask
    conda install -y -c anaconda flask-cors
    conda install -y -c conda-forge uwsgi
fi
