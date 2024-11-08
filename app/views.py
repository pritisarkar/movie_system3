# Django imports
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from django.db import IntegrityError
from django.db.models import Count
from django.views import View

# Third-party imports
import jwt
import bcrypt
import json
import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from functools import wraps

# Local imports
from .models import User, Genre, Movie, Customer, WatchList, WatchedList


@csrf_exempt
def user(request):
    print("hey user")
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            email = data["email"]
            password = data["password"].encode("utf-8")
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode("utf-8")
            user = User(email=email, password=hashed_password)
            user.save()
            return JsonResponse({"msg": "data inserted", "status": "success"})
        else:
            return "hello"
    except Exception as e:
        import traceback

        traceback.print_exc()
        return JsonResponse({"status": "error", "message": str(e)})


@csrf_exempt
def login(request):
    print("hey login")
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            email = data["email"]
            password = data["password"].encode("utf-8")
            user = User.objects.filter(email=email).first()
            if user:
                if bcrypt.checkpw(password, user.password.encode("utf-8")):
                    token_payload = {
                        "user_id": user.id,
                        "exp": datetime.datetime.now()
                        + datetime.timedelta(seconds=settings.JWT_EXPIRATION_DELTA),
                        "iat": datetime.datetime.now(),
                    }
                    token = jwt.encode(
                        token_payload, settings.SECRET_KEY, algorithm="HS256"
                    )

                    return JsonResponse(
                        {"msg": "login successful", "status": "success", "token": token}
                    )
                else:
                    return JsonResponse(
                        {"msg": "invalid password", "status": "error"}, status=401
                    )
            else:
                return JsonResponse(
                    {"msg": "user not found", "status": "error"}, status=404
                )

        return JsonResponse(
            {"msg": "invalid request method", "status": "error"}, status=405
        )

    except json.JSONDecodeError:
        return JsonResponse({"msg": "invalid JSON", "status": "error"}, status=400)
    except Exception as e:
        return JsonResponse({"msg": str(e), "status": "error"}, status=500)


# token validation
def is_token_valid(view_func):
    @wraps(view_func)
    def decorated(request, *args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return JsonResponse({"message": "Token is missing"}, status=401)
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token["user_id"]
            request.user_id = user_id
            return view_func(request, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return JsonResponse({"message": "Token has expired"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"message": "Invalid token"}, status=401)

    return decorated


# add genre
@csrf_exempt
@is_token_valid
def GenreADD(request):
    if request.method == "GET":
        try:
            genres = list(Genre.objects.values("id", "name", "description"))
            return JsonResponse(genres, safe=False)
        except Exception as e:
            return JsonResponse({"status": "error", "message": "Already Exist"})
    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            print(data["name"])
            genre = Genre.objects.create(
                name=data["name"], description=data.get("description", "")
            )

            return JsonResponse(
                {"id": genre.id, "name": genre.name, "description": genre.description},
                status=201,
            )
        except Exception as e:
            return JsonResponse({"status": "error", "message": "Already Exist"})


# update genre
@csrf_exempt
@is_token_valid
def GenreUPDATE(request, genre_id):
    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            genre = Genre.objects.get(id=genre_id)
            genre.name = data.get("name", genre.name)
            genre.description = data.get("description", genre.description)
            genre.save()
            return JsonResponse(
                {"id": genre.id, "name": genre.name, "description": genre.description},
                status=200,
            )
        except Genre.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "Genre not found"}, status=404
            )
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON"}, status=400
            )
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    else:
        return JsonResponse(
            {"status": "error", "message": "Invalid request method"}, status=405
        )


# Delete Genre
@csrf_exempt
@is_token_valid
def GenreDELETE(request, genre_id):
    if request.method == "DELETE":
        try:
            genre = Genre.objects.get(id=genre_id)
            genre.delete()
            return JsonResponse(
                {"status": "success", "message": "Genre deleted"}, status=204
            )
        except Genre.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "Genre not found"}, status=404
            )
    else:
        return JsonResponse(
            {"status": "error", "message": "Invalid request method. Use DELETE."},
            status=405,
        )


# movie add
@csrf_exempt
@is_token_valid
def movieADD(request):
    if request.method != "POST":
        return JsonResponse(
            {
                "status": "error",
                "message": "Invalid request method. Only POST is allowed.",
            },
            status=405,
        )

    try:
        data = json.loads(request.body)
        title = data.get("title")
        release_year = data.get("release_year")

        if not title or not release_year:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Missing required fields: title, release_year",
                },
                status=400,
            )

        # Check if genres are passed in the request
        genres_data = data.get("genres", [])
        genres = Genre.objects.filter(id__in=genres_data)

        # Create a new Movie object
        movie = Movie.objects.create(
            name=title,
            description=data.get("description", ""),
            release_year=release_year,
        )

        # Add the genres to the movie
        if genres.exists():
            movie.genres.set(genres)

        return JsonResponse(
            {
                "id": movie.id,
                "name": movie.name,
                "description": movie.description,
                "release_year": movie.release_year,
                "genres": list(movie.genres.values_list("id", flat=True)),
            },
            status=201,
        )

    except IntegrityError:
        return JsonResponse(
            {"status": "error", "message": "Movie with this title already exists."},
            status=400,
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"status": "error", "message": "Invalid JSON in request."}, status=400
        )

    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": f"An error occurred: {str(e)}"}, status=500
        )
    else:
        return JsonResponse({"status": "error", "message": "Token missing"})


