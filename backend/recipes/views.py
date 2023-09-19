from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

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
    FavoriteSerializer,
    FollowSerializer,
    FollowUserSerializer,
    IngredientSerializer,
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
        # получаем корзину пользователя
        basket = Basket.objects.filter(user=request.user)
        products = dict()
        # получаем ингридиенты из рецептов и добавляем их в список
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
        # user = get_object_or_404(User, id=user)
        followings = Follow.objects.filter(user=user)
        print(followings)
        serializer = FollowUserSerializer(followings, many=True)
        # users = User.objects.filter(id=followings)
        # serializer = FollowUserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, id):
        data = {}
        data["user"] = request.user.id
        data["following"] = id
        serializer = FollowSerializer(data=data)
        if serializer.is_valid():
            serializer.save(is_subscribed=True)
            # serializer = FollowUserSerializer(get_object_or_404(User, id=id))
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
