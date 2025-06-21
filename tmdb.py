import requests

API_KEY = '0621640672da05dd540952af6c06729b'

def get_filmes_populares(page=1):
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=pt-BR&page={page}"
    response = requests.get(url)
    return response.json()['results']