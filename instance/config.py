import os
basedir  = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(basedir,'../app.sqlite')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, '../migrations')
SECRET_KEY = '=54e!ka48(is5t)_@)!+$&-$j6jwkf-$a_$$zxn&fir*^3r5'
SQLALCHEMY_TRACK_MODIFICATIONS = False