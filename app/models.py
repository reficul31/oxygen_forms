# This file is to declare the models for the database which are concrete
from flask import Flask
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import VARCHAR, CHAR, JSON, Integer
from app import db
from random import choice
import inspect
# A decorator to automagically assign init variables.
def instanceVariables(func):
	def returnFunc(*args, **kwargs):
		self_var = args[0]

		arg_spec = inspect.getargspec(func)
		argument_names = arg_spec[0][1:]
		defaults = arg_spec[3]
		if defaults is not None:
			default_argdict = dict(zip(reversed(argument_names), reversed(defaults)))
			self_var.__dict__.update(default_argdict)

		arg_dict = dict(zip(argument_names, args[1:]))
		self_var.__dict__.update(arg_dict)

		valid_keywords = set(kwargs)&set(argument_names)
		kwarg_dict = {k: kwargs[k] for k in valid_keywords}
		self_var.__dict__.update(kwarg_dict)

		func(*args, **kwargs)

	return returnFunc

class CRUD():
	def add(self, resource):
		db.session.add(resource)
		return db.session.commit()

	def update(self):
		db.session.commit()

	def delete(self, resource):
		db.session.delete(resource)
		return db.session.commit()

	def rollback(self):
		db.session.rollback()

class Base(db.Model, CRUD):
	__abstract__ = True

class User(Base):
	id = Column(CHAR(5), unique=True, primary_key=True)
	username = Column(VARCHAR(30), default=None, nullable=False, unique = True)
	password = Column(VARCHAR(16), default=None, nullable= False)
	# forms = relationship('Child')

	def __init__(self, username, password):
		self.id = ''.join(choice('0123456789') for i in range(5)) 
		self.username = username
		self.password = password

	def __repr__(self):
		return "<User(username:%s)>"%self.username

class Forms(Base):
	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(VARCHAR(16), default = None )
	password = Column(VARCHAR(20), default = None)
	json = Column(VARCHAR(1000), default = None, nullable=False )
	# user_id = Column(CHAR(5), ForeignKey('user.id'))
	@instanceVariables
	def __init__(self, name, password, json):
		pass

	def __repr__(self):
		return "<Form(name:%s)>"%self.name