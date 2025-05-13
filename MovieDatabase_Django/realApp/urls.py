from django.urls import path
from . import views
from .views import genre_list, genre_create, genre_update, genre_delete, fetch_reviews

urlpatterns = [

    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('', views.dashboard_view, name='dashboard'),

    path("logout/", views.logout_view, name="logout"),
    path('movies/', views.movie_list_view, name='movie_list'),

    path('movie/<int:movie_id>/', views.movie_detail_view, name='movie_detail'),
    path('add/', views.add_movie_view, name='add_movie'),
    path('update/<int:movie_id>/', views.update_movie_view, name='update_movie'),
    path('delete/<int:movie_id>/', views.delete_movie_view, name='delete_movie'),


    path('movies/create/', views.movie_create, name='movie_create'),
    path('movies/<int:movie_id>/update/', views.movie_update, name='movie_update'),
    path('movies/<int:movie_id>/delete/', views.movie_delete, name='movie_delete'),
    path('movie/<int:movie_id>/reviews/', views.fetch_reviews, name='fetch_reviews'),
    path('genres/', genre_list, name='genre_list'),
    path('genres/create/', genre_create, name='genre_create'),
    path('genres/<int:genre_id>/update/', genre_update, name='genre_update'),
    path('genres/<int:genre_id>/delete/', genre_delete, name='genre_delete'),
    path('reviews/<int:movie_id>/', fetch_reviews, name='review_list'),
    path('directors/', views.get_directors, name='directors_list'),
    path('directors/add/', views.add_director, name='add_director'),
    path('directors/update/<int:director_id>/', views.update_director, name='update_director'),
    path('directors/delete/<int:director_id>/', views.delete_director, name='delete_director'),
]