from django import forms
from .models import Movie

class MovieUploadForm(forms.Form):
    movie_list_csv = forms.FileField()

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'release_year', 'genre', 'is_available', 'rating', 'notes']