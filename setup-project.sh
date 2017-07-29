#!/bin/sh

if [ -z "$HERO_RANCHER_PROD" ]
then
    set -x
    echo "setting up development virtualenv"
    export HERO_RANCHER_DEV=1
    export CFLAGS='-std=c99'
else
    echo "setting up production virtualenv"
fi

rm -rf hero-rancher-env node_modules

npm install

virtualenv --python=python3 --no-site-packages hero-rancher-env
. hero-rancher-env/bin/activate

python setup.py develop
pip install -r requirements.txt

if [ "$HERO_RANCHER_DEV" ]
then
    pip install -r requirements-dev.txt
fi
