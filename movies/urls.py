from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('pool/', views.movie_pool, name='movie_pool'),
    path('add-movies/', views.add_movies, name='add_movies'),
    path('generate-schedule/', views.generate_schedule, name='generate_schedule'),
    path('mark_watched', views.mark_watched, name='mark_watched'),
]