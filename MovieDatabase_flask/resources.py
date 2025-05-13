from flask import request
from flask_restful import Resource
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from flask_restful import Resource, reqparse
from models import db, User, Movie, Cart, Order, Review, Genre, Director, Actor, MovieActor,MovieAlt
from flask import url_for
from datetime import datetime


jwt = JWTManager()

# ===== User Registration =====
# ===== User Registration =====
class UserRegisterResource(Resource):
    def post(self):
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        name = data.get("name")  # Changed from username
        email = data.get("email")
        password = data.get("password")
        role = data.get("role", "user")

        if not all([name, email, password]):
            return {"message": "Name, email and password are required."}, 400

        if User.query.filter_by(email=email).first():
            return {"message": "Email already exists."}, 400

        user = User(name=name, email=email, role=role)
        user.set_password(password)  # Changed method name

        db.session.add(user)
        db.session.commit()
        return {"message": "User registered successfully."}, 201

class UserLoginResource(Resource):
    def post(self):
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return {"message": "Email and password required"}, 400

        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):  # Use renamed method
            token = create_access_token(identity=str(user.id))
            return {"access_token": token}, 200
            
        return {"message": "Invalid credentials"}, 401





class UserInfoResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        return {
            "id": user.id,
            "name": user.name,  # Return correct field name
            "email": user.email,
            "role": user.role
        }, 200



# ===== CART RESOURCE =====
class CartResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        cart_items = Cart.query.filter_by(user_id=user_id).all()
        return [{
            "cart_id": item.id,
            "movie_id": item.movie_id,
            "movie_title": item.movie.title  # Updated to reflect Movie model
        } for item in cart_items], 200

    @jwt_required()
    def post(self):
        data = request.get_json()
        user_id = get_jwt_identity()
        movie_id = data.get("movie_id")

        if not movie_id:
            return {"message": "Movie ID is required."}, 400

        item = Cart(user_id=user_id, movie_id=movie_id)
        db.session.add(item)
        db.session.commit()
        return {"message": "Movie added to cart."}, 201

    @jwt_required()
    def delete(self):
        user_id = get_jwt_identity()
        data = request.get_json()
        movie_id = data.get("movie_id")

        item = Cart.query.filter_by(user_id=user_id, movie_id=movie_id).first()
        if item:
            db.session.delete(item)
            db.session.commit()
            return {"message": "Item removed from cart."}, 200
        return {"message": "Item not found in cart."}, 404


# ===== ORDER RESOURCE =====
class OrderResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        orders = Order.query.filter_by(user_id=user_id).all()
        return [{
            "order_id": order.id,
            "movie_id": order.movie_id,
            "movie_title": order.movie.title,  # Updated to reflect Movie model
            "status": order.status
        } for order in orders], 200

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        data = request.get_json()
        movie_id = data.get("movie_id")

        if not movie_id:
            return {"message": "Movie ID is required."}, 400

        order = Order(user_id=user_id, movie_id=movie_id)
        db.session.add(order)
        db.session.commit()
        return {"message": "Order placed successfully."}, 201

    @jwt_required()
    def put(self):
        user_id = get_jwt_identity()
        data = request.get_json()
        order_id = data.get("order_id")
        new_status = data.get("status")

        order = Order.query.filter_by(id=order_id, user_id=user_id).first()
        if not order:
            return {"message": "Order not found."}, 404

        order.status = new_status
        db.session.commit()
        return {"message": "Order status updated."}, 200


from flask import request, url_for
from flask_restful import Resource, reqparse
from datetime import datetime
from models import db, Movie,Review
from werkzeug.utils import secure_filename
import os

# Allowed file extensions for image uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check if a file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to save uploaded files
def save_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return filename  # Return only the filename
    return None

    
def extract_filename(image_url):
    if not image_url:
        return None
    return os.path.basename(image_url.replace('\\', '/'))





# Function to return the full URL of the image based on the filename
def build_image_url(filename):
    if not filename:
        return None
    return f"http://127.0.0.1:5000/uploads/{filename}"



