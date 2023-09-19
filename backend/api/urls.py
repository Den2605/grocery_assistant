from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from recipes.views import (
    FollowAPIView,
    IngredientsViewSet,
    RecipesViewSet,
    TagsViewSet,
)
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"recipes", RecipesViewSet, basename="recipes")
router.register(r"tags", TagsViewSet, basename="tags")
router.register(r"ingredients", IngredientsViewSet, basename="ingredients")
# router.register(
#    r"users/(?P<following_id>\d+)/subscribe", FollowViewSet, basename="follow"
# )

urlpatterns = [
    # path("", include(router.urls)),
    path(
        "recipes/download_shopping_cart/",
        RecipesViewSet.as_view({"get": "download_shopping_cart"}),
        name="recipes_download_shopping_cart",
    ),
    path(
        "recipes/<int:pk>/shopping_cart/",
        RecipesViewSet.as_view(
            {"post": "shopping_cart", "delete": "shopping_cart"}
        ),
        name="recipes_shopping_cart",
    ),
    path("", include(router.urls)),
    path("users/subscriptions/", FollowAPIView.as_view()),
    path("users/<int:id>/subscribe/", FollowAPIView.as_view()),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
