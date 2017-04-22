from flask import Flask, render_template, request, redirect, jsonify, url_for, \
    flash, make_response, session as login_session
from sqlalchemy import create_engine, asc, desc, func
from sqlalchemy.orm import sessionmaker
from database import Base, Categories, Items, Users
import random, string, httplib2, json, requests
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())\
    ['web']['client_id']
APPLICATION_NAME = "Item Catalog Application"

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token
@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) \
        for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# Connect - Create a current user's token and their login_session
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
        response = make_response( \
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' \
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
        response = make_response( \
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response( \
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response( \
            json.dumps('Current user is already connected.'),200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['username'] = data['name']
    login_session['email'] = data['email']

    user_id = get_userid(login_session['email'])
    if not user_id:
        print 'user_id does not exist'
        user_id = create_user(login_session)
        print 'user_id', user_id
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# Disconnect - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
 	print 'Access Token is None'
    	response = make_response(json.dumps('Current user not connected.'), 401)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % \
        login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
	del login_session['access_token']
    	del login_session['gplus_id']
    	del login_session['username']
    	del login_session['email']
    	response = make_response(json.dumps('Successfully disconnected.'), 200)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    else:
    	response = make_response(json.dumps('Failed to revoke token for \
            given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response

# User helper functions
def createUser(login_session):
    newUser = User(name=login_session['username'],
                    email=login_session['email'])
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

# JSON API to view all items in the catalog
@app.route('/catalog.json/')
def catalogJSON():
    items = session.query(Items).all()
    return jsonify(Items=[item.serialize for item in items])

# Home page
@app.route('/')
@app.route('/catalog/')
def catalog():
    categories = session.query(Categories).all()
    items = session.query(Items).order_by(desc(Items.id)).limit(9)
    if 'username' not in login_session:
        return render_template('catalog.html', categories=categories, \
                                items=items)
    else:
        return render_template('catalogLogIn.html', categories=categories, \
                                items=items)

# Category page shows all items in that category
@app.route('/catalog/<category_name>/items')
def items(category_name):
    categories = session.query(Categories).all()
    items = session.query(Items).filter_by(category_name=category_name).all()
    count = session.query(Items).filter_by(category_name=category_name).count()
    return render_template('items.html', categories=categories, items=items, \
                            category_name=category_name, count=count)

# Item page shows name and description of that item
@app.route('/catalog/<category_name>/<item_name>')
def item(category_name, item_name):
    item = session.query(Items).filter_by(name=item_name).one()
    if 'username' not in login_session:
        return render_template('item.html', item=item)
    else:
        return render_template('itemLogIn.html', item=item)

# Add a new item page
@app.route('/catalog/add/', methods=['GET', 'POST'])
def add():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newItem = Items(name=request.form['name'], \
                        description=request.form['description'], \
                        category_name=request.form['category'], \
                        user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash("New Item %s Created!" % newItem.name)
        return redirect(url_for('catalog'))
    else:
        categories = session.query(Categories).all()
        return render_template('addItem.html', categories=categories)

# Edit an item page
@app.route('/catalog/<item_name>/edit/', methods=['GET', 'POST'])
def edit(item_name):
    if 'username' not in login_session:
        return redirect('/login')
    editItem = session.query(Items).filter_by(name=item_name).one()
    category_name = editItem.category_name
    if request.method == 'POST':
        if request.form['name']:
            editItem.name = request.form['name']
        if request.form['description']:
            editItem.description = request.form['description']
        if request.form['category_name']:
            editItem.category_name = request.form['category']
        if login_session['user_id']:
            editItem.user_id = login_session['user_id']
        session.add(editItem)
        session.commit()
        flash("Item %s Successfully Edited" % eidtItem.name)
        return redirect(url_for('item', category_name=editItem.category_name, \
                                item_name=editItem.name))
    else:
        categories = session.query(Categories).all()
        return render_template('edit.html', item=editItem, \
                                categories=categories)

# Delete an item page
@app.route('/catalog/<item_name>/delete/', methods=['GET', 'POST'])
def delete(item_name):
    if 'username' not in login_session:
        return redirect('/login')
    deleteItem = session.query(Items).filter_by(name=item_name).one()
    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()
        flash("Item %s Successfully Deleted" % deleteItem.name)
        return redirect(url_for('catalog'))
    else:
        return render_template('delete.html', item=deleteItem)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