def movie_to_dict(movie):
    image_filename = extract_filename(movie.image_url)
    backdrop_filename = extract_filename(movie.backdrop_url)

    return {
        "id": movie.id,
        "tmdb_id": movie.tmdb_id,
        "name": movie.name,
        "original_title": movie.original_title,
        "description": movie.description,
        "rating": movie.rating,
        "vote_count": movie.vote_count,
        "popularity": movie.popularity,
        "image_url": build_image_url(image_filename),
        "backdrop_url": build_image_url(backdrop_filename),
        "release_date": movie.release_date.isoformat() if movie.release_date else None,
        "budget": movie.budget,
        "revenue": movie.revenue,
        "runtime": movie.runtime,
        "original_language": movie.original_language
    }


# Update your movie_parser to allow file input
movie_parser = reqparse.RequestParser()
movie_parser.add_argument('tmdb_id', type=int)
movie_parser.add_argument('name', type=str, required=True, help='Name is required')
movie_parser.add_argument('original_title', type=str)
movie_parser.add_argument('description', type=str, required=True, help='Description is required')
movie_parser.add_argument('rating', type=float)
movie_parser.add_argument('vote_count', type=int)
movie_parser.add_argument('popularity', type=float)
movie_parser.add_argument('image', type=str)
movie_parser.add_argument('backdrop', type=str)
movie_parser.add_argument('release_date', type=str)
movie_parser.add_argument('budget', type=int)
movie_parser.add_argument('revenue', type=int)
movie_parser.add_argument('runtime', type=int)
movie_parser.add_argument('original_language', type=str)

# Movie Resource
class MovieResource(Resource):
    def get(self, movie_id=None):
        if movie_id:
            movie = Movie.query.get(movie_id)
            if not movie:
                return {"message": "Movie not found"}, 404
            return movie_to_dict(movie), 200
        movies = Movie.query.all()
        return [movie_to_dict(m) for m in movies], 200

    def post(self):
        args = movie_parser.parse_args()

        image_filename = None
        backdrop_filename = None

        if 'image' in request.files:
            image_file = request.files['image']
            image_filename = save_file(image_file)

        if 'backdrop' in request.files:
            backdrop_file = request.files['backdrop']
            backdrop_filename = save_file(backdrop_file)

        movie = Movie(
            tmdb_id=args['tmdb_id'],
            name=args['name'],
            original_title=args['original_title'],
            description=args['description'],
            rating=args['rating'],
            vote_count=args['vote_count'],
            popularity=args['popularity'],
            image_url=image_filename,
            backdrop_url=backdrop_filename,
            release_date=datetime.strptime(args['release_date'], '%Y-%m-%d') if args['release_date'] else None,
            budget=args['budget'],
            revenue=args['revenue'],
            runtime=args['runtime'],
            original_language=args['original_language']
        )
        db.session.add(movie)
        db.session.commit()
        return {"message": "Movie created", "movie": movie_to_dict(movie)}, 201

    def put(self, movie_id):
        movie = Movie.query.get(movie_id)
        if not movie:
            return {"message": "Movie not found"}, 404

        args = movie_parser.parse_args()

        if 'image' in request.files:
            image_file = request.files['image']
            movie.image_url = save_file(image_file)

        if 'backdrop' in request.files:
            backdrop_file = request.files['backdrop']
            movie.backdrop_url = save_file(backdrop_file)

        for field, value in args.items():
            if value is not None:
                if field == 'release_date' and value:
                    setattr(movie, field, datetime.strptime(value, '%Y-%m-%d'))
                else:
                    setattr(movie, field, value)

        db.session.commit()
        return {"message": "Movie updated", "movie": movie_to_dict(movie)}, 200

    def delete(self, movie_id):
        movie = Movie.query.get(movie_id)
        if not movie:
            return {"message": "Movie not found"}, 404

        db.session.delete(movie)
        db.session.commit()
        return {"message": "Movie deleted"}, 200



from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from flask_restful import Resource

class ReviewResource(Resource):
    def get(self, movie_id):
        reviews = Review.query.filter_by(movie_id=movie_id).all()
        return [{
            "review_id": r.id,
            "comment": r.comment,
            "rating": r.rating
        } for r in reviews], 200

    @jwt_required()
    def post(self, movie_id):
        data = request.get_json()
        print("Received data:", data)  # Log incoming data for debugging
        
        comment = data.get("comment")
        rating = data.get("rating")

        if not comment or rating is None:
            print("Missing comment or rating")  # Additional debug log
            return {"message": "Comment and rating are required."}, 400

        review = Review(movie_id=movie_id, comment=comment, rating=rating)
        db.session.add(review)
        db.session.commit()
        print(f"Review added: {review}")  # Log added review for debugging
        return {"message": "Review added."}, 201





