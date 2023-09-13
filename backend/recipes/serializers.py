import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import CustomUser as User

from .models import (
    Follow,
    Ingredients,
    IngredientsInRecipes,
    Recipes,
    Tags,
    TagsInRecipes,
)


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ("id", "name", "color", "slug")


class IngredientsSerializer(serializers.ModelSerializer):
    # name = serializers.SlugRelatedField(
    #    queryset=Ingredients.objects.all(),
    #    slug_field="name",
    # )

    class Meta:
        model = Ingredients
        fields = ("id", "name", "measurement_unit")


class IngredientsRecipesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source="ingredients.id",
        read_only=True,
    )
    # ingredient = serializers.SlugRelatedField(
    #    queryset=Ingredients.objects.all(),
    #    slug_field="name",
    # )
    name = serializers.CharField(
        source="ingredients.name",
        read_only=True,
    )
    measurement_unit = serializers.CharField(
        source="ingredients.measurement_unit",
        read_only=True,
    )

    class Meta:
        model = IngredientsInRecipes
        fields = ("id", "name", "number", "measurement_unit")
        # read_only_fields = "ingredient"


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f"temp.{ext}")
        return super().to_internal_value(data)


class RecipesSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field="id",
        default=serializers.CurrentUserDefault(),
    )
    ingredients = IngredientsRecipesSerializer(
        source="recipes_ingredients",
        many=True,
        #    read_only=True,
    )
    # ingredients = IngredientsRecipesSerializer(
    #    source="recipes_ingredients",
    #    many=True,
    # read_only=True,
    # )
    tags = TagsSerializer(
        # source="recipes_tags",
        many=True,
        read_only=True,
    )
    image = Base64ImageField(
        required=True,
    )

    class Meta:
        model = Recipes
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            # "is_favorited",
            # "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def create(self, validated_data):
        print(self.initial_data["tags"])
        print(self.initial_data)
        print(validated_data)
        ingredients = validated_data.pop("recipes_ingredients")
        # Уберем ingredients из словаря validated_data и сохраним его
        # Создадим рецепт пока без ingredients
        recipe = Recipes.objects.create(**validated_data)

        for ingredient in ingredients:
            try:
                current_ingredient = ingredient.get("ingredient")
                # current_ingredient = Ingredients.objects.get(name=ingredient)
                number = ingredient.get("number")
                IngredientsInRecipes.objects.create(
                    ingredient=current_ingredient,
                    recipe=recipe,
                    number=number,
                )
            except Ingredients.DoesNotExist:
                pass

        for tag in self.initial_data["tags"]:
            try:
                current_tag = Tags.objects.get(id=tag)
                TagsInRecipes.objects.create(
                    tag=current_tag,
                    recipe=recipe,
                )
            except Tags.DoesNotExist:
                pass
        return recipe

    def to_representation(self, instance):
        data = super().to_representation(instance)
        author = get_object_or_404(User, id=data["author"])
        data["author"] = {
            "email": author.email,
            "id": author.id,
            "username": author.username,
            "first_name": author.first_name,
            "last_name": author.last_name,
            # "is_subscribed": data["is_subscribed"],
            # "recipes": following_recipes,
            # "recipes_count": recipes_count,
        }
        return data


class FollowUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ("following",)


class FollowSerializer(serializers.ModelSerializer):
    following = serializers.SlugRelatedField(
        queryset=User.objects.all(), slug_field="id"
    )
    user = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field="id",
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Follow
        fields = ("id", "user", "following", "is_subscribed")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        following = get_object_or_404(User, id=data["following"])
        following_recipes = Recipes.objects.filter(author=following.id)
        recipes_count = len(following_recipes)
        data = {
            "email": following.email,
            "id": following.id,
            "username": following.username,
            "first_name": following.first_name,
            "last_name": following.last_name,
            "is_subscribed": data["is_subscribed"],
            "recipes": following_recipes,
            "recipes_count": recipes_count,
        }
        return data

    validators = [
        UniqueTogetherValidator(
            queryset=Follow.objects.all(), fields=("user", "following")
        )
    ]
