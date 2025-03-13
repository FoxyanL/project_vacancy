from django.contrib import admin
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('jobs.urls')),
    path('api/users/', include('users.urls')),
]

schema_view = get_schema_view(
    openapi.Info(
        title="API Сервиса Вакансий",
        default_version='v1',
        description="Документация API",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns += [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger'),
]
