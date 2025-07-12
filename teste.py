import requests

API_KEY = '0621640672da05dd540952af6c06729b'
TOKEN = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwNjIxNjQwNjcyZGEwNWRkNTQwOTUyYWY2YzA2NzI5YiIsIm5iZiI6MTc0ODcwNjA0Ny45MjMsInN1YiI6IjY4M2IyMmZmZGQ2ODYyNGY0OWFkNzY5OSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.MV7w56r-S66s4EqOunQyxoFTAxprwcec1lSAOp1i-og'
BASE_URL = 'https://api.themoviedb.org/3'

def get_classificacao_indicativa_filme(movie_id):
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
    
series, total_pages = get_series_populares(1)
print(f"Total de páginas: {total_pages}")
print(f"Primeira série retornada: {series[0] if series else 'Nenhuma série encontrada'}")