# 🎬 Flask Movie API Backend

A RESTful Flask API for managing movies, users, cart, orders, reviews, genres, and directors with JWT authentication.

## 🚀 Features

- User Registration & Login with JWT
- Admin functionality to manage movies, genres, and directors
- Add movies to cart and place orders
- Submit and retrieve reviews
- Protected routes with role-based access control
- Image URLs returned properly

---

## 🧪 API Testing in Postman

### 🔐 1. User Registration
 Endpoint:  `POST /api/register`  
 Headers: 
```json
Content-Type: application/json
```

 Body: 
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "password123"
}
```

---

### 🔓 2. User Login
 Endpoint:  `POST /api/login`  
 Headers: 
```json
Content-Type: application/json
```

 Body: 
```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

 Response: 
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJh..."
}
```

✅ Copy the `access_token` for use in other requests.

---

### 🔐 3. Using JWT in Protected Routes
Add this to  Headers  for all protected endpoints:
```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

### 🎬 4. Get All Movies
 Endpoint:  `GET /api/movies`  
 Headers: 
```http
Authorization: Bearer <access_token>
```

---

### ➕ 5. Add Movie (Admin only)
 Endpoint:  `POST /api/movies`  
 Headers: 
```json
Content-Type: application/json
Authorization: Bearer <access_token>
```

 Body: 
```json
{
  "title": "Inception",
  "description": "A mind-bending thriller.",
  "release_date": "2010-07-16",
  "genre_id": 1,
  "director_id": 1
}
```

---

### 🛒 6. Add to Watchlist
 Endpoint:  `POST /api/cart`  
 Headers:  as above  
 Body: 
```json
{
  "movie_id": 1
}
```



### 📝 8. Add a Review
 Endpoint:  `POST /api/reviews`  
 Headers:  as above  
 Body: 
```json
{
  "movie_id": 1,
  "rating": 5,
  "comment": "Amazing movie!"
}
```

---

### 🔁 Optional: Using Variables in Postman
Use an environment variable for your token:

 Pre-request Script: 
```js
pm.environment.set("accessToken", "your_token_here");
```

 Header: 
```http
Authorization: Bearer {{accessToken}}
```

---

## 📂 Project Structure
```
movie_api/
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   ├── schemas/
│   └── utils/
│
├── migrations/
├── .env
├── requirements.txt
├── run.py
└── README.md
```

---

## 🧰 Tech Stack

- Python (Flask, SQLAlchemy)
- JWT (Flask-JWT-Extended)
- SQLite / PostgreSQL
- Marshmallow for serialization
- Postman for API testing

---

## 📬 Contact

For any help or support, feel free to reach out!

---
