from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import select
from flask import Flask, render_template, jsonify, request
from flask_restful import Api, Resource, reqparse
import json
app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile("config.py")
db = SQLAlchemy(app)
from models import User, Forms

@app.route('/', methods=['GET','POST'])
def index():
	return render_template('index.html')

@app.route('/design',methods=['GET','POST'])
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
					query = query+str(field)+","
			query = query[:-1]
			query = query+")"
			query = query+" VALUES("
			for field in request.form:
				if field !='Submit':
					query = query+'"'+str(request.form[field])+'"'+","
			query = query[:-1]
			query = query+")"
			print(query)
			db.session.execute(query)
			db.session.commit()
			res = 'Form Submitted Successfully'
		except Exception:
			res = 'An Error occured'
	rendform = {'name':form.name,'json':json.loads(form.json),'id':form.id}
	return render_template('fillform.html', form = rendform, res=res)