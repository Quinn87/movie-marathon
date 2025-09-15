from django import forms

class MovieUploadForm(forms.Form):
    movie_list_csv = forms.FileField()