# ===== Director Resource =====
class DirectorResource(Resource):
    def get(self):
        directors = Director.query.all()
        return [{
            "id": director.id,
            "name": director.name
        } for director in directors], 200

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if user.role != 'admin':
            return {"message": "Only admins can add directors."}, 403

        data = request.get_json()
        name = data.get("name")

        if not name:
            return {"message": "Director name is required."}, 400

        director = Director(name=name)
        db.session.add(director)
        db.session.commit()
        return {"message": "Director added successfully."}, 201

    @jwt_required()
    def put(self, director_id):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if user.role != 'admin':
            return {"message": "Only admins can update directors."}, 403

        director = Director.query.get(director_id)
        if not director:
            return {"message": "Director not found."}, 404

        data = request.get_json()
        director.name = data.get("name", director.name)
        db.session.commit()
        return {"message": "Director updated successfully."}, 200

    @jwt_required()
    def delete(self, director_id):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if user.role != 'admin':
            return {"message": "Only admins can delete directors."}, 403

        director = Director.query.get(director_id)
        if not director:
            return {"message": "Director not found."}, 404

        db.session.delete(director)
        db.session.commit()
        return {"message": "Director deleted successfully."}, 200





class GenreResource(Resource):
    def get(self):
        genres = Genre.query.all()
        return [{
            "id": genre.id,
            "name": genre.name
        } for genre in genres], 200

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if user.role != 'admin':
            return {"message": "Only admins can add genres."}, 403

        data = request.get_json()
        name = data.get("name")

        if not name:
            return {"message": "Genre name is required."}, 400

        genre = Genre(name=name)
        db.session.add(genre)
        db.session.commit()
        return {"message": "Genre added successfully."}, 201

    @jwt_required()
    def put(self, genre_id):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if user.role != 'admin':
            return {"message": "Only admins can update genres."}, 403

        genre = Genre.query.get(genre_id)
        if not genre:
            return {"message": "Genre not found."}, 404

        data = request.get_json()
        genre.name = data.get("name", genre.name)
        db.session.commit()
        return {"message": "Genre updated successfully."}, 200

    @jwt_required()
    def delete(self, genre_id):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if user.role != 'admin':
            return {"message": "Only admins can delete genres."}, 403

        genre = Genre.query.get(genre_id)
        if not genre:
            return {"message": "Genre not found."}, 404

        db.session.delete(genre)
        db.session.commit()
        return {"message": "Genre deleted successfully."}, 200





# Update MovieManagementResource
class MovieManagementResource(Resource):
    @jwt_required()
    def put(self, movie_id):
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'admin':
            return {"message": "Only admins can update movies."}, 403

        movie = MovieAlt.query.get(movie_id)
        if not movie:
            return {"message": "Movie not found."}, 404

        movie.title = data.get("title", movie.title)
        movie.release_year = data.get("release_year", movie.release_year)
        movie.genre_id = data.get("genre_id", movie.genre_id)
        movie.director_id = data.get("director_id", movie.director_id)
        movie.description = data.get("description", movie.description)
        movie.image = data.get("image", movie.image)
        
        db.session.commit()
        return {"message": "Movie updated successfully."}, 200

    @jwt_required()
    def delete(self, movie_id):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'admin':
            return {"message": "Only admins can delete movies."}, 403

        movie = MovieAlt.query.get(movie_id)
        if not movie:
            return {"message": "Movie not found."}, 404
            
        db.session.delete(movie)
        db.session.commit()
        return {"message": "Movie deleted successfully."}, 200




class MovieListResource(Resource):
    def get(self):
        movies = MovieAlt.query.all()
        result = [{
            "id": movie.id,
            "title": movie.title,
            "release_year": movie.release_year,
            "genre_id": movie.genre_id,
            "director_id": movie.director_id,
            "description": movie.description,
            "image": url_for('static', filename='images/' + movie.image, _external=True)
            if movie.image else None
        } for movie in movies]
        return {"movies": result}, 200

class MovieDetailResource(Resource):
    def get(self, movie_id):
        movie = MovieAlt.query.get(movie_id)
        if not movie:
            return {"message": "Movie not found."}, 404

        result = {
            "id": movie.id,
            "title": movie.title,
            "release_year": movie.release_year,
            "genre_id": movie.genre_id,
            "director_id": movie.director_id,
            "description": movie.description,
            "image": movie.image
        }
        return result, 200



