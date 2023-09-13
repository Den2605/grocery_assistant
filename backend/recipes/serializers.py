import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from recipes.models import Follow, Ingredients, Recipes, Tags, TagsInRecipes
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import CustomUser as User


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ("id", "name", "color", "slug")


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ("id", "name", "number", "measurement_unit")


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
    # ingredients = IngredientsSerializer(
    #    source="recipes_ingredients",
    #    many=True,
    #    read_only=True,
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
            # "ingredients",
            # "is_favorited",
            # "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def create(self, validated_data):
        print(self.initial_data["tags"])
        print(validated_data)
        # Уберем tags из словаря validated_data и сохраним его
        # tags = validated_data.pop("tags")

        # Создадим рецепт пока без тега
        recipe = Recipes.objects.create(**validated_data)

        #
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
