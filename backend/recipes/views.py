from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import CustomUser as User

from .models import (
    Basket,
    Favorite,
    Follow,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    Tag,
)
from .permissions import AuthorOrReadOnly
from .serializers import (
    AuthorGetSerializer,
    AuthorSerializer,
    FavoriteSerializer,
    FollowSerializer,
    FollowUserSerializer,
    IngredientSerializer,
    RecipeFollowSerializer,
    RecipeSerializer,
    ShoppincartSerializer,
    TagSerializer,
)


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnly,)

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
        if request.method == "DELETE":
            basket = get_object_or_404(Basket, user=user, recipe=pk)
            basket.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        recipe = get_object_or_404(Recipe, id=pk)
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
        basket = Basket.objects.filter(user=request.user)
        products = dict()
        if basket:
            for recipe in basket:
                ingredients = IngredientInRecipe.objects.filter(
                    recipe=recipe.recipe.id
                ).values(
                    "ingredient__name",
                    "number",
                    "ingredient__measurement_unit",
                )
                for ingredient in ingredients:
                    name = ingredient["ingredient__name"]
                    number = ingredient["number"]
                    measurement_unit = ingredient[
                        "ingredient__measurement_unit"
                    ]
                    if name in products.keys():
                        last_number = products[name][0]
                        products[name] = [
                            number + last_number,
                            measurement_unit,
                        ]
                    else:
                        products[name] = [number, measurement_unit]
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
        if request.method == "DELETE":
            favorite_recipe = get_object_or_404(Favorite, user=user, recipe=pk)
            favorite_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        recipe = get_object_or_404(Recipe, id=pk)
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


class FollowAPIView(APIView):
    def get(self, request):
        user = self.request.user.id
        follow_list = Follow.objects.filter(user=user).values_list(
            "following_id", flat=True
        )
        follow_users = []
        for number in follow_list:
            follow_users.append(get_object_or_404(User, id=number))

        serializer = AuthorGetSerializer(follow_users, many=True)
        # serializer = FollowUserSerializer(follow, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        user_id = self.request.user.id
        serializer = FollowSerializer(
            data={
                "user": user_id,
                "following": pk,
            }
        )
        if serializer.is_valid():
            serializer.save(is_subscribed=True)
            serializer = AuthorSerializer(get_object_or_404(User, id=pk))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        condition = Follow.objects.filter(
            user=request.user.id,
            following=id,
        ).exists()
        if condition:
            Follow.objects.filter(
                user=request.user.id,
                following=id,
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
