from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

from authentication.views import LoginView, LogoutView

api_info = openapi.Info(
    title="Spectrespecs API",
    default_version="v1",
    description="Management backend service<br>"
    "for telegram groups administration</br>"
    "via bot through Telegram client API",
    terms_of_service="https://nianticlabs.com/terms/en/",
    contact=openapi.Contact(email="spacehug.o0@gmail.com"),
    license=openapi.License(name="MIT License"),
)

schema_view = get_schema_view(public=True, permission_classes=(AllowAny,))

urlpatterns = [
    path("manage/", admin.site.urls),
    path("auth/login/", LoginView.as_view(), name="rest_login"),
    path("auth/logout/", LogoutView.as_view(), name="rest_logout"),
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("profile/", include("core.urls")),
    path("nightwatch/", include("nightwatch.urls")),
]


