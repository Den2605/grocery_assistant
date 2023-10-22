from django.db.models.aggregates import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import CustomSearchFilter, RecipeFilter
from api.permissions import AuthorOrReadOnly
from api.serializers import (
    AuthorGetSerializer,
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
        self, current_model, current_serializer, request, pk=None
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
            Favorite, FavoriteSerializer, request, pk=pk
        )

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """Создан для добавления и удаления рецепта из списка покупок."""
        return self.shopping_or_favorite(
            Basket, ShoppincartSerializer, request, pk=pk
        )

    @action(
        detail=True,
        methods=["get"],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        """Создан для скачивания файла со списком покупок."""
        basket = Basket.objects.filter(user=request.user)
        if basket.exists():
            ingredients = (
                IngredientInRecipe.objects.filter(
                    recipe__baskets__user=request.user
                )
                .values("ingredient__name", "ingredient__measurement_unit")
                .annotate(total_amount=Sum("amount"))
                .values_list(
                    "ingredient__name",
                    "ingredient__measurement_unit",
                    "total_amount",
                )
            )
            products = [
                ("{} ({}) - {}".format(*ingredient))
                for ingredient in ingredients
            ]
            return HttpResponse(
                "Корзина:\n" + "\n".join(products), content_type="text/plain"
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowViewset(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Создан для отображения авторов на которых подписан пользователь."""

    serializer_class = AuthorGetSerializer

    def get_queryset(self):
        """Метод получения списка авторов на которых подписан пользователь."""
        user = self.request.user.id
        queryset = User.objects.filter(follow__user=user)
        return queryset

    def get_serializer_context(self):
        """Метод передачи параметра recipes_limit для сереализатора."""
        recipes_limit = self.request.query_params.get("recipes_limit", None)
        return {
            "request": self.request,
            "recipes_limit": recipes_limit,
            "view": self,
        }


class FollowAPIView(APIView):
    """Вью функция подписки и отписки пользователя на авторов рецептов."""

    def post(self, request, pk):
        """Метод создания подписки."""
        recipes_limit = self.request.query_params.get("recipes_limit", None)
        user_id = self.request.user.id
        serializer = FollowSerializer(
            data={
                "user": user_id,
                "following": pk,
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        queryset = User.objects.filter(id=pk)
        serializer = AuthorGetSerializer(
            queryset,
            context={
                "recipes_limit": recipes_limit,
            },
            many=True,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        """Метод удаления подписки."""
        condition = Follow.objects.filter(
            user=request.user.id,
            following=pk,
        ).exists()
        if condition:
            Follow.objects.filter(
                user=request.user.id,
                following=pk,
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
