from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash, g
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Days, MealOption, User
from flask import session as login_session
from functools import wraps
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "WhatsforDinner Application"

engine = create_engine('sqlite:///whatsfordinner.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token for the login session
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


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
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already \
            connected.'), 200)
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

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 200px; height: 200px;border-radius: \
    150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
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
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # If the given token was invalid notice the user.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON API for list of days of the week
@app.route('/whatsfordinner/JSON')
def whatsfordinnerJSON():
    dayslist = session.query(Days).all()
    return jsonify(DaysList=[r.serialize for r in dayslist])

# JSON API for an individual day of the week


@app.route('/whatsfordinner/<int:days_id>/JSON')
def daysJSON(days_id):
    days = session.query(Days).filter_by(id=days_id).one()
    meal = session.query(MealOption).filter_by(days_id=days.id)
    return jsonify(MealOption=[i.serialize for i in meal])

# JSON API for list of a specific meal on a day or unassigned


@app.route('/whatsfordinner/<int:days_id>/<int:meal_id>/JSON')
def itemJSON(days_id, meal_id):
    days = session.query(Days).filter_by(id=days_id).one()
    meal = session.query(MealOption).filter_by(id=meal_id).one()
    return jsonify(MealDetails=[meal.serialize])


# Login Required function
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash("You are not allowed to access there")
            return redirect('/login')
    return decorated_function


# Home page to view all meals
@app.route('/')
@app.route('/whatsfordinner')
def showWhatsfordinner():
    days = session.query(Days).all()
    meal = session.query(MealOption).all()
    if 'username' not in login_session:  # make sure user has logined
        return render_template('publicwhatsfordinner.html', days=days,
                               meal=meal)
    else:  # if user logined, able to access create a new item
        return render_template('whatsfordinner.html', days=days,
                               meal=meal)


# Enter a new Meal
@app.route('/whatsfordinner/new', methods=['GET', 'POST'])
@login_required
def newMeal():
    if request.method == 'POST':  # get data from the form
        newMeal = MealOption(
            name=request.form['name'],
            ingredients=request.form['ingredients'],
            days_id=request.form['days_id'],
            user_id=login_session['user_id'])
        session.add(newMeal)
        session.commit()
        return redirect(url_for('showWhatsfordinner'))
    else:
        return render_template('newmeal.html')


# Show meals inside the specific days
@app.route('/whatsfordinner/<int:days_id>')
def showDays(days_id):
    alldays = session.query(Days).all()
    days = session.query(Days).filter_by(id=days_id).one()
    meal = session.query(MealOption).filter_by(days_id=days.id)
    return render_template('day.html', days=days, meal=meal,
                           alldays=alldays)


# Show the specific meal and the description of it
@app.route('/whatsfordinner/<int:days_id>/<int:meal_id>')
def showMeal(days_id, meal_id):
    days = session.query(Days).filter_by(id=days_id).one()
    meal = session.query(MealOption).filter_by(id=meal_id).one()
    if 'username' not in login_session or meal.user_id != login_session['user_id']:
            # make sure user logined and user is the creator
            return render_template('publicmeal.html', days=days, meal=meal)
    else:  # if user is the creator, able to access update and delete the meal
        return render_template('meal.html', days=days, meal=meal)


# Edit the specific meal details or assignment
@app.route('/whatsfordinner/<int:days_id>/<int:meal_id>/edit',
           methods=['GET', 'POST'])
@login_required
def editMeal(days_id, meal_id):
    editedMeal = session.query(MealOption).filter_by(id=meal_id).one()
    # make sure user is the creator
    if editedMeal.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized"\
         "to edit this meal. Please create your own meal in order to edit.');"\
         "window.location = '/';}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        # if name is empty there is no change
        if request.form['name'] == "":
            editedMeal.name = editedMeal.name
        else:
            editedMeal.name = request.form['name']

        # if ingredients are empty there is no change
        if request.form['ingredients'] == "":
            editedMeal.ingredients = editedMeal.ingredients
        else:
            editedMeal.ingredients = request.form['ingredients']

        # if day is empty it will return unchange from previous set selection
        if request.form['days_id'] == "":
            editedMeal.days_id = editedMeal.days_id
        else:
            editedMeal.days_id = request.form['days_id']

        session.add(editedMeal)
        session.commit()

        return redirect(url_for('showMeal', days_id=days_id,
                                meal_id=meal_id))
    else:
        return render_template('editmeal.html', days_id=days_id,
                               meal_id=meal_id, meal=editedMeal)


# Delete the specific meal selected
@app.route('/whatsfordinner/<int:days_id>/<int:meal_id>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteMeal(days_id, meal_id):
    mealToDelete = session.query(MealOption).filter_by(id=meal_id).one()
    # make sure user is the creator
    if mealToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized "\
         "to delete this meal. Please create your own meal in order to delete"\
         " .');window.location = '/';}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(mealToDelete)
        session.commit()
        return redirect(url_for('showDays', days_id=days_id))
    else:
        return render_template('deletemeal.html', days_id=days_id,
                               meal_id=meal_id, meal=mealToDelete)


# Disconnect Login View to Edit
@app.route('/disconnect')
def disconnect():
    if 'username' in login_session:
        gdisconnect()
        flash("You have successfully been logged out.")
        return redirect(url_for('showWhatsfordinner'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showWhatsfordinner'))

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000, threaded=False)
