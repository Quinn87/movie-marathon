import csv
import io
import random
import json
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages #Used for displaying success/error messages
from .models import Movie, Schedule
from .forms import MovieUploadForm, MovieForm

# Create your views here.
def home(request):
    #Fetch the movies scheduled for October of the current year
    october_schedule = Schedule.objects.filter(
        date__month=10,
        date__year=2025 #You will need to update this each year or make it dynamic
    ).order_by('date')

    #Organize the data to send to the template
    context = {'october_schedule': october_schedule,}

    #Render the HTML template, passing the data
    return render(request, 'movies/home.html', context)

def add_movies(request):
    upload_form = MovieUploadForm()  # Initialize forms for both GET and POST
    single_movie_form = MovieForm()
    
    if request.method == 'POST':
        # Check if the single movie form was submitted
        if 'add_single_movie' in request.POST:
            single_movie_form = MovieForm(request.POST)
            if single_movie_form.is_valid():
                single_movie_form.save()
                messages.success(request, f"Successfully added {single_movie_form.cleaned_data['title']}!")
                return redirect('add_movies')
        
        # Check if the bulk upload form was submitted
        elif 'upload_csv' in request.POST:
            upload_form = MovieUploadForm(request.POST, request.FILES)
            if upload_form.is_valid():
                csv_file = request.FILES['movie_list_csv']
                file_data = csv_file.read().decode("utf-8")
                io_string = io.StringIO(file_data)
                reader = csv.reader(io_string)
                next(reader)
                
                movies_to_create = []
                for row in reader:
                    title, release_year, genre = row
                    movies_to_create.append(
                        Movie(
                            title=title.strip(),
                            release_year=int(release_year),
                            genre=genre.strip()
                        )
                    )
                
                Movie.objects.bulk_create(movies_to_create)
                messages.success(request, f"Successfully uploaded {len(movies_to_create)} movies!")
                return redirect('add_movies')
    
    context = {
        'single_movie_form': single_movie_form,
        'upload_form': upload_form,
    }
    return render(request, 'movies/add_movies.html', context)

def movie_pool(request):
    query = request.GET.get('q')
    if query:
        # Filter movies by title, genre, or release year (using __icontains for case-insensitive search)
        movie_list = Movie.objects.filter(
            title__icontains=query
        ).order_by('title')
        if not movie_list:
            # If no titles match, try searching other fields
            movie_list = Movie.objects.filter(
                genre__icontains=query
            ).order_by('title')
        if not movie_list and query.isdigit():
            # If still no matches, try searching by release year
            movie_list = Movie.objects.filter(
                release_year=int(query)
            ).order_by('title')
    else:
        # If no query is provided, show all movies
        movie_list = Movie.objects.all().order_by('title')

    context = {
        'movie_list': movie_list,
    }
    return render(request, 'movies/movie_pool.html', context)

def generate_schedule(request):
    if request.method == 'POST':
        # Get the JSON string from the hidden input field
        selected_movies_json = request.POST.get('movies', '[]')
        
        # Parse the JSON string into a Python list
        try:
            selected_movie_ids = json.loads(selected_movies_json)
        except json.JSONDecodeError:
            messages.error(request, "Invalid movie selection data.")
            return redirect('movie_pool')

        if not selected_movie_ids:
            messages.error(request, "Please select at least one movie to schedule.")
            return redirect('movie_pool')

        # Get the movies from the database
        movies_to_schedule = list(Movie.objects.filter(id__in=selected_movie_ids))

        # ... rest of the code is the same ...
        random.shuffle(movies_to_schedule)
        
        current_year = date.today().year
        october_start = date(current_year, 10, 1)

        Schedule.objects.filter(date__year=current_year, date__month=10).delete()
        
        for i, movie in enumerate(movies_to_schedule):
            if i >= 31:
                break
                
            schedule_date = october_start + timedelta(days=i)
            
            Schedule.objects.create(
                movie=movie,
                date=schedule_date
            )
        
        messages.success(request, "Your October schedule has been successfully generated!")
        return redirect('home')

    return redirect('movie_pool')

@require_POST
def mark_watched(request):
    schedule_id = request.POST.get('schedule_id')
    is_watched = request.POST.get('watched')

    schedule_entry = get_object_or_404(Schedule, id=schedule_id)
    
    if is_watched:
        schedule_entry.watched_year = date.today().year
        schedule_entry.save()
        
        # Update the is_watched status on the related Movie object
        schedule_entry.movie.is_watched = True
        schedule_entry.movie.save()
    else:
        schedule_entry.watched_year = None
        schedule_entry.save()
        
        # Update the is_watched status on the related Movie object
        schedule_entry.movie.is_watched = False
        schedule_entry.movie.save()
        
    return redirect('home')