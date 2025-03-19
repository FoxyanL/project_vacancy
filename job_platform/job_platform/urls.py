from django.contrib import admin
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.urls import path, include
from .views import home
from . import views
from django.contrib.auth import views as auth_views
from .views import VacancyList, ApplicationList
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .swagger import schema_view


urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path('api/vacancies/', VacancyList.as_view(), name='vacancy-list'),
    path('api/applications/', ApplicationList.as_view(), name='application-list'),
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
]

