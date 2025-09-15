from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.bulk_upload, name='bulk_upload'),
    path('pool/', views.movie_pool, name='movie_pool'),
]