import requests

API_KEY = '0621640672da05dd540952af6c06729b'
TOKEN = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwNjIxNjQwNjcyZGEwNWRkNTQwOTUyYWY2YzA2NzI5YiIsIm5iZiI6MTc0ODcwNjA0Ny45MjMsInN1YiI6IjY4M2IyMmZmZGQ2ODYyNGY0OWFkNzY5OSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.MV7w56r-S66s4EqOunQyxoFTAxprwcec1lSAOp1i-og'
BASE_URL = 'https://api.themoviedb.org/3'

def get_filmes_populares(page=1):
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=pt-BR&page={page}'
    response = requests.get(url)
    data = response.json()
    #print(data)  # DEBUG: veja o que está vindo da API

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

def get_generos():
    url = "https://api.themoviedb.org/3/genre/movie/list?language=pt-BR"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return data.get("genres", [])

def get_detalhes_filme(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {
        'api_key': API_KEY,
        'language': 'pt-BR',
        'append_to_response': 'credits,watch/providers'  # traz diretor, elenco e streamings juntos
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_trailer_filme(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/videos"
    params = {
        'api_key': API_KEY,
        'language': 'pt-BR'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        videos = response.json().get('results', [])
        for video in videos:
            if video['type'] == 'Trailer' and video['site'] == 'YouTube':
                return video['key']
    return None

def get_elenco_filme(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/credits"
    params = {
        'api_key': API_KEY,
        'language': 'pt-BR'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('cast', [])
    return []

def get_streamings_filme(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/watch/providers"
    params = {
        'api_key': API_KEY,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        # Aqui pega os dados para o Brasil ("BR"), pode adaptar para outros países
        providers = response.json().get('results', {}).get('BR', {})
        # Pode retornar os serviços de "flatrate" (streaming pago)
        return providers.get('flatrate', [])
    return []

def get_classificacao_indicativa(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/release_dates"
    params = {
        'api_key': API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()

    for item in data.get('results', []):
        if item['iso_3166_1'] == 'BR':
            for release in item['release_dates']:
                classificacao = release.get('certification')
                if classificacao:
                    return classificacao
    return 'N/A'
