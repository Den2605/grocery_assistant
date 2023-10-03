from django_filters import rest_framework as filter
from rest_framework import filters

from recipes.models import Recipe


class CustomSearchFilter(filters.SearchFilter):
    search_param = "name"


class RecipeFilter(filter.FilterSet):
    author = filter.NumberFilter(field_name="author__id")
    tags = filter.CharFilter(field_name="tags__slug")
    is_favorited = filter.BooleanFilter(method="is_favorite")
    is_in_shopping_cart = filter.BooleanFilter(method="shopping_cart")

    class Meta:
        model = Recipe
        fields = [
            "author",
            "tags",
            "is_favorited",
            "is_in_shopping_cart",
        ]

    def is_favorite(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(recipe_favorite__user=user)
        return queryset

    def shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(baskets__user=user)
        return queryset
