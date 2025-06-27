import requests

API_KEY = '0621640672da05dd540952af6c06729b'

def get_filmes_populares(page=1):
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=pt-BR&page={page}'
    response = requests.get(url)
    data = response.json()

    # Limitar total_pages a 500, pois é o número máximo permitido pela API    
    total_pages = data.get('total_pages', 1)
    if total_pages > 500:
        total_pages = 500

    return data['results'], total_pages

def buscar_filmes_por_nome(nome, page=1):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&language=pt-BR&query={nome}&page={page}"
    response = requests.get(url)
    data = response.json()

    total_pages = data.get('total_pages', 1)
    if total_pages > 500:
        total_pages = 500

    return data['results'], total_pages

def buscar_filmes_por_filtros(page, genero=None, nota_min=None, duracao_min=None):
    url = f"https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": API_KEY,
        "language": "pt-BR",
        "sort_by": "popularity.desc",
        "page": page,
        "with_genres": genero,
        "vote_average.gte": nota_min,
        "with_runtime.gte": duracao_min
    }

    # Remove filtros vazios
    params = {k: v for k, v in params.items() if v}

    response = requests.get(url, params=params)
    data = response.json()

    return data.get('results', []), data.get('total_pages', 1)


