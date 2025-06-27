from flask import Flask, render_template, request
from tmdb import get_filmes_populares, buscar_filmes_por_nome, buscar_filmes_por_filtros
from urllib.parse import urlencode

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
    genero = request.args.get('genero', '').strip()
    nota_min = request.args.get('nota_min', '').strip()
    duracao_min = request.args.get('duracao_min', '').strip()

    # Decide qual função da API usar
    if nome:
        filmes, total_pages = buscar_filmes_por_nome(nome, page)
    else:
        filmes, total_pages = buscar_filmes_por_filtros(page, genero, nota_min, duracao_min)
        # filmes, total_pages = get_filmes_populares(page)

    # Limita total de páginas a 500
    if total_pages > 500:
        total_pages = 500
    
    # Corrige se usuário tentar acessar página acima do limite
    if page > total_pages:
        page = total_pages
        if nome:
            filmes, _ = buscar_filmes_por_nome(nome, page)
        else:
            filmes, _ = get_filmes_populares(page)

    # Garante que 'filmes' seja uma lista
    if not filmes:
        filmes = []

    # Montar URLs da paginação mantendo filtros
    args = request.args.to_dict()
    args.pop('page', None)  # Remove o parâmetro 'page' atual para substituir depois
    def build_url(page_num):
        args['page'] = page_num
        return '/filmes?' + urlencode(args)

    return render_template('filmes.html',
                           filmes=filmes,
                           page=page,
                           total_pages=total_pages,
                           build_url=build_url)


if __name__ == '__main__':
    app.run(debug=True)
