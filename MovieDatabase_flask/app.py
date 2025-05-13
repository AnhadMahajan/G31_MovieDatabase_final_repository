from flask import Flask, jsonify, render_template, request, flash, redirect, url_for, send_from_directory, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, UserMixin, login_required, current_user
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_cors import CORS
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

import os
import sqlite3
from datetime import datetime

# Local imports
from models import db, Movie, Genre, ProductionCompany, MovieGenre, MovieProduction, Cast, Book, User ,Review
from resources import (
    UserRegisterResource,
    UserLoginResource,
    CartResource,
    OrderResource,
    ReviewResource,
    MovieResource,
    DirectorResource,
    GenreResource,
    MovieListResource,
    MovieDetailResource,
    MovieManagementResource,
    UserInfoResource
)

# --------------------------------------
# App & Config Setup
# --------------------------------------
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:8000"}})

basedir = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "movies.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "YourSecretKey"
app.config['JWT_SECRET_KEY'] = 'super-secret'

# Upload folder for images
UPLOAD_FOLDER = os.path.join(basedir, 'static/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# --------------------------------------
# Extensions Initialization
# --------------------------------------
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
jwt = JWTManager(app)
api = Api(app)
migrate = Migrate(app, db)

# --------------------------------------
# File Upload Helpers
# --------------------------------------

import os





def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return filename  # Return only the filename
    return None




# Route to serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



# --------------------------------------
# User Loader (Flask-Login)
# --------------------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --------------------------------------
# Raw SQLite Connection (Optional)
# --------------------------------------
def get_db_connection():
    conn = sqlite3.connect(os.path.join(basedir, "movies.db"))
    conn.row_factory = sqlite3.Row
    return conn

# --------------------------------------
# API Resources Registration
# --------------------------------------
api.add_resource(UserRegisterResource, '/api/register')
api.add_resource(UserLoginResource, '/api/login')
api.add_resource(CartResource, '/api/cart')
api.add_resource(OrderResource, '/api/order')

# Movie endpoints
api.add_resource(MovieResource, '/api/movie', '/api/movies/<int:movie_id>')
api.add_resource(MovieListResource, '/api/movies')
api.add_resource(MovieDetailResource, '/api/movies/<int:movie_id>')
api.add_resource(MovieManagementResource, '/api/movies/manage', '/api/movies/manage/<int:movie_id>')

# Other endpoints
api.add_resource(ReviewResource, '/api/movies/<int:movie_id>/reviews')
api.add_resource(DirectorResource, '/api/directors', '/api/directors/<int:director_id>')
api.add_resource(GenreResource, '/api/genres', '/api/genres/<int:genre_id>')
api.add_resource(UserInfoResource, '/api/user')



@app.route('/movies')
def movie_index():
    movies = Movie.query.all()
    return render_template('movies.html',movies=movies)

@app.route('/movies/<int:movie_id>', methods=['GET'])
def movie_detail(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    reviews = Review.query.filter_by(movie_id=movie_id).all()
    return render_template('movie_details.html', movie=movie, reviews=reviews)

@app.route('/movies/<int:movie_id>/review', methods=['POST'])
def add_review(movie_id):
    comment = request.form.get('comment')
    rating = request.form.get('rating')

    if not comment or not rating:
        return jsonify({'error': 'Comment and rating are required'}), 400

    review = Review(movie_id=movie_id, comment=comment, rating=float(rating))
    db.session.add(review)
    db.session.commit()

    return redirect(url_for('movie_detail', movie_id=movie_id))




# --------------------------------------
# Basic API Routes Using Raw SQL (Optional)
# --------------------------------------
@app.route('/api/movie_tmdb', methods=['GET'])
def get_movies():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        if not tables:
            return jsonify({'error': 'No tables found in database'}), 404
        table_name = tables[0][0]
        rows = conn.execute(f'SELECT * FROM {table_name}').fetchall()
        conn.close()
        results = [dict(row) for row in rows]
        return jsonify({'status': 'success', 'data': results, 'count': len(results)})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        if not tables:
            return jsonify({'error': 'No tables found in database'}), 404
        table_name = tables[0][0]
        movie = conn.execute(f'SELECT * FROM {table_name} WHERE id = ?', (movie_id,)).fetchone()
        conn.close()
        if not movie:
            return jsonify({'status': 'error', 'message': 'Movie not found'}), 404
        return jsonify({'status': 'success', 'data': dict(movie)})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500






@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('user_dashboard' if current_user.role != 'admin' else 'admin_dashboard'))

    reg_form = RegistrationForm(prefix="reg")
    login_form = LoginForm(prefix="log")

    if request.method == "POST":
        if "reg-submit" in request.form and reg_form.validate_on_submit():
            if User.query.filter_by(email=reg_form.email.data).first():
                flash("Email already exists!", "danger")
                return redirect(url_for("signup"))

            new_user = User(
                name=reg_form.name.data,
                email=reg_form.email.data,
                role="user"
            )
            new_user.set_password(reg_form.password.data)  # Hash password
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for('signup'))

        elif "log-submit" in request.form and login_form.validate_on_submit():
            user = User.query.filter_by(email=login_form.email.data).first()
            if user and user.check_password(login_form.password.data):  # Verify hashed password
                login_user(user)
                return redirect(url_for('user_dashboard' if user.role != 'admin' else 'admin_dashboard'))

            flash("Login unsuccessful. Please check your credentials.", "danger")

    return render_template("signup.html", reg_form=reg_form, login_form=login_form)

