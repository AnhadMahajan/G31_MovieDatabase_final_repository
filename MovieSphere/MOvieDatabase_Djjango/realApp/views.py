import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


FLASK_API_BASE = "http://localhost:5000"  # Change this to your Flask API base URL

def register_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role", "user")

        response = requests.post(f"{FLASK_API_BASE}/api/register", json={
            "name": name,
            "email": email,
            "password": password,
            "role": role
        })

        if response.status_code == 201:
            messages.success(request, "Registration successful! Please log in.")
            return redirect("login")
        else:
            messages.error(request, response.json().get("message", "Registration failed."))
    
    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        response = requests.post(f"{FLASK_API_BASE}/api/login", json={
            "email": email,
            "password": password
        })

        if response.status_code == 200:
            token = response.json()["access_token"]
            request.session["jwt_token"] = token
            return redirect("dashboard")  # Replace with your dashboard or home view
        else:
            messages.error(request, response.json().get("message", "Login failed."))
    
    return render(request, "login.html")





def dashboard_view(request):
    token = request.session.get("jwt_token")
    if not token:
        messages.error(request, "Please log in first.")
        return redirect("login")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{FLASK_API_BASE}/api/user", headers=headers)

    if response.status_code == 200:
        user_info = response.json()
        return render(request, "dashboard.html", {"user": user_info})
    else:
        messages.error(request, "Session expired or invalid token.")
        return redirect("login")



# def movie_list(request):
#     try:
#         response = requests.get('http://localhost:5000/api/movie')  # Flask API endpoint
#         if response.status_code == 200:
#             movies = response.json()  # This returns a list of movie dicts
#         else:
#             movies = []
#     except requests.exceptions.RequestException as e:
#         print("Error fetching movies:", e)
#         movies = []

#     return render(request, 'movie_list.html', {'movies': movies})


# views.py (in your Django app)
import requests
from django.shortcuts import render

def movie_list_view(request):
    try:
        # Change this URL if your Flask API is hosted elsewhere
        response = requests.get("http://localhost:5000/api/movie")
        response.raise_for_status()  # Raise error if not 200
        movies = response.json()
    except requests.exceptions.RequestException as e:
        print("Error fetching movies:", e)
        movies = []

    return render(request, 'movie_list.html', {'movies': movies})








def movie_detail_view(request, movie_id):
    try:
        response = requests.get(f'http://127.0.0.1:5000/api/movies/{movie_id}')
        response.raise_for_status()
        movie = response.json()
    except requests.exceptions.RequestException as e:
        print("Error fetching movie:", e)
        movie = None
    return render(request, 'movie_detail.html', {'movie': movie})



@csrf_exempt
def add_movie_view(request):
    if request.method == 'POST':
        payload = {
            "name": request.POST.get("name"),
            "description": request.POST.get("description"),
            "original_title": request.POST.get("original_title"),
            "tmdb_id": request.POST.get("tmdb_id"),
            "rating": request.POST.get("rating"),
            "vote_count": request.POST.get("vote_count"),
            "popularity": request.POST.get("popularity"),
            "image_url": request.POST.get("image_url"),
            "backdrop_url": request.POST.get("backdrop_url"),
            "release_date": request.POST.get("release_date"),
            "budget": request.POST.get("budget"),
            "revenue": request.POST.get("revenue"),
            "runtime": request.POST.get("runtime"),
            "original_language": request.POST.get("original_language")
        }
        try:
            response = requests.post('http://127.0.0.1:5000/api/movie', json=payload)
            response.raise_for_status()
            return redirect('movie_list')  # ✅ Redirect after successful add
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)
    return render(request, 'add_movie.html')

@csrf_exempt
def update_movie_view(request, movie_id):
    if request.method == 'POST':
        payload = {
            "name": request.POST.get("name"),
            "description": request.POST.get("description"),
            "original_title": request.POST.get("original_title"),
            "tmdb_id": request.POST.get("tmdb_id"),
            "rating": request.POST.get("rating"),
            "vote_count": request.POST.get("vote_count"),
            "popularity": request.POST.get("popularity"),
            "image_url": request.POST.get("image_url"),
            "backdrop_url": request.POST.get("backdrop_url"),
            "release_date": request.POST.get("release_date"),
            "budget": request.POST.get("budget"),
            "revenue": request.POST.get("revenue"),
            "runtime": request.POST.get("runtime"),
            "original_language": request.POST.get("original_language")
        }
        try:
            response = requests.put(f'http://127.0.0.1:5000/api/movies/{movie_id}', json=payload)
            response.raise_for_status()
            return redirect('movie_list')  # ✅ Redirect after update
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)



