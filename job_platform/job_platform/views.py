from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from users.models import Profile


User = get_user_model()


@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=user)
    
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'profile.html')

def home(request):
    return render(request, "index.html")

def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Неверное имя пользователя или пароль.")
    return redirect("home")

def user_register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password1 != password2:
            messages.error(request, "Пароли не совпадают!")
            return redirect("home")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Пользователь с таким именем уже существует!")
            return redirect("home")

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, "Регистрация успешна! Теперь войдите в систему.")
        return redirect("home")

    return redirect("home")

def edit_profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = None

    if profile is None:
        profile = Profile.objects.create(user=request.user)

    form = ProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')
