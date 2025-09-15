import csv
import io
from django.shortcuts import render, redirect
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