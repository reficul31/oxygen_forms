from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse
from flask_login import LoginManager, login_required, login_user, current_user, logout_user, UserMixin
from models import User, Forms
from itsdangerous import URLSafeTimedSerializer
from datetime import timedelta
import base64
import hashlib
import psutil

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile("config.py")
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=1)

db = SQLAlchemy(app)

api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login'
login_manager.session_protection = 'strong'

class FormUser(UserMixin):
	"""
	User Class for flask-login
	"""
	def __init__(self, userid, password, forms):
		self.id = userid
		self.password = password
		self.forms = forms

	def get_auth_token(self):
		"""
		Encode a secure token for cookie
		"""
		data = [str(self.id), self.password]
		return login_serializer.dumps(data)

	@staticmethod
	def get(userid = None, username = None):
		user = None
		if userid:
			user = User.query.filter_by(id = userid).first()

		elif username:
			user = User.query.filter_by(username = username).first()

		if user:
			return FormUser(user.id, user.password, user.forms)

		return None

def hash_pass(password):
	salted_password = password + app.secret_key
	return hashlib.sha1(salted_password).hexdigest()

@login_manager.user_loader
def load_user(userid):
	return FormUser.get(userid)

@login_manager.token_loader
def load_token(token):
	max_age = app.config['REMEMBER_COOKIE_DURATION'].total_seconds()
	data = login_serializer.loads(token, max_age=max_age)
	user = FormUser.get(data[0])
	if user and data[1] == user.password:
		return user
	return None