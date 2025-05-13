from django.db import models

class Movie(models.Model):
    tmdb_id = models.IntegerField()
    name = models.CharField(max_length=200)
    original_title = models.CharField(max_length=200)
    description = models.TextField()
    rating = models.FloatField()
    vote_count = models.IntegerField()
    popularity = models.FloatField()
    image_url = models.URLField()
    backdrop_url = models.URLField()
    release_date = models.DateField(null=True, blank=True)
    budget = models.BigIntegerField()
    revenue = models.BigIntegerField()
    runtime = models.IntegerField()
    original_language = models.CharField(max_length=50)

    def __str__(self):
        return self.name
