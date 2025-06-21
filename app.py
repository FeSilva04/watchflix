from flask import Flask, render_template
from tmdb import get_filmes_populares

app = Flask(__name__)

@app.route('/')
def index():
    filmes_populares = get_filmes_populares()
    return render_template('index.html', filmes_populares=filmes_populares)

if __name__ == '__main__':
    app.run(debug=True)
