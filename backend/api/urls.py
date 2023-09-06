from django.urls import include, path
from recipes.views import IngredientsViewSet, RecipesViewSet, TagsViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"recipes", RecipesViewSet, basename="recipes")
router.register(r"tags", TagsViewSet, basename="tags")
router.register(r"ingredients", IngredientsViewSet, basename="ingredients")

urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
