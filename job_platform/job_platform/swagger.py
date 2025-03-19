from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

security_definition = openapi.Parameter(
    'Authorization',
    openapi.IN_QUERY,
    description='JWT token. Example: "Bearer <your_token>"',
    required=True,
    type=openapi.TYPE_STRING
)


schema_view = get_schema_view(
    openapi.Info(
        title="API документация",
        default_version='v1',
        description="Документация для API вакансий",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[AllowAny],
    urlconf='job_platform.urls',
)
