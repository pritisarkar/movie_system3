from django.shortcuts import render
import jwt
from django.conf import settings
from django.http import JsonResponse
from .models import User
import json
from django.views.decorators.csrf import csrf_exempt
import bcrypt
import datetime
from .models import Genre
from django.views import View
from .models import Movie
from django.db import IntegrityError 
from django.contrib.auth import logout
from .models import Customer




@csrf_exempt
def user(request):
    print("hey user")
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            email = data['email']
            password = data['password'].encode('utf-8')
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
            user = User(email=email, password=hashed_password)
            user.save()
            return JsonResponse({"msg":"data inserted","status":"success"})
        else:
            return "hello"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"status":"error","message":str(e)})


@csrf_exempt
def login(request):
    print("hey login")
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            email = data['email']
            password = data['password'].encode('utf-8')
            user = User.objects.filter(email=email).first()
            if user:
                if bcrypt.checkpw(password, user.password.encode('utf-8')):
                    token_payload = {
                        'user_id': user.id,
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=settings.JWT_EXPIRATION_DELTA),
                        'iat': datetime.datetime.utcnow()
                    }
                    token = jwt.encode(token_payload, settings.JWT_SECRET, algorithm='HS256')

                    return JsonResponse({"msg": "login successful", "status": "success","token":token})
                else:
                    return JsonResponse({"msg": "invalid password", "status": "error"}, status=401)
            else:
                return JsonResponse({"msg": "user not found", "status": "error"}, status=404)

        return JsonResponse({"msg": "invalid request method", "status": "error"}, status=405)

    except json.JSONDecodeError:
        return JsonResponse({"msg": "invalid JSON", "status": "error"}, status=400)
    except Exception as e:
        return JsonResponse({"msg": str(e), "status": "error"}, status=500)
    

#token validation 
def is_token_valid(token):
    return token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MzAyMDA1OTYsImlhdCI6MTczMDE5Njk5Nn0.2zGrVXKtHQKz-zyUiPvy-T2b-A66JGLDQXIWWoUaUns"

#add genre
@csrf_exempt
def GenreADD(request):
   
    token = request.headers.get('Authorization')
    if not token or not is_token_valid(token.split(" ")[-1]):

        return JsonResponse({"status":"error","message":"Please login"},status=401)
    if request.method == 'GET':
        try:
            genres = list(Genre.objects.values('id', 'name', 'description'))
            return JsonResponse(genres, safe=False)
        except Exception as e:
            return JsonResponse({"status": "error", "message": 'Already Exist'})
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(data["name"])
            genre = Genre.objects.create(name=data['name'], description=data.get('description', ''))
            
            return JsonResponse({'id': genre.id, 'name': genre.name, 'description': genre.description}, status=201)
        except Exception as e:
            return JsonResponse({"status": "error", "message": 'Already Exist'})
        
        
#update genre
def GenreUPDATE(request, genre_id):
    token_error = is_token_valid(request)
    if token_error:
        return token_error
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            genre = Genre.objects.get(id=genre_id)
            genre.name = data.get('name', genre.name)
            genre.description = data.get('description', genre.description)
            genre.save()
            return JsonResponse(
                {'id': genre.id, 'name': genre.name, 'description': genre.description}, 
                status=200
            )
        except Genre.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Genre not found"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

#Delete Genre
def GenreDELETE(request, genre_id):
    token_error = is_token_valid(request)
    if token_error:
        return token_error

    if request.method == 'DELETE':
        try:
            genre = Genre.objects.get(id=genre_id)
            genre.delete()
            return JsonResponse({"status": "success", "message": "Genre deleted"}, status=204)
        except Genre.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Genre not found"}, status=404)
        

#movie add
@csrf_exempt  
def movieADD(request):
    token_error = is_token_valid(request)
    if token_error:
        return token_error

    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        title = data.get('title')
        release_year = data.get('release_year')

        if not title or not release_year:
            return JsonResponse(
                {"status": "error", "message": "Missing required fields: title, release_year"},
                status=400
            )
        movie = Movie.objects.create(
            name=title,
            description=data.get('description', ''),
            release_year=release_year
        )
        if 'genres' in data:
            movie.genres.set(data['genres'])

        return JsonResponse({
            'id': movie.id,
            'name': movie.name,
            'description': movie.description,
            'release_year': movie.release_year,
            'genres': list(movie.genres.values_list('id', flat=True))
        }, status=201)

    except IntegrityError:
        return JsonResponse({"status": "error", "message": "Movie with this title already exists"}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
    
# Movie update
@csrf_exempt  
def movieUpdate(request, movie_id):
    token_error = is_token_valid(request)
    if token_error:
        return token_error

    if request.method != 'PUT':
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)

        movie = Movie.objects.get(id=movie_id)
        movie.name = data.get('title', movie.name)
        movie.description = data.get('description', movie.description)
        movie.release_year = data.get('release_year', movie.release_year)
        if 'genres' in data:
            movie.genres.set(data['genres'])
        movie.save()
        return JsonResponse({
            'id': movie.id,
            'name': movie.name,
            'description': movie.description,
            'release_year': movie.release_year,
            'genres': list(movie.genres.values_list('id', flat=True))
        }, status=200)

    except Movie.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Movie not found"}, status=404)
    except IntegrityError:
        return JsonResponse({"status": "error", "message": "Movie with this title already exists"}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
    

#movie Delete
@csrf_exempt
def movieDelete(request, movie_id):
    token_error = is_token_valid(request)
    if token_error:
        return token_error

    if request.method != 'DELETE':
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    try:
        movie = Movie.objects.get(id=movie_id)
        movie.delete()

        return JsonResponse({"status": "success", "message": "Movie deleted successfully"}, status=200)

    except Movie.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Movie not found"}, status=404)
    

#signout
@csrf_exempt  # Disable CSRF for testing
def signout(request):
    token_error = is_token_valid(request)
    if token_error:
        return token_error

    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    # Logout the user and clear the session
    logout(request)

    return JsonResponse({"status": "success", "message": "Signed out successfully"}, status=200)

#for user
# User Register and login using email and password
# Authentication using JSON Web Token
# User Profile
# User logout

#customer Registration
@csrf_exempt
def customer(request):
    print("hey user")
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            email = data['email']
            name = data['name']
            password = data['password'].encode('utf-8')
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
            customer = Customer(email=email,name=name, password=hashed_password)
            customer.save()
            return JsonResponse({"msg":"data inserted","status":"success"})
        else:
            return "hello"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"status":"error","message":str(e)})