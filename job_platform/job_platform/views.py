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
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from jobs.models import Review, Vacancy, Rating, ReviewEmployer
from jobs.forms import ReviewForm, ReviewEmployerForm
from jobs.forms import VacancyForm
from users.models import Profile, Notification
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from applications.serializers import ApplicationSerializer
from rest_framework.decorators import action

User = get_user_model()

@login_required
def profile(request):
    interviews = Application.objects.filter(student=request.user, status='Принята')
    interview_data = []

    for interview in interviews:
        interview_data.append({
            'vacancy_title': interview.vacancy.title,
            'interview_date': interview.vacancy.deadline,
            'vacancy_id': interview.vacancy.id,
        })

    return render(request, 'profile.html', {
        'interviews': interview_data,
    })

def home(request):
    if isinstance(request.user, AnonymousUser):
        message = "Пожалуйста, авторизуйтесь, чтобы просматривать вакансии."
        return render(request, 'index.html', {'message': message})

    unread_notifications_count = 0
    if request.user.is_authenticated:
        unread_notifications_count = Notification.objects.filter(user=request.user, read=False).count()

    search_query = request.GET.get('search', '')
    sort_option = request.GET.get('sort', '')

    vacancies = Vacancy.objects.all()

    if search_query:
        vacancies = vacancies.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    if sort_option == 'salary_min':
        vacancies = vacancies.order_by('salary_min')
    
    if request.user.profile.role:
        role = request.user.profile.role

    return render(request, 'index.html', {
        'vacancies': vacancies,
        'search': search_query,
        'sort': sort_option,
        'role': role,
        'unread_notifications_count': unread_notifications_count,
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
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.student = request.user
            application.vacancy = vacancy
            application.save()

            employer = vacancy.employer
            Notification.objects.create(
                user=employer,
                message=f"Студент {request.user.username} подал заявку на вакансию '{vacancy.title}'."
            )

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
            users = get_user_model().objects.filter(profile__role='student')
            for user in users:
                Notification.objects.create(
                    user=user,
                    message=f"Новая вакансия: {vacancy.title} добавлена на платформу.",
                )
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

    student_reviews = {review.student.id: review for review in reviews}

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        student = get_user_model().objects.get(id=student_id)

        if 'action' in request.POST:
            action = request.POST.get('action')
            application = get_object_or_404(Application, vacancy=vacancy, student=student)

            if action == 'accept':
                application.status = 'Принята'
                application.save()

                Notification.objects.create(
                    user=student,
                    message=f"Ваша заявка на вакансию «{vacancy.title}» была принята."
                )

                messages.success(request, f"Вы приняли студента {student.username}.")
            elif action == 'reject':
                application.status = 'Отклонена'
                application.save()

                Notification.objects.create(
                    user=student,
                    message=f"Ваша заявка на вакансию «{vacancy.title}» была отклонена."
                )

                messages.warning(request, f"Вы отклонили студента {student.username}.")
            
            return redirect('vacancy_applicants', vacancy_id=vacancy_id)

        elif 'rating' in request.POST and 'comment' in request.POST:
            rating = request.POST.get('rating')
            comment = request.POST.get('comment')

            existing_review = ReviewEmployer.objects.filter(
                student=student,
                employer=request.user,
                vacancy=vacancy
            ).first()

            if existing_review:
                messages.warning(request, "Вы уже оставили отзыв для этого студента.")
            else:
                ReviewEmployer.objects.create(
                    student=student,
                    employer=request.user,
                    vacancy=vacancy,
                    rating=rating,
                    comment=comment
                )
                messages.success(request, "Ваш отзыв был успешно добавлен.")

            return redirect('vacancy_applicants', vacancy_id=vacancy_id)

    return render(request, 'vacancy_applicants.html', {
        'vacancy': vacancy,
        'applications': applications,
        'reviews': reviews,
        'student_reviews': student_reviews,
    })

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    notifications.update(read=True)

    return render(request, 'notifications.html', {
        'notifications': notifications,
    })


class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save()
        else:
            raise serializers.ValidationError(serializer.errors)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return super().create(request, *args, **kwargs)
        return Response(serializer.errors, status=400)

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

class ProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        profile = Profile.objects.get(user=request.user)
        return Response(ProfileSerializer(profile).data)

    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['get'])
    def interviews(self, request):
        applications = Application.objects.filter(student=request.user, status='Принята')
        interview_data = []
        for application in applications:
            interview_data.append({
                'vacancy_title': application.vacancy.title,
                'interview_date': application.vacancy.deadline,
                'vacancy_id': application.vacancy.id,
            })
        return Response(interview_data)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(student=self.request.user)
        else:
            raise serializers.ValidationError(serializer.errors)

class ReviewEmployerViewSet(viewsets.ModelViewSet):
    queryset = ReviewEmployer.objects.all()
    serializer_class = ReviewEmployerSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(employer=self.request.user)
        else:
            raise serializers.ValidationError(serializer.errors)

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(student=self.request.user)
        else:
            raise serializers.ValidationError(serializer.errors)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return super().create(request, *args, **kwargs)
        return Response(serializer.errors, status=400)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        if serializer.is_valid():
            serializer.save()
        else:
            raise serializers.ValidationError(serializer.errors)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return super().update(request, *args, **kwargs)
        return Response(serializer.errors, status=400)

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save()
        else:
            raise serializers.ValidationError(serializer.errors)