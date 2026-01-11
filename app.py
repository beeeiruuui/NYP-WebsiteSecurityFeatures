# Import Useful libraries
import flask_login
from flask_mysqldb import MySQL
import flask
from flask import Flask, render_template, request, redirect, url_for, session, flash, app
import re, requests
import MySQLdb.cursors
from database import Database
from user import User
import json
import datetime
from datetime import timedelta
from handRec import cv2, handTracker, numpy
import ast
from flask_wtf.csrf import CSRFProtect , CSRFError
import time
import random
import smtplib, ssl
from email.message import EmailMessage
from argon2 import PasswordHasher

#authy
from authy.api import AuthyApiClient

# global Vars
app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)
#database = Database()
app.secret_key = "ming"
#app.config['SECRET_KEY'] = "ming"
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '280504SQL'
app.config['MYSQL_DB'] = 'pythonlogin'
mysql = MySQL(app)

#authy
authy_api = AuthyApiClient('ZM50naEa7snljBqpnikO6HZuh1XZMW5H')

def is_Human(captcha_response):
    cap_secret = "6Lc9JPYgAAAAAKwXOSxVBPMlh1FSq3HvMrE0K-gt"
    cap_data = {"response":captcha_response,"secret":cap_secret}
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", cap_data)
    response_text = json.loads(response.text)
    return response_text['success']

#@app.route('/')


@app.before_first_request
def make_session_permanent():
    msg = "Inactivity for 1 hour"
    flask.session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(hours=1)
    flask.session.modified = True
    flask.g.user = flask_login.current_user
    render_template('login.html', msg=msg)

# Starting page which will be displayed to user when app is started

@app.route('/', methods=['GET', 'POST'])
def login():
    ph = PasswordHasher()
    # Message to be displayed
    msg = ''
    sitekey = "6Lc9JPYgAAAAAMxcrs-LwhfRXbK-yKNhh8ae-VTu"
    # Check is the call is post and fields are not empty
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        #account = database.getUser(username, password)
        captcha_response = request.form["g-recaptcha-response"]

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()
        authyid = account['authyid']
        session['authyid'] = account['authyid']

        # start session  If account exist otherwise display the message
        try:
            if ph.verify(account['password'], password):
                if is_Human(captcha_response):
                    session['loggedin'] = True
                    session['username'] = account['username']

                    cap = cv2.VideoCapture(0)
                    tracker = handTracker()
                    for i in range(100):
                        success,image = cap.read()
                        image = tracker.handsFinder(image)
                        lmList = tracker.positionFinder(image)
                        if len(lmList) != 0:
                            print(lmList[4])

                        cv2.imshow("Video", image)
                        cv2.waitKey(1)

                        print(account)
                        comparelist=ast.literal_eval(account['handrec'])
                        print(comparelist)
                        newlmlist=lmList[4]
                        print(newlmlist)

                        for keys in comparelist:
                            if (newlmlist[0] - keys[0] == 1 or 2 or 3 or 4 or 5 or 6 or 7 or 8 or 9 or 10 or 0) or (keys[1] - newlmlist[1] ==  1 or 2 or 3 or 4 or 5 or 6 or 7 or 8 or 9 or 10 or 0) or (newlmlist[1] - keys[1] == 1 or 2 or 3 or 4 or 5 or 6 or 7 or 8 or 9 or 10 or 0) or (keys[0] - newlmlist[0] ==  1 or 2 or 3 or 4 or 5 or 6 or 7 or 8 or 9 or 10 or 0):
                                print(keys)

                                session['authyid'] = authyid
                                sms = authy_api.users.request_sms(authyid)
                                print(sms.content)

                                msg = 'Logged in successfully !'
                                return render_template('twofactor.html', msg=msg)

                if not is_Human(captcha_response):
                    session['loggedin'] = True
                    session['username'] = account['username']
                    msg = 'Please do the Captcha!'
                    return render_template('login.html', msg=msg, siteky=sitekey)
        except:
            cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
            # Fetch one record and return result
            account = cursor.fetchone()
            flash("Please do the CAPTCHA")
            print(account['logincount'])
            newaccountlogincount=account['logincount']+1
            cursor.execute('UPDATE accounts set logincount = %s where id = %s;', (newaccountlogincount,account['id']))
            #cursor.execute(account['logincount']=newaccountlogincount)
            mysql.connection.commit()
            print(newaccountlogincount)
            if newaccountlogincount == 3:
                print("YEY")
                time.sleep(10)
                msg = 'timeout 30 secs'
                cursor.execute('UPDATE accounts set logincount = %s where id = %s;', (0,account['id']))
                mysql.connection.commit()
            msg = 'Incorrect username or Password'

    return render_template('login.html', msg=msg, siteky=sitekey)

