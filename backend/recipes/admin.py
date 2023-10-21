from django.contrib import admin

from .models import (
    Basket,
    Favorite,
    Follow,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    Tag,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "color",
        "slug",
    )
    empty_value_display = "-пусто-"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "measurement_unit",
    )
    search_fields = ("name",)
    empty_value_display = "-пусто-"


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    min_num = 1
    extra = 3


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "author",
        "image",
        "text",
        "cooking_time",
        "pub_date",
        "in_favorites",
        "get_ingredients",
    )
    search_fields = (
        "name",
        "author",
        "tags",
    )
    list_filter = (
        "name",
        "author",
    )
    inlines = (IngredientInRecipeInline,)
    empty_value_display = "-пусто-"

    @admin.display(description="В избранном")
    def in_favorites(self, obj):
        return obj.recipe_favorite.all().count()

    @admin.display(description="Ингредиенты")
    def get_ingredients(self, obj):
        ingredients_list = []
        for ingredient in obj.ingredients.all():
            ingredients_list.append(ingredient.name.lower())
        return ", ".join(ingredients_list)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "following",
    )
    search_fields = (
        "user",
        "following",
    )


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "recipe",
    )
    empty_value_display = "-пусто-"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "recipe",
    )
    empty_value_display = "-пусто-"
