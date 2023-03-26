from flask import *
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

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
