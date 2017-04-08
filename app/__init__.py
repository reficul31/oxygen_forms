from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, current_user, logout_user, UserMixin
from datetime import timedelta
from flask import Flask, render_template, jsonify, request, redirect, abort
import json
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile("config.py")
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=1)

db = SQLAlchemy(app)
from models import User, Forms
login_serializer = URLSafeTimedSerializer(app.secret_key)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"
login_manager.session_protection = "strong"

def checkUserAuth(func):
	@wraps(func)
	def returnFunc(*args, **kwargs):
		if not current_user.is_authenticated:
			abort(405)

		return func(*args, **kwargs)

	return returnFunc

class FormUser(UserMixin):
	def __init__(self, id, username, password, name):
		self.id = id
		self.username = username
		self.password = password
		self.name = name

	def get_auth_token(self):
		data = [str(self.id), self.password]
		return login_serializer.dumps(data)

	@staticmethod
	def get(id=None, username=None):
		user = None
		if id:
			user = User.query.filter_by(id = id).first()
		elif username:
			user = User.query.filter_by(username = username).first()

		if user:
			return FormUser(user.id, user.username, user.password, user.name)
		return None

@login_manager.user_loader
def load_user(id):
	return FormUser.get(id)

@login_manager.token_loader
def load_token(token):
	max_age = app.config["REMEMBER_COOKIE_DURATION"].total_seconds()

	# Decrypt the Security Token, data = [username, hashpass]
	data = login_serializer.loads(token, max_age=max_age)

	user = FormUser.get(data[0])

	if user and data[1] == user.password:
		return user

	return None	

@app.route('/login', methods = ['GET','POST'])
def login():
	res =''
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		if not current_user.is_authenticated:
			user = FormUser.get(username= username)
			if user and password == user.password:
				login_user(user, remember=True)
			else:
				res = 102
	if current_user.is_authenticated:
		return redirect('/home')
	else:
		return render_template('login.html', res = res)

@app.route('/register', methods=['GET','POST'])
def register():
	res = ''
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		name = request.form['name']
		number = request.form['number']
		try:
			user = User(username = username, password=password, name=name, number=number)
			user.add(user)
			res= 100
		except Exception:
			res = 102
	return render_template('register.html', res=res)

@app.route('/home', methods=['GET','POST'])
@login_required
def index():
	query = "select * from forms where user_id=%s"%current_user.id
	res = db.session.execute(query)
	return render_template('index.html', res=res, name=current_user.name)

@app.route('/')
def landing():
	return render_template('landing.html')

@app.route('/logout', methods=['GET'])
@login_required
def logout():
	logout_user()
	return redirect('/login')

@app.route('/design',methods=['GET','POST'])
@login_required
def designform():
	res = ''
	i=0
	form = None
	if request.method == 'POST':
		data_file = request.form['sender']
		data = json.loads(data_file)
		try:
			print(current_user.id)
			form = Forms(name=data['formname'], password=data['formpass'], json=json.dumps(data['form_data']), user_id=current_user.id, desc=data['formdesc'])
			form.add(form)
			query = "CREATE TABLE "+" "+data["formname"]+"("
			for k in data['form_data']['fields']:
				if i != 0:
					query = query+","
				query=query+str(k['label'].replace(" ","_").replace("?","").lower())+" VARCHAR(1000)"
				i+=1
			query = query+")"
			db.engine.execute(query)
			db.session.commit()
			res = 100
		except Exception:
			if form is not None:
				form.rollback()
				res = 102
	return render_template('makeform.html', res = res, name=current_user.name)

@app.route('/fill/<id>', methods=['GET','POST'])
def fillform(id):
	form = Forms.query.filter_by(id = id).with_entities(Forms.name, Forms.json, Forms.id, Forms.desc).first()
	res = 0
	if request.method == 'POST':
		try:
			query = "INSERT INTO "+form.name+"("
			for field in request.form:
				if field !='Submit':
					query = query+str(field.replace(" ","_").replace("?","").lower())+","
			query = query[:-1]
			query = query+")"
			query = query+" VALUES("
			for field in request.form:
				if field !='Submit':
					query = query+'"'+str(request.form[field])+'"'+","
			query = query[:-1]
			query = query+")"
			db.session.execute(query)
			db.session.commit()
			res = 100
		except Exception:
			res = 102
	rendform = {'name':form.name,'json':json.loads(form.json),'id':form.id, 'desc':form.desc}
	return render_template('fillform.html', form = rendform, res=res)

@app.route('/show/<id>')
@login_required
def showform(id):
	form = Forms.query.filter_by(id = id, user_id = current_user.id).with_entities(Forms.name, Forms.json).first()
	if form is not None:
		query = "select * from %s"%form.name
		data = db.session.execute(query)
		return render_template('showform.html', data=data, struct=json.loads(form.json), name=form.name)
	else:
		abort(404)

@app.errorhandler(404)
def reroute(e):
	return render_template('404.html')