@app.route('/my_wishlist')
def my_wishlist():
    return render_template('my_wishlist.html')





@app.route('/movie/<int:movie_id>', methods=['GET', 'POST'])
def movie_details(movie_id):
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
    movie = cursor.fetchone()
    
    if request.method == 'POST':
        if 'comment' in request.form and 'rating' in request.form:
            comment = request.form['comment']
            rating = float(request.form['rating'])
            new_review = Review(movie_id=movie_id, comment=comment, rating=rating)
            db.session.add(new_review)
            db.session.commit()
        elif 'watchlist' in request.form:
            if not Watchlist.query.filter_by(movie_id=movie_id).first():
                new_watchlist = Watchlist(movie_id=movie_id)
                db.session.add(new_watchlist)
                db.session.commit()
    
    reviews = Review.query.filter_by(movie_id=movie_id).all()
    watchlisted = Watchlist.query.filter_by(movie_id=movie_id).first() is not None
    
    cursor.execute("SELECT name FROM genres WHERE id IN (SELECT genre_id FROM movie_genre WHERE movie_id = ?)", (movie_id,))
    genres = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT actor_name, character_name, profile_path FROM cast WHERE movie_id = ? ORDER BY order ASC", (movie_id,))
    cast = cursor.fetchall()
    
    conn.close()
    
    return render_template('movie_details.html', movie=movie, genres=genres, cast=cast, reviews=reviews, watchlisted=watchlisted)

@app.route('/add_to_watchlist/<int:movie_id>')
def add_to_watchlist(movie_id):
    if not Watchlist.query.filter_by(movie_id=movie_id).first():
        new_watchlist = Watchlist(movie_id=movie_id)
        db.session.add(new_watchlist)
        db.session.commit()
    return redirect(url_for('movie_details', movie_id=movie_id))



@app.route('/watchlist')
def watchlist():
    watchlist_movies = db.session.query(Watchlist.movie_id, sqlite3.connect('movies.db').execute("SELECT name, image_url FROM movies WHERE id IN (SELECT movie_id FROM watchlist)")).fetchall()
    return render_template('watchlist.html', watchlist_movies=watchlist_movies)




@app.route("/user_dashboard")
@login_required
def user_dashboard():
    return render_template("user_dashboard.html", user=current_user)

@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    return render_template("admin_dashboard.html", user=current_user)



@app.route('/contactus')
def contactus():
    return render_template('contactus.html')

@app.route('/about_us')
def about_us():
    return render_template("about_us.html")




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    books = Book.query.all()
    return render_template('landing.html', books=books)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):  
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("index"))

        flash("Invalid email or password!", "danger")

    return render_template("login.html")






@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    if request.method == 'POST':
        try:
            # Handle file uploads
            image_file = request.files.get('image_file')
            backdrop_file = request.files.get('backdrop_file')

            image_url = None
            backdrop_url = None

            # Validate files and handle image uploads
            if image_file and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image_file.save(image_path)
                image_url = f'/{image_path}'
            else:
                flash("Invalid image file uploaded!", "danger")

            if backdrop_file and allowed_file(backdrop_file.filename):
                filename = secure_filename(backdrop_file.filename)
                backdrop_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                backdrop_file.save(backdrop_path)
                backdrop_url = f'/{backdrop_path}'
            else:
                flash("Invalid backdrop file uploaded!", "danger")

            # Validate the form fields before adding to the database
            if not request.form['name'] or not request.form['description']:
                flash("Name and Description are required!", "danger")
                return redirect('/movie')

            movie = Movie(
                name=request.form['name'],
                original_title=request.form.get('original_title', ''),
                description=request.form['description'],
                rating=float(request.form.get('rating', 0)),
                vote_count=int(request.form.get('vote_count', 0)),
                popularity=float(request.form.get('popularity', 0)),
                image_url=image_url,
                backdrop_url=backdrop_url,
                release_date=datetime.strptime(request.form['release_date'], '%Y-%m-%d') if request.form.get('release_date') else None,
                budget=int(request.form.get('budget', 0)),
                revenue=int(request.form.get('revenue', 0)),
                runtime=int(request.form.get('runtime', 0)),
                original_language=request.form.get('original_language', '')
            )

            db.session.add(movie)
            db.session.commit()

            # Handle genres (if provided)
            genre_ids = [int(i.strip()) for i in request.form.get('genre_ids', '').split(',') if i.strip().isdigit()]
            for gid in genre_ids:
                db.session.add(MovieGenre(movie_id=movie.id, genre_id=gid))

            # Handle production companies (if provided)
            company_ids = [int(i.strip()) for i in request.form.get('company_ids', '').split(',') if i.strip().isdigit()]
            for cid in company_ids:
                db.session.add(MovieProduction(movie_id=movie.id, company_id=cid))

            db.session.commit()

            flash("Movie added successfully!", "success")
            return redirect('/add_movie')

        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")

    return render_template('add_movie.html')


