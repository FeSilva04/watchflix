import requests

API_KEY = '0621640672da05dd540952af6c06729b'

def get_filmes_populares():
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=pt-BR"
    response = requests.get(url)
    return response.json()['results']
