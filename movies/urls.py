from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add-movies/', views.add_movies, name='add_movies'),
    path('pool/', views.movie_pool, name='movie_pool'),
]