from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from users.models import Profile
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from applications.models import Application
from jobs.models import Vacancy
from jobs.forms import ApplicationForm
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from django.utils.timezone import localtime



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
    if isinstance(request.user, AnonymousUser):
        message = "Пожалуйста, авторизуйтесь, чтобы просматривать вакансии."
        return render(request, 'index.html', {'message': message})
    
    vacancies = Vacancy.objects.all()
    return render(request, 'index.html', {'vacancies': vacancies})

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
            return render(request, "login.html")

    return render(request, "login.html")

def user_register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Пароли не совпадают!")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Пользователь с таким именем уже существует!")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Пользователь с таким email уже существует!")
            return redirect("register")

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, "Регистрация успешна! Теперь войдите в систему.")
        return redirect("login")

    return render(request, "register.html")

@login_required
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

@login_required
def vacancy_detail(request, vacancy_id):
    vacancy = Vacancy.objects.get(id=vacancy_id)
    
    is_applied = Application.objects.filter(student=request.user, vacancy=vacancy).exists()

    if request.method == 'POST' and not is_applied:
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.student = request.user
            application.vacancy = vacancy
            application.save()
            return redirect('applications')
    else:
        form = ApplicationForm()

    return render(request, 'vacancy_detail.html', {
        'vacancy': vacancy,
        'form': form,
        'is_applied': is_applied
    })

@login_required
def applications(request):
    applications = Application.objects.filter(student=request.user)
    
    for application in applications:
        application.date_submitted = localtime(application.date_submitted)

    return render(request, 'applications.html', {'applications': applications})

