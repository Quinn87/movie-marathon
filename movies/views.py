import csv
import io
import random
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
    if request.method == 'POST':
        #Check if the single movie form was submitted
        if 'add_single_movie' in request.POST:
            single_movie_form = MovieForm(request.POST)
            if single_movie_form.is_valid():
                single_movie_form.save()
                messages.success(request, f"Successfully added {single_movie_form.cleaned_data['title']}!")
                return redirect('add_movies') #Redirect to the same page to show the success message

        #Check if the bulk upload form was submitted    
        elif 'upload_csv' in request.POST:
            upload_form = MovieUploadForm(request.POST, request.FILES)
            if upload_form.is_valid():
                csv_file = request.FILES['movie_list_csv']
                #Decode the uploaded file from bytes to a string
                file_data = csv_file.read().decode("utf-8")
                #Create an in-memory file object
                io_string = io.StringIO(file_data)
                #Use csv.render to parse the data
                reader = csv.reader(io_string)
                next(reader)

                movies_to_create = []
                for row in reader:
                    #Assuming CSV columns are: title, release_year, genre
                    title, release_year, genre = row
                    movies_to_create.append(
                        Movie(
                            title=title.strip(),
                            release_year=int(release_year),
                            genre=genre.strip()
                        )
                    )

                #Bulk create movies for efficiency
                Movie.objects.bulk_create(movies_to_create)
                messages.success(request, f"Successfully uploaded {len(movies_to_create)} movies!")
                return redirect('home') #redirect to home page after upload
    else:
        #If it's a GET request, create an empty form
        single_movie_form = MovieForm()
        upload_form = MovieUploadForm()
        
    context = {
        'single_movie_form': single_movie_form,
        'upload_form': upload_form,
    }
    return render(request, 'movies/bulk_upload.html', {'form': form})

def movie_pool(request):
    movie_list = Movie.objects.all().order_by('title')
    return render(request, 'movies/movie_pool.html', {'movie_list': movie_list})

def generate_schedule(request):
    if request.method == 'POST':
        selected_movie_ids = request.POST.getlist('movies')

        if not selected_movie_ids:
            messages.error(request, "Please select at lease one movie to schedule.")
            return redirect('movie_pool')
        
        #Get the movies from the database
        movies_to_schedule = list(Movie.objects.filter(id__in=selected_movie_ids))

        #Shuffle the list randomly
        random.shuffle(movies_to_schedule)

        #Get the current year and the start of October
        current_year = date.today().year
        october_start = date(current_year, 10, 1)

        #Clear any existing schedule for current year's October
        Schedule.objects.filter(date__year=current_year, date__month=10).delete()

        #Create a new schedule
        for i, movie in enumerate(movies_to_schedule):
            #If the number of selected movies exceeds the days in October, stop
            if i>=31:
                break

            schedule_date = october_start + timedelta(days=i)

            #Create the schedule entry
            Schedule.objects.create(
                movie=movie,
                date=schedule_date
            )

        messages.success(request, "Your October schedulke has been successfully generated!")
        return redirect('home')
    
    #if the user tries to access this page with a GET request, redirect them
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