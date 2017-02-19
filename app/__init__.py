from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse
from flask import Flask, render_template, jsonify
from flask_restful import Api, Resource, reqparse
import json
app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile("config.py")
api = Api(app)
db = SQLAlchemy(app)
from models import User, Forms

@app.route('/')
def index():
	return render_template('index.html')

class Form(Resource):
	def post(self):
		response = ''
		i=0
		form = None
		# try:
		parser = reqparse.RequestParser()
		parser.add_argument('formstring',type=str, help='Form JSON String')
		args = parser.parse_args()
		formstring = args['formstring']
		formdict = json.loads(formstring)
		print(formdict)
		form = Forms(name=formdict['formname'], password=formdict['formpass'], json=str(formdict['form_data']))
		form.add(form)
		query = "CREATE TABLE "+" "+formdict["formname"]+"("
		for k in formdict['form_data']['fields']:
			if i != 0:
				query = query+","
			query=query+str(k['label'].replace(" ","").replace("?","").lower())+" VARCHAR(1000)"
			i+=1
		query = query+")"
		db.engine.execute(query)
		db.session.commit()
		response = {'status_code':110}
		# except Exception as e:
		# 	if form is not None:
		# 		form.rollback()
		# 	response = {'status_code':111}
		return jsonify(response)

api.add_resource(Form, '/form')
