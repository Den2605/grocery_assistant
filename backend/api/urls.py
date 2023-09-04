from django.urls import include, path
from recipes.views import RecipesViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"recipes", RecipesViewSet, basename="recipes")

urlpatterns = [
    path("", include(router.urls)),
    # path("v1/auth/signup/", UserSignUpView.as_view(), name="signup"),
    # path("v1/auth/token/", TokenView.as_view(), name="get_token"),
]