#2FA
@app.route('/twofactor', methods=['GET', 'POST'])
def twofactor():
    authy_api = AuthyApiClient('ZM50naEa7snljBqpnikO6HZuh1XZMW5H')
    msg = ''
    authyid = session['authyid']

    if sms.ok():
        print(sms.content)
        print('ok')

    if request.method == 'POST' and 'TFA' in request.form:
        print(request.form['TFA'])
        TFA = request.form['TFA']
        #print(request.form['authyid'])
        #authyid = request.form['authyid']
        verification = authy_api.tokens.verify(authyid, token=TFA)
        print(verification.ok())
        if verification.ok():
            msg = 'Logged in successfully-!'
            return render_template('index.html', msg=msg)
        else:
            msg = 'wrong 2fa code'
            sms = authy_api.users.request_sms(authyid)
            print(sms.content)
            return render_template('twofactor.html', msg=msg, authyid=int(authyid))
    return render_template('twofactor.html', msg=msg)


# Function to signout the user when clicked
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


# Function to use for Registring the element
@app.route('/register', methods=['GET', 'POST'])
def register():
    ph = PasswordHasher()
    handStor=[]
    logincount='0'
    msg = ''
    # Check if the call is post and fields are not empty
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'country' in request.form and 'gender' in request.form:
        username = request.form['username']
        password = ph.hash(request.form['password'])
        email = request.form['email']
        countrycode = request.form['countrycode']
        phoneNO = request.form['phoneNO']
        country = request.form['country']
        gender = request.form['gender']
        print("hi")

        cap = cv2.VideoCapture(0)
        tracker = handTracker()
        for i in range(15):
            success,image = cap.read()
            image = tracker.handsFinder(image)
            lmList = tracker.positionFinder(image)
            if len(lmList) != 0:
                print(lmList[4])
                handStor.append(lmList[4])
            cv2.imshow("Video", image)
            cv2.waitKey(1)
        print('hi')



        # Check if user with that username already exist
        #account = database.getUser(username, password)
        #if account:
        ###user = authy_api.users.create(email=email, phone=phoneNO, country_code=countrycode)
        print(email,phoneNO,countrycode)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        account = cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        if cursor.execute('select * from accounts where username = %s and password = %s', (username, password,)):
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        elif not user.ok():
            print(email,phoneNO,countrycode)
            msg = 'Authy error'
            print('ok')
            print(user.errors())
        else:
            #database.AddUser(User(username, password, gender, email, country))
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            print(handStor)
            authyid = user.id
            cursor.execute("insert into `accounts` (`id`, `username`, `password`, `email`, `country`, `gender`, `handrec`, `countrycode`, `phoneNO`, `authyid`, `logincount`) values (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);" , (username, password, email, country, gender, str(handStor), countrycode, phoneNO, authyid, logincount))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            #msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)