@csrf_exempt
def delete_movie_view(request, movie_id):
    if request.method == 'POST':
        try:
            response = requests.delete(f'http://127.0.0.1:5000/api/movies/{movie_id}')
            response.raise_for_status()
            return redirect('movie_list')  # ✅ Redirect after delete
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)



def update_movie_view(request, movie_id):
    movie = {}
    try:
        res = requests.get(f'http://127.0.0.1:5000/api/movies/{movie_id}')
        res.raise_for_status()
        movie = res.json()
    except requests.exceptions.RequestException:
        pass

    if request.method == 'POST':
        payload = {
            "name": request.POST.get("name"),
            "description": request.POST.get("description"),
            "original_title": request.POST.get("original_title"),
            "release_date": request.POST.get("release_date"),
            "image_url": request.POST.get("image_url")
        }
        try:
            res = requests.put(f'http://127.0.0.1:5000/api/movies/{movie_id}', json=payload)
            return redirect('movie_detail', movie_id=movie_id)
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'update_movie.html', {'movie': movie})


def movie_create(request):
    if request.method == "POST":
        form = MovieForm(request.POST)
        if form.is_valid():
            response = requests.post(f"{FLASK_API_BASE}/movies", json=form.cleaned_data)
            if response.status_code == 201:
                messages.success(request, "Movie created successfully.")
                return redirect("movie_list")
            messages.error(request, "Failed to create movie.")
    else:
        form = MovieForm()
    return render(request, "movie_form.html", {"form": form, "action": "Add"})

def movie_update(request, movie_id):
    # Fetch current data
    response = requests.get(f"{FLASK_API_BASE}/movies/{movie_id}")
    if response.status_code != 200:
        messages.error(request, "Movie not found.")
        return redirect("movie_list")

    movie_data = response.json()
    if request.method == "POST":
        form = MovieForm(request.POST)
        if form.is_valid():
            update_resp = requests.put(
                f"{FLASK_API_BASE}/movies/{movie_id}",
                json=form.cleaned_data
            )
            if update_resp.status_code == 200:
                messages.success(request, "Movie updated successfully.")
                return redirect("movie_detail", movie_id=movie_id)
            messages.error(request, "Failed to update movie.")
    else:
        form = MovieForm(initial=movie_data)
    return render(request, "movie_form.html", {"form": form, "action": "Update"})

def movie_delete(request, movie_id):
    response = requests.delete(f"{FLASK_API_BASE}/movies/{movie_id}")
    if response.status_code == 200:
        messages.success(request, "Movie deleted.")
    else:
        messages.error(request, "Failed to delete movie.")
    return redirect("movie_list")




#by anhad

def fetch_reviews(request, movie_id):
    try:
        url = f"http://127.0.0.1:5000/api/reviews/{movie_id}"
        response = requests.get(url)

        if response.status_code == 200:
            reviews = response.json()
            return render(request, 'movies/review_list.html', {
                'reviews': reviews,
                'movie_id': movie_id
            })
        else:
            return JsonResponse({'error': 'Failed to fetch reviews.'}, status=response.status_code)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)




# def director_list(request):
#     # Define the Flask API endpoint to fetch directors
#     api_url = 'http://localhost:5000/api/directors/'  # Replace with your actual Flask API URL

#     try:
#         # Make the GET request to the Flask API
#         response = requests.get(api_url)
        
#         # Check if the request was successful (status code 200)
#         if response.status_code == 200:
#             directors = response.json()  # Convert the response to JSON
#         else:
#             directors = []  # Handle case where the API request fails

#     except requests.exceptions.RequestException as e:
#         directors = []  # Handle any exceptions that occur during the request
#         print(f"Error fetching data from API: {e}")
    
#     # Render the directors data to the template
#     return render(request, 'directors_list.html', {'directors': directors})


import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings

# Flask API URLs
FLASK_API_URL = "http://127.0.0.1:5000/api/"  # Replace with your Flask API URL

# Get all directors
def get_directors(request):
    token = request.session.get("jwt_token")
    response = requests.get(f"{FLASK_API_URL}/directors")
    
    if response.status_code == 200:
        directors = response.json()
        return render(request, 'directors_list.html', {'directors': directors})
    return JsonResponse({'error': 'Failed to fetch directors from the API'}, status=400)

