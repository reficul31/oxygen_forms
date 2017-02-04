from flask import Flask
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import VARCHAR, CHAR, JSON
from app import db
from random import choice

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
	forms = relationship('Child')

	def __init__(self, username, password):
		self.id = ''.join(choice('0123456789') for i in range(5)) 
		self.username = username
		self.password = password

	def __repr__(self):
		return "<User(username:%s)>"%self.username

class Forms(Base):
	id = Column(CHAR(5), default=None, primary_key=True)
	name = Column(VARCHAR(16), default = None )
	json = Column(VARCHAR(1000), default = None, nullable=False )
	user_id = Column(CHAR(5), ForeignKey('user.id'))

	def __init(self, name, json, user_id):
		self.id = ''.join(choice('0123456789') for i in range(5)) 
		self.name = name
		self.json = json
		user_id = user_id

	def __repr__(self):
		return "<Form(name:%s)>"%self.name