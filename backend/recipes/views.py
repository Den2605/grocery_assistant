from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import HttpResponse

from recipes.filters import CustomSearchFilter, RecipeFilter
from recipes.models import (
    Basket,
    Favorite,
    Follow,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    Tag,
)
from recipes.permissions import AuthorOrReadOnly
from recipes.serializers import (
    AuthorGetSerializer,
    AuthorSerializer,
    FavoriteSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShoppincartSerializer,
    TagSerializer,
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
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        return super().perform_create(serializer)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        user = request.user.id
        if not Recipe.objects.filter(id=pk).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.method == "DELETE":
            basket = Basket.objects.filter(user=user, recipe=pk)
            if basket:
                basket.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        recipe = Recipe.objects.get(id=pk)
        serializer = ShoppincartSerializer(
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
        methods=["get"],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        basket = Basket.objects.filter(user=request.user)
        products = dict()
        if basket:
            for recipe in basket:
                ingredients = IngredientInRecipe.objects.filter(
                    recipe=recipe.recipe.id
                ).values(
                    "ingredient__name",
                    "amount",
                    "ingredient__measurement_unit",
                )
                for ingredient in ingredients:
                    name = ingredient["ingredient__name"]
                    amount = ingredient["amount"]
                    measurement_unit = ingredient[
                        "ingredient__measurement_unit"
                    ]
                    if name in products.keys():
                        last_number = products[name][0]
                        products[name] = [
                            amount + last_number,
                            measurement_unit,
                        ]
                    else:
                        products[name] = [amount, measurement_unit]
            content = ""
            for k, v in products.items():
                product = f"Наименование: {k}, количество: {v[0]}, {v[1]}.\n"
                content += product
            return HttpResponse(content, content_type="text/plain")
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        user = request.user.id
        if not Recipe.objects.filter(id=pk).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.method == "DELETE":
            favorite_recipe = Favorite.objects.filter(user=user, recipe=pk)
            if favorite_recipe:
                favorite_recipe.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        recipe = Recipe.objects.get(id=pk)
        serializer = FavoriteSerializer(
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
        if serializer.is_valid():
            serializer.save(is_subscribed=True)
            queryset = User.objects.filter(id=pk)
            recipes_count = len(Recipe.objects.filter(author=pk))
            serializer = AuthorSerializer(
                queryset,
                context={
                    "recipes_limit": recipes_limit,
                    "recipes_count": recipes_count,
                },
                many=True,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
