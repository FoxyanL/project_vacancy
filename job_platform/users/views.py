from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password

User = get_user_model()

def user_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Пользователь уже существует'})

        user = User(username=username, email=email, password=make_password(password))
        user.save()

        return redirect('login')

    return render(request, 'register.html')

class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
