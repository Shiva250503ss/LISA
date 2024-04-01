from flask import Flask,render_template,request,flash

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/live", methods=['GET','POST'])
def live():
    return render_template("live.html")

@app.route("/home",methods=['GET','POST'])
def home():
    return render_template("index.html")

if __name__ == '__main__':
 
    # run() method of Flask class runs the application
    # on the local development server.
    app.run(use_reloader = True,  debug=True)