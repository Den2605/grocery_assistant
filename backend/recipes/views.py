from recipes.models import Ingredients, Recipes, Tags
from recipes.serializers import (
    IngredientsSerializer,
    RecipesSerializer,
    TagsSerializer,
)
from rest_framework import viewsets


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
