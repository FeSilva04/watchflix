from flask import Flask, render_template, request
from tmdb import get_filmes_populares

app = Flask(__name__)

@app.route('/filmes')
def filmes():
    page = request.args.get('page', 1)
    filmes_populares = get_filmes_populares(page)
    return render_template('filmes.html', filmes=filmes_populares)

if __name__ == '__main__':
    app.run(debug=True)
