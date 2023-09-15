from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import CustomUser as User

from .models import Follow, Ingredient, IngredientInRecipe, Recipe, Tag
from .serializers import (
    FollowSerializer,  # RecipeReadSerializer,
    FollowUserSerializer,
    IngredientSerializer,
    RecipeSerializer,
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
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    # def get_serializer_class(self):
    #    if self.request.method == "GET":
    #        return RecipesReadSerializer
    #    return RecipesSerializer

    # def get_ingredients(self, obj):
    #    ingredients = IngredientsInRecipes.objects.filter(recipe=obj)
    #    print(">>>")
    #    print(ingredients[0].get("number"))
    #    return [ingredient.ingredient for ingredient in ingredients]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        return super().perform_create(serializer)


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
