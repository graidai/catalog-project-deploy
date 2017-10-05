from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, User, Item
from flask import session as login_session
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///itemsDatabase.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Show catalog
@app.route('/')
@app.route('/catalog')
def showCatalog():
    return render_template('landing.html')

# Show items in a particual sport
@app.route('/catalog/<sport>/items')
def showSportnItem(sport):
    return 'show sports-items in the list %s' % sport

# Show indiviual item info of the sport
@app.route('/catalog/<sport>/<item>')
def showEachItem(sport, item):
    return 'show the individual items of the sport'

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
