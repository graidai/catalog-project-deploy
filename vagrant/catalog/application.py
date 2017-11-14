from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, redirect
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import bleach
import os

app = Flask(__name__)

#load the client_id from google credentials
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Udacity Catalog"


# Connect to Database and create database session
engine = create_engine('sqlite:///itemsDatabase.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


#google login
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    print("user id is %s" % user_id)
    print("user id is %s" % data['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        response = make_response(json.dumps('Successfully disconnected.', 200))
        response.headers['Content-Type'] = 'application/json'
        flash('success in disconnection')
        return redirect(url_for('showCatalog'))
    else:
        print login_session
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Catalog Information
@app.route('/catalog.JSON')
def catalogJSON():
    category_array = []

    category = session.query(Category).order_by(asc(Category.id))

    for i in category:
        cat_object = {}
        cat_object['id'] = i.id
        cat_object['name'] = i.name
        item_array = []
        items = session.query(Item).filter_by(cat_id=i.id)
        for j in items:
            item_array.append(j.serialize)
        cat_object['item'] = item_array
        category_array.append(cat_object)

    return jsonify(category=category_array)



# Show catalog
@app.route('/')
@app.route('/catalog')
def showCatalog():
    isLoggedIn = False
    category = session.query(Category).order_by(asc(Category.name))
    items = session.query(Item).order_by(desc(Item.id)).limit(10).all()
    if 'username' not in login_session:
        return render_template('landing.html', category=category, items=items, isLoggedIn=False)
    return render_template('landing.html', category=category, items=items, isLoggedIn=True)

# Show items in a particular sport
@app.route('/catalog/<int:cat_id>/items')
def showSportItem(cat_id):
    isLoggedIn = False
    category = session.query(Category).order_by(asc(Category.name))
    items = session.query(Item).filter_by(cat_id=cat_id).all()
    if 'username' not in login_session:
        return render_template('item.html', items=items, category=category, isLoggedIn=False)
    return render_template('item.html', items=items, category=category, isLoggedIn=True)

# Show indiviual item info of the sport
@app.route('/catalog/<int:cat_id>/<int:item_id>/')
def showEachItem(cat_id, item_id):
    isLoggedIn = False
    itemname = []
    isOwner = False
    if 'username' not in login_session:
        isLoggedIn = False
    else:
        isLoggedIn = True
    try:
        items = session.query(Item).filter_by(cat_id=cat_id).all()
        oneItem = session.query(Item).filter_by(id=item_id).one()
    except:
        return 'item not found'
    for names in items:
        itemname.append(names.name)
    print oneItem.user_id
    if 'username' in login_session:
        if oneItem.user_id == login_session['user_id']:
            isOwner = True
    #item number doesn't match the item category
    if oneItem.name not in itemname:
        return 'item not found in sports current sports category'
    else:
        return render_template('sports.html', item=oneItem, isOwner=isOwner, isLoggedIn=isLoggedIn)

# Create item
@app.route('/catalog/createitem', methods=['GET', 'POST'])
def createItem():
    isLoggedIn = False
    category = session.query(Category).order_by(asc(Category.name))
    if 'username' not in login_session:
        flash('Please login first to create your item')
        return redirect('/login')
    if request.method == 'POST':
        if request.form['item_name'] and request.form['item_desc'] and request.form['item_cat']:
            cat_name = (request.form['item_cat'])
            static_category = session.query(Category).filter_by(name=cat_name).one()
            #sanitize your input
            newItem = Item(name=bleach.clean(request.form['item_name']),
                           description=bleach.clean(request.form['item_desc']),
                           cat_id=static_category.id,
                           user_id=login_session['user_id'] )
        else:
            flash('Please fill out all the forms')
            return render_template('item_create.html', category=category, isLoggedIn=True)

        session.add(newItem)
        session.commit()
        flash('New Item created')
        return redirect(url_for('showSportItem',cat_id=newItem.cat_id))
    else:
        return render_template('item_create.html', category=category, isLoggedIn=True)


# Edit edit item page
@app.route('/catalog/<int:item_id>/edit/', methods=['GET', 'POST'])
def editItem(item_id):
    isLoggedIn = False
    editedItem = session.query(Item).filter_by(id=item_id).one()
    category = session.query(Category).order_by(asc(Category.name))
    if 'username' not in login_session:
        flash('Please login first to edit your item')
        return redirect('/login')
    print(login_session['user_id'])
    print("user id is %s" % editedItem.user_id)
    if editedItem.user_id != login_session['user_id']:
        return "<script>function noNo(){alert('you are not authorized to edit this item')}</script><body onload=noNo()>"
    if request.method == 'POST':
        if request.form['item_name']:
            editedItem.name = bleach.clean(request.form['item_name'])
        if request.form['item_desc']:
            editedItem.description = bleach.clean(request.form['item_desc'])
        if request.form['item_cat']:
            cat_name = (request.form['item_cat'])
            static_category = session.query(Category).filter_by(name=cat_name).one()
            editedItem.cat_id = static_category.id
        session.add(editedItem)
        session.commit()
        flash(' %s Successfully Edited' % editedItem.name)
        return redirect(url_for('showSportItem',cat_id=editedItem.cat_id))
    else:
        return render_template('item_edit.html', category=category, item=editedItem, isLoggedIn=True )

# Edit edit item page
@app.route('/catalog/<int:item_id>/delete/', methods=['GET', 'POST'])
def deleteItem(item_id):
    isLoggedIn = False
    deleteItem = session.query(Item).filter_by(id=item_id).one()
    if 'username' not in login_session:
        flash('Please login first to delete your item')
        return redirect('/login')
    if deleteItem.user_id != login_session['user_id']:
        return "<script>function noNo(){alert('you are not authorized to edit this item')}</script><body onload=noNo()>"
    if request.method == 'POST':
        session.delete(deleteItem)
        flash('%s Successfully Deleted' % deleteItem.name)
        session.commit()
        return redirect(url_for('showSportItem', cat_id=deleteItem.cat_id))
    else:
        return render_template('item_delete.html', item=deleteItem, isLoggedIn=True)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
