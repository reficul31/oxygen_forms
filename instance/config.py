import os
basedir  = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(basedir,'../app.sqlite')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, '../migrations')
SECRET_KEY = 'db51542b6345e5d681809ffe9b2ec271'
SQLALCHEMY_TRACK_MODIFICATIONS = False