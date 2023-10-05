from django.forms import ValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.fields import Base64ImageField
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


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request.user.is_authenticated:
            return Follow.objects.filter(
                user=request.user.id, following=obj.id
            ).exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient.id")

    name = serializers.CharField(
        source="ingredient.name",
        read_only=True,
    )
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit",
        read_only=True,
    )

    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class RecipeGetSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(source="recipe_in", many=True)
    tags = TagSerializer(many=True)
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
        return Basket.objects.filter(user=user.id, recipe=obj.id).exists()

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        user = request.user
        return Favorite.objects.filter(user=user.id, recipe=obj.id).exists()


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        source="recipes",
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
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
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def validate_tags(self, tags):
        if not tags:
            raise ValidationError("Поле тег не может быть пустым.")
        if len(tags) != len(set(tags)):
            raise ValidationError(f"{tags} уже выбран.")
        return tags

    def validate_ingredients(self, data):
        if not data:
            raise ValidationError("Добавьте ингредиенты.")
        ingredients_list = []
        for ingredient in data:
            if int(ingredient["amount"]) < 1:
                raise ValidationError(
                    "Заполните поле количества ингредиентов."
                )
            id = ingredient["ingredient"]["id"]
            if id in ingredients_list:
                raise ValidationError(
                    f"Ингредиент id = {id} уже есть в списке."
                )
            ingredients_list.append(id)
        return data

    def ingredients_recipe(self, recipe, ingredients):
        ingredient_obj = []
        for ingredient in ingredients:
            amount = ingredient.get("amount")
            id = ingredient.get("ingredient")["id"]
            ingredient_obj.append(
                IngredientInRecipe(
                    ingredient_id=id,
                    recipe=recipe,
                    amount=amount,
                )
            )
        IngredientInRecipe.objects.bulk_create(ingredient_obj)
        return recipe

    def create(self, validated_data):
        ingredients = validated_data.pop("recipes")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        return self.ingredients_recipe(recipe, ingredients)

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop("recipes")
        tags = validated_data.pop("tags")
        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)
        if ingredients:
            recipe.ingredients.clear()
            self.ingredients_recipe(recipe, ingredients)
        super().update(instance=self.instance, validated_data=validated_data)
        return recipe

    def to_representation(self, instance):
        serializer = RecipeGetSerializer(
            instance, context={"request": self.context.get("request")}
        )
        return serializer.data


def delete_recipe_user(data):
    if data["recipe"]:
        del data["recipe"]
    if data["user"]:
        del data["user"]
    return data


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
        delete_recipe_user(data)
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
        delete_recipe_user(data)
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
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )


# class GetRecipe:
#    def get_author_recipes(self, obj):
#        recipes_limit = self.context.get("recipes_limit")
#        if recipes_limit:
#           recipe = Recipe.objects.filter(author=obj.id)[: int(recipes_limit)]
#        else:
#            recipe = Recipe.objects.filter(author=obj.id)
#        return RecipeFollowSerializer(recipe, many=True).data


# class AuthorSerializer(serializers.ModelSerializer, GetRecipe):
#    recipes = serializers.SerializerMethodField(read_only=True)
#    recipes_count = serializers.SerializerMethodField()
#
#    class Meta:
#        model = User
#        fields = (
#            "email",
#            "id",
#            "username",
#            "first_name",
#            "last_name",
#            "recipes",
#            "recipes_count",
#        )

#    def get_recipes(self, obj):
#        return super().get_author_recipes(obj)

#    def get_recipes_count(self, obj):
#        return self.context.get("recipes_count")

#    def to_representation(self, instance):
#        data = super().to_representation(instance)
#        data["is_subscribed"] = True
#        return data


class AuthorGetSerializer(serializers.ModelSerializer):
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
            recipe = Recipe.objects.filter(author=obj.id)[: int(recipes_limit)]
        else:
            recipe = Recipe.objects.filter(author=obj.id)
        return RecipeFollowSerializer(recipe, many=True).data
        # return super().get_author_recipes(obj)

    def get_recipes_count(self, obj):
        recipe_count = Recipe.objects.filter(author=obj.id).count()
        return recipe_count


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
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(), fields=("user", "following")
            )
        ]