@app.route('/movie/update/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        movie.name = request.form['name']
        movie.original_title = request.form.get('original_title', '')
        movie.description = request.form['description']
        movie.rating = float(request.form.get('rating', 0))
        movie.vote_count = int(request.form.get('vote_count', 0))
        movie.popularity = float(request.form.get('popularity', 0))
        movie.image_url = request.form.get('image_url', '')
        movie.backdrop_url = request.form.get('backdrop_url', '')
        movie.release_date = datetime.strptime(request.form.get('release_date', '2000-01-01'), '%Y-%m-%d')
        movie.budget = int(request.form.get('budget', 0))
        movie.revenue = int(request.form.get('revenue', 0))
        movie.runtime = int(request.form.get('runtime', 0))
        movie.original_language = request.form.get('original_language', '')

        db.session.commit()
        flash("Movie updated successfully!", "success")
        return redirect(url_for('dashboard', movie_id=movie.id))

    return render_template('update_movie.html', movie=movie)



@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash("Movie deleted successfully!", "success")
    return redirect(url_for('dashboard'))  # Change 'home' to your movie list page





@app.route('/update_order/<int:order_id>/<string:status>')
@login_required
def update_order(order_id, status):
    if current_user.role != 'admin':
        flash("Access denied!", "danger")
        return redirect(url_for('index'))
    
    order = Order.query.get_or_404(order_id)
    order.status = status
    db.session.commit()
    flash(f"Order {status}!", "success")
    return redirect(url_for('orders'))

@app.route('/track_orders')
@login_required
def track_orders():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('track_orders.html', orders=orders)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form.get("role", "user")

        if User.query.filter_by(email=email).first():
            flash("Email already exists!", "danger")
            return redirect(url_for("register"))

        new_user = User(name=name, email=email, role=role)
        new_user.set_password(password)  # Hash password
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")




@app.route('/add_to_cart/<int:book_id>')
@login_required
def add_to_cart(book_id):
    book = Book.query.get(book_id)
    if not book:
        flash("Book not found!", "danger")
        return redirect(url_for('index'))
    

    existing_item = Cart.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    if existing_item:
        flash("Book is already in your cart!", "warning")
        return redirect(url_for('cart'))

    cart_item = Cart(user_id=current_user.id, book_id=book_id)
    db.session.add(cart_item)
    db.session.commit()
    flash("Book added to cart!", "success")
    return redirect(url_for('cart'))

@app.route('/add_to_cart/<int:book_id>')
@login_required
def add_to_wishlist(book_id):
    cart_item = Cart(user_id=current_user.id, book_id=book_id)
    db.session.add(cart_item)
    db.session.commit()
    flash("Book added to cart!", "success")
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:book_id>')
@login_required
def remove_from_cart(book_id):
    cart_item = Cart.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        flash("Book removed from cart!", "success")
    return redirect(url_for('cart'))

@app.route('/cart')
@login_required
def cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    total_price = sum(item.book.price for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@app.route('/place_order')
@login_required
def place_order():
    if current_user.role == 'admin':  
        flash("Admins cannot place orders!", "danger")
        return redirect(url_for('index'))

    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash("Your cart is empty!", "warning")
        return redirect(url_for('cart'))
    
    for item in cart_items:
        new_order = Order(user_id=current_user.id, book_id=item.book_id, status='Pending')
        db.session.add(new_order)
        db.session.delete(item)  
    db.session.commit()
    
    flash("Order placed successfully!", "success")
    return redirect(url_for('orders'))


@app.route('/orders')
@login_required
def orders():
    if current_user.role != 'admin':
        flash("Access denied!", "danger")
        return redirect(url_for('index'))
    orders = Order.query.all()
    return render_template('orders.html', orders=orders)

@app.route('/custom_details/<int:book_id>')
def custom_details(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('custom_movies.html', book=book)

@app.route('/book/<int:book_id>')
def book_details(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_details.html', book=book)

@app.route('/dashboard')
@login_required
def dashboard():
    Movies = Movie.query.all() if current_user.role == 'admin' else []
    return render_template('dashboard.html', movies=Movies)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))



@app.route('/movies-card')
def view_movies_card():
    movies = Movie.query.all()
    return render_template('movie_cards.html', movies=movies)





if __name__ == "__main__":
    with app.app_context():
        db.create_all() 
    app.run(debug=True)