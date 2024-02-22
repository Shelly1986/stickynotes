import flask
import sqlite3
from flask import Flask, redirect, url_for, flash, session


from forms import RegistrationForm, LoginForm


app = Flask('__name__')
app.config['SECRET_KEY'] = '5b5517e6013e2c3b1b1745f65a646ec1'

def initialise_db():
    connection = sqlite3.connect('login.db')
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users(email TEXT, password TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS sticky(id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT,note_text TEXT, note_color TEXT, FOREIGN KEY(email) REFERENCES users(email))")
    connection.commit()

initialise_db()

@app.route('/')
def home():
    form = LoginForm()
    return flask.render_template('index.html',title='Login',form=form)

@app.route('/login',methods = ['POST'])
def login():
    form = LoginForm()
    
    if flask.request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.password.data
        connection = sqlite3.connect('login.db')
        cursor = connection.cursor()
        cursor.execute("SELECT password from users WHERE email=?",[ email ])
        stored_password = cursor.fetchone()
        if stored_password is None:
            message =  "User not found"
        elif password == stored_password[0]:
            session['email'] = email
            cursor.execute("SELECT email from users WHERE email=?",(email,))
            email = cursor.fetchone()
            cursor.execute("SELECT * from sticky WHERE email=?",(email[0],))
            notes = cursor.fetchall()
            return flask.render_template('sticky.html',email=email,notes=notes)
        else:
            message = "Login Failed"
        
    else:
        message = 'Login Failed'
    connection.close()
    return flask.render_template('index.html', form=form, message = message)

    
@app.route('/register')
def register():
    form = RegistrationForm()
    return flask.render_template('signup.html', title ='register', form=form)

@app.route('/signup',methods=['POST'])
def signup():
    form = RegistrationForm()
    if flask.request.method == 'POST':
       
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            connection = sqlite3.connect('login.db')
            cursor = connection.cursor()
            result=cursor.execute("SELECT email from users where email=?",(email,))
            fetched_result = result.fetchone()
            if fetched_result is None:
                cursor.execute("INSERT INTO users(email,password) VALUES(?,?)",[ email, password ])
                connection.commit()
                message_signup = "Sign up successful"
                
            else:
                message_signup = "This email already exists. Try again!"
            return flask.render_template('signup.html',message_signup=message_signup,form=form)
    connection.close()
    return flask.render_template('signup.html',form=form)


@app.route('/showsticky',methods=['GET'])
def showsticky():
    email= flask.session.get('email')
    connection = sqlite3.connect('login.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * from sticky WHERE email=?",[email])
    notes = cursor.fetchall()
    connection.close()
    return flask.render_template('sticky.html',email=email,notes=notes)

@app.route('/addsticky',methods=['POST'])
def addsticky():
    email= flask.session.get('email')
    notetext = flask.request.values.get('notetext')
    notecolor = flask.request.values.get('notecolor')
    if notetext == '':
        flash("Please enter some text on your sticky note")
    else:
        connection = sqlite3.connect('login.db')
        with connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO sticky (email, note_text,note_color) VALUES(?,?,?)", [ email,notetext,notecolor ])
        connection.close()
    return flask.redirect("/showsticky")


@app.route('/deletesticky/<int:note_id>',methods = ['POST'])
def deletesticky(note_id):
    email = flask.session.get('email')
    note_id = flask.request.values.get('note_id')
    print(note_id)
    connection = sqlite3.connect('login.db')
    cursor = connection.cursor()
    cursor.execute("DELETE from sticky where id=?",(note_id,))
    connection.commit()
    cursor.execute("SELECT email from users WHERE email=?",(email,))
    email = cursor.fetchone()
    cursor.execute("SELECT * from sticky WHERE email=?",(email[0],))
    notes = cursor.fetchall()
    print(notes)
    connection.close()
    return flask.render_template('sticky.html',email=email,notes=notes)
    
