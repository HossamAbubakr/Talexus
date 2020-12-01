import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True
# Connect to the database Ex. postgresql://postgres:password@localhost:5432/databasename
SQLALCHEMY_DATABASE_URI = 'CONNECTION STRING HERE'
