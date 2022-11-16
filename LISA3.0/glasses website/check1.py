# importing modules
from flask import Flask, render_template

# declaring app name
app = Flask(__name__)

# making list of pokemons
Pokemons =["Pikachu", "Charizard", "Squirtle", "Jigglypuff",
		"Bulbasaur", "Gengar", "Charmander", "Mew", "Lugia", "Gyarados"]

# defining home page
@app.route('/')
def homepage():

# returning index.html and list
# and length of list to html page
	return render_template("check.html", len = len(Pokemons), Pokemons = Pokemons)


if __name__ == '__main__':
 
    # run() method of Flask class runs the application
    # on the local development server.
    app.run(use_reloader = True,  debug=True)