# Movie update
@csrf_exempt
@is_token_valid
def movieUpdate(request, movie_id):
    if request.method != "PUT":
        return JsonResponse(
            {"status": "error", "message": "Invalid request method"}, status=405
        )

    try:
        data = json.loads(request.body)
        print(data, "hello")
        movie = Movie.objects.get(id=movie_id)
        movie.name = data.get("title", movie.name)
        movie.description = data.get("description", movie.description)
        movie.release_year = data.get("release_year", movie.release_year)
        if "genres" in data:
            movie.genres.set(data["genres"])

        movie.save()
        return JsonResponse(
            {
                "id": movie.id,
                "name": movie.name,
                "description": movie.description,
                "release_year": movie.release_year,
                "genres": list(movie.genres.values_list("id", flat=True)),
            },
            status=200,
        )

    except Movie.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "Movie not found"}, status=404
        )
    except IntegrityError:
        return JsonResponse(
            {"status": "error", "message": "Movie with this title already exists"},
            status=400,
        )
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)


# movie Delete
@csrf_exempt
@is_token_valid
def movieDelete(request, movie_id):
    if request.method != "DELETE":
        return JsonResponse(
            {"status": "error", "message": "Invalid request method, DELETE expected."},
            status=405,
        )
    try:
        movie = Movie.objects.get(id=movie_id)
        movie.delete()
        return JsonResponse(
            {
                "status": "success",
                "message": f"Movie with ID {movie_id} deleted successfully.",
            },
            status=200,
        )
    except Movie.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": f"Movie with ID {movie_id} not found."},
            status=404,
        )
    except Exception as e:
        return JsonResponse(
            {
                "status": "error",
                "message": "An unexpected error occurred. Please try again later.",
                "details": str(e),
            },
            status=500,
        )


# signout
@csrf_exempt
@is_token_valid
def signout(request):
    # token_error = request.headers.get('Authorization')
    # token_error = is_token_valid(request)
    # if token_error:
    #     return token_error
    if request.method != "POST":
        return JsonResponse(
            {"status": "error", "message": "Invalid request method"}, status=405
        )
    logout(request)
    return JsonResponse(
        {"status": "success", "message": "Signed out successfully"}, status=200
    )


# for user
# User Register and login using email and password(Done)
# Authentication using JSON Web Token
# User Profile
# User logout


# customer Registration
@csrf_exempt
def customer(request):
    print("hey user")
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            email = data["email"]
            name = data["name"]
            password = data["password"].encode("utf-8")
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode("utf-8")
            customer = Customer(email=email, name=name, password=hashed_password)
            customer.save()
            return JsonResponse({"msg": "data inserted", "status": "success"})
        else:
            return "hello"
    except Exception as e:
        import traceback

        traceback.print_exc()
        return JsonResponse({"status": "error", "message": str(e)})


# customer login
@csrf_exempt
def loginCustomer(request):
    print("hey login")
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            email = data["email"]
            password = data["password"].encode("utf-8")
            customer = Customer.objects.filter(email=email).first()
            if user:
                if bcrypt.checkpw(password, customer.password.encode("utf-8")):
                    token_payload = {
                        "user_id": customer.id,
                        "exp": datetime.datetime.now()
                        + datetime.timedelta(seconds=settings.JWT_EXPIRATION_DELTA),
                        "iat": datetime.datetime.now(),
                    }
                    token = jwt.encode(
                        token_payload, settings.JWT_SECRET, algorithm="HS256"
                    )

                    return JsonResponse(
                        {"msg": "login successful", "status": "success", "token": token}
                    )
                else:
                    return JsonResponse(
                        {"msg": "invalid password or email", "status": "error"},
                        status=401,
                    )
            else:
                return JsonResponse(
                    {"msg": "invalid password or email", "status": "error"}, status=404
                )

        return JsonResponse(
            {"msg": "invalid request method", "status": "error"}, status=405
        )

    except json.JSONDecodeError:
        return JsonResponse({"msg": "invalid JSON", "status": "error"}, status=400)
    except Exception as e:
        return JsonResponse({"msg": str(e), "status": "error"}, status=500)


