#!/usr/bin/env bash

# activate virtual environment
source ~/pylot/bin/activate

# cd into project folder
cd ~/lod

# pull the latest code base
git pull

# install app dependencies
pip install -r requirements.txt

# run database migration
python manage.py migrage

# run the collect static command
python manage.py collectstatic --no-input

# put all other commands that required

# deactivate
deactivate

# reload nginx
sudo systemctl reload nginx

# restart gunicorn
sudo systemctl restart gunicorn

