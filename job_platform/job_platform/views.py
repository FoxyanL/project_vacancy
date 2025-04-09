from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm, ProfileUpdateForm
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
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from jobs.serializers import VacancySerializer
from applications.serializers import ApplicationSerializer
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .serializers import ProfileUpdateSerializer, UserUpdateSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from jobs.models import Review, Vacancy, Rating, ReviewEmployer
from jobs.forms import ReviewForm, ReviewEmployerForm
from jobs.forms import VacancyForm
from users.models import Profile


class VacancyList(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        vacancies = Vacancy.objects.all()
        serializer = VacancySerializer(vacancies, many=True)
        return Response(serializer.data)

class ApplicationList(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        applications = Application.objects.filter(student=request.user)
        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ApplicationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


User = get_user_model()

@login_required
def profile(request):
    return render(request, 'profile.html')

def home(request):
    if isinstance(request.user, AnonymousUser):
        message = "Пожалуйста, авторизуйтесь, чтобы просматривать вакансии."
        return render(request, 'index.html', {'message': message})

    search_query = request.GET.get('search', '')
    sort_option = request.GET.get('sort', '')

    vacancies = Vacancy.objects.filter(currency='RUB')

    if search_query:
        vacancies = vacancies.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    if sort_option == 'salary_min':
        vacancies = vacancies.order_by('salary_min')

    return render(request, 'index.html', {
        'vacancies': vacancies,
        'search': search_query,
        'sort': sort_option,
        'role': request.user.profile.role
    })

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
        role = request.POST.get("role")

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
        Profile.objects.create(user=user, role=role)

        messages.success(request, "Регистрация успешна! Теперь войдите в систему.")
        return redirect("login")

    return render(request, "register.html")

@login_required
def edit_profile(request):
    user_form = ProfileUpdateForm(request.POST or None, instance=request.user)
    
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    
    profile_form = ProfileForm(request.POST or None, instance=profile)

    if request.method == 'POST':
        if user_form.is_valid():
            user_form.save()
            
            if profile_form.is_valid():
                profile_form.save()
                return redirect('profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')

    return render(request, 'edit_profile.html', {'user_form': user_form, 'profile_form': profile_form})

def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def vacancy_detail(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    
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

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user_serializer = UserUpdateSerializer(instance=request.user, data=request.data)
    profile_serializer = ProfileUpdateSerializer(instance=request.user.profile, data=request.data)

    user_serializer.is_valid(raise_exception=True)
    profile_serializer.is_valid(raise_exception=True)

    user_serializer.save()
    profile_serializer.save()

    return Response({
        'user': user_serializer.data,
        'profile': profile_serializer.data
    })

@login_required
def leave_review(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    has_applied = Application.objects.filter(student=request.user, vacancy=vacancy).exists()

    if not has_applied:
        return render(request, 'error.html', {'message': 'Вы не можете оставить отзыв, если не подавали заявку.'})

    reviews = Review.objects.filter(vacancy=vacancy)

    existing_review = Review.objects.filter(student=request.user, employer=vacancy.employer, vacancy=vacancy).first()

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.student = request.user
            review.employer = vacancy.employer
            review.vacancy = vacancy
            review.save()
            return redirect('applications')
    else:
        form = ReviewForm()

    return render(request, 'leave_review.html', {
        'vacancy': vacancy,
        'form': form,
        'reviews': reviews,
        'existing_review': existing_review,
    })

@login_required
def rate_employer(request, vacancy_id):
    vacancy = Vacancy.objects.get(id=vacancy_id)
    if request.user != vacancy.student:
        return redirect('home')

    if request.method == 'POST':
        rating = request.POST.get('rating')
        if rating:
            Rating.objects.create(
                student=request.user,
                job=vacancy,
                employer=vacancy.employer,
                rating=int(rating)
            )
            return redirect('vacancy_detail', vacancy_id=vacancy.id)
    
    return render(request, 'rate_employer.html', {'vacancy': vacancy})

@login_required
def create_vacancy(request):
    if not request.user.is_authenticated or request.user.profile.role != 'employer':
        return redirect('home')

    if request.method == 'POST':
        form = VacancyForm(request.POST)
        if form.is_valid():
            vacancy = form.save(commit=False)
            vacancy.employer = request.user
            vacancy.save()
            return redirect('my_vacancies')
    else:
        form = VacancyForm()
    
    return render(request, 'create_vacancy.html', {'form': form})

def my_vacancies(request):
    if not request.user.is_authenticated or request.user.profile.role != 'employer':
        return redirect('home')
    
    vacancies = Vacancy.objects.filter(employer=request.user)
    return render(request, 'my_vacancies.html', {'vacancies': vacancies})


@login_required
def vacancy_applicants_view(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id, employer=request.user)
    applications = Application.objects.filter(vacancy=vacancy)

    reviews = ReviewEmployer.objects.filter(vacancy=vacancy)

    review_status = False

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        student = get_user_model().objects.get(id=student_id)


        ReviewEmployer.objects.create(
            student=student,
            employer=request.user,
            vacancy=vacancy,
            rating=rating,
            comment=comment
        )
        messages.success(request, "Ваш отзыв был успешно добавлен.")
        review_status = True

        return redirect('vacancy_applicants', vacancy_id=vacancy_id)

    return render(request, 'vacancy_applicants.html', {
        'vacancy': vacancy,
        'applications': applications,
        'reviews': reviews,
        'review_status': review_status,
    })