def is_token_valid_customer(view_func):
    @wraps(view_func)
    def decorated(request, *args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return JsonResponse({"message": "Token is missing"}, status=401)

        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token["user_id"]
            request.user_id = user_id
            return view_func(request, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return JsonResponse({"message": "Token has expired"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"message": "Invalid token"}, status=401)

    return decorated


# customer profile show only name password and email


@csrf_exempt
@is_token_valid_customer
def customerprofile(request, customer_id=None):
    print(customer_id)
    if customer_id is not None:
        try:
            customer = Customer.objects.get(id=customer_id)
            customer_data = {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
                "password": customer.password,
            }
            return JsonResponse({"status": "success", "data": customer_data})
        except Customer.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "Data not found"}, status=404
            )
    else:
        return JsonResponse({"message": "customer_id is required"}, status=400)


@csrf_exempt
@is_token_valid_customer
def signoutCustomer(request):

    if request.method != "POST":
        return JsonResponse(
            {"status": "error", "message": "Invalid request method"}, status=405
        )
    logout(request)
    return JsonResponse(
        {"status": "success", "message": "Signed out successfully"}, status=200
    )


# add watchlist
@csrf_exempt
@is_token_valid_customer
class AddToWatchedListView(View):
    def post(self, request, movie_id):
        movie = get_object_or_404(Movie, id=movie_id)
        watched_entry, created = WatchedList.objects.get_or_create(
            movie=movie, customer=request.user
        )
        if created:
            return JsonResponse({"message": "Movie added to watched list"}, status=201)
        return JsonResponse({"message": "Movie already in watched list"}, status=400)


# delete watchlist
@csrf_exempt
@is_token_valid_customer
class DeleteFromWatchedListView(View):
    def delete(self, request, movie_id):
        watched_movie = get_object_or_404(
            WatchedList, movie_id=movie_id, customer=request.user
        )
        watched_movie.delete()
        return JsonResponse({"message": "Movie removed from watched list"}, status=204)


# show a watchlist
@csrf_exempt
@is_token_valid_customer
def watched_list_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "User not authenticated"}, status=401)
    watched_movies = WatchedList.objects.filter(customer=request.user)
    if not watched_movies.exists():
        return JsonResponse({"message": "No movies in watched list"}, status=404)
    movie_data = []
    for entry in watched_movies:
        movie = entry.movie
        movie_data.append(
            {
                "id": movie.id,
                "title": movie.title,
                "release_date": movie.release_date.strftime("%Y-%m-%d"),
            }
        )
    return JsonResponse({"watched_movies": movie_data}, status=200)


# user dashboard
@csrf_exempt
@is_token_valid
@api_view(["GET"])
def admin_dashboard(request):
    genre_movie_count = Genre.objects.annotate(movie_count=Count("movies")).values(
        "name", "movie_count"
    )
    user_count = User.objects.count()
    users_with_watchlist = WatchedList.objects.values("user").distinct().count()
    movie_watchlist_count = (
        Movie.objects.annotate(watchlist_count=Count("watchlisted_by"))
        .annotate(watched_count=Count("watched_by"))
        .values("title", "watchlist_count", "watched_count")
    )
    data = {
        "genre_movie_count": list(genre_movie_count),
        "user_count": user_count,
        "users_with_watchlist": users_with_watchlist,
        "movie_watchlist_count": list(movie_watchlist_count),
    }
    return Response(data)


# customer admin
@csrf_exempt
@is_token_valid_customer
def client_dashboard(request):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "User not authenticated"}, status=401)
    watchlist_count = WatchList.objects.filter(customer=request.user).count()
    watchedlist_count = WatchedList.objects.filter(customer=request.user).count()
    return JsonResponse(
        {"watchlist_count": watchlist_count, "watchedlist_count": watchedlist_count},
        status=200,
    )





#user dashboard
@csrf_exempt
def user_dashboard(request):
    # Count of movies per genre
    movies_per_genre = Movie.objects.values('genre').annotate(count=Count('id'))

    # Count of registered users
    user_count = User.objects.count()

    # Count of users with movies in their watchlist
    users_with_watchlist = (
        User.objects.filter(watchlist__isnull=False)
        .distinct()
        .count()
    )

    watchlist_count = (
        WatchList.objects.values('movie__title')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    
    watched_count = (
        WatchedList.objects.values('movie__title')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    context = {
        "movies_per_genre": list(movies_per_genre),
        "user_count": user_count,
        "users_with_watchlist": users_with_watchlist,
        "watchlist_count": list(watchlist_count),
        "watched_count": list(watched_count),
    }

    return JsonResponse(context)



#customer dashboad
@csrf_exempt
def customer_dashboard(request):
    watchlist_count = WatchList.objects.filter(user=request.user).count()
    watchedlist_count = WatchedList.objects.filter(user=request.user).count()

    data = {
        'watchlist_count': watchlist_count,
        'watchedlist_count': watchedlist_count,
    }

    return JsonResponse(data)




