from flask import *
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import smtplib
import ssl
import math
import random

smtp_port = 587
smtp_server = "smtp.gmail.com"
images=os.path.join('static','images')
otp=""

app = Flask(__name__)
app.config['SECRET_KEY'] = "Your_secret_string"

def dbconnect():
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (name VARCHAR(255) NOT NULL, email TEXT primary key, password VARCHAR(255) NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS contacts (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT NOT NULL, message TEXT NOT NULL)")
    con.commit()
    return cur, con


@app.route('/')
def index():
    # session.clear()
    if 'email' not in session:
        return render_template('index.html', user="Get Started")
    else:
        return render_template('index.html', user=session['name'])

@app.route("/getstarted")
def getstarted():
    if 'email' not in session:
        return render_template('login.html')
    return render_template('login.html')

@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        cur, con = dbconnect()
        data = request.get_json()
        check_email = cur.execute("SELECT name, password  FROM users WHERE email = '{0}'".format(data['email']))
        check_email = check_email.fetchone()
        if check_email and check_password_hash(check_email[1], data['password']): 
            session['email'] = data['email']
            session['name'] = check_email[0]
            return jsonify({'msg': 'logged in',
                            'status': 220})
        else:
            return jsonify({'msg': 'Invalid email or password',
                            'status': 320})
        
def OTP():
    digits = "0123456789"
    OTP = ""
    for i in range(6):
        OTP += digits[math.floor(random.random() * 10)]
    return OTP

@app.route('/otp', methods=['POST'])
def otpt():
    global otp
    # global simple_email_context
    data = request.get_json()
    email = data['email']
    conn_cred = sqlite3.connect('cred.db')

    # Create a cursor
    cursor_cred = conn_cred.cursor()

        # Execute an SQL command to retrieve the first row from the user table
    cursor_cred.execute('SELECT * FROM user LIMIT 1')

        # Fetch the first row and print it
    row = cursor_cred.fetchone()
    email_from=row[1]
    decrypted=row[2]

        # Close the connection
    conn_cred.close()
    try:
        otp = OTP() 
        otpp= otp + " is your OTP!"
        subject = f"Welcome th LISA!"
        message = f"{otpp}.\nPlease do not share it with anyone."
        simple_email_context = ssl.create_default_context()
        print("Connecting to server...")
        tie_server = smtplib.SMTP(smtp_server,smtp_port)
        tie_server.starttls(context=simple_email_context)
        tie_server.login(email_from, decrypted)
        print()
        print(f"Sending email to - {email}")
        tie_server.sendmail(email_from, email, f"Subject: {subject}\n\n{message}")
        print(f"Email successfully sent to - {email}")
        return "success"
    except Exception as e:
        print(e)
        return "failure"
    
@app.route('/otp1', methods=['POST'])
def otp1():
    global otp
    # global simple_email_context
    data = request.get_json()
    otp_1 = data['otp']
    print(otp_1)
    print(otp_1,otp)
    if (otp_1==otp):
        return "Success"
    else:
        return "Failure"

@app.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method == 'POST':
        session.clear()
        return "logout"
    
@app.route("/signup", methods=['POST'])
def signup():
    if request.method == 'POST':
        cur,con = dbconnect()
        data = request.get_json()
        check_email = cur.execute("SELECT email FROM users WHERE email = '{0}'".format(data['email']))
        check_email = check_email.fetchone()
        print(check_email)
        if check_email:
            return jsonify({'msg':"Email already exists",
                            'status':310})
        cur.execute("INSERT INTO users (name, email, password) VALUES (?,?,?)", (data['username'], data['email'], generate_password_hash(data['password'])))
        con.commit()
        session['email'] = data['email']
        session['name'] = data['username']
        return jsonify({'msg':"Signup successful", 'status':210})

@app.route('/contact', methods=['POST'])
def contact():
    if request.method == 'POST':
        cur, con = dbconnect()
        data = request.get_json()
        cur.execute("INSERT INTO contacts (name, email, message) VALUES (?,?,?)", (data['name'], data['email'], data['message']))
        con.commit()
        return jsonify({'msg':"Contact and Message has been received",'status':250})
    return jsonify({'msg':'Some Internal Error','status':550})
        
if __name__ == "__main__":
    app.run(debug=True)