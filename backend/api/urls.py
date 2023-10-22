from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers

from api.views import (
    FollowAPIView,
    FollowViewset,
    IngredientsViewSet,
    RecipesViewSet,
    TagsViewSet,
)

router = routers.DefaultRouter()
router.register(r"recipes", RecipesViewSet, basename="recipes")
router.register(r"tags", TagsViewSet, basename="tags")
router.register(r"ingredients", IngredientsViewSet, basename="ingredients")

urlpatterns = [
    # path(
    #     "recipes/download_shopping_cart/",
    #     RecipesViewSet.as_view({"get": "download_shopping_cart"}),
    #     name="recipes_download_shopping_cart",
    # ),
    # path(
    #     "recipes/<int:pk>/shopping_cart/",
    #     RecipesViewSet.as_view(
    #         {"post": "shopping_cart", "delete": "shopping_cart"}
    #     ),
    #     name="recipes_shopping_cart",
    # ),
    # path(
    #     "recipes/<int:pk>/favorite/",
    #     RecipesViewSet.as_view({"post": "favorite", "delete": "favorite"}),
    #     name="recipes_favorite",
    # ),
    path("", include(router.urls)),
    path(
        "users/subscriptions/",
        FollowViewset.as_view({"get": "list"}),
        name="follow_users",
    ),
    path("users/<int:pk>/subscribe/", FollowAPIView.as_view()),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
