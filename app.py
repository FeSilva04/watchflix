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

    nome = request.args.get('nome', '').strip()

    if nome:
        filmes, total_pages = buscar_filmes_por_nome(nome, page)
    else:
        filmes, total_pages = get_filmes_populares(page)

    # Limita total de páginas a 500
    if total_pages > 500:
        total_pages = 500
    if page > total_pages:
        page = total_pages

    max_next_pages = min(page + 3, total_pages + 1)

    return render_template('filmes.html',
                           filmes=filmes,
                           page=page,
                           total_pages=total_pages,
                           max_next_pages=max_next_pages)


if __name__ == '__main__':
    app.run(debug=True)
