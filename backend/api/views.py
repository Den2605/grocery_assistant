from django.db.models.aggregates import Count, Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import CustomSearchFilter, RecipeFilter
from api.permissions import AuthorOrReadOnly
from api.serializers import (
    AuthorGetSerializer,
    CustomUserSerializer,
    FavoriteSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeGetSerializer,
    RecipeSerializer,
    ShoppincartSerializer,
    TagSerializer,
)
from recipes.models import (
    Basket,
    Favorite,
    Follow,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    Tag,
)
from users.models import CustomUser as User


class CustomUserViewSet(UserViewSet):
    """
    Вьюсет представления пользовательской модели пользователя
    с дополнительными действиями.
    """

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, **kwargs):
        """Метод для подписки и отписки пользователя на авторов рецептов."""
        author_id = self.kwargs.get("id")
        user_id = self.request.user.id
        if request.method == "POST":
            serializer = FollowSerializer(
                data={
                    "user": user_id,
                    "following": author_id,
                }
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            queryset = User.objects.filter(id=author_id).annotate(
                recipes_count=Count("recipes")
            )
            serializer = AuthorGetSerializer(
                queryset,
                many=True,
                context={"request": request},
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        follow = Follow.objects.filter(user=user_id, following=author_id)
        if follow:
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        """Метод для просмотра авторов на которых подписан пользователь."""
        user = self.request.user.id
        queryset = User.objects.filter(follow__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = AuthorGetSerializer(
            pages,
            many=True,
            context={"request": request},
        )
        return self.get_paginated_response(serializer.data)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с тегами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (CustomSearchFilter,)
    search_fields = ["^name"]


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self, *args, **kwargs):
        """Метод определения сереализатора."""
        if self.request.method == "GET":
            return RecipeGetSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        """Метод сохранения данных сереализатора."""
        serializer.save(author=self.request.user)
        return super().perform_create(serializer)

    def shopping_or_favorite(
        self,
        current_model,
        current_serializer,
        request,
        pk=None,
    ):
        """Метод добавления рецептов в корзину,избраное или удаление из них."""
        user = request.user.id
        if not Recipe.objects.filter(id=pk).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.method == "DELETE":
            basket = current_model.objects.filter(user=user, recipe=pk)
            if basket.exists():
                basket.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        recipe = Recipe.objects.get(id=pk)
        serializer = current_serializer(
            data={
                "user": user,
                "recipe": pk,
                "name": recipe.name,
                "image": recipe.image,
                "cooking_time": recipe.cooking_time,
            },
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        """Создан для добавления и удаления рецепта из избранного."""
        return self.shopping_or_favorite(
            Favorite,
            FavoriteSerializer,
            request,
            pk=pk,
        )

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """Создан для добавления и удаления рецепта из списка покупок."""
        return self.shopping_or_favorite(
            Basket,
            ShoppincartSerializer,
            request,
            pk=pk,
        )

    @action(
        detail=True,
        methods=["get"],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        """Создан для скачивания файла со списком покупок."""
        user = request.user
        basket = Basket.objects.filter(user=user)
        if basket.exists():
            ingredients = (
                IngredientInRecipe.objects.filter(recipe__baskets__user=user)
                .values("ingredient__name", "ingredient__measurement_unit")
                .annotate(total_amount=Sum("amount"))
                .values_list(
                    "ingredient__name",
                    "ingredient__measurement_unit",
                    "total_amount",
                )
            )
            for ingredient in ingredients:
                products = ["{} ({}) - {}".format(*ingredient)]
            return HttpResponse(
                "Корзина:\n" + "\n".join(products), content_type="text/plain"
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
