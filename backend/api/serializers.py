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
    """Сереализатор информации о пользователе."""

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
        """Метод получение статуса подписки на пользователя."""
        request = self.context.get("request")
        user = request.user
        return (
            user.is_authenticated
            and Follow.objects.filter(user=user.id, following=obj.id).exists()
        )


class TagSerializer(serializers.ModelSerializer):
    """Сереализатор тегов."""

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    """Сереализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Список ингредиентов с количеством для рецепта."""

    id = serializers.IntegerField(source="ingredient.id")

    name = serializers.CharField(
        source="ingredient.name",
        read_only=True,
    )
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit",
        read_only=True,
    )

    class Meta:
        model = IngredientInRecipe
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сереализатор списка рецептов."""

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
        """Проверка - находится ли рецепт в списке покупок."""
        request = self.context.get("request")
        user = request.user
        return Basket.objects.filter(user=user.id, recipe=obj.id).exists()

    def get_is_favorited(self, obj):
        """Проверка - находится ли рецепт в избранном."""
        request = self.context.get("request")
        user = request.user
        return Favorite.objects.filter(user=user.id, recipe=obj.id).exists()


class RecipeSerializer(serializers.ModelSerializer):
    """Сереализатор создания, удаления, редактирования рецепта."""

    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        source="recipes",
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
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
        """Метод валидации тегов для создания рецептов."""
        if not tags:
            raise ValidationError("Поле тег не может быть пустым.")
        if len(tags) != len(set(tags)):
            raise ValidationError(f"{tags} уже выбран.")
        return tags

    def validate_ingredients(self, data):
        """Метод валидации ингредиентов для создания рецепта."""
        if not data:
            raise ValidationError("Добавьте ингредиенты.")
        ingredients_list = []
        for ingredient in data:
            if int(ingredient["amount"]) < 1:
                raise ValidationError("Поле количества ингредиентов пусто.")
            id = ingredient["ingredient"]["id"]
            if id in ingredients_list:
                raise ValidationError(f"Ингредиент id={id} уже есть в списке.")
            ingredients_list.append(id)
        return data

    def ingredients_recipe(self, recipe, ingredients):
        """Вспомогательный метод для обработки
        создания объектов IngredientInRecipe.
        """
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
        """Создание рецепта."""
        ingredients = validated_data.pop("recipes")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        return self.ingredients_recipe(recipe, ingredients)

    def update(self, recipe, validated_data):
        """Редактирование рецепта."""
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


class ShoppincartSerializer(serializers.ModelSerializer):
    """Сереализатор добавления рецепта в карзину."""

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


class FavoriteSerializer(serializers.ModelSerializer):
    """Сереализатор добавления рецепта в избранное."""

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


class RecipeFollowSerializer(serializers.ModelSerializer):
    """
    Сереализатор для отображения рецептов авторов
    на которых подписан пользователь.
    """

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


class AuthorGetSerializer(serializers.ModelSerializer):
    """Сереализатор Подписок. для GET запроса."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField()

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
        """Метод получение рецепта."""
        request = self.context.get("request")
        recipes_limit = request.GET.get("recipes_limit")
        recipe = obj.recipes.all()
        if recipes_limit is not None and recipes_limit.isdigit():
            recipe = recipe[: int(recipes_limit)]
        return RecipeFollowSerializer(recipe, many=True).data


class FollowSerializer(serializers.ModelSerializer):
    """Сереализатор добавления подписки."""

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

    def validate_following(self, value):
        """Проверка подписчика."""
        if value.id == self.initial_data["user"]:
            raise serializers.ValidationError("Нельзя подписаться на себя.")
        return value