# Add a new director
def add_director(request):
    token = request.session.get("jwt_token")
    if request.method == 'POST':
        name = request.POST.get('name')
        if not name:
            return JsonResponse({'error': 'Director name is required.'}, status=400)
        
        data = {'name': name}
        response = requests.post(f"{FLASK_API_URL}/directors", json=data,     headers = {"Authorization": f"Bearer {token}"})

        
        if response.status_code == 201:
            return redirect('directors_list')  # Redirect to the director list page
        return JsonResponse(response.json(), status=response.status_code)

# Update a director
def update_director(request, director_id):
    token = request.session.get("jwt_token")
    if request.method == 'POST':
        name = request.POST.get('name')
        if not name:
            return JsonResponse({'error': 'Director name is required.'}, status=400)
        
        data = {'name': name}
        response = requests.put(f"{FLASK_API_URL}/directors/{director_id}", json=data,    headers = {"Authorization": f"Bearer {token}"}
)
        
        if response.status_code == 200:
            return redirect('directors_list')  # Redirect to the director list page
        return JsonResponse(response.json(), status=response.status_code)

# Delete a director
def delete_director(request, director_id):
    token = request.session.get("jwt_token")
    response = requests.delete(f"{FLASK_API_URL}/directors/{director_id}",     headers = {"Authorization": f"Bearer {token}"}
)
    
    if response.status_code == 200:
        return redirect('directors_list')  # Redirect to the director list page
    return JsonResponse(response.json(), status=response.status_code)



# FLASK_API_BASE_URL = 'http://localhost:5000/api/genre/'

def genre_list(request):
    try:
        response = requests.get('http://localhost:5000/api/genres/')
        if response.status_code == 200:
            genres = response.json()  # This returns a list of genre dicts
        else:
            genres = []
    except requests.exceptions.RequestException as e:
        print("Error fetching genres:", e)
        genres = []

    return render(request, 'genres/genre_list.html', {'genres': genres})

def genre_create(request):
    token = request.session.get("jwt_token")
    if not token:
        messages.error(request, "You must be logged in to add a genre.")
        return redirect("login")

    if request.method == 'POST':
        genre_name = request.POST.get('name')
        if not genre_name:
            messages.error(request, 'Genre name is required.')
            return redirect('genre_create')

        try:
            response = requests.post(
                'http://localhost:5000/api/genres/',
                json={"name": genre_name},
                headers={'Authorization': f'Bearer {token}'}
            )
            if response.status_code == 201:
                messages.success(request, 'Genre added successfully.')
                return redirect('genre_list')
            else:
                messages.error(request, f'Error adding genre: {response.json().get("message", "Unknown error")}')
        except requests.exceptions.RequestException as e:
            print("Error adding genre:", e)
            messages.error(request, 'An error occurred while adding the genre.')

    return render(request, 'genres/genre_create.html')


def genre_update(request, genre_id):
    if request.method == 'POST':
        genre_name = request.POST.get('name')
        if not genre_name:
            messages.error(request, 'Genre name is required.')
            return redirect('genre_update', genre_id=genre_id)

        try:
            # Make a PUT request to update the genre
            response = requests.put(
                f'{FLASK_API_BASE_URL}{genre_id}/',
                json={"name": genre_name},
                headers={'Authorization': f'Bearer {request.user.auth_token}'}
            )
            if response.status_code == 200:
                messages.success(request, 'Genre updated successfully.')
            else:
                messages.error(request, 'Error updating genre.')
        except requests.exceptions.RequestException as e:
            print("Error updating genre:", e)
            messages.error(request, 'An error occurred while updating the genre.')

        return redirect('genre_list')

    # Fetch genre details to pre-populate the form for update
    try:
        response = requests.get(f'http://localhost:5000/api/genres/{genre_id}/')
        if response.status_code == 200:
            genre = response.json()
        else:
            genre = None
    except requests.exceptions.RequestException as e:
        print("Error fetching genre:", e)
        genre = None

    return render(request, 'genres/genre_update.html', {'genre': genre})

def genre_delete(request, genre_id):
    try:
        # Make a DELETE request to delete the genre
        response = requests.delete(
            f'{http://localhost:5000/api/genres/}{genre_id}/',
            headers={'Authorization': f'Bearer {request.user.auth_token}'}
        )
        if response.status_code == 200:
            messages.success(request, 'Genre deleted successfully.')
        else:
            messages.error(request, 'Error deleting genre.')
    except requests.exceptions.RequestException as e:
        print("Error deleting genre:", e)
        messages.error(request, 'An error occurred while deleting the genre.')

    return redirect('genre_list')