"""
Nathan D. Hernandez
Udacity FullStack NanoDegree

Item Catalog Application:
    - ver: 0.2  05/30/17 (PostgreSQL version)
    - ver: 0.1  05/2017
"""

import os
import hashlib
import httplib2
import requests
import json

from flask import (Flask, render_template, request, redirect,
                   flash, url_for, make_response, jsonify,
                   session as login_session)

from sqlalchemy import create_engine, desc, exc
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker, exc as orm_exc
from database_setup import (Base, Category, Item, LoginType, User, Role,
                            DATABASE)

# OAuth2 related imports
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

APP_PATH = '/opt/webapps/udacity-fullstack-catalog-postgres/'
CLIENT_ID = json.loads(
                   open(APP_PATH + 'client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)

engine = create_engine(URL(**DATABASE))
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Helper functions
def createUser(login_session):
    # Set Google login type
    logintype = session.query(LoginType).filter_by(
                                    source=login_session['login_type']).one()

    # 1st time User, grab default 'contrib' Role
    c_role = session.query(Role).filter_by(permission="contrib").one()
    # Admin role
    a_role = session.query(Role).filter_by(permission="admin").one()
    # Applies both Admin and Contrib roles
    new_user_roles = [c_role, a_role]
    # UNCOMMENT next line if you comment preceding line, to limit roles
    # Can be limited to just Contrib role (without ADMIN)
    # new_user_roles = [c_role]

    # Store our User info to recall later
    new_user = User(name=login_session['username'],
                    picture=login_session['picture'],
                    email=login_session['email'], roles=new_user_roles,
                    logintype_id=logintype.id)

    session.add(new_user)
    session.commit()
    return new_user.id


def getUser(source, user_email):
    # Grab login type
    logintype = session.query(LoginType).filter_by(source=source).one()

    # Grab the User object
    try:
        print "Source is %s and Email is %s" % (source, user_email)
        email = user_email
        user = session.query(User).filter_by(logintype_id=logintype.id,
                                             email=email).one()
        return user
    except orm_exc.NoResultFound:
        print "User doesn't exist, or error retrieving, from our database."
        return None


def getUserRoles(user):
    roles = {'admin': False, 'contrib': False}

    if user is not None:
        for role in user.roles:
            if role.permission == "admin":
                roles['admin'] = True
            if role.permission == "contrib":
                roles['contrib'] = True

    return roles


def getAppAuth():
    # Dictionary for return values
    auth = dict()
    user = None
    # Priviledge specific (For Category/Item CRUD, and certain UI elements)
    user_roles = None

    # Check if we have a user logged on in our login_session
    if 'email' in login_session:
        user = getUser(login_session['login_type'], login_session['email'])

    user_roles = getUserRoles(user)

    # Build our response
    auth['roles'] = user_roles

    return auth


"""
Route Specific
"""


@app.route('/')
@app.route('/catalog/')
def catalogHome():
    print "In catalogHome()"
    # Grab app authorizations, if any
    auth = getAppAuth()
    is_admin = auth['roles']['admin']
    is_contrib = auth['roles']['contrib']
    categories = session.query(Category).all()
    latest_items = session.query(Item).order_by(
                                            desc(Item.created)).limit(10).all()

    return render_template("catalog.html", is_admin=is_admin,
                           is_contrib=is_contrib, categories=categories,
                           latest_items=latest_items)


@app.route('/catalog/full/')
def catalogHomeFull():
    """
    Endpoint to view ALL items, as only 10 are displayed in LatestItems
    on page load by default.
    """
    print "In catalogHomeFull()"
    auth = getAppAuth()
    is_admin = auth['roles']['admin']
    is_contrib = auth['roles']['contrib']
    categories = session.query(Category).all()
    all_items = session.query(Item).order_by(
                                         desc(Item.created)).all()

    return render_template("catalog.html", is_admin=is_admin,
                           is_contrib=is_contrib, categories=categories,
                           all_items=all_items)


"""
Category Specific
"""


@app.route('/catalog/<category>/')
def categoryInfo(category):
    print "In categoryInfo(category) for %s" % category
    # Grab app authorizations, if any
    auth = getAppAuth()
    is_admin = auth['roles']['admin']

    curr_categ = session.query(Category).filter(
                                          Category.name == str(category)).one()

    return render_template("category.html", is_admin=is_admin,
                           curr_categ=curr_categ)


@app.route('/catalog/category/new/', methods=['GET', 'POST'])
def newCategory():
    print "In newCategory()"
    # Login redirect if User Not Logged IN for CREATE
    if 'email' not in login_session:
        return redirect(url_for('showLogin'))

    # Grab our user
    user = getUser(login_session['login_type'], login_session['email'])
    # Get authorizations for logged on user
    auth = getAppAuth()
    # If user is NOT 'admin' then redirect to Main Page with Flash
    if auth['roles']['admin'] is False:
        flash("You need ADMIN privileges to CREATE categories!")
        redirect(url_for(catalogHome))

    # Otherwise proceed with our requests
    if request.method == 'POST':
        print "In Post"

        # Grab our user
        user = getUser(login_session['login_type'], login_session['email'])
        # Get authorizations for logged on user
        auth = getAppAuth()

        # Grab our values
        name = request.form['name']
        desc = request.form['desc']

        if name != "" and desc != "":
            try:
                # Create our Category
                new_categ = Category(name=name, description=desc,
                                     created_by=user.id)

                session.add(new_categ)
                session.commit()

                flash("Catalog CATEGORY added successfully!")
            except exc.IntegrityError as e:
                session.rollback()
                flash("""Cannot Add, Category with chosen NAME
                      already exists...""")
            finally:
                return redirect(url_for('catalogHome'))
    else:
        print "Get called"
        return render_template("new-category.html")


@app.route('/catalog/<category>/edit/', methods=['GET', 'POST'])
def editCategory(category):
    print "In editCategory()"
    # Login redirect if User Not Logged IN for CREATE
    if 'email' not in login_session:
        return redirect(url_for('showLogin'))

    # Grab our user
    user = getUser(login_session['login_type'], login_session['email'])
    # Get authorizations for logged on user
    auth = getAppAuth()
    # If user is NOT 'admin' then redirect to Main Page with Flash
    if auth['roles']['admin'] is False:
        flash("You need ADMIN privileges to EDIT categories!")
        redirect(url_for(catalogHome))

    # Otherwise proceed with our requests
    curr_categ = session.query(
                        Category).filter(Category.name == str(category)).one()

    if request.method == 'POST':
        print "In Post"

        # Grab our values
        name = request.form['name']
        desc = request.form['desc']
        categ = request.form['category']

        # Lookup actual category object for verification of submit
        category = session.query(Category).filter(
                                            Category.name == str(categ)).one()

        if category and (category == curr_categ):
            # Edit our existing Category
            try:
                curr_categ.name = name
                curr_categ.description = desc
                curr_categ.last_update_by = user.id

                session.commit()

                msg = "Edited category %s successfully!" % curr_categ.name
                flash(msg)
            except exc.IntegrityError as e:
                session.rollback()
                flash("Cannot Edit: Category Name already exists...")
            finally:
                return redirect(url_for('catalogHome'))
    else:
        print "Get request called"
        return render_template("edit-category.html", category=curr_categ)


@app.route('/catalog/<category>/delete/', methods=['GET', 'POST'])
def deleteCategory(category):
    print "In deleteCategory()"
    # Login redirect if User Not Logged IN for CREATE
    if 'email' not in login_session:
        return redirect(url_for('showLogin'))

    # Grab our user
    user = getUser(login_session['login_type'], login_session['email'])
    # Get authorizations for logged on user
    auth = getAppAuth()
    # If user is NOT 'admin' then redirect to Main Page with Flash
    if auth['roles']['admin'] is False:
        flash("You need ADMIN privileges to DELETE categories!")
        redirect(url_for(catalogHome))

    # Otherwise proceed with requests
    curr_categ = session.query(
                        Category).filter(Category.name == str(category)).one()

    if request.method == 'POST':
        print "In Post"

        # Grab our hidden form values
        frm_name = request.form['name']

        if (curr_categ.name == frm_name):

            # We should be good to DELETE our category
            for item in curr_categ.items:
                session.delete(item)

            session.delete(curr_categ)
            session.commit()

            msg = "Deleted %s successfully!" % curr_categ.name
            flash(msg)
            return redirect(url_for('catalogHome'))
    else:
        print "Get request called"
        return render_template("delete-category.html", category=curr_categ)


"""
Item Specific
"""


@app.route('/catalog/<category>/items/')
def categItems(category):
    print "In categItems(category) for %s" % category
    # Grab app authorizations, if any
    auth = getAppAuth()
    is_contrib = auth['roles']['contrib']

    categories = session.query(Category).all()
    curr_categ = session.query(Category).filter(
                                          Category.name == str(category)).one()

    categ_items = session.query(Item).filter(
                         Item.category == curr_categ).order_by(Item.name).all()

    return render_template("categ-items.html", is_contrib=is_contrib,
                           categories=categories, curr_categ=curr_categ,
                           categ_items=categ_items)


@app.route('/catalog/<category>/<item>/')
def itemInfo(category, item):
    print "In itemInfo(category, item) for %s | %s" % (category, item)
    # Grab app authorizations, if any
    auth = getAppAuth()
    is_contrib = auth['roles']['contrib']

    curr_categ = session.query(Category).filter(
                                          Category.name == str(category)).one()

    curr_item = session.query(Item).filter_by(name=str(item),
                                              category=curr_categ).one()

    return render_template("item.html", is_contrib=is_contrib,
                           curr_item=curr_item)


@app.route('/catalog/item/new/', methods=['GET', 'POST'])
def newCatalogItem():
    print "In newCatalogItem()"
    # Login redirect if User Not Logged IN for EDIT
    if 'email' not in login_session:
        return redirect(url_for('showLogin'))

    # Grab our user
    user = getUser(login_session['login_type'], login_session['email'])
    # Get authorizations for logged on user
    auth = getAppAuth()
    # If user is NOT 'contrib' then redirect to Main Page with Flash
    if auth['roles']['contrib'] is False:
        flash("You need CONTRIB privileges to EDIT items!")
        redirect(url_for(catalogHome))

    # Otherwise proceed with our requests
    categories = session.query(Category).order_by(Category.name).all()

    if request.method == 'POST':
        print "In Post"

        # Grab our values
        name = request.form['name']
        desc = request.form['desc']
        categ = request.form['category']

        # Lookup actual category object
        category = session.query(Category).filter(
                                             Category.name == str(categ)).one()

        if category:
            try:
                # Create our Item
                new_item = Item(name=name, description=desc, category=category,
                                created_by=user.id)

                session.add(new_item)
                session.commit()

                flash("Catalog ITEM added successfully!")
            except exc.IntegrityError as e:
                session.rollback()
                flash("""Cannot Add, ITEM Name/Chosen Category combination
                       already exists...""")
            finally:
                return redirect(url_for('catalogHome'))
    else:
        print "Get called"
        return render_template("new-item.html", categories=categories)


@app.route('/catalog/<category>/<item>/edit/', methods=['GET', 'POST'])
def editCatalogItem(category, item):
    print "In editCatalogItem()"
    # Login redirect if User Not Logged IN for EDIT
    if 'email' not in login_session:
        return redirect(url_for('showLogin'))

    # Grab our user
    user = getUser(login_session['login_type'], login_session['email'])
    # Get authorizations for logged on user
    auth = getAppAuth()
    # If user is NOT 'contrib' then redirect to Main Page with Flash
    if auth['roles']['contrib'] is False:
        flash("You need CONTRIB privileges to EDIT items!")
        redirect(url_for(catalogHome))

    # Otherwise proceed with our requests
    curr_categ = session.query(
                         Category).filter(Category.name == str(category)).one()
    curr_item = session.query(Item).filter_by(name=str(item),
                                              category=curr_categ).one()
    categories = session.query(Category).order_by(Category.name).all()

    if request.method == 'POST':
        print "In Post"

        # Grab our values
        name = request.form['name']
        desc = request.form['desc']
        categ = request.form['category']

        # Lookup actual category object
        category = session.query(Category).filter(
                                             Category.name == str(categ)).one()

        if category and (category == curr_categ):
            # Edit our existing Item
            try:
                curr_item.name = name
                curr_item.description = desc
                curr_item.category = category
                curr_item.last_update_by = user.id

                session.commit()

                msg = "Edited %s successfully!" % curr_item.name
                flash(msg)
            except exc.IntegrityError as e:
                session.rollback()
                flash("""Cannot Edit: Item Name/Chosen Category combination
                       already exists...""")
            finally:
                return redirect(url_for('catalogHome'))
    else:
        print "Get request called"
        return render_template("edit-item.html", item=curr_item,
                               categories=categories)


@app.route('/catalog/<category>/<item>/delete/', methods=['GET', 'POST'])
def deleteCatalogItem(category, item):
    print "In deleteCatalogItem()"
    # Login redirect if User Not Logged IN for DELETE
    if 'email' not in login_session:
        return redirect(url_for('showLogin'))

    # Grab our user
    user = getUser(login_session['login_type'], login_session['email'])
    # Get authorizations for logged on user
    auth = getAppAuth()
    # If user is NOT 'contrib' then redirect to Main Page with Flash
    if auth['roles']['contrib'] is False:
        flash("You need CONTRIB privileges to DELETE items!")
        redirect(url_for(catalogHome))

    # Otherwise proceed with our requests
    curr_categ = session.query(
                         Category).filter(Category.name == str(category)).one()
    curr_item = session.query(Item).filter_by(name=str(item),
                                              category=curr_categ).one()

    if request.method == 'POST':
        print "In Post"

        # Grab our hidden
        frm_name = request.form['name']
        frm_categ = request.form['category']

        if (curr_item.name == frm_name and curr_categ.name == frm_categ):

            # We should be good to DELETE our item
            session.delete(curr_item)
            session.commit()

            msg = "Deleted %s successfully!" % curr_item.name
            flash(msg)
            return redirect(url_for('catalogHome'))
    else:
        print "Get request called"
        return render_template("delete-item.html", item=curr_item)


@app.route('/users/')
def getUsers():
    print "In getUsers()"
    users = session.query(User).all()

    return render_template("users.html", users=users)


"""
Login Specific
"""


@app.route('/login/')
@app.route('/catalog/login/')
def showLogin():
    state = hashlib.sha256(os.urandom(1024)).hexdigest()
    login_session['state'] = state
    return render_template("login.html", STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        print "request args: %s" % request.args.get('state')
        print "login_session: %s" % login_session['state']
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        code = request.data
        try:
            # Upgrade auth code into credentials object
            oauth_flow = flow_from_clientsecrets('client_secrets.json',
                                                 scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(code)
        except FlowExchangeError:
            response = make_response(json.dumps("""Failed to upgrade the
                                     authorization code."""), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Check that access token is valid
        access_token = credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
               % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])

        # Check result for errors
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Verify access token is for intended user
        gplus_id = credentials.id_token['sub']
        if result['user_id'] != gplus_id:
            response = make_response(json.dumps("""Token's user ID doesn't
                                    match given user ID."""), 401)
            response.header['Content-Type'] = 'application/json'
            return response

        # Verify access token is valid for this app
        if result['issued_to'] != CLIENT_ID:
            response = make_response(json.dumps("""Token's client ID doesn't
                                     match the app."""), 401)
            print "Token's client ID does not match the app's."
            response.headers['Content-Type'] = 'application/json'
            return response

        # Check if user is already LOGGED IN
        stored_credentials = login_session.get('credentials')
        stored_gplus_id = login_session.get('gplus_id')
        if stored_credentials is not None and gplus_id == stored_gplus_id:
            response = make_response(json.dumps("""Current user is already
                                     connected."""), 200)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Store access token in session for later use
        login_session['credentials'] = credentials.access_token
        login_session['gplus_id'] = gplus_id

        # Get Google User info
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        answer = requests.get(userinfo_url, params=params)

        data = answer.json()

        login_session['username'] = data['name']
        login_session['picture'] = data['picture']
        login_session['email'] = data['email']
        login_session['login_type'] = "google"

        # See if user is already in our database
        user = getUser("google", login_session['email'])
        if user is None:
            # Then create our User in database
            createUser(login_session)
        else:
            print user.email
            print data['email']
            user.email == data['email']
            # Just update our stored data in case something changed:
            user.name = data['name']
            user.picture = data['picture']
            session.commit()

        flash("You are now logged in as %s" % login_session['username'])
        return render_template("loggedin-welcome.html")


@app.route('/gdisconnect/')
def gdisconnect():
    # Disconnect a logged in / connected user from Google
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps("Current user not connected."),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # Execute GET to revoke current token
        access_token = credentials
        url = ("https://accounts.google.com/o/oauth2/revoke?token=%s" %
               access_token)
        h = httplib2.Http()
        result = h.request(url, 'GET')[0]

        if result['status'] == '200':
            # Reset the user's session
            del login_session['credentials']
            del login_session['gplus_id']
            del login_session['username']
            del login_session['picture']
            del login_session['email']
            del login_session['login_type']

            response = make_response(json.dumps("Successfully disconnected."),
                                     200)
            response.headers['Content-Type'] = 'application/json'
            return response
        else:
            # Other than 200 response
            print result['status']

            # Cleanup session variables either way, otherwise we may not be
            # able to Logout
            del login_session['credentials']
            del login_session['gplus_id']
            del login_session['username']
            del login_session['picture']
            del login_session['email']
            del login_session['login_type']

            response = make_response(json.dumps(
                                 "Failed to revoke token for the given user."),
                                 400)
            response.headers['Content-Type'] = 'application/json'
            return response


@app.route('/logout/')
@app.route('/catalog/logout/')
def logout():
    print "In logout()"
    if 'login_type' in login_session:
        if login_session['login_type'] == 'google':
            gdisconnect()
        # Can add OTHER providers here as needed
    else:
        flash("You are not logged in...")

    return redirect(url_for('catalogHome'))


""" API Endpoint Specific """


# Our Entire Catalog with Items
@app.route('/catalog.json')
def catalogJSON():
    print "In catalogJSON()"

    catalog = []
    categories = session.query(Category).all()
    for category in categories:
        me = {'Category': category, 'Items': category.items}
        catalog.append(me)

    return jsonify(Catalog=list(catalog))


# Individual API Endpoints for Entities
@app.route('/categories.json')
@app.route('/catalog/categories/json/')
def categoriesJSON():
    print "In categoriesJSON()"

    categories = session.query(Category).all()
    return jsonify(Categories=list(categories))


@app.route('/catalog/<category>/json/')
def singleCategJSON(category):
    print "In singleCategJSON()"

    category = [session.query(Category).filter_by(name=category).one()]
    return jsonify(Category=list(category))


@app.route('/catalog/<category>/items/json/')
def singleCategItemsJSON(category):
    print "In singleCategItemsJSON()"

    category = session.query(Category).filter_by(name=category).one()
    categItems = [{'Category': category, 'Items': category.items}]
    return jsonify(CategItems=list(categItems))


@app.route('/items.json')
@app.route('/catalog/items/json/')
def itemsJSON():
    print "In itemsJSON()"

    items = session.query(Item).all()
    return jsonify(Items=list(items))


@app.route('/catalog/<category>/<item>/json/')
def singleItemJSON(category, item):
    print "In singleItemJSON()"

    curr_categ = session.query(Category).filter(
                                               Category.name == category).one()
    item = [session.query(Item).filter_by(
                                name=item, category=curr_categ).one()]
    return jsonify(Item=list(item))


@app.route('/login-types.json')
@app.route('/catalog/login-types/json/')
def loginTypesJSON():
    print "In loginTypesJSON()"

    login_types = session.query(LoginType).all()
    return jsonify(LoginTypes=list(login_types))


@app.route('/roles.json')
@app.route('/catalog/roles/json/')
def rolesJSON():
    print "In rolesJSON()"

    roles = session.query(Role).all()
    return jsonify(Roles=list(roles))


@app.route('/users.json')
@app.route('/catalog/users/json/')
def usersJSON():
    print "In usersJSON()"

    users = session.query(User).all()
    return jsonify(Users=list(users))


if __name__ == '__main__':
    app.secret_key = "secret"
    app.template_folder = 'templates'
    app.debug = True
    app.run(host='0.0.0.0', port=9090)
