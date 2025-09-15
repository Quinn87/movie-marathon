from django.db import models

# Create your models here.
class Movie(models.Model):
    title = models.CharField(max_length=200)
    release_year = models.IntegerField()
    genre = models.CharField(max_length=100)
    is_watched = models.BooleanField(default=False)
    is_available = models.BooleanField(default=False)
    rating = models.IntegerField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def get_last_watched_year(self):
        last_watched = self.schedule_set.filter(watched_year__isnull=False).order_by('-watched_year').first()
        if last_watched:
            return last_watched.date.year
        return None

    def __str__(self):
        return self.title

class Schedule(models.Model):
    date = models.DateField(unique=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    watched_year = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.date} - {self.movie.title}"