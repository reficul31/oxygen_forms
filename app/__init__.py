from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, current_user, logout_user, UserMixin
from datetime import timedelta
from flask import Flask, render_template, jsonify, request, redirect
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
	def __init__(self, id, username, password):
		self.id = id
		self.username = username
		self.password = password

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
			return FormUser(user.id, user.username, user.password)
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
				res = 'Enter valid login credentials'
	if current_user.is_authenticated:
		return redirect('/')
	else:
		return render_template('login.html', res = res)

@app.route('/register', methods=['GET','POST'])
def register():
	res = ''
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		try:
			user = User(username = username, password=password)
			user.add(user)
			res= 'Registration Successfull'
		except Exception:
			res = 'Registration Unsuccessfull'
	return render_template('register.html', res=res)

@app.route('/', methods=['GET','POST'])
@login_required
def index():
	print(current_user.id)
	return render_template('index.html')

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
			form = Forms(name=data['formname'], password=data['formpass'], json=json.dumps(data['form_data']))
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
			res = 'Everything is Awesome'
		except Exception:
			if form is not None:
				form.rollback()
				res = 'WRONG!!!'
	return render_template('makeform.html', res = res)

@app.route('/fill/<id>', methods=['GET','POST'])
def fillform(id):
	form = Forms.query.filter_by(id = id).with_entities(Forms.name, Forms.json, Forms.id).first()
	res = ''
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
			res = 'Form Submitted Successfully'
		except Exception:
			res = 'An Error occured'
	rendform = {'name':form.name,'json':json.loads(form.json),'id':form.id}
	return render_template('fillform.html', form = rendform, res=res)