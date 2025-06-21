from flask import Flask, render_template, request
from tmdb import get_filmes_populares

app = Flask(__name__)

@app.route('/')
def index():
    filmes_populares, _ = get_filmes_populares()
    return render_template('index.html', filmes_populares=filmes_populares)

@app.route('/filmes')
def filmes():
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    filmes_populares, total_pages = get_filmes_populares(page)

    # Limita página ao máximo permitido pela API
    if page > total_pages:
        page = total_pages

    max_next_pages = min(page + 3, total_pages + 1)

    return render_template('filmes.html',
                           filmes=filmes_populares,
                           page=page,
                           total_pages=total_pages,
                           max_next_pages=max_next_pages)


if __name__ == '__main__':
    app.run(debug=True)
