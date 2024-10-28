from django.shortcuts import render
# your_app_name/views.py


from django.http import JsonResponse
from .models import User
import json
from django.views.decorators.csrf import csrf_exempt
import bcrypt

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
                    return JsonResponse({"msg": "login successful", "status": "success"})
                else:
                    return JsonResponse({"msg": "invalid password", "status": "error"}, status=401)
            else:
                return JsonResponse({"msg": "user not found", "status": "error"}, status=404)

        return JsonResponse({"msg": "invalid request method", "status": "error"}, status=405)

    except json.JSONDecodeError:
        return JsonResponse({"msg": "invalid JSON", "status": "error"}, status=400)
    except Exception as e:
        return JsonResponse({"msg": str(e), "status": "error"}, status=500)