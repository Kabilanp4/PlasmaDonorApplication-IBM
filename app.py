import re
from distutils.log import debug
import ibm_db
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for

load_dotenv()

def connection():
    try:
        conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=b1bc1829-6f45-4cd4-bef4-10cf081900bf.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32304;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=zqb38336;PWD=mXZtKeezysuDOfK2;",'','')
        print("Connected to Database")
        return conn
    except:
        print("Not Connected to Database")


app = Flask(__name__)
app.secret_key = '123'
conn = connection()
app.debug = True
app.config['SESSION_TYPE'] = 'filesystem'



@app.route('/')  
@app.route('/home')
def dash():
    return render_template('dashboard.html')

@app.route('/homepage')
def dashboard():
    return render_template('dashboard1.html')
      
@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/loginpage',methods=['GET', 'POST'])
def loginpage():
    global userid
    msg = ''

    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
        sql = "SELECT * FROM donor WHERE username =? AND password=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print (account)
        if account:
            session['loggedin'] = True
            session['id'] = account['USERNAME']
            userid=  account['USERNAME']
            session['username'] = account['USERNAME']
            msg = 'Logged in successfully !'
            return redirect(url_for('dashboard'))
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)
   
@app.route('/registration')
def home():
    return render_template('register.html')

@app.route('/register',methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        city = request.form['city']
        infect = request.form['infect']
        blood = request.form['blood']
        sql = "SELECT * FROM donor WHERE username =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        else:
            insert_sql = "INSERT INTO  donor VALUES (?, ?, ?, ?, ?, ?, ?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, username)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, password)
            ibm_db.bind_param(prep_stmt, 4, city)
            ibm_db.bind_param(prep_stmt, 5, infect)
            ibm_db.bind_param(prep_stmt, 6, blood)
            ibm_db.bind_param(prep_stmt, 7, phone)

            ibm_db.execute(prep_stmt)
            msg = 'You have successfully registered !'
                       
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

@app.route('/status')
def status():
    
        sql = "SELECT COUNT(*), (SELECT COUNT(*) FROM DONOR WHERE blood= 'O Positive'), (SELECT COUNT(*) FROM DONOR WHERE blood='A Positive'), (SELECT COUNT(*) FROM DONOR WHERE blood='B Positive'), (SELECT COUNT(*) FROM DONOR WHERE blood='AB Positive'), (SELECT COUNT(*) FROM DONOR WHERE blood='O Negative'), (SELECT COUNT(*) FROM DONOR WHERE blood='A Negative'), (SELECT COUNT(*) FROM DONOR WHERE blood='B Negative'), (SELECT COUNT(*) FROM DONOR WHERE blood='AB Negative') FROM donor"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        return render_template('status.html',b=account)

@app.route('/requester')
def requester():
    return render_template('request.html')

@app.route('/requested',methods=['POST'])
def requested():
    bloodgrp = request.form['blood']
    address = request.form['address']
    name=  request.form['username']
    email=  request.form['email']
    phone= request.form['phone']
    insert_sql = "INSERT INTO  requested VALUES (?, ?, ?, ?, ?)"
    prep_stmt = ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(prep_stmt, 1, bloodgrp)
    ibm_db.bind_param(prep_stmt, 2, address)
    ibm_db.bind_param(prep_stmt, 3, name)
    ibm_db.bind_param(prep_stmt, 4, email)
    ibm_db.bind_param(prep_stmt, 5, phone)
    ibm_db.execute(prep_stmt)
    return render_template('request.html', pred="Your request is sent to the concerned people.")


@app.route('/')

def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return render_template('dashboard1.html')


if __name__ == '__main__':
   app.run(host='0.0.0.0',port=5000)

        