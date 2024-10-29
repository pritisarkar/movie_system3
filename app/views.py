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
    

@csrf_exempt
def GenreADD(request):
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
