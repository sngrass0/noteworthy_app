from flask_app import app, bcrypt
from flask import render_template, redirect, request, session, flash
from flask_app.models.user import User

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template('index.html')

@app.route('/signup')
def display_signup():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template('signup.html')

# ! CREATE
@app.route("/register", methods = ['post'])
def register():
    print(request.form)
    print('hi')
    #validate our user
    if not User.validate_user(request.form):
        return redirect('/signup')

    #hash the password
    hashed_pw = bcrypt.generate_password_hash(request.form['password'])
    print(hashed_pw)

    #save the user to the database
    data = {
        'username' : request.form['username'],
        'name' : request.form['name'],
        'email' : request.form['email'],
        'password' : hashed_pw,
    }
    #call correct model class to save as new entry
    #this will return a user ID of the newly added user
    user_id = User.save(data)

    #log in the user by setting the session user id and first name
    session['user_id'] = user_id
    session['name'] = request.form['name']

    #redirect user to app
    return redirect('/dashboard')

#! READ and VERIFY AKA LOGIN
@app.route('/login', methods=['post'])
def login():
    print(session)
    if not User.validate_login(request.form):
        return redirect('/')

    # see of the email is in our DB
    user = User.get_by_email(request.form);
    if not user:
        flash('invalid email', 'login')
        return redirect('/')

    #check to see of the password provided matches the password in our DB
    if not bcrypt.check_password_hash(user.password, request.form['password']):
        # if we get False after checking the password
        flash("Invalid Email/Password", 'login')
        return redirect('/')

    #log in the user
    session['user_id'] = user.id
    session['name'] = user.name

    #redirect user to app
    return redirect('/dashboard')

# ! DELETE and LOGOUT
@app.route('/logout')
def login_user():
    # clear the session
    session.clear()
    # redirect back to login
    return redirect('/')