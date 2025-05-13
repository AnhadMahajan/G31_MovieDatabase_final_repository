from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer)
    name = db.Column(db.String(200), nullable=False)
    original_title = db.Column(db.String(200))
    description = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float)
    vote_count = db.Column(db.Integer)
    popularity = db.Column(db.Float)
    image_url = db.Column(db.String(500))
    backdrop_url = db.Column(db.String(500))
    release_date = db.Column(db.Date)
    budget = db.Column(db.Integer)
    revenue = db.Column(db.Integer)
    runtime = db.Column(db.Integer)
    original_language = db.Column(db.String(10))

class Review(db.Model):
    __tablename__ = 'review'  # use double underscore here
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float, nullable=False)

    movie = db.relationship('Movie', backref=db.backref('reviews', lazy=True))

class Genre(db.Model):
    _tablename_ = 'genres'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class ProductionCompany(db.Model):
    _tablename_ = 'production_companies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    origin_country = db.Column(db.String(10))
    logo_path = db.Column(db.String(500))

class MovieGenre(db.Model):
    _tablename_ = 'movie_genre'
    movie_id = db.Column(db.Integer, primary_key=True)
    genre_id = db.Column(db.Integer, primary_key=True)

class MovieProduction(db.Model):
    _tablename_ = 'movie_production'
    movie_id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, primary_key=True)

class Cast(db.Model):
    _tablename_ = 'cast'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer)
    actor_name = db.Column(db.String(100), nullable=False)
    character_name = db.Column(db.String(200))
    profile_path = db.Column(db.String(500))
    order = db.Column(db.Integer)



class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):  # Rename method
        return check_password_hash(self.password_hash, password)






class Watchlist(db.Model):
    _tablename_ = 'watchlist'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, nullable=False)

class Book(db.Model):
    _tablename_ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(300))
    uploaded_by = db.Column(db.Integer)

class Cart(db.Model):
    _tablename_ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    book_id = db.Column(db.Integer, nullable=False)

class Order(db.Model):
    _tablename_ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    book_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50))

class Wishlist(db.Model):
    _tablename_ = 'wishlist'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    book_id = db.Column(db.Integer, nullable=False)

class Director(db.Model):
    _tablename_ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Actor(db.Model):
    _tablename_ = 'actor'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class GenreAlt(db.Model):
    _tablename_ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class MovieAlt(db.Model):
    __tablename__ = 'movie_alt'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    release_year = db.Column(db.Integer, nullable=False)
    genre_id = db.Column(db.Integer)
    director_id = db.Column(db.Integer)
    description = db.Column(db.Text)
    image = db.Column(db.String(300))

class MovieActor(db.Model):
    _tablename_ = 'movie_actor'
    movie_id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, primary_key=True)