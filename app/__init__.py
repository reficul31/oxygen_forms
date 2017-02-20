from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse
from flask import Flask, render_template, jsonify
from flask_restful import Api, Resource, reqparse
import json
# Initializing the app with the flask microframework
app = Flask(__name__, instance_relative_config=True)
# Setting configuration for the app
app.config.from_pyfile("config.py")
# Initializing the restful api
api = Api(app)
# Initializing the sqlalchemy
db = SQLAlchemy(app)
# Avoiding the circular imports
from models import User, Forms
# Default route
@app.route('/')
def index():
	return render_template('index.html')
# First end point
class Form(Resource):
	# Post request come here
	def post(self):
		response = ''
		i=0
		form = None
		try:
			# Request parser used to parse the post requests
			parser = reqparse.RequestParser()
			parser.add_argument('formstring',type=str, help='Form JSON String')
			args = parser.parse_args()
			formstring = args['formstring']
			# Loading the json from the string
			formdict = json.loads(formstring)
			# Saving the form in the database
			form = Forms(name=formdict['formname'], password=formdict['formpass'], 
				json=str(formdict['form_data']))
			form.add(form)
			# Making the form table
			query = "CREATE TABLE "+" "+formdict["formname"]+"("
			for k in formdict['form_data']['fields']:
				if i != 0:
					query = query+","
				query=query+str(k['label'].replace(" ","").replace("?","").lower())+
				" VARCHAR(1000)"
				i+=1
			query = query+")"
			# Execute the query
			db.engine.execute(query)
			# Commiting the database
			db.session.commit()
			# Sending success response
			response = {'status_code':110}
		except Exception as e:
			# Catching exceptions
			if form is not None:
				# Rollback if an error occurred
				form.rollback()
			# Response of failure sent
			response = {'status_code':111}
		return jsonify(response)
# Adding the resource to the api end point
api.add_resource(Form, '/form')
