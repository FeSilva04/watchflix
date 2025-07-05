import requests

url = "https://api.themoviedb.org/3/movie/popular?language=pt-BR&page=1"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwNjIxNjQwNjcyZGEwNWRkNTQwOTUyYWY2YzA2NzI5YiIsIm5iZiI6MTc0ODcwNjA0Ny45MjMsInN1YiI6IjY4M2IyMmZmZGQ2ODYyNGY0OWFkNzY5OSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.MV7w56r-S66s4EqOunQyxoFTAxprwcec1lSAOp1i-og"
}

response = requests.get(url, headers=headers)

print(response.text)