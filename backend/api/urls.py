from django.urls import include, path
from recipes.views import RecipesViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"recipes", RecipesViewSet, basename="recipes")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls")),
    # JWT-эндпоинты, для управления JWT-токенами:
    path("auth/", include("djoser.urls.jwt")),
]
