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
    AuthorSerializer,
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
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (CustomSearchFilter,)
    search_fields = ["^name"]


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == "GET":
            return RecipeGetSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        return super().perform_create(serializer)

    def shopping_or_favorite(
        self, current_model, current_serializer, request, pk=None
    ):
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
        return self.shopping_or_favorite(
            Favorite, FavoriteSerializer, request, pk=pk
        )

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        return self.shopping_or_favorite(
            Basket, ShoppincartSerializer, request, pk=pk
        )

    @action(
        detail=True,
        methods=["get"],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        basket = Basket.objects.filter(user=request.user)
        products = dict()
        if basket.exists():
            ingredients = (
                IngredientInRecipe.objects.filter(
                    recipe__baskets__user=request.user
                )
                .values("ingredient__name", "ingredient__measurement_unit")
                .annotate(total_amount=Sum("amount"))
                .order_by()
            )
            for ingredient in ingredients:
                name = ingredient["ingredient__name"]
                amount = ingredient["total_amount"]
                measurement_unit = ingredient["ingredient__measurement_unit"]
                products[name] = [amount, measurement_unit]
            content = ""
            for k, v in products.items():
                product = f"Наименование: {k}, количество: {v[0]}, {v[1]}.\n"
                content += product
            return HttpResponse(content, content_type="text/plain")
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowViewset(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AuthorGetSerializer

    def get_queryset(self):
        user = self.request.user.id
        queryset = User.objects.filter(follow__user=user)
        return queryset


class FollowAPIView(APIView):
    def post(self, request, pk):
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
        recipes_count = Recipe.objects.filter(author=pk).count()
        serializer = AuthorSerializer(
            queryset,
            context={
                "recipes_limit": recipes_limit,
                "recipes_count": recipes_count,
            },
            many=True,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
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
