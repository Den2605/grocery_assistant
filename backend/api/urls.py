from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers

from api.views import (
    CustomUserViewSet,
    IngredientsViewSet,
    RecipesViewSet,
    TagsViewSet,
)

router = routers.DefaultRouter()
router.register(r"recipes", RecipesViewSet, basename="recipes")
router.register(r"tags", TagsViewSet, basename="tags")
router.register(r"ingredients", IngredientsViewSet, basename="ingredients")
router.register(r"users", CustomUserViewSet, basename="users")

urlpatterns = [
    path(
        "recipes/download_shopping_cart/",
        RecipesViewSet.as_view({"get": "download_shopping_cart"}),
        name="recipes_download_shopping_cart",
    ),
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
