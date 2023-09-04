from recipes.models import Ingredients, Recipes, Tags
from rest_framework import serializers


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        # exclude = ("id",)
        # lookup_field = "slug"
        fields = ("id", "name", "color", "slug")
        model = Tags


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        # exclude = ("id",)
        # lookup_field = "slug"
        fields = ("id", "name", "number", "measurement_unit")
        model = Ingredients


class RecipesSerializer(serializers.ModelSerializer):
    class Meta:
        # exclude = ("id",)
        # lookup_field = "slug"
        fields = (
            "id",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
        )
        model = Recipes
