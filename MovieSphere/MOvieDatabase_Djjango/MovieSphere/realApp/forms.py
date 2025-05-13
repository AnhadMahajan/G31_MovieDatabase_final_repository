from django import forms

class MovieForm(forms.Form):
    tmdb_id = forms.IntegerField()
    name = forms.CharField(max_length=100)
    original_title = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    rating = forms.FloatField()
    vote_count = forms.IntegerField()
    popularity = forms.FloatField()
    image_url = forms.URLField()
    backdrop_url = forms.URLField()
    release_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    budget = forms.IntegerField(required=False)
    revenue = forms.IntegerField(required=False)
    runtime = forms.IntegerField()
    original_language = forms.CharField(max_length=10)



from django import forms
from .models import Movie

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = [
            'tmdb_id', 'name', 'original_title', 'description', 'rating',
            'vote_count', 'popularity', 'image_url', 'backdrop_url',
            'release_date', 'budget', 'revenue', 'runtime', 'original_language'
        ]
