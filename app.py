import flask
import sqlite3
import pyotp
from flask import Flask, redirect, url_for, flash, session
from flask_mail import Mail,Message
from forms import RegistrationForm, LoginForm, ForgotForm,VerifyForm,ForgotOtp,ResetForm
app = Flask('__name__')
app.config['SECRET_KEY'] = '5b5517e6013e2c3b1b1745f65a646ec1'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'computersciencecis@gmail.com'
app.config['MAIL_PASSWORD'] = 'kqja ound rjsw nehg'
app.config['MAIL_DEFAULT_SENDER'] = 'computersciencecis@gmailcom'
mail = Mail(app)

def initialise_db():
    connection = sqlite3.connect('login.db')
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users(email TEXT, password TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS sticky(id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT,note_text TEXT, note_color TEXT, FOREIGN KEY(email) REFERENCES users(email))")
    connection.commit()

initialise_db()

def send_otp_email(email, otp):
    subject = 'Email Verification OTP'
    body = f'Your OTP for email verification is: {otp}.The OTP is valid for 10 minutes.'
    msg = Message(subject, recipients=[email], body=body)
    mail.send(msg)

def reset_password_send(email, otp):
    subject = 'OTP for Password Reset'
    body = f'Your OTP for resetting your password is: {otp}.The OTP is valid for 10 minutes.'
    msg = Message(subject, recipients=[email], body=body)
    mail.send(msg)
    
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
            return flask.render_template('sticky.html',email=form.email.data,notes=notes)
        else:
            message = "Login Failed"
    else:
        message=""
    
    return flask.render_template('index.html', form=form, message = message)

    
@app.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    return flask.render_template('signup.html', title ='register', form=form)

@app.route('/signup',methods=['GET','POST'])
def signup():
    form = RegistrationForm()
    if flask.request.method == 'POST' and form.validate():
        email = form.email.data
        session['email'] = email
        password = form.password.data
        session['password'] = password
        connection = sqlite3.connect('login.db')
        cursor = connection.cursor()
        result=cursor.execute("SELECT email from users where email=?",(email,))
        fetched_result = result.fetchone()
        if fetched_result is None:
            totp = pyotp.TOTP(pyotp.random_base32(),interval=600)
            otp = totp.now()
            send_otp_email(email, otp)
            session['otp'] = otp
            return flask.redirect('/verify')
        else:
            message_signup = "This email already exists. Try again!"
            return flask.render_template('signup.html',message_signup=message_signup,form=form)
            
    return flask.render_template('signup.html',form=form)

@app.route('/verify',methods=['GET','POST'])
def verify():
    form = VerifyForm()
    email = flask.session.get('email')
    password = flask.session.get('password')
    user_otp = form.otp.data
    system_otp = flask.session.get('otp')
    if flask.request.method == 'POST' and form.validate_on_submit():
        email = flask.session.get('email')
        password = flask.session.get('password')
        user_otp = form.otp.data
        if user_otp == system_otp:
            connection = sqlite3.connect('login.db')
            cursor = connection.cursor()
            cursor.execute("INSERT INTO users(email,password) VALUES(?,?)",[ email, password ])
            connection.commit()
            message_signup = "Sign up successful. Please login"
            session.pop('otp')
            return flask.render_template('index.html',message_signup=message_signup,form=LoginForm())
        else:
            message_signup = "The OTP is not correct"
            return flask.render_template('signup.html',message_signup=message_signup,form=RegistrationForm())
    else:
        return flask.render_template('verify.html',form=form)

@app.route('/showsticky',methods=['GET'])
def showsticky():
    email= flask.session.get('email')
    connection = sqlite3.connect('login.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * from sticky WHERE email=?",(email,))
    notes = cursor.fetchall()
    connection.close()
    return flask.render_template('sticky.html',email=email,notes=notes)

@app.route('/addsticky',methods=['POST'])
def addsticky():
    email= flask.session.get('email')
    notetext = flask.request.values.get('notetext')
    notecolor = flask.request.values.get('notecolor')
    if notetext == '':
        flash("Please enter some text to your sticky note")
    else:
        connection = sqlite3.connect('login.db')
        with connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO sticky (email, note_text,note_color) VALUES(?,?,?)", [ email,notetext,notecolor ])
        
    return flask.redirect("/showsticky")


@app.route('/deletesticky/<int:note_id>',methods = ['POST'])
def deletesticky(note_id):
    email = flask.session.get('email')
    note_id = flask.request.values.get('note_id')
    connection = sqlite3.connect('login.db')
    cursor = connection.cursor()
    cursor.execute("DELETE from sticky where id=?",(note_id,))
    connection.commit()
    cursor.execute("SELECT email from users WHERE email=?",(email,))
    email = cursor.fetchone()
    cursor.execute("SELECT * from sticky WHERE email=?",(email[0],))
    notes = cursor.fetchall()
    connection.close()
    return flask.render_template('sticky.html',email=flask.session.get('email'),notes=notes)

@app.route('/forgot',methods=['GET','POST'])
def forgot():
    form = ForgotForm()
    return flask.render_template('forgot.html',form=form) 

@app.route('/forgot_password',methods=['GET','POST'])
def forgot_password():
    form = ForgotForm()
    message = ''
    if flask.request.method == 'POST':
        
        if form.validate():
            
            email = form.email.data
            print(email)
            connection = sqlite3.connect('login.db')
            cursor = connection.cursor()
            cursor.execute("SELECT email from users where email=?",(email,))
            result = cursor.fetchone()
            print(result)
            if result is None:
                message = "This user does not exist in our database"
                return flask.render_template('forgot.html',form=form,message=message)
            else:
                totp = pyotp.TOTP(pyotp.random_base32(),interval=600)
                otp = totp.now()
                reset_password_send(email, otp)
                session['otp'] = otp
                message = "We've sent you an OTP on your email address which is valid for the next 10 minutes"   
                return flask.render_template('forgot_otp.html',form=ForgotOtp(),message=message)
        else:
            return flask.render_template('forgot.html',form=form,message=message)
    else:
        return flask.render_template('forgot.html',form=form,message=message)

@app.route('/for_otp',methods=['GET','POST'])
def for_otp():
    form = ForgotOtp()
    message=''
    user_otp = form.otp.data
    if user_otp == flask.session.get('otp'):
        return flask.redirect('/reset_password')
    else:
        message = "The OTP is not correct"
        return flask.render_template('forgot.html',message=message,form=ForgotForm())
    
@app.route('/reset_password',methods=['GET','POST'])
def reset_password():
    form = ResetForm()
    return flask.render_template('reset.html',form=form)

@app.route('/reset',methods = ['GET','POST'])
def reset():
    form = ResetForm()
    new_password = form.new_password.data
    message_reset=''
    if flask.request.method == 'POST' and form.validate_on_submit():
        print("validated")
        email = flask.session.get('email')
        connection = sqlite3.connect('login.db')
        cursor = connection.cursor()
        cursor.execute("UPDATE users SET password = ? WHERE email=?",(new_password,email))
        connection.commit()
        message_reset="Your password has been reset. Please login with the new password"
        return flask.render_template('index.html',message_reset=message_reset,form=LoginForm())
    else:
        return flask.render_template('reset.html',form=form)
    
    
app.run(host="0.0.0.0", port = 8080, debug=True)