# @app.route('/otpP1', methods=['GET', 'POST'])
# def otpP1():
#     if request.method == 'POST' and 'username' in request.form:
#         username = request.form['username']
#
#         otpno = random.randint(1000,9999)
#         # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         # cursor.execute("insert into `accounts`(`otp`) values (%s) where username = '%s'",(otpno,username))
#
#         #email
#         email_sender = 'sspprojectemailsend@gmail.com'
#         email_password = 'ihzcmrhafbuuxcdy'
#         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         cursor.execute("select * from accounts where username ='%s'" % username)
#
#         cf = cursor.fetchone()
#
#         email_receiver = '%s', cf['email']
#         print(email_receiver)
#         #print(email)
#         #print(cursor.execute("select `email` from `accounts` where `username` = '%s'; " % username))
#         subject = 'OTP Number'
#         body = """
#         Your OTP Number is: %s
#         If this Email was not meant for you, Please Ignore This Email
#         """ % otpno
#         em = EmailMessage()
#         em['From'] = email_sender
#         em['To'] = email_receiver
#         em['Subject'] = subject
#         em.set_content(body)
#
#         context = ssl.create_default_context()
#
#         # Log in and send the email
#         with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
#             smtp.login(email_sender, email_password)
#             smtp.sendmail(email_sender, email_receiver, em.as_string())
#         return render_template('otpP2.html')
#
#     return render_template('otpP1.html')
@app.route("/otpP1", methods=[ 'GET','POST'])
def otpP1():
    msg = ''
    ph=PasswordHasher()
    if request.method == 'POST' and 'username' in request.form:
        username = request.form['username']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = "%s"', (username))
        account = cursor.fetchone()


        # start session  If account exist otherwise display the message

        if account:
            session['loggedin'] = True
            session['username'] = account['username']
            return render_template('otpP2.html', msg=msg)

    return render_template("otpP1.html", msg=msg)


@app.route('/otpP2', methods=['GET','POST'])
def otpP2():
    if 'loggedin' in session:
        otpno = random.randint(1000,9999)
        #email
        email_sender = 'sspprojectemailsend@gmail.com'
        email_password = 'ihzcmrhafbuuxcdy'
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("select * from accounts where username ='%s'" % session['username'])

        cf = cursor.fetchone()

        email_receiver = '%s', cf['email']
        #print(email)
        #print(cursor.execute("select `email` from `accounts` where `username` = '%s'; " % username))
        subject = 'OTP Number'
        body = """
        Your OTP Number is: %s
        If this Email was not meant for you, Please Ignore This Email
        """ % otpno
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()

        # Log in and send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())
        if request.method == 'POST' and 'otp' in request.form:
            otp = request.form['otp']
            if otp == otpno:
                return render_template('forgetpass.html')
            else:
                return render_template('otpP2.html')
        return render_template('otpP2.html')
    return redirect(url_for('otpP1'))


@app.route('/forgetpass', methods=['POST'])
def forgetpass():
    msg = ''
    ph=PasswordHasher()
    if 'loggedin' in session:
        if request.method == 'POST' and 'password' in request.form:
            password = ph.hash(request.form['password'])
            username = session['username']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("Update accounts set password = %s where username = %s",(password,username))
            mysql.connection.commit()
            msg = 'You have successfully updated !'
            return render_template("login.html")
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template("forgetpass.html", msg=msg)
    return redirect(url_for('otpP1'))

@app.route("/index")
def index():
    print('hi')
    if 'loggedin' in session:
        print("hi")
        return render_template("index.html")
    return redirect(url_for('login'))

#NEED REEEEEEEEEEEEEEE
@app.route("/display", methods=['post','get'])
def display():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #account = database.getUserbyName(session['username'])
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        country = request.form['country']
        gender = request.form['gender']
        cursor = cursor.execute('select * from accounts where username = %s and password = %s and email = %s and country = %s and gender = %s', (username, password, email, country, gender))
        mysql.connection.commit()
        return render_template("display.html", cursor=cursor)
    return redirect(url_for('login'))


@app.route("/update", methods=['GET', 'POST'])
def update():
    msg = ''
    ph=PasswordHasher()
    if 'loggedin' in session:
        if request.method == 'POST' and 'password' in request.form:
            password = ph.hash(request.form['password'])
            username = session['username']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("Update accounts set password = %s where username = %s",(password,username))
            mysql.connection.commit()
            msg = 'You have successfully updated !'
            return render_template("login.html")
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template("update.html", msg=msg)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()
    #database.CloseDatabase(debug=True)
