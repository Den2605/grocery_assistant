import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import (
    Basket,
    Favorite,
    Follow,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    Tag,
    TagInRecipe,
)
from users.models import CustomUser as User
from users.serializers import CustomUserSerializer


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
    author = CustomUserSerializer(read_only=True)
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
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        user = request.user
        if request.method == "GET" or "PATCH":
            if Basket.objects.filter(user=user.id, recipe=obj.id).exists():
                return True
            return False
        return False

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        user = request.user
        if request.method == "GET" or "PATCH":
            if Favorite.objects.filter(user=user.id, recipe=obj.id).exists():
                return True
            return False
        return False

    def create(self, validated_data):
        ingredients = validated_data.pop("recipe_in")
        recipe = Recipe.objects.create(**validated_data)
        for tag in self.initial_data["tags"]:
            try:
                current_tag = Tag.objects.get(id=tag)
                TagInRecipe.objects.create(
                    tag=current_tag,
                    recipe=recipe,
                )
            except Tag.DoesNotExist:
                pass
        for ingredient in ingredients:
            try:
                current_ingredient = ingredient.get("ingredient")
                number = ingredient.get("number")
                IngredientInRecipe.objects.create(
                    ingredient=current_ingredient,
                    recipe=recipe,
                    number=number,
                )
            except Ingredient.DoesNotExist:
                pass
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


class ShoppincartSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="recipe.name")
    image = Base64ImageField(source="recipe.image")
    cooking_time = serializers.IntegerField(source="recipe.cooking_time")

    class Meta:
        model = Basket
        fields = ("id", "name", "image", "cooking_time", "recipe", "user")
        validators = [
            UniqueTogetherValidator(
                queryset=Basket.objects.all(), fields=("user", "recipe")
            )
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        del data["recipe"]
        del data["user"]
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="recipe.name")
    image = Base64ImageField(source="recipe.image")
    cooking_time = serializers.IntegerField(source="recipe.cooking_time")

    class Meta:
        model = Favorite
        fields = ("id", "name", "image", "cooking_time", "recipe", "user")
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(), fields=("user", "recipe")
            )
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        del data["recipe"]
        del data["user"]
        return data


class RecipeFollowSerializer(serializers.ModelSerializer):
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
            # "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )


class AuthorSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        recipes_limit = self.context.get("recipes_limit")
        if recipes_limit:
            recipe = Recipe.objects.all()[: int(recipes_limit)]
        else:
            recipe = Recipe.objects.all()
        return RecipeFollowSerializer(
            recipe, many=True, source="recipes_user"
        ).data

    def get_recipes_count(self, obj):
        return self.context.get("recipes_count")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["is_subscribe"] = True
        return data


class AuthorGetSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "recipes",
        )

    def get_recipes(self, obj):
        request = self.context["request"]
        recipes_limit = request.query_params.get("recipes_limit", None)
        if recipes_limit:
            recipe = Recipe.objects.all()[: int(recipes_limit)]
        else:
            recipe = Recipe.objects.all()
        return RecipeFollowSerializer(
            recipe, many=True, source="recipes_user"
        ).data


class FollowSerializer(serializers.ModelSerializer):
    def validate_following(self, value):
        if value.id == self.initial_data["user"]:
            raise serializers.ValidationError(
                "Нельзя подписаться на самого себя."
            )
        return value

    class Meta:
        model = Follow
        fields = (
            "id",
            "user",
            "following",
            "is_subscribed",
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(), fields=("user", "following")
            )
        ]
