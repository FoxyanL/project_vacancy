from django.contrib import admin
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.urls import path, include
from .views import home
from . import views
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .swagger import schema_view
from rest_framework.routers import DefaultRouter
from .views import (
    VacancyViewSet,
    ReviewViewSet,
    ReviewEmployerViewSet,
    ProfileViewSet,
    ApplicationList,
    NotificationViewSet,
    ApplicationViewSet,
    UserViewSet,
    RatingViewSet
)

# Инициализация роутера
router = DefaultRouter()
router.register(r'applications', ApplicationViewSet)
router.register(r'users', UserViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'vacancies', VacancyViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'review-employers', ReviewEmployerViewSet)
router.register(r'ratings', RatingViewSet)

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger/json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='user_logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('vacancy/<int:vacancy_id>/', views.vacancy_detail, name='vacancy_detail'),
    path('applications/', views.applications, name='applications'),
    path('vacancy/<int:vacancy_id>/leave_review/', views.leave_review, name='leave_review'),
    path('vacancy/<int:vacancy_id>/rate_employer/', views.rate_employer, name='rate_employer'),
    path('my_vacancies/', views.my_vacancies, name='my_vacancies'),
    path('create_vacancy/', views.create_vacancy, name='create_vacancy'),
    path('vacancy/<int:vacancy_id>/applicants/', views.vacancy_applicants_view, name='vacancy_applicants'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('api/', include(router.urls)),
    path('api/applications/', ApplicationList.as_view(), name='applications-list'),
]
