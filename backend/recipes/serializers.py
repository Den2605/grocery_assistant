import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import CustomUser as User

from .models import (
    Follow,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    Tag,
    TagInRecipe,
)

# from users.serializers import CustomUserSerializer


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IngredientRecipeSerializer(serializers.ModelSerializer):
    ingredient = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Ingredient.objects.all(),
    )
    id = serializers.IntegerField(
        source="ingredient.id",
        read_only=True,
    )
    # name = serializers.CharField(
    #    source="ingredients.name",
    #    read_only=True,
    # )
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit",
        read_only=True,
    )

    class Meta:
        model = IngredientInRecipe
        # read_only = "ingredient"
        fields = (
            "id",
            "ingredient",
            #    "name",
            "number",
            "measurement_unit",
        )
        read_only_field = "ingredient"


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f"temp.{ext}")
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field="id",
        default=serializers.CurrentUserDefault(),
    )
    ingredients = IngredientRecipeSerializer(
        source="recipe_in",
        many=True,
    )
    tags = TagSerializer(
        many=True,
        read_only=True,
    )
    image = Base64ImageField(
        required=True,
    )

    class Meta:
        model = Recipe
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
        print(validated_data)
        ingredients = validated_data.pop("recipe_in")
        recipe = Recipe.objects.create(**validated_data)
        print(">>>")
        for tag in self.initial_data["tags"]:
            try:
                current_tag = Tag.objects.get(id=tag)
                TagInRecipe.objects.create(
                    tag=current_tag,
                    recipe=recipe,
                )
            except Tag.DoesNotExist:
                pass
        print(">>>")
        for ingredient in ingredients:
            try:
                current_ingredient = ingredient.get("ingredient")
                print(current_ingredient)
                number = ingredient.get("number")
                print(ingredient["number"])
                IngredientInRecipe.objects.create(
                    ingredient=current_ingredient,
                    recipe=recipe,
                    number=number,
                )
            except Ingredient.DoesNotExist:
                pass
        print(validated_data)
        return recipe

    def update(self, instance, validated_data):
        instance.author = validated_data.get("author", instance.author)
        instance.name = validated_data.get("name", instance.name)
        instance.image = validated_data.get("image", instance.image)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        instance.save()
        return instance
        # return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        print(data)
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
        following_recipes = Recipe.objects.filter(author=following.id)
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
